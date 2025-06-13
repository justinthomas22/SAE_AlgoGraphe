# Vue
import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QFileDialog, QDockWidget, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtGui import QPen, QColor
from typing import List, Tuple
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter
from PyQt6.QtCore import Qt
from model import Chemin

class Image(QLabel):
    def __init__(self, chemin: str, taille_cellule: int = 10):
        super().__init__()
        self.taille_cellule = taille_cellule
        self.image = QPixmap(chemin)

        #Détermine la taille maximale de l'image redimensionnée en fonction de l'écran
        ecran = QApplication.primaryScreen().availableGeometry()
        largeur_max = int(ecran.width() * 0.8)
        hauteur_max = int(ecran.height() * 0.8)

        # Redimensionnement de l'imagetout mais en conservant son ratio d'aspect
        self.image_redim = self.image.scaled(
            largeur_max, hauteur_max,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        print("Image redimensionnée en:", self.image_redim.size())

        #Initialisation liste de produits et du chemin optimal
        self.produits = []
        self.chemin_optimal = []  
        self.setPixmap(self.image_redim)
        self.setFixedSize(self.image_redim.size())

        # Création d'un objet Chemin permettant de calculer les trajets
        self.chemin = Chemin(
            self.image_redim.width(),
            self.image_redim.height(),
            taille_cellule
        )

    # Définir les coordonnées des produits
    def set_produits(self, coordonnees):
        self.produits = coordonnees
        self.repaint()

    # Permet de stocker et afficher le chemin optimal 
    def set_chemin_optimal(self, chemin: List[Tuple[int, int]]):
        self.chemin_optimal = chemin
        self.repaint()

    # Calculer et afficher le chemin optimal pour les produits choisis
    def calculer_et_afficher_chemin(self, coordonnees_produits: List[Tuple[int, int]]):
        if not coordonnees_produits:
            self.chemin_optimal = []
            self.repaint()
            return

        # Permet de calculer le chemin optimal entre les produits
        chemin, distance = self.chemin.calculer_chemin_optimal(coordonnees_produits)

        if chemin:
            self.set_chemin_optimal(chemin)
            print(f"Chemin optimal calculé: {len(chemin)} points, distance: {distance:.2f}")
        else:
            self.chemin_optimal = []
            self.repaint()
            print("Aucun chemin optimal trouvé")

    # Permet de dessiner l'image ainsi que les chemins et les points spécifiques
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        # Décalage comme dans l'Application 1
        decalage = 7

        # Permet de dessinner le chemin optimal entre les produits en bleu 
        if self.chemin_optimal:
            painter.setPen(QPen(Qt.GlobalColor.blue, 3))

            for i in range(len(self.chemin_optimal) - 1):
                x1, y1 = self.chemin_optimal[i]
                x2, y2 = self.chemin_optimal[i + 1]

                px1 = x1 * self.taille_cellule + decalage + self.taille_cellule // 2
                py1 = y1 * self.taille_cellule + self.taille_cellule // 2
                px2 = x2 * self.taille_cellule + decalage + self.taille_cellule // 2
                py2 = y2 * self.taille_cellule + self.taille_cellule // 2

                painter.drawLine(px1, py1, px2, py2)

        # Permet de dessiner le point d'entrée en vert
        painter.setPen(Qt.GlobalColor.green)
        painter.setBrush(Qt.GlobalColor.green)
        entree_x = self.chemin.entree[0] * self.taille_cellule + decalage
        entree_y = self.chemin.entree[1] * self.taille_cellule
        painter.drawEllipse(entree_x - 8, entree_y - 8, 16, 16)

        # Permet de dessiner la caisse en magenta
        painter.setPen(Qt.GlobalColor.magenta)
        painter.setBrush(Qt.GlobalColor.magenta)
        caisse_x = self.chemin.caisse[0] * self.taille_cellule + decalage
        caisse_y = self.chemin.caisse[1] * self.taille_cellule
        painter.drawRect(caisse_x - 10, caisse_y - 10, 20, 20)

        # Permet de dessiner les produits en rouge
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

    #Dessine les zones bloquées
    def _dessiner_zones_bloquees(self, painter, decalage):
        painter.setPen(Qt.GlobalColor.gray)
        painter.setBrush(QColor(128, 128, 128, 100))

        for x, y in self.chemin.zones_bloquees:
            px = x * self.taille_cellule + decalage
            py = y * self.taille_cellule
            painter.drawRect(px, py, self.taille_cellule, self.taille_cellule)

class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin
        
        # Paramètres de la fenêtre principale
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

    # Affiche tous les produits enregistrés sur l'image.
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

    # Mise à jour de l'affichage des produits
    def mettre_a_jour_carre_rouge(self):
        if not self.billet_liste or not self.image:
            return

        coordonnees = []
        items = self.billet_liste.selectedItems()

        if items:
            # Affiche seulement les produits qui sont sélectionnés
            for item in items:
                coord = item.data(0, Qt.ItemDataRole.UserRole)
                if coord and len(coord) >= 2:
                    coordonnees.append(tuple(coord))

            self.image.set_produits(coordonnees)
            self.image.calculer_et_afficher_chemin(coordonnees)
        else:
            # Sinon, affiche tous les produits disponibles
            self.afficher_tous_les_produits()

    # Ouvre une boîte de dialogue pour sélectionner un fichier.
    def ouvrir(self):
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory=sys.path[0])
        if validation:
            self.__chemin = chemin
            self.affiche_image()

    # Ouvre une boîte de dialogue pour enregistrer un fichier.
    def enregistrer(self):
        boite = QFileDialog()
        chemin, validation = boite.getSaveFileName(directory=sys.path[0])
        if validation:
            self.__chemin = chemin

    # Affiche l'image principale et met à jour les produits et le chemin optimal
    def affiche_image(self, coordonnees=None, taille_cellule=10):
        self.image = Image(self.__chemin, taille_cellule=taille_cellule)
        if coordonnees:
            self.image.set_produits(coordonnees)
            self.image.calculer_et_afficher_chemin(coordonnees)
        else:
            self.image.set_produits([])

        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)

    # Affiche une fenêtre pop-up pour demander le nom du magasin à rechercher
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

    # Fermer la fenêtre pop-up
    def fermer_popup(self):
        self.voile.close()
        self.popup.close()

    # Recherche le magasin et charge ses produits
    def traiter_recherche_magasin(self, nom_magasin):
        if not nom_magasin.strip():
            return

        fichier = f"{nom_magasin.strip()}_liste_produits.json"
        chemin_complet = os.path.join(os.path.dirname(__file__), "..", "..", "Exemples_Projets_Application1", f"{fichier}")

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
        
        # Ajout des produits dans l'arborescence
        for categorie, produits in data.items():
            item_categorie = QTreeWidgetItem([categorie])
            for produit in produits:
                item_produit = QTreeWidgetItem([produit["nom"]])
                item_produit.setData(0, Qt.ItemDataRole.UserRole, produit.get("coordonnées"))
                item_produit.setCheckState(0, Qt.CheckState.Unchecked)
                item_categorie.addChild(item_produit)
            self.arbre.addTopLevelItem(item_categorie)

        # Définition du plan du magasin et affichage
        self.__chemin = os.path.join(os.path.dirname(__file__), "..", "..", "Plan", "plan_magasin.jpg")
        self.affiche_image()

    # Crée un panneau latéral affichant la liste des produits du magasin
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

        # Arbre contenant les catégories et les produits
        self.arbre = QTreeWidget()
        self.arbre.setHeaderLabels(["Catégories et Produits"])
        layout.addWidget(self.arbre)

        self.dock.setWidget(widget_contenu)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        # Création de la liste de courses à côté
        self.creer_liste_course()

    # Crée un panneau latéral affichant la liste de courses
    def creer_liste_course(self):
        if self.billet_liste:
            return

        self.billet_course = QDockWidget("Liste de course", self)
        self.billet_course.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)

        widget_billet = QWidget()
        layout_billet = QVBoxLayout(widget_billet)

        # Liste des produits sélectionnés
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

    # Efface le chemin optimal affiché sur l'image.
    def effacer_chemin(self):
        """Efface le chemin optimal affiché"""
        if self.image:
            self.image.set_chemin_optimal([])

    # Recherche un produit dans l'arbre des catégories et le sélectionne si il existe
    def rechercher_produit(self):
        terme = self.recherche_input.text().strip().lower()
        if not terme:
            return

        # Parcours toutes les catégories et leurs produits
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
                    
    #Ajoute les produits sélectionnés à la liste de courses
    def ajouter_a_liste(self):
        if not self.billet_liste:
            return

        # Parcours les produits cochés et les ajouter à la liste
        for i in range(self.arbre.topLevelItemCount()):
            categorie = self.arbre.topLevelItem(i)
            for j in range(categorie.childCount()):
                produit = categorie.child(j)
                if produit.checkState(0) == Qt.CheckState.Checked:
                    item = QTreeWidgetItem(self.billet_liste)
                    item.setText(0, produit.text(0))

                    coord = produit.data(0, Qt.ItemDataRole.UserRole)
                    item.setData(0, Qt.ItemDataRole.UserRole, coord)

                    bouton_supprimer = QPushButton("Supprimer")
                    bouton_supprimer.clicked.connect(lambda _, i=item: self.supprimer_produit(i))
                    self.billet_liste.setItemWidget(item, 1, bouton_supprimer)

                    produit.setCheckState(0, Qt.CheckState.Unchecked)

        # Mettre à jour l'affichage après ajout
        self.afficher_tous_les_produits()

    # Supprime un produit de la liste de courses
    def supprimer_produit(self, item):
        index = self.billet_liste.indexOfTopLevelItem(item)
        if index >= 0:
            self.billet_liste.takeTopLevelItem(index)

        # Mettre à jour l'affichage après suppression
        self.afficher_tous_les_produits()

    # Ferme l'application ;)
    def destroy(self):
        QApplication.quit()
