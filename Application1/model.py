import os 
import json

class MagasinModel:
    def __init__(self):
        #Définition des zones pour chaque catégorie de produits
        self.zones_autorisees = {
            "Légumes": [((19, 8), (19, 28)), ((23, 8), (23, 16)), ((25, 8), (25, 16))],       
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
        self.produits_data = {}
        self.projet_info = {
            "nom_projet": "",
            "auteur": "",
            "date_creation": "",
            "nom_magasin": "",
            "adresse_magasin": "",
            "chemin_image": ""
        }
    
    #Permet de charger la liste de produits depuis un fichier JSON
    def charger_produits_depuis_json(self): 
        chemin_fichier = os.path.join(os.path.dirname(__file__), 'liste_produit.json')
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            self.produits_data = json.load(f)
        return self.produits_data

    #Permet de vérifier si les données sont dans une zone autorisée lorsqu'on clique
    def est_dans_zone_autorisee(self, categorie: str, coord: tuple) -> bool:
        zones = self.zones_autorisees.get(categorie, [])
        for (x1, y1), (x2, y2) in zones:
            if x1 <= coord[0] <= x2 and y1 <= coord[1] <= y2:
                return True
        return False
    
    #Permet de sauvegarder le projet dans un fichier JSON
    def sauvegarder_projet(self, chemin, produits_selectionnes):
        donnees = self.projet_info.copy()
        donnees["produits_selectionnes"] = produits_selectionnes
        
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=4)
    
    #Permet de charger un projet depuis un fichier JSON
    def charger_projet(self, chemin):
        with open(chemin, "r", encoding="utf-8") as f:
            donnees = json.load(f)
        
        self.projet_info.update(donnees)
        return donnees
    
    #Permet d'esxporter les produits sélectionnés dans un fichier JSON
    def exporter_produits_selectionnes(self, produits_selectionnes, nom_magasin):
        if not nom_magasin:
            nom_magasin = "magasin"
        nom_fichier = f"{nom_magasin}_liste_produits.json"
        
        dossier = os.path.join(os.path.dirname(__file__), 'listes_produits_entreprise')
        if not os.path.exists(dossier):
            os.makedirs(dossier)
        chemin_complet = os.path.join(dossier, nom_fichier)
        
        with open(chemin_complet, 'w', encoding='utf-8') as f:
            json.dump(produits_selectionnes, f, ensure_ascii=False, indent=4)
        
        return nom_fichier
    
