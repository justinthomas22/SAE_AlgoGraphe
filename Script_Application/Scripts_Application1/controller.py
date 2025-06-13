import os
from PyQt6.QtWidgets import QFileDialog, QTreeWidgetItem
from PyQt6.QtCore import Qt
from model import MagasinModel
from view import MainView, ImageView

# Contrôleur principal de l'application Magasin fait le lien entre le modèle et la vue.
class MagasinController:
    def __init__(self):
        self.model = MagasinModel()
        self.view = MainView(self)
        self.image_view = None
        self.categorie_selectionnee = None
        self.chemin_image = None

    # Retourne la catégorie qui est actuellement sélectionnée dans l'arbre
    def get_categorie_selectionnee(self):
        return self.categorie_selectionnee

    # Permet de mettre à jour la catégorie sélectionnée quand l'utilisateur clique dans l'arbre.
    def mis_a_jour_selection(self):
        item = self.view.arbre.currentItem()
        if item:
            if not item.parent():
                self.categorie_selectionnee = item.text(0)
            else:
                self.categorie_selectionnee = item.parent().text(0)
        else:
            self.categorie_selectionnee = None
        
        if self.image_view:
            self.image_view.update()
    
    # Attribue une position à un produit sélectionné dans l'arbre.                     
    def attribuer_position_produit(self, coordonnees):
        item = self.view.arbre.currentItem()
        if item and item.parent():
            categorie = item.parent().text(0)
            if self.model.est_dans_zone_autorisee(categorie, coordonnees):
                item.setData(0, Qt.ItemDataRole.UserRole, coordonnees)
                self.view.afficher_message_status(f"{item.text(0)} positionné en {coordonnees}", 3000)
            else:
                self.view.afficher_message_status(f"Zone invalide pour la catégorie {categorie}, {coordonnees}", 4000)
        else:
            self.view.afficher_message_status("Veuillez sélectionner un produit pour lui assigner une position", 3000)
    
    #Permet de charger les produits depuis le JSON et les affiche dans l'arbre de la vue
    def charger_produits_dans_arbre(self):
        data = self.model.charger_produits_depuis_json()
        for categorie, produits in data.items():
            item_categorie = QTreeWidgetItem([categorie])
            for produit in produits:
                item_produit = QTreeWidgetItem([produit["nom"]])
                item_produit.setCheckState(0, Qt.CheckState.Unchecked)
                item_produit.setData(0, Qt.ItemDataRole.UserRole, None)
                item_categorie.addChild(item_produit)
            self.view.arbre.addTopLevelItem(item_categorie)

    # Recherche un produit dans l'arbre en fonction du texte que l'utilisateur saisit
    def rechercher_produit(self):
        terme = self.view.recherche_input.text().strip().lower()
        if not terme:
            return
        
        for i in range(self.view.arbre.topLevelItemCount()):
            categorie = self.view.arbre.topLevelItem(i)
            for j in range(categorie.childCount()):
                produit = categorie.child(j)
                if terme in produit.text(0).lower():
                    self.view.arbre.scrollToItem(produit)
                    produit.setSelected(True)
                    categorie.setExpanded(True)
                else:
                    produit.setSelected(False)
                    
    #Exporte les produits sélectionnés dans un fichier JSON
    def exporter_produits(self):
        produits_selectionnes = {}
        
        for i in range(self.view.arbre.topLevelItemCount()):
            categorie = self.view.arbre.topLevelItem(i)
            produits = []
            for j in range(categorie.childCount()):
                produit_item = categorie.child(j)
                if produit_item.checkState(0) == Qt.CheckState.Checked:
                    coords = produit_item.data(0, Qt.ItemDataRole.UserRole)
                    if coords is None:
                        self.view.afficher_message_status(f"Le produit '{produit_item.text(0)}' n'est pas positionné, il ne sera pas exporte", 4000)
                        continue  
                    produits.append({
                        "nom": produit_item.text(0),
                        "coordonnées": coords
                    })
            if produits:
                produits_selectionnes[categorie.text(0)] = produits

        if produits_selectionnes:
            nom_magasin = self.view.nom_magasin_edit.text().strip()
            nom_fichier = self.model.exporter_produits_selectionnes(produits_selectionnes, nom_magasin)
            self.view.afficher_message_status(f"Produits exportés dans {nom_fichier}", 5000)
        else:
            self.view.afficher_message_status("Aucun produit sélectionné pour l'exportation", 5000)

    # Ouvre une boîte de dialogue pour créer un nouveau projet
    def nouveau(self):
        self.view.afficher_message_status('Créer un nouveau ....', 2000)
        chemin, _ = QFileDialog.getOpenFileName(directory=os.path.dirname(__file__))
        if chemin:
            self.chemin_image = chemin

    #Ouvre un projet existant à partir d'un fichier JSON.
    def ouvrir(self):
        self.view.afficher_message_status('Ouvrir un projet...', 2000)
        chemin_json, _ = QFileDialog.getOpenFileName(
            self.view,
            "Ouvrir un projet",
            directory=os.path.dirname(__file__),
            filter="Fichiers JSON (*.json)"
        )

        if chemin_json:
            donnees = self.model.charger_projet(chemin_json)
            self.view.changer_donnees_projet(donnees) # Met à jour la vue avec les données du projet

            chemin_image = donnees.get("chemin_image")
            if chemin_image and os.path.exists(chemin_image):
                self.chemin_image = chemin_image
                self.afficher_image(taille_cellule=13)

            self.view.arbre.clear()
            self.charger_produits_dans_arbre()

            produits_sel = donnees.get("produits_selectionnes", {}) # Permet d'appliquer les produits sélectionnés et leurs coordonnées sauvegardées
            self.appliquer_produits_sauvegardes(produits_sel)
            self.view.afficher_message_status(f"Projet chargé depuis {chemin_json}", 3000)

    # Parcourt l'arbre pour cocher les produits déjà sélectionnés et appliquer leurs coordonnées
    def appliquer_produits_sauvegardes(self, produits_sel): 
        for i in range(self.view.arbre.topLevelItemCount()):
            categorie = self.view.arbre.topLevelItem(i)
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

    # Sauvegarde les données du projet dans un fichier JSON
    def enregistrer(self):
        self.view.afficher_message_status('Enregistrer....', 2000)
        chemin, _ = QFileDialog.getSaveFileName(
            self.view,
            "Enregistrer le projet",
            directory=os.path.dirname(__file__),
            filter="Fichiers JSON (*.json)"
        )
        if not chemin:
            return

        # Récupère les informations du projet depuis la vue
        info_projet = self.view.donnees_projet()
        info_projet["chemin_image"] = self.chemin_image
        self.model.projet_info.update(info_projet)

        # Récupère les produits sélectionnés et leurs positions
        produits_selectionnes = self.collecter_produits_selectionnes()
        chemin_json = os.path.splitext(chemin)[0] + ".json"
        
        # Sauvegarde le projet à travers le modèle
        self.model.sauvegarder_projet(chemin_json, produits_selectionnes)
        self.view.afficher_message_status(f"Données sauvegardées dans {chemin_json}", 3000)

    # Parcourt l'arbre pour collecter les produits cochés et leurs coordonnées
    def collecter_produits_selectionnes(self):
        produits_selectionnes = {}
        for i in range(self.view.arbre.topLevelItemCount()):
            categorie = self.view.arbre.topLevelItem(i)
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
                produits_selectionnes[categorie.text(0)] = produits
        return produits_selectionnes

    def afficher_image(self, taille_cellule=10):
        self.image_view = ImageView(self.chemin_image, self, taille_cellule=taille_cellule)
        self.image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view.setCentralWidget(self.image_view)
        self.view.dock.setVisible(True)
        self.charger_produits_dans_arbre()

    # Permet d'ouvrir une image de plan via la boîte de dialogue et l'affiche
    def ouvrir_plan(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self.view,
            "Ouvrir un plan",
            directory=os.path.dirname(__file__),
            filter="Images (*.jpg *.jpeg *.png)"
        )
        if fichier:
            self.chemin_image = fichier
            self.afficher_image(taille_cellule=10)

    #Lance l'application
    def run(self):
        return self.view
        