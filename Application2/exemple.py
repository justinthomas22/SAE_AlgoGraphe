import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QTextEdit, QFileDialog, QDockWidget, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt


class Image(QLabel):
    def __init__(self, chemin: str):
        super().__init__()
        self.image = QPixmap(chemin)
        ecran = QApplication.primaryScreen().availableGeometry()
        largeur_max = int(ecran.width() * 0.8)
        hauteur_max = int(ecran.height() * 0.8)
        image_redim = self.image.scaled(
            largeur_max, hauteur_max,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(image_redim)


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
        menu_fichier.addAction('Nouveau', self.nouveau)
        menu_fichier.addAction('Ouvrir', self.ouvrir)
        menu_fichier.addAction('Enregistrer', self.enregistrer)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.destroy)

        barre_outil = QToolBar('Principaux outils')
        self.addToolBar(barre_outil)

        action_afficher_image = QAction('Afficher le plan', self)
        action_afficher_image.triggered.connect(self.ouvrir_plan)
        barre_outil.addAction(action_afficher_image)

        self.arbre = None
        self.recherche_input = None
        self.dock = None
        self.billet_course = None
        self.billet_texte = None

        self.showMaximized()

    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau ....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory=sys.path[0])
        if validation:
            self.__chemin = chemin

    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un nouveau....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory=sys.path[0])
        if validation:
            self.__chemin = chemin
            self.affiche_image()

    def enregistrer(self):
        self.barre_etat.showMessage('Enregistrer....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getSaveFileName(directory=sys.path[0])
        if validation:
            self.__chemin = chemin

    def affiche_image(self):
        self.image = Image(self.__chemin)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)

    def ouvrir_plan(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un plan",
            directory=sys.path[0],
            filter="Images (*.jpg *.jpeg *.png *.bmp)"
        )
        if fichier:
            self.__chemin = fichier
            self.affiche_image()
            self.creer_dock_liste()

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

        self.charger_produits()
        self.dock.setWidget(widget_contenu)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        self.creer_billet_course()

    def creer_billet_course(self):
        if self.billet_course:
            return  # déjà créé

        self.billet_course = QDockWidget("Liste de course", self)
        self.billet_course.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)

        self.billet_texte = QTextEdit()
        self.billet_texte.setReadOnly(True)
        self.billet_course.setWidget(self.billet_texte)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.billet_course)

    def charger_produits(self):
        with open("liste_produits.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for categorie, produits in data.items():
            item_categorie = QTreeWidgetItem([categorie])
            item_categorie.setFlags(item_categorie.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            for produit in produits:
                item_produit = QTreeWidgetItem([produit])
                item_produit.setCheckState(0, Qt.CheckState.Unchecked)
                item_categorie.addChild(item_produit)
            self.arbre.addTopLevelItem(item_categorie)

    def rechercher_produit(self):
        terme = self.recherche_input.text().strip().lower()
        if not terme:
            return

        for i in range(self.arbre.topLevelItemCount()):
            categorie = self.arbre.topLevelItem(i)
            categorie.setExpanded(False)
            for j in range(categorie.childCount()):
                produit = categorie.child(j)
                if terme in produit.text(0).lower():
                    self.arbre.scrollToItem(produit)
                    produit.setSelected(True)
                    categorie.setExpanded(True)
                else:
                    produit.setSelected(False)

    def ajouter_au_billet(self):
        if not self.billet_texte:
            return

        lignes = []
        for i in range(self.arbre.topLevelItemCount()):
            categorie = self.arbre.topLevelItem(i)
            for j in range(categorie.childCount()):
                produit = categorie.child(j)
                if produit.checkState(0) == Qt.CheckState.Checked:
                    lignes.append(f"- {produit.text(0)}")

        if lignes:
            self.billet_texte.append("\n".join(lignes))
            self.billet_texte.append("")  # Pour espacement     



if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreAppli()
    sys.exit(app.exec())