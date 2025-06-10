import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QFileDialog, QDockWidget, QTreeWidget, QTreeWidgetItem
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Liste de courses")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 800, 600)

        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("Application lancée...", 2000)

        self.creer_menu()
        self.creer_toolbar()
        self.creer_dock_liste()
        self.dock.setVisible(False)

        self.showMaximized()

    def creer_menu(self):
        menu_bar = self.menuBar()
        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_fichier.addAction('Quitter', self.close)

    def creer_toolbar(self):
        barre_outil = QToolBar('Outils')
        self.addToolBar(barre_outil)

        action_afficher_plan = QAction('Afficher le plan', self)
        action_afficher_plan.triggered.connect(self.ouvrir_plan)
        barre_outil.addAction(action_afficher_plan)

    def ouvrir_plan(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un plan",
            directory=sys.path[0],
            filter="Images (*.jpg *.jpeg *.png)"
        )
        if fichier:
            self.affiche_image(fichier)
            self.dock.setVisible(True)

    def affiche_image(self, chemin):
        self.image = Image(chemin)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)

    def creer_dock_liste(self):
        self.dock = QDockWidget("Liste des produits", self)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)

        self.arbre = QTreeWidget()
        self.arbre.setHeaderLabels(["Catégories et Produits"])
        self.charger_produits()

        self.dock.setWidget(self.arbre)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

    def charger_produits(self):
        chemin_json = os.path.join(sys.path[0], "liste_produits.json")

        try:
            with open(chemin_json, "r", encoding="utf-8") as f:
                categories = json.load(f)

            for categorie, produits in categories.items():
                item_categorie = QTreeWidgetItem([categorie])
                item_categorie.setExpanded(False)
                self.arbre.addTopLevelItem(item_categorie)

                for produit in produits:
                    item_produit = QTreeWidgetItem([produit])
                    item_produit.setFlags(item_produit.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item_produit.setCheckState(0, Qt.CheckState.Unchecked)
                    item_categorie.addChild(item_produit)

        except Exception as e:
            print(f"Erreur lors du chargement de la liste : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreAppli()
    sys.exit(app.exec())
