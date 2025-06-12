import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QFileDialog, QDockWidget, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtGui import QPen, QColor
import heapq
from typing import List, Tuple
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter
from PyQt6.QtCore import Qt


class Image(QLabel):
    def __init__(self, chemin: str, taille_cellule: int = 10):
        super().__init__()
        self.taille_cellule = taille_cellule
        self.image = QPixmap(chemin)
        
        # Redimensionnement avec la même logique que l'App1
        ecran = QApplication.primaryScreen().availableGeometry()
        largeur_max = int(ecran.width() * 0.8)
        hauteur_max = int(ecran.height() * 0.8)

        self.image_redim = self.image.scaled(
            largeur_max, hauteur_max,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        print("Image redimensionnée en:", self.image_redim.size())

        self.produits = []
        self.chemin_optimal = []  # Stockage du chemin optimal
        self.setPixmap(self.image_redim)
        self.setFixedSize(self.image_redim.size())
        
        # Initialiser le chemin
        self.chemin = Chemin(
            self.image_redim.width(), 
            self.image_redim.height(), 
            taille_cellule
        )

    def set_produits(self, coordonnees):
        self.produits = coordonnees
        self.repaint()

    def set_chemin_optimal(self, chemin: List[Tuple[int, int]]):
        self.chemin_optimal = chemin
        self.repaint()

    def calculer_et_afficher_chemin(self, coordonnees_produits: List[Tuple[int, int]]):
        if not coordonnees_produits:
            self.chemin_optimal = []
            self.repaint()
            return
        
        # Calculer le chemin optimal
        chemin, distance = self.chemin.calculer_chemin_optimal(coordonnees_produits)
        
        if chemin:
            self.set_chemin_optimal(chemin)
            print(f"Chemin optimal calculé: {len(chemin)} points, distance: {distance:.2f}")
        else:
            self.chemin_optimal = []
            self.repaint()
            print("Aucun chemin optimal trouvé")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        # Décalage comme dans l'App1
        decalage = 7
        
        if self.chemin_optimal:
            painter.setPen(QPen(Qt.GlobalColor.blue, 3))
            
            for i in range(len(self.chemin_optimal) - 1):
                x1, y1 = self.chemin_optimal[i]
                x2, y2 = self.chemin_optimal[i + 1]
                
                # Convertion des coordonnées de grille en pixels
                px1 = x1 * self.taille_cellule + decalage + self.taille_cellule // 2
                py1 = y1 * self.taille_cellule + self.taille_cellule // 2
                px2 = x2 * self.taille_cellule + decalage + self.taille_cellule // 2
                py2 = y2 * self.taille_cellule + self.taille_cellule // 2
                
                painter.drawLine(px1, py1, px2, py2)
        
        # Dessin pour point de départ / Caisse
        painter.setPen(Qt.GlobalColor.green)
        painter.setBrush(Qt.GlobalColor.green)
        
        # Point d'entrée
        entree_x = self.chemin.entree[0] * self.taille_cellule + decalage
        entree_y = self.chemin.entree[1] * self.taille_cellule
        painter.drawEllipse(entree_x - 8, entree_y - 8, 16, 16)
        
        # Point de caisse
        painter.setPen(Qt.GlobalColor.magenta)
        painter.setBrush(Qt.GlobalColor.magenta)
        caisse_x = self.chemin.caisse[0] * self.taille_cellule + decalage
        caisse_y = self.chemin.caisse[1] * self.taille_cellule
        painter.drawRect(caisse_x - 10, caisse_y - 10, 20, 20)
        
        if self.produits:
            painter.setPen(Qt.GlobalColor.red)
            painter.setBrush(Qt.GlobalColor.red)
            
            # Taille du carré rouge pour la position des produits
            size = 12
            
            for coord in self.produits:
                if not coord or len(coord) < 2:
                    continue
                    
                grid_x, grid_y = coord
                
                px = grid_x * self.taille_cellule + decalage - size // 2
                py = grid_y * self.taille_cellule - size // 2
                
                # Vérifier que les coordonnées sont dans les limites de l'image
                if 0 <= px < self.image_redim.width() and 0 <= py < self.image_redim.height():
                    painter.drawRect(px, py, size, size)
        
        painter.end()
    
    def _dessiner_zones_bloquees(self, painter, decalage):
        """Dessine les zones bloquées (pour débogage)"""
        painter.setPen(Qt.GlobalColor.gray)
        painter.setBrush(QColor(128, 128, 128, 100)) 
        
        for x, y in self.chemin.zones_bloquees:
            px = x * self.taille_cellule + decalage
            py = y * self.taille_cellule
            painter.drawRect(px, py, self.taille_cellule, self.taille_cellule)


class Chemin:
    def __init__(self, largeur: int, hauteur: int, taille_cellule: int = 10):
        self.largeur = largeur
        self.hauteur = hauteur
        self.taille_cellule = taille_cellule
        self.grille_largeur = largeur // taille_cellule
        self.grille_hauteur = hauteur // taille_cellule
        
        # Zones bloquées
        self.zones_bloquees = set()
        self._definir_zones_bloquees()
        
        self.entree = (62, 58)  # Position de l'entrée
        self.caisse = (35, 56)  # Position de la caisse
    
    def _definir_zones_bloquees(self):
        """Définit les zones qui ne peuvent pas être traversées"""
        rayons = [
            # Rayon horizontal
            ((68, 8), (80, 9)), 
            ((22, 1), (29, 1)),
            ((33, 1), (47, 1)),
            ((49, 3), (57, 4)),
            ((59, 3), (80, 4)),
            ((68, 12), (80, 13)),
            ((68, 16), (80, 17)),
            ((68, 20), (80, 21)),

            ((68, 24), (80, 25)),
            ((68, 28), (80, 29)),
            ((68, 32), (80, 34)),
            ((68, 37), (80, 38)),
            ((68, 41), (80, 42)),
            ((68, 45), (80, 46)),
            ((68, 49), (80, 50)),
            ((68, 53), (80, 55)),
            ((68, 57), (84, 58)),
            ((4, 59), (18, 59)),
            ((12, 2), (19, 3)),
            
            # Rayon vertical
            ((2, 9), (3, 28)),
            ((2, 33), (3, 59)),
            ((7, 9), (8, 28)),
            ((7, 33), (8, 51)),
            ((12, 33), (13, 41)),
            ((12, 44), (13, 51)),
            ((13, 8), (14, 28)),
            ((16, 33), (17, 41)),

            ((16, 44), (17, 51)),
            ((18, 8), (19, 28)),
            ((21, 33), (22, 41)),
            ((21, 44), (22, 51)),
            ((23, 8), (25, 16)),
            ((23, 19), (25, 19)),
            ((23, 22), (25, 28)),

            ((25, 33), (26, 41)),
            ((25, 44), (26, 41)),
            ((29, 8), (31, 28)),
            ((29, 33), (30, 41)),
            ((29, 44), (30, 51)),
            ((35, 8), (36, 16)),
            ((35, 20), (36, 28)),

            ((33, 33), (35, 51)),
            ((38, 33), (39, 41)),
            ((38, 44), (39, 51)),
            ((40, 8), (42, 28)),
            ((42, 33), (43, 41)),
            ((42, 44), (43, 51)),
            ((45, 8), (47, 28)),

            ((48, 33), (49, 41)),
            ((46, 48), (51, 51)),
            ((50, 8), (52, 28)),
            ((54, 8), (55, 16)),
            ((54, 20), (55, 28)),
            ((54, 33), (55, 41)),
            ((54, 44), (55, 51)),

            ((58, 8), (60, 28)),
            ((58, 33), (60, 51)),
            ((84, 7), (84, 56)),
            
            # Zones spéciale (poisson)
            ((2, 6), (3, 6)), 
            ((3, 5), (4, 5)), 
            ((4, 4), (5, 4)), 
            ((5, 3), (6, 3)), 
            ((6, 2), (7, 2))
        ]
        
        # Ajouter tous les points des rayons aux zones bloquées
        for (x1, y1), (x2, y2) in rayons:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 <= x < self.grille_largeur and 0 <= y < self.grille_hauteur:
                        self.zones_bloquees.add((x, y))
    
    #Verifie qu'une position est valide
    def est_position_valide(self, x: int, y: int) -> bool:
        return (0 <= x < self.grille_largeur and 
                0 <= y < self.grille_hauteur and 
                (x, y) not in self.zones_bloquees)
    

    def obtenir_voisins(self, x: int, y: int) -> List[Tuple[int, int, float]]:
        voisins = []
        directions = [
            (-1, 0, 1.0),   # Gauche
            (1, 0, 1.0),    # Droite  
            (0, -1, 1.0),   # Haut
            (0, 1, 1.0),    # Bas
            (-1, -1, 1.4),  # Diagonale haut-gauche
            (1, -1, 1.4),   # Diagonale haut-droite
            (-1, 1, 1.4),   # Diagonale bas-gauche
            (1, 1, 1.4),    # Diagonale bas-droite
        ]
        
        for dx, dy, cout in directions:
            nx, ny = x + dx, y + dy
            if self.est_position_valide(nx, ny):
                voisins.append((nx, ny, cout))
        
        return voisins
    
    # Algo de Dijkstra -> Détermine chemin le plus court
    def dijkstra(self, debut: Tuple[int, int], fin: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        # File de priorité : (distance, x, y)
        file_priorite = [(0, debut[0], debut[1])]
        
        # Distances minimales
        distances = {debut: 0}
        
        # Prédécesseurs pour reconstruire le chemin
        predecesseurs = {}
        
        # Ensemble des nœuds visités
        visites = set()
        
        while file_priorite:
            dist_actuelle, x, y = heapq.heappop(file_priorite)
            
            if (x, y) in visites:
                continue
                
            visites.add((x, y))
        
            if (x, y) == fin:
                break
        
            for nx, ny, cout in self.obtenir_voisins(x, y):
                if (nx, ny) not in visites:
                    nouvelle_distance = dist_actuelle + cout
                    
                    if (nx, ny) not in distances or nouvelle_distance < distances[(nx, ny)]:
                        distances[(nx, ny)] = nouvelle_distance
                        predecesseurs[(nx, ny)] = (x, y)
                        heapq.heappush(file_priorite, (nouvelle_distance, nx, ny))
        
        if fin not in predecesseurs and fin != debut:
            # Cas ou aucun chemin trouvé
            return [], float('inf')  
        
        chemin = []
        actuel = fin
        while actuel is not None:
            chemin.append(actuel)
            actuel = predecesseurs.get(actuel)
        chemin.reverse()
        distance_totale = distances.get(fin, float('inf'))
        
        return chemin, distance_totale
    

    # Calcul du chemin le meilleur
    def calculer_chemin_optimal(self, positions_produits: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], float]:
        if not positions_produits:
            return [], 0
        
        points_a_visiter = [self.entree] + positions_produits + [self.caisse]
        if len(points_a_visiter) <= 3:  # entrée + produit + caisse
            chemin_complet = []
            distance_totale = 0
            for i in range(len(points_a_visiter) - 1):
                chemin_segment, distance = self.dijkstra(points_a_visiter[i], points_a_visiter[i + 1])
                if chemin_segment:
                    if chemin_complet:
                        chemin_segment = chemin_segment[1:] 
                    chemin_complet.extend(chemin_segment)
                    distance_totale += distance
                else:
                    return [], float('inf') 
            
            return chemin_complet, distance_totale
        return self._chemin_glouton(points_a_visiter)
    
    def _chemin_glouton(self, points: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], float]:
        if len(points) <= 2:
            return self.dijkstra(points[0], points[-1])
        
        chemin_complet = []
        distance_totale = 0

        position_actuelle = points[0]
        points_restants = points[1:-1]  # Exclus entrée et caisse
        caisse = points[-1]
        
        while points_restants:
            distances_aux_points = []
            for point in points_restants:
                _, distance = self.dijkstra(position_actuelle, point)
                distances_aux_points.append((distance, point))
            
            distances_aux_points.sort()
            if distances_aux_points[0][0] == float('inf'):
                return [], float('inf')  # Pas de chemin possible
            
            prochain_point = distances_aux_points[0][1]
            points_restants.remove(prochain_point)
            
            # Calculer le chemin vers ce point
            chemin_segment, distance = self.dijkstra(position_actuelle, prochain_point)
            if chemin_segment:
                if chemin_complet:
                    chemin_segment = chemin_segment[1:]  # Éviter les doublons
                chemin_complet.extend(chemin_segment)
                distance_totale += distance
                position_actuelle = prochain_point
            else:
                return [], float('inf')
        
        # Aller à la caisse
        chemin_segment, distance = self.dijkstra(position_actuelle, caisse)
        if chemin_segment:
            if chemin_complet:
                chemin_segment = chemin_segment[1:]  # Éviter les doublons
            chemin_complet.extend(chemin_segment)
            distance_totale += distance
        else:
            return [], float('inf')
        
        return chemin_complet, distance_totale


class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin
        self.setWindowTitle("Votre première application à l'IUT")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 500, 300)

        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("L'application est démarrée...", 2000)

        menu_bar = self.menuBar()
        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_fichier.addAction('Ouvrir', self.ouvrir)
        menu_fichier.addAction('Enregistrer', self.enregistrer)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.destroy)

        barre_outil = QToolBar('Principaux outils')
        self.addToolBar(barre_outil)

        action_rechercher_magasin = QAction('Rechercher un magasin', self)
        action_rechercher_magasin.triggered.connect(self.demander_nom_magasin)
        barre_outil.addAction(action_rechercher_magasin)

        self.arbre = None
        self.recherche_input = None
        self.billet_liste = None
        self.image = None
        self.showMaximized()

    # Affiche tous les produits et calcule la meilleure distance
    def afficher_tous_les_produits(self):
        coordonnees = []
        for i in range(self.billet_liste.topLevelItemCount()):
            item = self.billet_liste.topLevelItem(i)
            coord = item.data(0, Qt.ItemDataRole.UserRole)
            if coord and len(coord) >= 2:
                coordonnees.append(tuple(coord))

        if self.image:
            self.image.set_produits(coordonnees)
            # Calculer et afficher le chemin optimal
            self.image.calculer_et_afficher_chemin(coordonnees)

    def mettre_a_jour_carre_rouge(self):
        if not self.billet_liste or not self.image:
            return

        coordonnees = []
        items = self.billet_liste.selectedItems()
        
        if items:
            # Affiche seulement les produits sélectionnés
            for item in items:
                coord = item.data(0, Qt.ItemDataRole.UserRole)
                if coord and len(coord) >= 2:
                    coordonnees.append(tuple(coord))
            
            self.image.set_produits(coordonnees)
            self.image.calculer_et_afficher_chemin(coordonnees)
        else:
            # Si aucun produit sélectionné, affiche tous les produits de la liste
            self.afficher_tous_les_produits()

    def ouvrir(self):
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory=sys.path[0])
        if validation:
            self.__chemin = chemin
            self.affiche_image()

    def enregistrer(self):
        boite = QFileDialog()
        chemin, validation = boite.getSaveFileName(directory=sys.path[0])
        if validation:
            self.__chemin = chemin

    def affiche_image(self, coordonnees=None, taille_cellule=10):
        self.image = Image(self.__chemin, taille_cellule=taille_cellule)
        if coordonnees:
            self.image.set_produits(coordonnees)
            self.image.calculer_et_afficher_chemin(coordonnees)
        else:
            self.image.set_produits([])

        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)

    def demander_nom_magasin(self):
        self.voile = QWidget(self)
        self.voile.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        self.voile.setGeometry(self.rect())
        self.voile.show()

        self.popup = QWidget(self.voile)
        self.popup.setFixedSize(400, 150)
        self.popup.move(
            self.width() // 2 - 200,
            self.height() // 2 - 75
        )
        self.popup.setStyleSheet("background-color: white; border: 2px solid black;")

        layout = QVBoxLayout(self.popup)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Entrez le nom du magasin...")
        self.nom_input.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(self.nom_input)

        bouton_valider = QPushButton("Valider")
        bouton_valider.clicked.connect(lambda: self.traiter_recherche_magasin(self.nom_input.text()))
        layout.addWidget(bouton_valider)

        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.fermer_popup)
        layout.addWidget(bouton_annuler)

        self.popup.show()

    def fermer_popup(self):
        self.voile.close()
        self.popup.close()

    def traiter_recherche_magasin(self, nom_magasin):
        if not nom_magasin.strip():
            return

        fichier = f"{nom_magasin.strip()}_liste_produits.json"
        chemin_complet = os.path.join(os.path.dirname(__file__), "..", "Application1", "listes_produits_entreprise", f"{fichier}")

        try:
            with open(chemin_complet, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Magasin introuvable",
                f"Le magasin '{nom_magasin}' n'existe pas. Veuillez réesayer"
            )
            return  
        
        self.voile.close()
        self.popup.close()

        self.creer_dock_liste()

        self.arbre.clear()
        for categorie, produits in data.items():
            item_categorie = QTreeWidgetItem([categorie])
            for produit in produits:
                item_produit = QTreeWidgetItem([produit["nom"]])
                item_produit.setData(0, Qt.ItemDataRole.UserRole, produit.get("coordonnées"))
                item_produit.setCheckState(0, Qt.CheckState.Unchecked)
                item_categorie.addChild(item_produit)
            self.arbre.addTopLevelItem(item_categorie)

        self.__chemin = os.path.join(os.path.dirname(__file__), "images", "plan.jpg")
        self.affiche_image()

    def creer_dock_liste(self):
        self.dock = QDockWidget("Liste des produits", self)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)

        widget_contenu = QWidget()
        layout = QVBoxLayout(widget_contenu)

        self.recherche_input = QLineEdit()
        self.recherche_input.setPlaceholderText("Rechercher un produit...")
        bouton_recherche = QPushButton("Rechercher")
        bouton_recherche.clicked.connect(self.rechercher_produit)
        bouton_ajouter = QPushButton("Ajouter à la liste")
        bouton_ajouter.clicked.connect(self.ajouter_a_liste)

        layout.addWidget(self.recherche_input)
        layout.addWidget(bouton_recherche)
        layout.addWidget(bouton_ajouter)

        self.arbre = QTreeWidget()
        self.arbre.setHeaderLabels(["Catégories et Produits"])
        layout.addWidget(self.arbre)

        self.dock.setWidget(widget_contenu)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        self.creer_liste_course()

    def creer_liste_course(self):
        if self.billet_liste:
            return

        self.billet_course = QDockWidget("Liste de course", self)
        self.billet_course.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)

        widget_billet = QWidget()
        layout_billet = QVBoxLayout(widget_billet)

        self.billet_liste = QTreeWidget()
        self.billet_liste.itemSelectionChanged.connect(self.mettre_a_jour_carre_rouge)

        self.billet_liste.setHeaderLabels(["Produit", "Supprimer"])
        layout_billet.addWidget(self.billet_liste)

        # Bouton pour voir tous les produits sur la carte
        bouton_afficher_tous = QPushButton("Afficher tous les produits avec chemin optimal")
        bouton_afficher_tous.clicked.connect(self.afficher_tous_les_produits)
        layout_billet.addWidget(bouton_afficher_tous)

        # Bouton pour effacer le chemin
        bouton_effacer_chemin = QPushButton("Effacer le chemin")
        bouton_effacer_chemin.clicked.connect(self.effacer_chemin)
        layout_billet.addWidget(bouton_effacer_chemin)

        self.billet_course.setWidget(widget_billet)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.billet_course)

    def effacer_chemin(self):
        """Efface le chemin optimal affiché"""
        if self.image:
            self.image.set_chemin_optimal([])

    def rechercher_produit(self):
        terme = self.recherche_input.text().strip().lower()
        if not terme:
            return

        for i in range(self.arbre.topLevelItemCount()):
            categorie = self.arbre.topLevelItem(i)
            for j in range(categorie.childCount()):
                produit = categorie.child(j)
                if terme in produit.text(0).lower():
                    self.arbre.scrollToItem(produit)
                    produit.setSelected(True)
                    categorie.setExpanded(True)
                else:
                    produit.setSelected(False)

    def ajouter_a_liste(self):
        if not self.billet_liste:
            return

        for i in range(self.arbre.topLevelItemCount()):
            categorie = self.arbre.topLevelItem(i)
            for j in range(categorie.childCount()):
                produit = categorie.child(j)
                if produit.checkState(0) == Qt.CheckState.Checked:
                    item = QTreeWidgetItem(self.billet_liste)
                    item.setText(0, produit.text(0))
                    
                    # Stocker la coordonnée dans l'item de la liste de courses
                    coord = produit.data(0, Qt.ItemDataRole.UserRole)
                    item.setData(0, Qt.ItemDataRole.UserRole, coord)

                    bouton_supprimer = QPushButton("Supprimer")
                    bouton_supprimer.clicked.connect(lambda _, i=item: self.supprimer_produit(i))
                    self.billet_liste.setItemWidget(item, 1, bouton_supprimer)

                    produit.setCheckState(0, Qt.CheckState.Unchecked)

        # Mettre à jour l'affichage après ajout
        self.afficher_tous_les_produits()

    def supprimer_produit(self, item):
        index = self.billet_liste.indexOfTopLevelItem(item)
        if index >= 0:
            self.billet_liste.takeTopLevelItem(index)
        
        # Mettre à jour l'affichage après suppression
        self.afficher_tous_les_produits()

    def destroy(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreAppli()
    fenetre.show()
    sys.exit(app.exec())