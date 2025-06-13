# model.py
from typing import List, Tuple
import heapq

class Chemin:
    def __init__(self, largeur: int, hauteur: int, taille_cellule: int = 10):
        self.largeur = largeur
        self.hauteur = hauteur
        self.taille_cellule = taille_cellule
        self.grille_largeur = largeur // taille_cellule
        self.grille_hauteur = hauteur // taille_cellule

        # Zones bloquées
        self.zones_bloquees = set()
        self._definir_zones_bloquees()

        self.entree = (62, 58)  # Position de l'entrée
        self.caisse = (35, 56)  # Position de la caisse

    def trouver_case_accessible_autour(self, x: int, y: int) -> Tuple[int, int] | None:
        from collections import deque
        visited = set()
        queue = deque()
        queue.append((x, y, 0))
        visited.add((x, y))
        max_distance = 3

        while queue:
            cx, cy, dist = queue.popleft()
            # On saute la case de départ (bloquée)
            if dist > 0 and self.est_position_valide(cx, cy):
                return (cx, cy)
            if dist >= max_distance:
                continue
            # Explore toutes les cases autour (dans les 8 directions)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) not in visited and 0 <= nx < self.grille_largeur and 0 <= ny < self.grille_hauteur:
                        visited.add((nx, ny))
                        queue.append((nx, ny, dist + 1))
        return None

    def _definir_zones_bloquees(self):
        """Définit les zones qui ne peuvent pas être traversées"""
        rayons = [
            # Rayon horizontal
            ((68, 8), (80, 9)),
            ((22, 1), (29, 1)),
            ((33, 1), (47, 1)),
            ((49, 3), (57, 4)),
            ((59, 3), (80, 4)),
            ((68, 12), (80, 13)),
            ((68, 16), (80, 17)),
            ((68, 20), (80, 21)),

            ((68, 24), (80, 25)),
            ((68, 28), (80, 29)),
            ((68, 32), (80, 34)),
            ((68, 37), (80, 38)),
            ((68, 41), (80, 42)),
            ((68, 45), (80, 46)),
            ((68, 49), (80, 50)),
            ((68, 53), (80, 55)),
            ((68, 57), (84, 58)),
            ((4, 59), (18, 59)),
            ((12, 2), (19, 3)),

            # Rayon vertical
            ((2, 9), (3, 28)),
            ((2, 33), (3, 59)),
            ((7, 9), (8, 28)),
            ((7, 33), (8, 51)),
            ((12, 33), (13, 41)),
            ((12, 44), (13, 51)),
            ((13, 8), (14, 28)),
            ((16, 33), (17, 41)),

            ((16, 44), (17, 51)),
            ((18, 8), (19, 28)),
            ((21, 33), (22, 41)),
            ((21, 44), (22, 51)),
            ((23, 8), (25, 16)),
            ((23, 19), (25, 19)),
            ((23, 22), (25, 28)),

            ((25, 33), (26, 41)),
            ((25, 44), (26, 51)),
            ((29, 8), (31, 28)),
            ((29, 33), (30, 41)),
            ((29, 44), (30, 51)),
            ((35, 8), (36, 16)),
            ((35, 20), (36, 28)),

            ((33, 33), (35, 51)),
            ((38, 33), (39, 41)),
            ((38, 44), (39, 51)),
            ((40, 8), (42, 28)),
            ((42, 33), (43, 41)),
            ((42, 44), (43, 51)),
            ((45, 8), (47, 28)),

            ((48, 33), (49, 41)),
            ((46, 48), (51, 51)),
            ((50, 8), (52, 28)),
            ((54, 8), (55, 16)),
            ((54, 20), (55, 28)),
            ((54, 33), (55, 41)),
            ((54, 44), (55, 51)),

            ((58, 8), (60, 28)),
            ((58, 33), (60, 51)),
            ((84, 7), (84, 56)),

            # Zones spéciale (poisson)
            ((2, 6), (3, 6)),
            ((3, 5), (4, 5)),
            ((4, 4), (5, 4)),
            ((5, 3), (6, 3)),
            ((6, 2), (7, 2)),

            # Zones spéciale (caisses)
            ((21, 55), (34, 59)),
            ((38, 55), (59, 59)),

            # Zones spéciale (rond bleu)
            ((46, 46), (46, 46)),
            ((48, 44), (49, 45)),
            ((46, 43), (46, 43)),
            ((51, 43), (51, 43)),
            ((51, 46), (51, 46)),

        ]

        # Ajouter tous les points des rayons aux zones bloquées
        for (x1, y1), (x2, y2) in rayons:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if 0 <= x < self.grille_largeur and 0 <= y < self.grille_hauteur:
                        self.zones_bloquees.add((x - 1, y))

    def est_position_valide(self, x: int, y: int) -> bool:
        return (0 <= x < self.grille_largeur and
                0 <= y < self.grille_hauteur and
                (x, y) not in self.zones_bloquees)

    def obtenir_voisins(self, x: int, y: int) -> List[Tuple[int, int, float]]:
        voisins = []
        directions = [
            (-1, 0, 1.0),   # Gauche
            (1, 0, 1.0),    # Droite
            (0, -1, 1.0),   # Haut
            (0, 1, 1.0),    # Bas
            (-1, -1, 1.4),  # Diagonale haut-gauche
            (1, -1, 1.4),   # Diagonale haut-droite
            (-1, 1, 1.4),   # Diagonale bas-gauche
            (1, 1, 1.4),    # Diagonale bas-droite
        ]

        for dx, dy, cout in directions:
            nx, ny = x + dx, y + dy
            if self.est_position_valide(nx, ny):
                voisins.append((nx, ny, cout))

        return voisins

    def dijkstra(self, debut: Tuple[int, int], fin: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        file_priorite = [(0, debut[0], debut[1])]
        distances = {debut: 0}
        predecesseurs = {}
        visites = set()

        while file_priorite:
            dist_actuelle, x, y = heapq.heappop(file_priorite)

            if (x, y) in visites:
                continue

            visites.add((x, y))

            if (x, y) == fin:
                break

            for nx, ny, cout in self.obtenir_voisins(x, y):
                if (nx, ny) not in visites:
                    nouvelle_distance = dist_actuelle + cout

                    if (nx, ny) not in distances or nouvelle_distance < distances[(nx, ny)]:
                        distances[(nx, ny)] = nouvelle_distance
                        predecesseurs[(nx, ny)] = (x, y)
                        heapq.heappush(file_priorite, (nouvelle_distance, nx, ny))

        if fin not in predecesseurs and fin != debut:
            return [], float('inf')

        chemin = []
        actuel = fin
        while actuel is not None:
            chemin.append(actuel)
            actuel = predecesseurs.get(actuel)
        chemin.reverse()
        distance_totale = distances.get(fin, float('inf'))

        return chemin, distance_totale

    def calculer_chemin_optimal(self, positions_produits: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], float]:
        if not positions_produits:
            return [], 0

        points_a_visiter = [self.entree]

        points_a_visiter = [self.entree]

        for x, y in positions_produits:
            if not self.est_position_valide(x, y):
                voisin = self.trouver_case_accessible_autour(x, y)
                if voisin:
                    points_a_visiter.append(voisin)
            else:
                points_a_visiter.append((x, y))

        points_a_visiter.append(self.caisse)

        if len(points_a_visiter) <= 3:
            chemin_complet = []
            distance_totale = 0
            for i in range(len(points_a_visiter) - 1):
                chemin_segment, distance = self.dijkstra(points_a_visiter[i], points_a_visiter[i + 1])
                if chemin_segment:
                    if chemin_complet:
                        chemin_segment = chemin_segment[1:]
                    chemin_complet.extend(chemin_segment)
                    distance_totale += distance
                else:
                    return [], float('inf')

            return chemin_complet, distance_totale
        return self._chemin_glouton(points_a_visiter)

    def _chemin_glouton(self, points: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], float]:
        if len(points) <= 2:
            return self.dijkstra(points[0], points[-1])

        chemin_complet = []
        distance_totale = 0

        position_actuelle = points[0]
        points_restants = points[1:-1]  # Exclus entrée et caisse
        caisse = points[-1]

        while points_restants:
            distances_aux_points = []
            for point in points_restants:
                _, distance = self.dijkstra(position_actuelle, point)
                distances_aux_points.append((distance, point))

            distances_aux_points.sort()
            if distances_aux_points[0][0] == float('inf'):
                return [], float('inf')  # Pas de chemin possible

            prochain_point = distances_aux_points[0][1]
            points_restants.remove(prochain_point)

            # Calculer le chemin vers ce point
            chemin_segment, distance = self.dijkstra(position_actuelle, prochain_point)
            if chemin_segment:
                if chemin_complet:
                    chemin_segment = chemin_segment[1:]  # Éviter les doublons
                chemin_complet.extend(chemin_segment)
                distance_totale += distance
                position_actuelle = prochain_point
            else:
                return [], float('inf')

        # Aller à la caisse
        chemin_segment, distance = self.dijkstra(position_actuelle, caisse)
        if chemin_segment:
            if chemin_complet:
                chemin_segment = chemin_segment[1:]  # Éviter les doublons
            chemin_complet.extend(chemin_segment)
            distance_totale += distance
        else:
            return [], float('inf')

        return chemin_complet, distance_totale
