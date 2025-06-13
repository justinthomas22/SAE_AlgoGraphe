import sys
from PyQt6.QtWidgets import QApplication
from controller import MagasinController

#Fonction principale 
def main():
    app = QApplication(sys.argv)
    controller = MagasinController()
    fenetre = controller.run()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()