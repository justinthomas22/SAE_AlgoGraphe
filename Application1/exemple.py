import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, \
    QLabel, QFileDialog, QDockWidget, QWidget, QLineEdit, QFormLayout, QDateEdit
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter
from PyQt6.QtCore import Qt, QDate

from odf.opendocument import OpenDocumentText
from odf.text import H, P
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class Image(QLabel):
    def __init__(self, chemin: str, taille_cellule: int = 10):
        super().__init__()
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

    def mousePressEvent(self, event):
        x = event.position().x()
        y = event.position().y()
        grid_x = x // self.taille_cellule
        grid_y = y // self.taille_cellule
        print(f"Carré cliqué: ({grid_x}, {grid_y})")

class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin

        self.setWindowTitle("Plan_magasin")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 500, 300)

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
        self.dock.setWidget(self.form_widget)

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

    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau ....', 2000)
        chemin, _ = QFileDialog.getOpenFileName(directory=sys.path[0])
        if chemin:
            self.__chemin = chemin

    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un nouveau....', 2000)
        chemin, _ = QFileDialog.getOpenFileName(directory=sys.path[0])
        if chemin:
            self.__chemin = chemin
            self.affiche_image(taille_cellule=13)

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

        nom_projet = self.nom_projet_edit.text()
        auteur = self.auteur_edit.text()
        date_creation = self.date_creation_edit.date().toString("dd/MM/yyyy")
        nom_magasin = self.nom_magasin_edit.text()
        adresse_magasin = self.adresse_magasin_edit.text()

        texte = f"""Nom du projet : {nom_projet}
Auteur : {auteur}
Date de création : {date_creation}
Nom du magasin : {nom_magasin}
Adresse du magasin : {adresse_magasin}
"""

        # création du dossier pour stocker les images avec "_images" à la fin
        dossier = os.path.splitext(chemin)[0] + "_image"
        os.makedirs(dossier, exist_ok=True)

        # copie de l'image chargé au début pour la mettre dans le dossier créer au dessus
        if self.__chemin and os.path.exists(self.__chemin):
            shutil.copy(self.__chemin, dossier)

        if chemin.endswith(".odt"):
            doc = OpenDocumentText()
            doc.text.addElement(H(outlinelevel=1, text="Informations du Projet"))
            for ligne in texte.strip().split("\n"):
                doc.text.addElement(P(text=ligne))
            doc.save(chemin)
            self.barre_etat.showMessage(f"Projet enregistré en ODT : {chemin}", 3000)

        elif chemin.endswith(".pdf"):
            c = canvas.Canvas(chemin, pagesize=A4)
            width, height = A4
            y = height - 50
            for ligne in texte.strip().split("\n"):
                c.drawString(50, y, ligne)
                y -= 20

            dossier = os.path.splitext(chemin)[0] + "_image"
            os.makedirs(dossier, exist_ok=True)
            img_dest = None
            if self.__chemin and os.path.exists(self.__chemin):
                try:
                    img_dest = os.path.join(dossier, os.path.basename(self.__chemin))
                    shutil.copy(self.__chemin, img_dest)
                    max_width = 400
                    max_height = 300
                    pix = QPixmap(img_dest)
                    img_width = pix.width()
                    img_height = pix.height()

                    ratio = min(max_width / img_width, max_height / img_height)
                    w = img_width * ratio
                    h = img_height * ratio

                    c.drawImage(img_dest, 50, y - h - 10, width=w, height=h, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    print("Erreur image dans PDF :", e)

            c.save()
            self.barre_etat.showMessage(f"Projet enregistré en PDF : {chemin}", 3000)


    def affiche_image(self, taille_cellule=10):
        self.image = Image(self.__chemin, taille_cellule=taille_cellule)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image)
        self.dock.setVisible(True)

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
