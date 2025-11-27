"""
controller.py
Le Chef d'Orchestre. Il initialise le jeu et gère la boucle principale.
Peut fonctionner avec une ou plusieurs views simultanément.
"""
from typing import Type
from models import Hero, Board
from console_view import ConsoleView
from settings import START_HP, START_FORCE, ENABLE_HIGHSCORE, PlayerAction

# Import optionnel du système de highscore
try:
    from highscore import HighScoreManager
    HIGHSCORE_AVAILABLE = True
except ImportError:
    HIGHSCORE_AVAILABLE = False

def main(view_class: Type[ConsoleView] = ConsoleView) -> None:
    """
    Fonction principale du jeu.
    
    Args:
        view_class: Classe de la view à utiliser (ConsoleView, TkinterView, etc.)
    """
    # 1. Initialisation (Setup)
    view = view_class()
    
    # Initialisation optionnelle du highscore
    if ENABLE_HIGHSCORE and HIGHSCORE_AVAILABLE:
        highscore_manager = HighScoreManager()
    else:
        highscore_manager = None
    
    hero = Hero(hp=START_HP, base_force=START_FORCE)
    board = Board()
    
    running = True
    last_action_message = None  # Message de la dernière action
    in_combat = False  # État de combat
    current_monster = None  # Monstre actuellement en combat

    # 2. Boucle de jeu
    while running:
        # Vérifier si le héros est mort, si oui fin
        if hero.is_dead():
            view.display_board(hero, board)
            view.show_game_over(hero)
            running = False
            continue
        
        # A. Affichage
        view.display_board(hero, board)
        view.show_stats(hero)
        
        # Afficher le message de la dernière action s'il y en a un
        if last_action_message:
            view.show_action_message(last_action_message)
            last_action_message = None  # Réinitialiser après affichage
        
        # Affichage spécial en combat
        if in_combat and current_monster:
            view.show_combat_prompt()

        # B. Input Joueur
        action = view.get_player_input()

        # C. Logique
        if action == PlayerAction.QUIT:
            running = False
            view.show_goodbye()
        elif action == PlayerAction.ATTACK and in_combat and current_monster:
            # Attaque en combat
            combat_result = hero.attack(current_monster)
            last_action_message = view.format_combat_message(combat_result, hero.score)
            
            if combat_result.monster_died:
                board.remove_monster(current_monster)
                in_combat = False
                current_monster = None
            
        elif action in [PlayerAction.MOVE_UP, PlayerAction.MOVE_DOWN, PlayerAction.MOVE_LEFT, PlayerAction.MOVE_RIGHT]:
            # Sortir du combat si on se déplace
            in_combat = False
            current_monster = None
            
            # Appel direct avec l'enum PlayerAction
            hero.move(action)
            
            # Vérification de collecte d'équipement
            equipment = board.get_equipment_at(hero.position)
            if equipment:
                last_action_message = hero.use_equipment(equipment)
                board.remove_equipment(equipment)
            
            # Vérification de combat avec monstre
            monster = board.get_monster_at(hero.position)
            if monster:
                # Entrer en combat
                in_combat = True
                current_monster = monster
                combat_result = hero.attack(monster)
                last_action_message = view.format_combat_message(combat_result, hero.score)
                
                if combat_result.monster_died:
                    board.remove_monster(monster)
                    in_combat = False
                    current_monster = None
            
        # Condition de victoire
        if hero.has_won():
            view.display_board(hero, board)
            
            # Affichage de victoire (message simple, sans popup)
            view.show_victory(hero)
            
            # Highscores EN PREMIER (immédiatement visibles)
            if ENABLE_HIGHSCORE and HIGHSCORE_AVAILABLE and highscore_manager:
                is_new_record, old_record = highscore_manager.update_stats(
                    hero.score, hero.monsters_defeated, hero.move_count
                )
                
                if is_new_record:
                    view.show_new_record(old_record)
                else:
                    best_score = highscore_manager.get_best_score()
                    if best_score > 0:
                        view.show_current_best(best_score)
            
            # Popup d'adieu EN DERNIER (après lecture des highscores)
            view.show_farewell()
            running = False

if __name__ == "__main__":
    print("AVENTURIER - Choisissez votre interface")
    print("=" * 45)
    print("1. Mode Console (classique)")
    print("2. Mode GUI (interface graphique)")
    print("x. Quitter")
    print("=" * 45)
    
    while True:
        try:
            choice = input("Votre choix (1-2, x) : ").strip().lower()
            
            if choice == "1":
                print("\nLancement en mode Console...")
                main()
                break
                
            elif choice == "2":
                print("\nLancement en mode GUI...")
                try:
                    from tkinter_view import TkinterView
                    main(TkinterView)
                    break  # Ajouté pour éviter la relance du menu après fermeture GUI
                except ImportError:
                    print("Erreur: tkinter non disponible sur ce système")
                    print("Merci de choisir le mode console.") 
                
            elif choice == "x":
                print("\nAu revoir !")
                break
                
            else:
                print("Choix invalide. Veuillez entrer 1, 2 ou x.")
                
        except KeyboardInterrupt:
            print("\n\nAu revoir !")
            break
        except ImportError as e:
            print(f"Erreur d'import critique : {e}")
            print("Un module essentiel est manquant. Vérifiez votre installation.")
            break
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            print("Quelque chose s'est mal passé. Contactez le développeur.")
            break