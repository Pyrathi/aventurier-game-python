"""
views.py
Ce fichier gère l'affichage (La Vue).
Il ne prend aucune décision, il se contente d'afficher l'état du modèle.

# Pour une meilleure organisation, il serait préférable de placer tous les messages 
# affichés dans un dictionnaire dans un fichier textes.py.
# Exemple : TEXTES = {"game_over": "GAME OVER !", ...}
"""
import os
import re
from typing import TYPE_CHECKING
from settings import (
    GRID_SIZE, NB_MONSTERS, POINTS_PER_MONSTER, POINTS_PER_HP, 
    ELEMENT_COLORS, SHOW_SCORE_DURING_GAME,
    DEPARTURE_SYMBOL, ARRIVAL_SYMBOL, PlayerAction
)

# Import conditionnel pour les type hints uniquement (évite les imports circulaires)
# TYPE_CHECKING = True seulement durant l'analyse statique (mypy/IDE)
# TYPE_CHECKING = False durant l'exécution → pas d'import réel → pas de circularité
if TYPE_CHECKING:
    from models import Hero, Board, CombatResult

class ConsoleView:
    def clear_screen(self) -> None:
        """Nettoie la console pour un affichage fluide"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_board(self, hero: 'Hero', board: 'Board') -> None:
        """Affiche la grille, le héros, les monstres et les équipements"""
        self.clear_screen()
        print("-" * (board.size * 4 + 1))
        
        for y in range(board.size):
            row_str = "|"
            for x in range(board.size):
                cell_content = "   " # Case vide
                
                # Vérifier si le héros est là
                if hero.x == x and hero.y == y:
                    cell_content = f" {ELEMENT_COLORS['HERO']}{hero.symbol}{ELEMENT_COLORS['RESET']} "
                
                # Vérifier si un monstre est là
                else:
                    for m in board.monsters:
                        if m.x == x and m.y == y:
                            cell_content = f" {ELEMENT_COLORS['MONSTER']}{m.symbol}{ELEMENT_COLORS['RESET']} "
                            break
                    
                    # Si pas de monstre, vérifier s'il y a un équipement
                    if cell_content == "   ":
                        for equipment in board.equipments:
                            if equipment.x == x and equipment.y == y:
                                cell_content = f" {ELEMENT_COLORS['EQUIPMENT']}{equipment.symbol}{ELEMENT_COLORS['RESET']} "
                                break
                    
                    # Si pas d'équipement, afficher départ/arrivée
                    if cell_content == "   ":
                        if x == 0 and y == 0:  # Case départ
                            cell_content = f" {ELEMENT_COLORS['DEPARTURE']}{DEPARTURE_SYMBOL}{ELEMENT_COLORS['RESET']} "
                        elif x == board.size - 1 and y == board.size - 1:  # Case arrivée
                            cell_content = f" {ELEMENT_COLORS['ARRIVAL']}{ARRIVAL_SYMBOL}{ELEMENT_COLORS['RESET']} "
                
                row_str += cell_content + "|"
            print(row_str)
            print("-" * (board.size * 4 + 1))

    def show_stats(self, hero: 'Hero') -> None:
        """Affiche les stats du joueur"""
        print(f"\nHEROS | {ELEMENT_COLORS['HP']}PV: {hero.hp}/{hero.max_hp}{ELEMENT_COLORS['RESET']} | {ELEMENT_COLORS['FORCE']}Force: {hero.force}{ELEMENT_COLORS['RESET']} (base: {hero.base_force})")
        
        # Affichage conditionnel du score
        if SHOW_SCORE_DURING_GAME:
            print(f"Score: {hero.score} | Monstres vaincus: {hero.monsters_defeated}/{NB_MONSTERS} | Mouvements: {hero.move_count}")
        if hero.inventory:
            print(f"{ELEMENT_COLORS['INVENTORY']}Inventaire:{ELEMENT_COLORS['RESET']}")
            # Tri des armes par puissance décroissante (du plus fort au plus faible)
            sorted_weapons = sorted(hero.inventory, reverse=True)  # Utilise __gt__ de Weapon
            
            # Utilisation de map() + lambda pour formater chaque arme
            weapon_descriptions = map(
                lambda w: f"  - {w.weapon_name} ({ELEMENT_COLORS['FORCE']}+{w.force_bonus} Force{ELEMENT_COLORS['RESET']})",
                sorted_weapons
            )
            print("\n".join(weapon_descriptions))
            
            # Affichage  de l'arme la plus puissante
            strongest_weapon = max(hero.inventory)  # Utilise __gt__ de Weapon
            print(f"    ⚡ Arme la plus puissante: {strongest_weapon.weapon_name}")
        else:
            print(f"{ELEMENT_COLORS['INVENTORY']}Inventaire:{ELEMENT_COLORS['RESET']} aucune arme")
        print(f"Légende: {ELEMENT_COLORS['HERO']}H{ELEMENT_COLORS['RESET']}=Héros, {ELEMENT_COLORS['MONSTER']}M{ELEMENT_COLORS['RESET']}=Monstre, {ELEMENT_COLORS['EQUIPMENT']}O{ELEMENT_COLORS['RESET']}=Équipement, {ELEMENT_COLORS['DEPARTURE']}D{ELEMENT_COLORS['RESET']}=Départ, {ELEMENT_COLORS['ARRIVAL']}A{ELEMENT_COLORS['RESET']}=Arrivée")
        print("Commandes: ↑ (Haut), ← (Gauche), ↓ (Bas), → (Droite), ESPACE (Attaquer), X (Quitter)")
    
    def show_victory(self, hero: 'Hero') -> None:
        """Affiche le message de victoire avec le score"""
        print("\n" + "="*50)
        print(f"{ELEMENT_COLORS['VICTORY']}🎉 VICTOIRE ! Vous avez atteint la sortie ! 🎉{ELEMENT_COLORS['RESET']}")
        print(f"\n🏆 VOTRE SCORE FINAL: {ELEMENT_COLORS['ACTION_MESSAGE']}{hero.score} POINTS{ELEMENT_COLORS['RESET']}")
        print(f"   ⚔️  Monstres vaincus: {hero.monsters_defeated} (+{POINTS_PER_MONSTER * hero.monsters_defeated} pts)")
        print(f"   ❤️  PV restants: {hero.hp} (+{POINTS_PER_HP * hero.hp} pts)")
        print(f"   👾 Déplacements: {hero.move_count} (-{hero.move_count} pts)")
        
        # Évaluation du score
        # Calcul des seuils de score basés sur la configuration (incluant PV max)
        perfect_score = (NB_MONSTERS * POINTS_PER_MONSTER) + (hero.max_hp * POINTS_PER_HP) - (2 * GRID_SIZE - 2)  # Score parfait
        very_good_threshold = perfect_score - (NB_MONSTERS + hero.max_hp)  # Très bien
        good_threshold = very_good_threshold - (NB_MONSTERS + hero.max_hp)  # OK
        
        # Messages de performance basés sur les seuils calculés
        if hero.score == perfect_score:
            print(f"🏆 SCORE PARFAIT ! Félicitations ! ({hero.score}pts)")
        elif hero.score >= very_good_threshold:
            print(f"⭐⭐⭐ TRÈS BIEN ! Excellent travail ! ({hero.score}pts)")
        elif hero.score >= good_threshold:
            print(f"⭐⭐ OK ! Performance correcte ! ({hero.score}pts)")
        elif hero.score > 0:
            print(f"⭐ Peut mieux faire ! Continuez vos efforts ! ({hero.score}pts)")
        else:
            print(f"🌟 Gardez espoir ! La prochaine fois sera meilleure ! ({hero.score}pts)")
        
        print(f"\n🎯 Astuce: Score parfait = {perfect_score}pts (tous les monstres + chemin optimal + PV max)")
        print("="*50)
    
    def show_game_over(self, hero: 'Hero') -> None:
        """Affiche un écran de GAME OVER dramatique"""
        print("\n" + "="*60)
        print("█▀▀▀ █▀▀█ █▀▄▀█ █▀▀     █▀▀█ █   █ █▀▀ █▀▀█")
        print("█ ▀█ █▄▄█ █ █ █ █▀▀     █  █ █   █ █▀▀ █▄▄▀") 
        print("▀▀▀▀ ▀  ▀ ▀   ▀ ▀▀▀     ▀▀▀▀  ▀▀▀  ▀▀▀ ▀ ▀▀")
        print("="*60)
        print("\n💀 Vous êtes mort ! Votre aventure se termine ici...")
        print(f"\n📊 VOTRE SCORE FINAL: {ELEMENT_COLORS['ACTION_MESSAGE']}{hero.score} POINTS{ELEMENT_COLORS['RESET']}")
        print(f"   ⚔️  Monstres vaincus: {hero.monsters_defeated}")
        print(f"   👣 Déplacements: {hero.move_count}")
        print("   💔 Cause: Épuisement (0 PV)")
        print("="*60)
    
    def show_action_message(self, message: str) -> None:
        """Affiche un message d'action coloré"""
        print(f"\n{ELEMENT_COLORS['ACTION_MESSAGE']}{message}{ELEMENT_COLORS['RESET']}")
    
    def show_combat_prompt(self) -> None:
        """Affiche le prompt de combat"""
        print(f"\n{ELEMENT_COLORS['COMBAT_PROMPT']}⚔️  EN COMBAT ! Appuyez sur ESPACE pour attaquer ou déplacez-vous pour fuir{ELEMENT_COLORS['RESET']}")
    
    def show_goodbye(self) -> None:
        """Affiche le message d'au revoir"""
        print("Au revoir !")
    
    def show_farewell(self) -> None:
        """Affiche le message de fin de partie"""
        print("Merci d'avoir joué !")
    
    def show_new_record(self, old_record: int) -> None:
        """Affiche le message de nouveau record"""
        if old_record > 0:
            print(f"\n{ELEMENT_COLORS['ACTION_MESSAGE']}🏆 NOUVEAU RECORD ! Ancien record battu : {old_record} points{ELEMENT_COLORS['RESET']}")
        else:
            print(f"\n{ELEMENT_COLORS['ACTION_MESSAGE']}🏆 PREMIER RECORD ÉTABLI !{ELEMENT_COLORS['RESET']}")
    
    def show_current_best(self, best_score: int) -> None:
        """Affiche le meilleur score actuel"""
        print(f"\n🏅 Meilleur score actuel: {best_score} points")
    
    def format_combat_message(self, combat_result: 'CombatResult', hero_score: int) -> str:
        """Formate le message de combat basé sur les résultats du modèle"""
        dice_roll = combat_result.dice_roll
        
        # Utiliser le seuil pré-calculé dans CombatResult (évite la redondance)
        threshold_to_beat = combat_result.failure_threshold
        
        message = f"🎲 Jet: {dice_roll}/{threshold_to_beat:.0f} "
        
        if combat_result.hit:
            if combat_result.monster_died:
                message += f"{ELEMENT_COLORS['COMBAT_SUCCESS']}💀 MONSTRE VAINCU ! 🎉{ELEMENT_COLORS['RESET']}"
            else:
                remaining_hp = combat_result.monster_hp
                max_hp = combat_result.monster_max_hp
                message += f"{ELEMENT_COLORS['COMBAT_HIT']}💥 Touché ! Monstre: {ELEMENT_COLORS['HP']}{remaining_hp}/{max_hp} HP{ELEMENT_COLORS['RESET']}"
        else:
            hero_hp = combat_result.hero_hp
            hero_max_hp = combat_result.hero_max_hp
            message += f"{ELEMENT_COLORS['COMBAT_MISS']}❌ Raté ! Vous perdez {combat_result.damage_taken} HP ({ELEMENT_COLORS['HP']}{hero_hp}/{hero_max_hp}{ELEMENT_COLORS['RESET']}){ELEMENT_COLORS['RESET']}"
        
        return message

    def get_player_input(self) -> PlayerAction:
        """Capture l'input du joueur et retourne une PlayerAction"""
        if os.name == 'nt':  # Windows
            import msvcrt
            print("Votre action > ", end='', flush=True)
            key = msvcrt.getch()
            
            if key == b'\xe0':  # Séquence d'échappement pour les touches spéciales
                key = msvcrt.getch()
                if key == b'H':    # Flèche haut
                    print("↑")
                    return PlayerAction.MOVE_UP
                elif key == b'P':  # Flèche bas
                    print("↓")
                    return PlayerAction.MOVE_DOWN
                elif key == b'K':  # Flèche gauche
                    print("←")
                    return PlayerAction.MOVE_LEFT
                elif key == b'M':  # Flèche droite
                    print("→")
                    return PlayerAction.MOVE_RIGHT
            elif key.lower() == b'x':
                print("x")
                return PlayerAction.QUIT
            elif key == b' ':  # Barre d'espace
                print("ESPACE")
                return PlayerAction.ATTACK
            else:
                print(key.decode('utf-8', errors='ignore'))
                return PlayerAction.UNKNOWN
        else:  # Linux/Mac (fallback avec input classique)
            action = input("Votre action (↑/↓/←/→/espace/x) > ").strip()
            
            # Patterns regex pour chaque action (plus élégant que les elif)
            action_patterns = {
                PlayerAction.MOVE_UP: r'^(up|u|z|↑)$',
                PlayerAction.MOVE_DOWN: r'^(down|d|s|↓)$',
                PlayerAction.MOVE_LEFT: r'^(left|l|q|←)$',
                PlayerAction.MOVE_RIGHT: r'^(right|r|→)$',
                PlayerAction.ATTACK: r'^(espace|space| )$',
                PlayerAction.QUIT: r'^(x|quit|exit)$'
            }
            
            # Parser avec regex : teste chaque pattern jusqu'à trouver un match
            for player_action, pattern in action_patterns.items():
                if re.match(pattern, action, re.IGNORECASE):
                    return player_action
            
            # VERSION AVEC GENERATOR EXPRESSION (équivalent plus fonctionnel) :
            # matched_actions = (
            #     player_action for player_action, pattern in action_patterns.items()
            #     if re.match(pattern, action, re.IGNORECASE)
            # )
            # return next(matched_actions, PlayerAction.UNKNOWN)
            
            # Aucun pattern ne correspond
            return PlayerAction.UNKNOWN

if __name__ == "__main__":
    print("ATTENTION: Ce fichier contient les vues et l'affichage du jeu.")
    print("Pour lancer le jeu, exécutez : python controller.py")
