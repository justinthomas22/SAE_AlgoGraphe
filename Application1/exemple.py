import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, \
                            QLabel, QTextEdit, QFileDialog, QDockWidget
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter
from PyQt6.QtCore import Qt


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
        self.dock = QDockWidget('Bloc Notes')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setMaximumWidth(400)
        self.text_edit = QTextEdit()
        self.dock.setWidget(self.text_edit)

        
        

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

        action_annuler = QAction(QIcon(sys.path[0] + '/icones/left.png'), 'Précédent', self)
        action_annuler.setShortcut('Ctrl+Z')
        action_annuler.triggered.connect(self.text_edit.undo)
        menu_edition.addAction(action_annuler)

        action_retablir = QAction(QIcon(sys.path[0] + '/icones/right.png'), 'Rétablir', self)
        action_retablir.setShortcut('Ctrl+Y')
        action_retablir.triggered.connect(self.text_edit.redo)
        menu_edition.addAction(action_retablir)

        # ajout d'une barre d'outils
        barre_outil = QToolBar('Principaux outils')
        self.addToolBar(barre_outil)

        barre_outil.addAction(action_annuler)
        barre_outil.addAction(action_retablir)

        # Action pour afficher l'image
        action_afficher_image = QAction('Afficher le plan', self)
        action_afficher_image.triggered.connect(self.ouvrir_plan)
        barre_outil.addAction(action_afficher_image)


        self.showMaximized()


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