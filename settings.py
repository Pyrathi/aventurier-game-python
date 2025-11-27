"""
settings.py
Ce fichier contient toutes les constantes de configuration du jeu.
"""
from enum import Enum, auto


class PlayerAction(Enum):
    """
    Énumération des actions possibles du joueur.
    
    Utilise auto() pour générer automatiquement les valeurs,
    ce qui rend le code plus maintenable.
    """
    QUIT = auto()           # Quitter le jeu
    ATTACK = auto()         # Attaquer en combat
    MOVE_UP = auto()        # Se déplacer vers le haut
    MOVE_DOWN = auto()      # Se déplacer vers le bas
    MOVE_LEFT = auto()      # Se déplacer vers la gauche
    MOVE_RIGHT = auto()     # Se déplacer vers la droite
    UNKNOWN = auto()        # Action non reconnue


# Configuration de la Carte
GRID_SIZE = 5  # Taille de la grille (5x5)
START_POSITION = (0, 0)  # Position de départ du héros
END_POSITION = (GRID_SIZE - 1, GRID_SIZE - 1)  # Position d'arrivée (calculée selon GRID_SIZE)
NB_MONSTERS = 7 # Nombre de monstres sur la carte

# Configuration du Héros
   
START_HP = 7       # Points de vie de départ
START_FORCE = 10   # Force de frappe de base
HERO_DAMAGE = 1    # Dégâts infligés par le héros quand il touche
HERO_SYMBOL = "H"  # Symbole pour l'affichage

# Configuration des Monstres
MONSTER_HP = 1        # Points de vie des monstres (mort en 1 coup)
MONSTER_DAMAGE = 1    # Dégâts infligés par le monstre
MONSTER_DEFENSE = 20  # Défense du monstre (utilisée pour calculer les chances de toucher)
MONSTER_SYMBOL = "M"

# Configuration du Scoring
POINTS_PER_MONSTER = 5   # Points gagnés par monstre vaincu
POINTS_PER_HP = 2        # Points gagnés par PV restant à la fin
ENABLE_HIGHSCORE = True  # Activer/désactiver le système de highscore
SHOW_SCORE_DURING_GAME = False  # Afficher le score pendant la partie

# Symboles d'affichage
DEPARTURE_SYMBOL = "D"  # Symbole pour la case de départ
ARRIVAL_SYMBOL = "A"    # Symbole pour la case d'arrivée

# Configuration des Équipements
POTION_HEAL = 2       # PV rendus par une potion
NB_EQUIPMENTS_MIN = 4 # Nombre minimum d'équipements sur la carte
NB_EQUIPMENTS_MAX = 5 # Nombre maximum d'équipements sur la carte
EQUIPMENT_SYMBOL = "O"  # Symbole pour les équipements

# Codes couleurs ANSI de base
ANSI_COLORS = {
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'GREEN': '\033[92m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'MAGENTA': '\033[95m',
    'WHITE': '\033[97m',
    'RESET': '\033[0m'
}

# Configuration des couleurs par élément du jeu
ELEMENT_COLORS = {
    'HERO': ANSI_COLORS['BLUE'],          # Héros (H)
    'MONSTER': ANSI_COLORS['RED'],        # Monstres (M)
    'EQUIPMENT': ANSI_COLORS['YELLOW'],   # Équipements (O)
    'DEPARTURE': ANSI_COLORS['GREEN'],    # Case départ (D)
    'ARRIVAL': ANSI_COLORS['GREEN'],      # Case arrivée (A)
    'COMBAT_SUCCESS': ANSI_COLORS['GREEN'],  # Messages de succès au combat
    'COMBAT_HIT': ANSI_COLORS['YELLOW'],     # Messages de coup réussi
    'COMBAT_MISS': ANSI_COLORS['RED'],       # Messages de coup raté
    'COMBAT_PROMPT': ANSI_COLORS['CYAN'],    # Prompt d'instruction de combat
    'HP': ANSI_COLORS['RED'],             # Points de vie
    'FORCE': ANSI_COLORS['BLUE'],         # Force/Attaque
    'INVENTORY': ANSI_COLORS['MAGENTA'],  # Inventaire
    'COMMANDS': ANSI_COLORS['CYAN'],      # Dernière phrase active (commandes)
    'ACTION_MESSAGE': ANSI_COLORS['CYAN'], # Messages d'action (potions, armes)
    'VICTORY': ANSI_COLORS['GREEN'],      # Message de victoire
    'RESET': ANSI_COLORS['RESET']
}

if __name__ == "__main__":
    print("ATTENTION: Ce fichier contient uniquement des constantes de configuration.")
    print("Pour lancer le jeu, exécutez : python controller.py")
