import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QFileDialog, QDockWidget, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
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
        self.setPixmap(self.image_redim)
        self.setFixedSize(self.image_redim.size())

    def set_produits(self, coordonnees):
        self.produits = coordonnees
        self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.produits:
            return
            
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.red)
        painter.setBrush(Qt.GlobalColor.red)

        # Taille du carré rouge
        size = 15
        
        # Décalage comme dans l'App1
        decalage = 7

        for coord in self.produits:
            if not coord or len(coord) < 2:
                continue
                
            grid_x, grid_y = coord
            
            # Conversion des coordonnées de grille en pixels (même logique que App1)
            px = grid_x * self.taille_cellule + decalage - size // 2
            py = grid_y * self.taille_cellule - size // 2
            
            # Vérifier que les coordonnées sont dans les limites de l'image
            if 0 <= px < self.image_redim.width() and 0 <= py < self.image_redim.height():
                painter.drawRect(px, py, size, size)

        painter.end()


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
        self.showMaximized()

    def mettre_a_jour_carre_rouge(self):
        if not self.billet_liste:
            return

        coordonnees = []
        items = self.billet_liste.selectedItems()
        for item in items:
            coord = item.data(0, Qt.ItemDataRole.UserRole)
            if coord:
                coordonnees.append(coord)

        self.affiche_image(coordonnees if coordonnees else None)


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
        """
        Affiche le plan
        """
        self.image = Image(self.__chemin, taille_cellule=taille_cellule)
        
        if coordonnees:
            self.image.set_produits(coordonnees)
        else:
            self.image.set_produits([])

        # Centrer l'image dans la fenêtre
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
            return  # Ne ferme pas la popup

        # Le fichier a été chargé avec succès, on ferme la popup
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
        bouton_ajouter.clicked.connect(self.ajouter_au_billet)

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

        self.billet_course.setWidget(widget_billet)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.billet_course)

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

    def ajouter_au_billet(self):
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

        self.mettre_a_jour_carre_rouge()


    def supprimer_produit(self, item):
        index = self.billet_liste.indexOfTopLevelItem(item)
        if index >= 0:
            self.billet_liste.takeTopLevelItem(index)
        self.affiche_image()

    def destroy(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreAppli()
    fenetre.show()
    sys.exit(app.exec())
