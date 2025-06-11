import sys
import os
import shutil
import json

from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, \
    QLabel, QTextEdit, QFileDialog, QDockWidget, QWidget, QLineEdit, QFormLayout, \
    QDateEdit, QTreeWidgetItem, QTreeWidget, QPushButton, QVBoxLayout

from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QDate, QRect

from odf.opendocument import OpenDocumentText
from odf.text import H, P
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class Image(QLabel):
    def __init__(self, chemin: str, parent, taille_cellule: int = 10):
        super().__init__(parent)
        self.parent = parent
        self.chemin = chemin
        self.taille_cellule = taille_cellule

        self.image = QPixmap(self.chemin)
        ecran = QApplication.primaryScreen().availableGeometry()
        largeur_max = int(ecran.width() * 0.8)
        hauteur_max = int(ecran.height() * 0.8)

        self.image_redim = self.image.scaled(
            largeur_max, hauteur_max,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(self.image_redim)
        self.setFixedSize(self.image_redim.size())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.black)
        largeur = self.image_redim.width()
        hauteur = self.image_redim.height()
        decalage = 7

        for x in range(decalage, largeur, self.taille_cellule):
            painter.drawLine(x, 0, x, hauteur)
        for y in range(0, hauteur, self.taille_cellule):
            painter.drawLine(0, y, largeur, y)

        categorie = self.parent.categorie_selectionnee
        if categorie:
            zones = self.parent.zones_autorisees.get(categorie, [])
            painter.setBrush(QColor(255, 255, 0, 80))  
            
            # Création du rectangle de couleur
            for (x1, y1), (x2, y2) in zones:
                rectangle = QRect(
                    min(x1, x2) * self.taille_cellule,
                    min(y1, y2) * self.taille_cellule,
                    (abs(x2 - x1) + 1) * self.taille_cellule,
                    (abs(y2 - y1) + 1) * self.taille_cellule
                )
                painter.drawRect(rectangle)


    def mousePressEvent(self, event):
        x = event.position().x()
        y = event.position().y()
        grid_x = int(x) // self.taille_cellule
        grid_y = int(y) // self.taille_cellule
        self.parent.attribuer_position_produit((grid_x, grid_y))


class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin

        self.categorie_selectionnee = None


        self.setWindowTitle("Plan_magasin")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 500, 300)

        self.zones_autorisees = {
        "Légumes": [((19, 8), (19, 28)), ((23, 8), (25, 16))],       
        "Poissons": [((2, 6), (3, 6)), ((3, 5), (4, 5)), ((4, 4), (5, 4)), ((5, 3), (6, 3)), ((6, 2), (7, 2))],
        "Viandes": [((33, 1), (47, 1))],
        "Épicerie": [((13, 44), (13, 51)), ((16, 44), (17, 51)), ((21, 44), (22, 51)), ((25, 44), (26, 51)), ((29, 44), (30, 51)), ((33, 33), (33, 51))],
        "Épicerie sucrée": [((17, 33), (17, 41)), ((21, 33), (22, 41)), ((25, 33), (26, 41)), ((29, 33), (30, 41))],
        "Petit déjeuner": [((68, 17), (80, 17)), ((68, 20), (80, 21)), ((68, 24), (80, 25)), ((68, 28), (80, 28))],
        "Fruits": [((23, 22), (25, 28)), ((29, 8), (29, 28))],
        "Rayon frais": [((2, 9), (3, 28)), ((7, 9), (7, 28))],
        "Crèmerie": [((12, 14), (13, 28))],
        "Conserves": [((68, 38), (80, 38))],
        "Apéritifs": [((8, 44), (9, 51))],
        "Boissons": [((7, 33), (7, 51))],
        "Articles Maison": [((84, 23), (84, 56))],
        "Hygiène": [((68, 41), (80, 42)), ((68, 45), (80, 46))],
        "Bureau": [((68, 49), (80, 50)), ((68, 53), (80, 55)), ((68, 57), (83, 57))],   
        "Animaux": [((42, 8), (42, 28)), ((45, 8), (45, 28))],       
    }


        self.dock = QDockWidget('Nouveau Projet', self)
        self.dock.setMinimumWidth(20)
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
        self.arbre.itemSelectionChanged.connect(self.mis_a_jour)

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


        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)

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

        self.showMaximized()

    def mis_a_jour(self):
        item = self.arbre.currentItem()
        if item:
            if not item.parent():
                self.categorie_selectionnee = item.text(0)  # Catégorie sélectionnée
            else:
                self.categorie_selectionnee = item.parent().text(0)  # Produit sélectionné → remonter à la catégorie
        else:
            self.categorie_selectionnee = None
        if hasattr(self, 'image'):
            self.image.update()


    def est_dans_zone_autorisee(self, categorie: str, coord: tuple) -> bool:
        zones = self.zones_autorisees.get(categorie, [])
        for (x1, y1), (x2, y2) in zones:
            if x1 <= coord[0] <= x2 and y1 <= coord[1] <= y2:
                return True
        return False


    def attribuer_position_produit(self, coordonnees):
        item = self.arbre.currentItem()
        if item and item.parent():  # S'assure que ce n'est pas une catégorie
            categorie = item.parent().text(0)
            if self.est_dans_zone_autorisee(categorie, coordonnees):
                item.setData(0, Qt.ItemDataRole.UserRole, coordonnees)
                self.barre_etat.showMessage(f"{item.text(0)} positionné en {coordonnees}", 3000)
            else:
                self.barre_etat.showMessage(f"Zone invalide pour la catégorie {categorie}, {coordonnees}", 4000)
        else:
            self.barre_etat.showMessage("Veuillez sélectionner un produit pour lui assigner une position", 3000)


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
                item_produit.setData(0, Qt.ItemDataRole.UserRole, None)
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
                    coords = produit_item.data(0, Qt.ItemDataRole.UserRole)

                    # Obliger de mettre le produit sur le plan pour qu'il soit exporté
                    if coords is None:
                        self.barre_etat.showMessage(f"Le produit '{produit_item.text(0)}' n'est pas positionné, il ne sera pas exporte", 4000)
                        continue  
                    produits.append({
                        "nom": produit_item.text(0),
                        "coordonnées": coords
                    })
            if produits:
                produits_selectionnes[categorie.text(0)] = produits

        if produits_selectionnes:
            nom_magasin = self.nom_magasin_edit.text().strip()

            # Cas ou il n'y a pas de nom de magasin
            if not nom_magasin:
                nom_magasin = "magasin"
            nom_fichier = f"{nom_magasin}_liste_produits.json"

            dossier = "listes_produits_entreprise"

            # Permet de mettre le json dans un fichier (lien avec app2)
            chemin_complet = os.path.join(dossier, nom_fichier)

            with open(chemin_complet, 'w', encoding='utf-8') as f:
                json.dump(produits_selectionnes, f, ensure_ascii=False, indent=4)

            self.barre_etat.showMessage(f"Produits exportés dans {nom_fichier}", 5000)
        else:
            self.barre_etat.showMessage("Aucun produit sélectionné pour l'exportation", 5000)



    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau ....', 2000)
        chemin, _ = QFileDialog.getOpenFileName(directory=sys.path[0])
        if chemin:
            self.__chemin = chemin

    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un projet...', 2000)
        chemin_json, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un projet",
            directory=sys.path[0],
            filter="Fichiers JSON (*.json)"
        )

        if chemin_json:
            with open(chemin_json, "r", encoding="utf-8") as f:
                donnees = json.load(f)

            self.nom_projet_edit.setText(donnees.get("nom_projet", ""))
            self.auteur_edit.setText(donnees.get("auteur", ""))

            date_str = donnees.get("date_creation", "")
            if date_str:
                date = QDate.fromString(date_str, "dd/MM/yyyy")
                if date.isValid():
                    self.date_creation_edit.setDate(date)

            self.nom_magasin_edit.setText(donnees.get("nom_magasin", ""))
            self.adresse_magasin_edit.setText(donnees.get("adresse_magasin", ""))

            chemin_image = donnees.get("chemin_image")
            if chemin_image and os.path.exists(chemin_image):
                self.__chemin = chemin_image
                self.affiche_image(taille_cellule=13)

            # Rechage l'arbre en fonction des produits choisi avant
            self.arbre.clear()
            self.charger_produits()

            # Appliquer les produits sauvegardés (cochés + coordonnées)
            produits_sel = donnees.get("produits_selectionnes", {})

            for i in range(self.arbre.topLevelItemCount()):
                categorie = self.arbre.topLevelItem(i)
                cat_nom = categorie.text(0)

                if cat_nom in produits_sel:
                    liste_produits = produits_sel[cat_nom]

                    dict_produits = {p["nom"]: p.get("coordonnees") for p in liste_produits}

                    for j in range(categorie.childCount()):
                        produit_item = categorie.child(j)
                        nom_produit = produit_item.text(0)

                        if nom_produit in dict_produits:
                            produit_item.setCheckState(0, Qt.CheckState.Checked)
                            produit_item.setData(0, Qt.ItemDataRole.UserRole, dict_produits[nom_produit])

            self.barre_etat.showMessage(f"Projet chargé depuis {chemin_json}", 3000)



    def enregistrer(self):
        self.barre_etat.showMessage('Enregistrer....', 2000)
        chemin, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le projet",
            directory=sys.path[0],
            filter="Fichiers ODT (*.odt);;Fichiers PDF (*.pdf)"
        )
        if not chemin:
            return

        # Permet de récupérer les infos de l'application
        nom_projet = self.nom_projet_edit.text()
        auteur = self.auteur_edit.text()
        date_creation = self.date_creation_edit.date().toString("dd/MM/yyyy")
        nom_magasin = self.nom_magasin_edit.text()
        adresse_magasin = self.adresse_magasin_edit.text()

        # Sauvegardes dans un JSON
        donnees = {
            "nom_projet": nom_projet,
            "auteur": auteur,
            "date_creation": date_creation,
            "nom_magasin": nom_magasin,
            "adresse_magasin": adresse_magasin,
            "chemin_image": self.__chemin,
            "produits_selectionnes": {}
        }

        # Parcourir de l'arbre pour enregistrer les produits qui sont cochés
        for i in range(self.arbre.topLevelItemCount()):
            categorie = self.arbre.topLevelItem(i)
            produits = []
            for j in range(categorie.childCount()):
                produit_item = categorie.child(j)
                if produit_item.checkState(0) == Qt.CheckState.Checked:
                    produit = {
                        "nom": produit_item.text(0),
                        "coordonnees": produit_item.data(0, Qt.ItemDataRole.UserRole)
                    }
                    produits.append(produit)
            if produits:
                donnees["produits_selectionnes"][categorie.text(0)] = produits

        chemin_json = os.path.splitext(chemin)[0] + ".json"
        with open(chemin_json, "w", encoding="utf-8") as f_json:
            json.dump(donnees, f_json, ensure_ascii=False, indent=4)

        self.barre_etat.showMessage(f"Données sauvegardées dans {chemin_json}", 3000)


    def affiche_image(self, taille_cellule=10):
        self.image = Image(self.__chemin, self, taille_cellule=taille_cellule)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)
        self.dock.setVisible(True)
        self.charger_produits()


    def ouvrir_plan(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un plan",
            directory=sys.path[0],
            filter="Images (*.jpg *.jpeg *.png)"
        )
        if fichier:
            self.__chemin = fichier
            self.affiche_image(taille_cellule=10)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open(sys.path[0] + "/fichiers_qss/Diffnes.qss", 'r') as fichier_style:
            qss = fichier_style.read()
            app.setStyleSheet(qss)
    except:
        pass

    fenetre = FenetreAppli()
    sys.exit(app.exec())
