# controller.py
import sys
from PyQt6.QtWidgets import QApplication
from view import FenetreAppli

class Controller:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.view = FenetreAppli()
        self.view.show()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = Controller()
    controller.run()
