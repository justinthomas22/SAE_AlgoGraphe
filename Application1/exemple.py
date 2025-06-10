import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, \
                            QLabel, QTextEdit, QFileDialog, QDockWidget
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt


# --- class widget: hérite de QLabel ------------------------------------------
class Image(QLabel):

    def __init__(self, chemin: str):
        '''Constructeur de la classe'''

        # appel au constructeur de la classe mère
        super().__init__() 
        
        self.image = QPixmap(chemin)
        self.setPixmap(self.image)
        



# -----------------------------------------------------------------------------
# --- class FenetreAppli
# -----------------------------------------------------------------------------
class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin
        
        self.setWindowTitle("Votre première application à l'IUT")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 500, 300)

        # widget central
        if not chemin is None:
            self.affiche_image()

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
            self.affiche_image()


    def enregistrer(self):
        self.barre_etat.showMessage('Enregistrer....', 2000 )
        boite = QFileDialog()
        chemin, validation = boite.getSaveFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin

        
    def affiche_image(self):
        self.image = Image(self.__chemin)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)



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

    # # création de la fenêtre de l'application
    fenetre = FenetreAppli(sys.path[0] + '/images/plan_accessibilite.png')

    # lancement de l'application
    sys.exit(app.exec())