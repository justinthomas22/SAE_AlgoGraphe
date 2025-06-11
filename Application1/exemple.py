import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, \
                            QLabel, QTextEdit, QFileDialog, QDockWidget, QWidget, QLineEdit, QFormLayout, QDateEdit, QTreeWidgetItem, QTreeWidget, QPushButton, QVBoxLayout
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter
from PyQt6.QtCore import Qt, QDate

# --- class widget: hérite de QLabel ------------------------------------------
class Image(QLabel):
    def __init__(self, chemin: str, taille_cellule: int = 10):
        super().__init__()
        self.chemin = chemin
        self.taille_cellule = taille_cellule

        # Utilisation d'internet afin de redimensionner l'image, en fonction
        # de la taille de l'écran.

        self.image = QPixmap(self.chemin)

        # Obtenir la taille maximale autorisée par l'écran
        ecran = QApplication.primaryScreen().availableGeometry()
        largeur_max = int(ecran.width() * 0.8)
        hauteur_max = int(ecran.height() * 0.8)

        # Redimensionner l’image en conservant les proportions
        self.image_redim = self.image.scaled(
            largeur_max, hauteur_max,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(self.image_redim)
        self.setFixedSize(self.image_redim.size())

    def paintEvent(self, event):
        super().paintEvent(event)  # Affiche l'image de base

        # Dessiner la grille
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.black)

        largeur = self.image_redim.width()
        hauteur = self.image_redim.height()

        # Décalage pour les lignes verticales
        decalage = 7  # Ajustez cette valeur pour le décalage souhaité

        # Dessiner les lignes verticales et horizontales de la grille
        for x in range(decalage, largeur, self.taille_cellule):
            painter.drawLine(x, 0, x, hauteur)

        for y in range(0, hauteur, self.taille_cellule):
            painter.drawLine(0, y, largeur, y)

        painter.end()

    def mousePressEvent(self, event):
        # Recupère les coordonnées au clic de la souris
        x = event.position().x()
        y = event.position().y()

        # Donne le carré de la grille en (x et y)
        grid_x = x // self.taille_cellule
        grid_y = y // self.taille_cellule

        print(f"Carré cliqué: ({grid_x}, {grid_y})")

# -----------------------------------------------------------------------------
# --- class FenetreAppli
# -----------------------------------------------------------------------------
class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin

        self.setWindowTitle("Plan_magasin")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 500, 300)

        # widget central

        # dock
        self.dock = QDockWidget('Nouveau Projet', self)
        self.dock.setMinimumWidth(20)

        # Permet de s'afficher en même temps que le chargement de la carte du magasin
        self.dock.setVisible(False) 
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

        self.form_widget = QWidget()
        self.form_layout = QFormLayout()

        self.nom_projet_edit = QLineEdit()
        self.auteur_edit = QLineEdit()
        self.date_creation_edit = QDateEdit()
        self.date_creation_edit.setDate(QDate.currentDate())
        self.nom_magasin_edit = QLineEdit()
        self.adresse_magasin_edit = QLineEdit()

        self.form_layout.addRow('Nom du Projet :', self.nom_projet_edit)
        self.form_layout.addRow('Auteur :', self.auteur_edit)
        self.form_layout.addRow('Date de Création :', self.date_creation_edit)
        self.form_layout.addRow('Nom du Magasin :', self.nom_magasin_edit)
        self.form_layout.addRow('Adresse du Magasin :', self.adresse_magasin_edit)

        self.form_widget.setLayout(self.form_layout)

        self.recherche_input = QLineEdit()
        self.recherche_input.setPlaceholderText("Rechercher un produit...")
        bouton_recherche = QPushButton("Rechercher")
        bouton_recherche.clicked.connect(self.rechercher_produit)

        bouton_exporter = QPushButton("Exporter")
        bouton_exporter.clicked.connect(self.exporter_produits)

        self.arbre = QTreeWidget()
        self.arbre.setHeaderLabels(["Catégories et Produits"])

        layout = QVBoxLayout()
        layout.addWidget(self.form_widget)
        layout.addWidget(self.recherche_input)
        layout.addWidget(bouton_recherche)
        layout.addWidget(self.arbre)
        layout.addWidget(bouton_exporter)

        container = QWidget()
        container.setLayout(layout)
        self.dock.setWidget(container)


        # barre d'état
        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("L'application est démarrée...", 2000)

        # barre de menu
        menu_bar = self.menuBar()

        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_edition = menu_bar.addMenu('&Edition')
        menu_aide = menu_bar.addMenu('&Aide')

        menu_fichier.addAction('Nouveau', self.nouveau)
        menu_fichier.addAction('Ouvrir', self.ouvrir)
        menu_fichier.addAction('Enregistrer', self.enregistrer)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.destroy)

        # ajout d'une barre d'outils
        barre_outil = QToolBar('Principaux outils')
        self.addToolBar(barre_outil)

        # Action pour afficher l'image
        action_afficher_image = QAction('Afficher le plan', self)
        action_afficher_image.triggered.connect(self.ouvrir_plan)
        barre_outil.addAction(action_afficher_image)

        self.showMaximized()

    def charger_produits(self):
        chemin_fichier = "C:/Users/Utilisateur.G650-09/Documents/BUT1/Semestre2/SAE_AlgoGraphe/SAE_AlgoGraphe/Application1/liste_produit.json"
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        for categorie, produits in data.items():
            
            # Permet de faire un genre de sous menu
            item_categorie = QTreeWidgetItem([categorie])
            for produit in produits:
                item_produit = QTreeWidgetItem([produit["nom"]])
                item_produit.setCheckState(0, Qt.CheckState.Unchecked)
                item_produit.setData(0, Qt.ItemDataRole.UserRole, produit["coordonnées"])
                item_categorie.addChild(item_produit)
            self.arbre.addTopLevelItem(item_categorie)


    def rechercher_produit(self):
        terme = self.recherche_input.text().strip().lower()
        # N'ouvre pas de menus si il n'y a rien
        if not terme:
            return
        
        #Utilisation d'internet 
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

    def exporter_produits(self):
        produits_selectionnes = {}

        # Parcours de chaque catégorie de l'arbre
        for i in range(self.arbre.topLevelItemCount()):
            categorie = self.arbre.topLevelItem(i)
            produits = []
            for j in range(categorie.childCount()):
                produit_item = categorie.child(j)
                if produit_item.checkState(0) == Qt.CheckState.Checked:
                    produit = {
                        "nom": produit_item.text(0),
                        "coordonnées": produit_item.data(0, Qt.ItemDataRole.UserRole)
                    }
                    produits.append(produit)
            if produits:
                produits_selectionnes[categorie.text(0)] = produits

        if produits_selectionnes:
            nom_magasin = self.nom_magasin_edit.text().strip()
            
            # Cas ou il n'y a pas de nom de magasin
            if not nom_magasin:
                nom_magasin = "magasin"
            nom_fichier = f"{nom_magasin}.json"

            with open(nom_fichier, 'w', encoding='utf-8') as f:
                json.dump(produits_selectionnes, f, ensure_ascii=False, indent=4)

            self.barre_etat.showMessage(f"Produits exportés dans {nom_fichier}", 5000)
        else:
            self.barre_etat.showMessage("Aucun produit sélectionné pour l'exportation", 5000)


        

    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau ....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin

    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un nouveau....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin
            self.affiche_image(taille_cellule = 13)

    def enregistrer(self):
        self.barre_etat.showMessage('Enregistrer....', 2000 )
        boite = QFileDialog()
        chemin, validation = boite.getSaveFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin

    def affiche_image(self, taille_cellule=10):
        self.image = Image(self.__chemin, taille_cellule=taille_cellule)  # Taille de cellule ajustable
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)
        self.dock.setVisible(True)  # Afficher le dock lorsque l'image est chargée
        self.charger_produits()

    def ouvrir_plan(self):
        """Permet de choisir parmi les fichiers un plan de magasin"""
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un plan",
            directory=sys.path[0],
            filter="Images (*.jpg *.jpeg )"
        )
        if fichier:
            self.__chemin = fichier
            self.affiche_image(taille_cellule = 10)

# --- main --------------------------------------------------------------------
if __name__ == "__main__":
    # création d'une QApplication
    app = QApplication(sys.argv)

    # ouverture d'un fichier de style (il y en a d'autres...)
    fichier_style = open(sys.path[0] + "/fichiers_qss/Diffnes.qss", 'r')

    # récupération du contenu et application du style
    # with fichier_style :
    #     qss = fichier_style.read()
    #     app.setStyleSheet(qss)

    fenetre = FenetreAppli()

    # lancement de l'application
    sys.exit(app.exec())
