import sys
from PyQt6.QtWidgets import QMainWindow, QToolBar, QStatusBar, \
    QLabel, QFileDialog, QDockWidget, QWidget, QLineEdit, QFormLayout, \
    QDateEdit, QTreeWidget, QPushButton, QVBoxLayout

from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QDate, QRect
from PyQt6.QtWidgets import QApplication

# Classe d'affichage d'image 
class ImageView(QLabel):
    def __init__(self, chemin: str, controller, taille_cellule: int = 10):
        super().__init__()
        self.controller = controller
        self.chemin = chemin
        self.taille_cellule = taille_cellule

        # Permet de charger et redimensionner de l’image pour qu'elle s’adapte à l’écran
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
    
    # Permet de mettre les zones autorisées (grilles) en surbrillance
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
            
        # Récupère de la catégorie sélectionnée pour afficher les zones qui lui sont associées
        categorie = self.controller.get_categorie_selectionnee()
        if categorie:
            zones = self.controller.model.zones_autorisees.get(categorie, [])
            painter.setBrush(QColor(255, 255, 0, 80))  
            
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
        self.controller.attribuer_position_produit((grid_x, grid_y))

#Vue principale de l'application
class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Plan_magasin")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 500, 300)

        self.setup_dock_widget()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        
        self.showMaximized()

    def setup_dock_widget(self):
        self.dock = QDockWidget('Nouveau Projet', self)
        self.dock.setMinimumWidth(20)
        self.dock.setVisible(False)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

        self.form_widget = QWidget()
        self.form_layout = QFormLayout()

        # Champs du formulaire
        self.nom_projet_edit = QLineEdit()
        self.auteur_edit = QLineEdit()
        self.date_creation_edit = QDateEdit()
        self.date_creation_edit.setDate(QDate.currentDate())
        self.nom_magasin_edit = QLineEdit()
        self.adresse_magasin_edit = QLineEdit()

        # Ajout des champs au formulaire 
        self.form_layout.addRow('Nom du Projet :', self.nom_projet_edit)
        self.form_layout.addRow('Auteur :', self.auteur_edit)
        self.form_layout.addRow('Date de Création :', self.date_creation_edit)
        self.form_layout.addRow('Nom du Magasin :', self.nom_magasin_edit)
        self.form_layout.addRow('Adresse du Magasin :', self.adresse_magasin_edit)

        self.form_widget.setLayout(self.form_layout)

        #Zone de recherche
        self.recherche_input = QLineEdit()
        self.recherche_input.setPlaceholderText("Rechercher un produit...")
        bouton_recherche = QPushButton("Rechercher")
        bouton_recherche.clicked.connect(self.controller.rechercher_produit)

        #Bouton exporter
        bouton_exporter = QPushButton("Exporter")
        bouton_exporter.clicked.connect(self.controller.exporter_produits)

        #Arbre des catégories/produits
        self.arbre = QTreeWidget()
        self.arbre.itemSelectionChanged.connect(self.controller.mis_a_jour_selection)
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

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_fichier.addAction('Nouveau', self.controller.nouveau)
        menu_fichier.addAction('Ouvrir', self.controller.ouvrir)
        menu_fichier.addAction('Enregistrer', self.controller.enregistrer)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.destroy)

    def setup_toolbar(self):
        barre_outil = QToolBar('Principaux outils')
        self.addToolBar(barre_outil)
        action_afficher_image = QAction('Afficher le plan', self)
        action_afficher_image.triggered.connect(self.controller.ouvrir_plan)
        barre_outil.addAction(action_afficher_image)

    def setup_status_bar(self):
        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)

    def afficher_message_status(self, message, duree=3000):
        self.barre_etat.showMessage(message, duree)

    # Extraction des données du formulaire projet
    def donnees_projet(self):
        return {
            "nom_projet": self.nom_projet_edit.text(),
            "auteur": self.auteur_edit.text(),
            "date_creation": self.date_creation_edit.date().toString("dd/MM/yyyy"),
            "nom_magasin": self.nom_magasin_edit.text(),
            "adresse_magasin": self.adresse_magasin_edit.text()
        }

    # Chargement des données dans le formulaire projet
    def changer_donnees_projet(self, info):
        self.nom_projet_edit.setText(info.get("nom_projet", ""))
        self.auteur_edit.setText(info.get("auteur", ""))
        
        date_str = info.get("date_creation", "")
        if date_str:
            date = QDate.fromString(date_str, "dd/MM/yyyy")
            if date.isValid():
                self.date_creation_edit.setDate(date)
        
        self.nom_magasin_edit.setText(info.get("nom_magasin", ""))
        self.adresse_magasin_edit.setText(info.get("adresse_magasin", ""))