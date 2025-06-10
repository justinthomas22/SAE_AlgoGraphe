import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal


# -----------------------------------------------------------------------------
# --- class VueOutil
# -----------------------------------------------------------------------------
class VueOutil(QWidget):

    # constructeur
    def __init__(self):
        
        super().__init__()
        
        # layout vertical --> principal layout
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        # layout horizontal 
        self.hlayout = QHBoxLayout()

        # widgets
        self.texte1 : QLabel = QLabel('Outil sélectionné : ')
        self.affiche_outil : QLabel = QLabel('Outil')
        self.affiche_outil.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.bouton_precedent : QPushButton = QPushButton('Précédent')
        self.bouton_suivant : QPushButton = QPushButton('Suivant')
        self.texte2 : QLabel = QLabel('Nouvel outil :')
        self.nouvel_outil : QLineEdit = QLineEdit('')
        self.bouton_ajout : QPushButton = QPushButton('Ajouter')

        # ajout des widgets au layout horizontal
        
        self.hlayout.addWidget(self.bouton_precedent)
        self.hlayout.addWidget(self.bouton_suivant)

        # ajouts dans le layout principal
        self.mainlayout.addWidget(self.texte1)
        self.mainlayout.addWidget(self.affiche_outil)
        self.mainlayout.addSpacing(10)
        self.mainlayout.addLayout(self.hlayout)
        self.mainlayout.addSpacing(40)
        self.mainlayout.addWidget(self.texte2)
        self.mainlayout.addWidget(self.nouvel_outil)
        self.mainlayout.addWidget(self.bouton_ajout)

        # signaux and slots (signaux à l'intérieur)
        self.bouton_precedent.clicked.connect(self.outilPrecedent)
        self.bouton_suivant.clicked.connect(self.outilSuivant)
        self.bouton_ajout.clicked.connect(self.ajoutOutil)

        # show
        self.setWindowTitle('Boîte à outils')
        self.resize(300, 200)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        self.move((QApplication.screens()[0].size().width() - self.width())// 2, (QApplication.screens()[0].size().height() - self.height()) // 2)
        self.show()

    # signaux vers extérieur
    precedentClicked : pyqtSignal = pyqtSignal()
    suivantClicked : pyqtSignal = pyqtSignal()
    ajoutClicked : pyqtSignal = pyqtSignal(str)
    
    # slots
    def outilPrecedent(self) -> None :
        self.precedentClicked.emit()
    
    def outilSuivant(self) -> None :
        self.suivantClicked.emit()
    
    def ajoutOutil(self) -> None :
        self.ajoutClicked.emit(self.nouvel_outil.text())
        self.nouvel_outil.setText('')
    
    # mise à jour de la vue
    def updateVue(self, outil: str) -> None:
        self.affiche_outil.setText(outil)
        self.nouvel_outil.setText('')



## Programme principal : test de la vue ---------------------------------------
if __name__ == "__main__":

    print(f' --- main --- ')
    app = QApplication(sys.argv)
    
    fenetre = VueOutil()
    
    sys.exit(app.exec())