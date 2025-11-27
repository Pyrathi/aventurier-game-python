from __future__ import annotations
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from settings import (
    GRID_SIZE, START_POSITION, END_POSITION, NB_MONSTERS, NB_EQUIPMENTS_MIN, NB_EQUIPMENTS_MAX,
    EQUIPMENT_SYMBOL, HERO_SYMBOL, MONSTER_SYMBOL,
    MONSTER_HP, MONSTER_DAMAGE, MONSTER_DEFENSE, HERO_DAMAGE,
    POTION_HEAL,
    POINTS_PER_MONSTER, POINTS_PER_HP,
    PlayerAction
)

"""
models.py
Ce fichier gère la logique des données (Le Modèle).
Il contient les classes Hero, Monster et Board.

# -------------------------------------------------------------
# NOTE PEDAGOGIQUE :
# Ce fichier est volontairement gardé unique pour faciliter l'exercice git
# Il serait préférable de le scinder en plusieurs modules :
#   - entities.py      (Hero, Monster, Entity)
#   - equipment.py     (Weapon, Potion, Equipment, WeaponType)
#   - board.py         (Board, génération de la grille)
#   - combat.py        (CombatResult, logique d'attaque)
# Cela rendrait le code plus modulaire, maintenable et réutilisable.
# -------------------------------------------------------------
"""
@dataclass
class CombatResult:
    """Résultat d'une attaque de combat"""
    hit_chance: float
    dice_roll: int
    hit: bool
    hero_magic: int
    monster_died: bool
    monster_hp: int
    monster_max_hp: int
    hero_hp: int
    hero_max_hp: int
    damage_taken: int
    failure_threshold: int  # Seuil à atteindre pour réussir l'attaque

class WeaponType(Enum):
    """Types d'armes disponibles avec leurs caractéristiques"""
    RUSTY_SWORD = ("Épée rouillée", 1)
    IRON_SWORD = ("Épée en fer", 2)
    ENCHANTED_SWORD = ("Épée enchantée", 3)
    POISON_DAGGER = ("Dague empoisonnée", 2)
    WAR_HAMMER = ("Marteau de guerre", 3)
    ELVEN_BOW = ("Arc elfique", 2)
    MAGIC_STAFF = ("Bâton magique", 1)
    
    def __init__(self, display_name: str, force_bonus: int):
        self.display_name = display_name
        self.force_bonus = force_bonus
    
    def __str__(self):
        return self.display_name

class Entity:
    """Classe de base pour toute entité sur la carte"""
    def __init__(self, position, symbol):
        self.position = position  # (x, y) tuple
        self.symbol = symbol
    
    @property
    def x(self):
        """Position X (première valeur du tuple)"""
        return self.position[0] if self.position else None
    
    @property
    def y(self):
        """Position Y (deuxième valeur du tuple)"""
        return self.position[1] if self.position else None
    
    @x.setter
    def x(self, value):
        """Met à jour la position X"""
        if self.position:
            self.position = (value, self.position[1])
        else:
            self.position = (value, None)
    
    @y.setter
    def y(self, value):
        """Met à jour la position Y"""
        if self.position:
            self.position = (self.position[0], value)
        else:
            self.position = (None, value)

class Equipment(Entity, ABC):
    """Classe abstraite pour les équipements ramassables"""
    def __init__(self, position):
        super().__init__(position, EQUIPMENT_SYMBOL)
    
    @abstractmethod
    def apply_effect(self, hero: 'Hero') -> str:
        """Applique l'effet de l'équipement au héros - doit être redéfinie dans les classes filles"""
        pass

class Potion(Equipment):
    """Potion consommée immédiatement qui restaure les HP (ne peut pas dépasser les HP max)"""
    def apply_effect(self, hero: 'Hero') -> str:
        old_hp = hero.hp
        hero.hp = min(hero.hp + POTION_HEAL, hero.max_hp)
        actual_heal = hero.hp - old_hp
        return f"Vous buvez une potion ! +{actual_heal} PV (HP: {hero.hp}/{hero.max_hp})"

class Weapon(Equipment):
    """Arme ajoutée à l'inventaire qui augmente la force totale du héros"""
    def __init__(self, position, weapon_type: WeaponType):
        super().__init__(position)
        self.weapon_type = weapon_type
        self.found_position = None  # Position (x, y) où l'arme a été trouvée
    
    @property
    def weapon_name(self):
        """Nom d'affichage de l'arme"""
        return self.weapon_type.display_name
    
    @property
    def force_bonus(self):
        """Bonus de force de l'arme"""
        return self.weapon_type.force_bonus
    
    def apply_effect(self, hero: 'Hero') -> str:
        # Sauvegarder où l'arme a été trouvée
        self.found_position = self.position
        # Marquer comme équipée (plus de position sur la carte)
        self.position = None
        # Stocker l'objet Weapon 
        hero.weapons.append(self)
        return f"Vous équipez {self.weapon_name} ! +{self.force_bonus} Force (Total: {hero.force})"
    
    # Méthodes dunder de comparaison des armes basées sur force_bonus
    def __eq__(self, other):
        """Comparaison d'égalité basée sur la force_bonus"""
        if not isinstance(other, Weapon):
            return NotImplemented
        return self.force_bonus == other.force_bonus
    
    def __lt__(self, other):
        """Comparaison 'inférieur à' basée sur la force_bonus"""
        if not isinstance(other, Weapon):
            return NotImplemented
        return self.force_bonus < other.force_bonus
    
    def __le__(self, other):
        """Comparaison 'inférieur ou égal' basée sur la force_bonus"""
        if not isinstance(other, Weapon):
            return NotImplemented
        return self.force_bonus <= other.force_bonus
    
    def __gt__(self, other):
        """Comparaison 'supérieur à' basée sur la force_bonus"""
        if not isinstance(other, Weapon):
            return NotImplemented
        return self.force_bonus > other.force_bonus
    
    def __ge__(self, other):
        """Comparaison 'supérieur ou égal' basée sur la force_bonus"""
        if not isinstance(other, Weapon):
            return NotImplemented
        return self.force_bonus >= other.force_bonus
    
    def __str__(self):
        origin = f" (trouvée en {self.found_position})" if self.found_position else ""
        return f"{self.weapon_name}{origin}"

class Monster(Entity):
    """Monstre ennemi avec HP"""
    def __init__(self, position):
        super().__init__(position, MONSTER_SYMBOL)
        self.hp = MONSTER_HP
        self.max_hp = MONSTER_HP

class Hero(Entity):
    """Le héros contrôlé par le joueur"""
    def __init__(self, hp, base_force):
        super().__init__(START_POSITION, HERO_SYMBOL) # Départ selon START_POSITION
        self.hp = hp
        self.magic = magic
        self.max_hp = hp  # HP maximum pour les potions
        self.base_force = base_force
        self.weapons = []  # Liste des armes équipées
        self.move_count = 0  # Compteur de mouvements
        self.monsters_defeated = 0  # Compteur de monstres vaincus
    
    @property
    def force(self) -> int:
        """Force totale = force de base + somme des bonus des armes"""
        # Generator expression : calcule efficacement la somme sans créer de liste
        weapon_bonus = sum(weapon.force_bonus for weapon in self.weapons)
        return self.base_force + weapon_bonus + self.magic
    
    @property
    def inventory(self):
        """Inventaire visible (seulement les armes)"""
        return self.weapons.copy()
    
    @property
    def score(self):
        """Calcul du score : POINTS_PER_MONSTER * monstres vaincus + POINTS_PER_HP * PV restants - nombre de déplacements
        Retourne 0 si le héros est mort (Game Over)"""
        if self.is_dead():
            return 0  # Game Over = 0 points
        
        return (POINTS_PER_MONSTER * self.monsters_defeated) + (POINTS_PER_HP * self.hp) - self.move_count
    
    def has_won(self):
        """Vérifie si le héros a atteint la condition de victoire"""
        return self.position == END_POSITION
    
    def is_dead(self):
        """Vérifie si le héros est mort"""
        return self.hp <= 0

    def move(self, action: PlayerAction) -> None:
        """Déplace le héros selon l'action PlayerAction fournie"""
        x, y = self.position
        new_x, new_y = x, y
        if action == PlayerAction.MOVE_UP and y > 0:
            new_y -= 1  # Haut
        elif action == PlayerAction.MOVE_DOWN and y < GRID_SIZE - 1:
            new_y += 1  # Bas
        elif action == PlayerAction.MOVE_LEFT and x > 0:
            new_x -= 1  # Gauche
        elif action == PlayerAction.MOVE_RIGHT and x < GRID_SIZE - 1:
            new_x += 1  # Droite
        
        # Si le héros a effectivement bougé, incrémenter le compteur
        if (new_x, new_y) != (x, y):
            self.move_count += 1
        
        self.position = (new_x, new_y)

    def attack(self, monster: 'Monster') -> CombatResult:
        """Attaque un monstre avec un système de probabilité. Retourne un CombatResult"""
        hit_chance = min(95, max(5, self.force / MONSTER_DEFENSE * 100))  # Entre 5% et 95%
        dice_roll = random.randint(1, 100)
        
        # Nouveau système : réussir sur les GROS jets (au-dessus du seuil d'échec)
        failure_threshold = 100 - hit_chance
        hit = dice_roll >= failure_threshold  # Changement ici : >= au lieu de <=
        monster_died = False
        damage_taken = 0
        
        if hit:
            # Touché !
            monster.hp -= HERO_DAMAGE  # Utiliser HERO_DAMAGE au lieu de 1 hardcodé
            monster_died = monster.hp <= 0
            if monster_died:
                self.monsters_defeated += 1
        else:
            # Raté !
            damage_taken = MONSTER_DAMAGE
            self.hp -= MONSTER_DAMAGE
        
        return CombatResult(
            hit_chance=hit_chance,
            dice_roll=dice_roll,
            hit=hit,
            monster_died=monster_died,
            monster_hp=monster.hp,
            monster_max_hp=monster.max_hp,
            hero_hp=self.hp,
            hero_max_hp=self.max_hp,
            damage_taken=damage_taken,
            failure_threshold=failure_threshold
        )
    
    def use_equipment(self, equipment: Equipment) -> str:
        """Utilise un équipement (potion ou arme)"""
        return equipment.apply_effect(self)

class Board:
    """Gère la grille de jeu"""
    def __init__(self):
        self.size = GRID_SIZE
        self.monsters = []
        self.equipments = []
        # Créer UN SEUL générateur pour tout le board
        self.position_generator = self._unique_valid_positions_generator()
        self.generate_monsters()
        self.generate_equipments()

    def _unique_valid_positions_generator(self):
        """
        Generator : Génère des positions valides uniques.
        """
        forbidden_positions = {START_POSITION, END_POSITION}
        
        # Générer toutes les positions possibles et les mélanger
        all_positions = []
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) not in forbidden_positions:
                    all_positions.append((x, y))
        
        # VERSION AVEC LIST COMPREHENSION (équivalent plus concis) :
        # all_positions = [
        #     (x, y) for x in range(self.size)
        #     for y in range(self.size)
        #     if (x, y) not in forbidden_positions
        # ]
        
        random.shuffle(all_positions)  # Mélange pour l'aléatoire
        
        # Boucle infinie : re-parcourt la même séquence indéfiniment
        while True:
            yield from all_positions  # Pattern "yield from" - Délègue au générateur de liste
    
    def generate_monsters(self):
        """Place des monstres aléatoirement (hors cases départ et arrivée)"""
        # Utilisation du generator UNIQUE partagé pour garantir des positions différentes
        for _ in range(NB_MONSTERS):
            try:
                position = next(self.position_generator)  # Récupère la prochaine position unique
                self.monsters.append(Monster(position))
            except StopIteration:
                # Plus de positions disponibles - ne devrait pas arriver avec une grille normale
                break
    
    def generate_equipments(self):
        """Place des équipements aléatoirement sur la carte (hors cases départ et arrivée)"""
        # Utilisation du générateur partagé pour éviter les collisions avec les monstres
        nb_equipments = random.randint(NB_EQUIPMENTS_MIN, NB_EQUIPMENTS_MAX)
        
        for _ in range(nb_equipments):
            try:
                position = next(self.position_generator)  # Récupère la prochaine position unique
                # Plus besoin de vérifier les collisions puisque le générateur garantit l'unicité
                # 50% de chance d'être une potion, 50% une arme
                if random.choice([True, False]):
                    # Créer une potion
                    self.equipments.append(Potion(position))
                else:
                    # Créer une arme aléatoire
                    weapon_type = random.choice(list(WeaponType))
                    self.equipments.append(Weapon(position, weapon_type))
            except StopIteration:
                # Plus de positions disponibles
                break
    
    def get_equipment_at(self, position):
        """Retourne l'équipement à la position donnée, s'il y en a un"""
        for equipment in self.equipments:
            if equipment.position == position:
                return equipment
        return None
    
    def remove_equipment(self, equipment):
        """Supprime un équipement de la carte"""
        if equipment in self.equipments:
            self.equipments.remove(equipment)
    
    def get_monster_at(self, position):
        """Retourne le monstre à la position donnée, s'il y en a un"""
        for monster in self.monsters:
            if monster.position == position:
                return monster
        return None
    
    def remove_monster(self, monster):
        """Supprime un monstre de la carte"""
        if monster in self.monsters:
            self.monsters.remove(monster)

if __name__ == "__main__":
    print("ATTENTION: Ce fichier contient les modèles de données du jeu.")

    print("Pour lancer le jeu, exécutez : python controller.py")
