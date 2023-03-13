import logging
import random
import sys
from enum import Enum
import json
import os


class DamageType(Enum):
    HERO = 'hero'
    FIRE = 'fire'
    WALL = 'hitting a wall'


class Hero:
    """
    A class representing a Hero
    """

    def __init__(self, name: str):
        """Initialize a new instance of the Hero class.
                Args:
                    self.coords (tuple): Coordinates of the hero in the labyrinth.
                    self._previous_coords(tuple): Previous Coordinates of the hero in the labyrinth.
                    self.name (str): Hero Name.
                    self.num_heals (int): Number of healing potions.
                    self.has_key (int): Whether the hero has a key..
                    self.health (int): Number of health.
        """
        self._coords: tuple[int, int] = (0, 3)
        self._previous_coords: tuple[int, int] = (0, 3)
        self.name: str = name
        self.health: int = 5
        self.num_heals: int = 3
        self.max_health: int = 5
        self.has_key: bool = False

    def get_name(self) -> str:
        """Return hero name"""
        return self.name

    def get_info(self) -> None:
        """Displays information about the hero"""
        logging.info(
            f"Name: {self.name}, Position: {self.coords}, Previous position: {self.previous_coords} "
            f"Health: {self.health},Healing Potions: {self.num_heals},"
            f"Has key : {'Yes' if self.has_key else 'No'}, ")

    def get_hero_information(self) -> dict:
        """Return information about the hero. Need for saving."""
        return {
            'name': self.name,
            'position': self._coords,
            'previous_coords': self.previous_coords,
            'health': self.health,
            'num_heals': self.num_heals,
            'has_key': self.has_key,
        }

    def set_hero_information(self, dict_hero_information: dict) -> None:
        """Take information about the hero. Need for loading."""
        self._coords = tuple(dict_hero_information.get('position'))
        self.previous_coords = tuple(dict_hero_information.get('previous_coords'))
        self.health = dict_hero_information.get('health')
        self.num_heals = dict_hero_information.get('num_heals')
        self.has_key = dict_hero_information.get('has_key')

    @property
    def previous_coords(self):
        return self._previous_coords

    @previous_coords.setter
    def previous_coords(self, value: tuple):
        self._previous_coords = value

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, value: tuple):
        self._coords = value

    def use_healing(self) -> bool:
        """The use heal. Returns a bool for the game to work correctly. Displays information about using potion."""
        if self.num_heals == 0:
            logging.info(f"Hero {self.name} don't have heal. Use another action")
            return False
        if self.health < self.max_health:
            self.num_heals -= 1
            self.health += 1
            logging.info(f"Hero {self.name} has used a healing potion. Their health is now {self.health}")
            return True
        else:
            logging.info(f"Hero {self.name} has reached maximum health. Healing isn't necessary. Use another command.")
            return False

    def is_alive(self) -> bool:
        """Checking if the hero is alive"""
        if self.health > 1:
            return True
        return False

    def heal_cell(self) -> None:
        """Activates when hero move to heal cell"""
        self.health = 5

    def is_dead(self) -> bool:
        """Checking if the hero is dead"""
        if self.health <= 0:
            return True
        return False

    def get_key(self) -> None:
        self.has_key = True

    def have_key(self) -> bool:
        return self.has_key

    def take_damage(self, damage_type: DamageType) -> None:
        """Show information about the hero taking attacks. Displays information about damage."""
        self.health -= 1
        if damage_type == DamageType.HERO:
            pass
        else:
            logging.info(f"{self.name} received damage from {damage_type.value}. Health left: {self.health}")

    def attack(self, enemy) -> None:
        """Show information about the hero attacks. Displays information about attack."""
        logging.info(f'Hero {self.name} attacked {enemy} with a sword')


class Maze:
    """The class in which the maze is implemented"""

    def __init__(self):
        """Initialize a new instance of the Maze class.
                Args:
                    self.fire_cells (list): List of coordinates where the fire burns.
                    self.key_location(tuple): Coordinates where the key is located.
                    self.name (key_exists): Whether there is a key in the labyrinth.
                    self.boss_location (int): Coordinates where boss is located.
                    self.safe_positions (int): Coordinates where fire can't burn.
                    self.maze (int): Map of the maze.
        """
        self.fire_cells: list = []
        self.key_location: tuple = (2, 1)
        self.key_exists: bool = True
        self.boss_location: tuple = (7, 0)
        self.safe_positions: list = [(2, 1), (6, 2), (4, 0)]
        self.maze: list = [
            [False, False, False, False, True, True, True, True],
            [False, False, True, False, False, True, False, False],
            [False, True, True, True, False, True, True, False],
            [True, True, False, True, True, True, False, False]
        ]
        self.movable_positions: list = [(x, y) for y in range(4) for x in range(8) if self.maze[y][x]]
        self.movable_positions.remove((2, 1))
        self.movable_positions.remove((6, 2))
        self.movable_positions.remove((4, 0))

    def get_dict_maze_information(self) -> dict:
        """Return information about the hero. Need for saving."""
        return {
            "key_location": self.key_location,
            "key_exists": self.key_exists
        }

    def set_dict_maze_information(self, dict_maze_information: dict) -> None:
        """Take information about the hero. Need for loading."""
        self.key_location = tuple(dict_maze_information.get('key_location'))
        self.key_exists = dict_maze_information.get('key_exists')

    def get_safe_positions(self) -> list:
        """Return list of coords where fire can't burn"""
        return self.safe_positions

    def check_key(self) -> tuple:
        """Check key on the map"""
        return self.key_location, self.key_exists

    def drop_key(self, position: tuple) -> None:
        """When the hero with the key dies, the key falls to the ground"""
        self.key_location = position
        self.key_exists = True

    def taking_key(self) -> None:
        """When hero take key"""
        self.key_exists = False

    def shuffle_fires(self) -> None:
        """Create fires in random 4 coords."""
        random.shuffle(self.movable_positions)
        self.fire_cells = self.movable_positions[:4]
        logging.info(f"Fires at positions: {self.fire_cells}")

    def get_position_status(self, position, direction: tuple) -> str:
        """Return event when hero moving."""
        x, y = position
        delta_x, delta_y = direction
        if not (0 <= x + delta_x < 8 and 0 <= y + delta_y < 4):
            return "fail"
        if (x + delta_x, y + delta_y) == self.boss_location:
            return 'boss'
        if self.maze[y + delta_y][x + delta_x]:
            if (x + delta_x, y + delta_y) in self.fire_cells:
                return 'burned'
            return "heal" if (x + delta_x, y + delta_y) in self.safe_positions[1:] else "success"
        else:
            return "fail"


class Game:
    """The class with a game"""

    def __init__(self):
        """Initialize a new instance of the Maze class.
                Args:
                    self.maze (Maze): Maze class instance.
                    self.heroes (list): List of heroes
        """
        self.maze = Maze()
        self.heroes = []

    def load_file(self):
        """loading file from json"""
        with open('heroes.json', 'r') as file:
            data = json.load(file)
            for i, hero in enumerate(data.get('heroes_dict')):
                self.add_hero(hero.get('name'))
                self.heroes[i].set_hero_information(hero)
                self.heroes[i].get_info()
        self.maze.set_dict_maze_information(data.get("maze_dict"))

    def save_file(self):
        """save file from json"""
        heroes_dict = []
        for hero in self.heroes:
            heroes_dict.append(hero.get_hero_information())

        with open('heroes.json', 'w') as f:
            data = {
                "heroes_dict": heroes_dict,

                "maze_dict": self.maze.get_dict_maze_information()
            }
            json.dump(data, f)
        logging.info("Save was successful")

    def starting_new_game(self):
        """New game"""
        logging.info('Choose the number of heroes: ')
        try:
            num_heroes = int(input())
            for num in range(num_heroes):
                logging.info(f'Write hero name.')
                self.add_hero(input())
            logging.info('All heroes were added.')
        except ValueError:
            logging.critical("Game was closed. Please write only number.")
            sys.exit()
        logging.info('Game was starting...')

    def game(self):
        """Realization of choosing game actions """
        while True:
            if not os.path.isfile('heroes.json'):
                self.starting_new_game()
                break
            else:
                logging.info(f"You have save file. Do you want continue?(y/n)")
            result = input()
            if result.strip().lower() == 'y':
                self.load_file()
                logging.info('Game was continue...')
                break
            if result.strip().lower() == 'n':
                os.remove('heroes.json')
                logging.info('Save was deleting')
                self.starting_new_game()
                break
            logging.info('Incorrect command. Please type y or n.')
        while True:
            if len(self.heroes) == 0:
                logging.info("All heroes died. Game over.")
                break
            self.maze.shuffle_fires()
            is_save = False
            for hero in self.heroes:
                if hero.is_dead():
                    logging.info(f"Hero {hero.get_name()} die.")
                    self.remove_hero(hero)
                    continue
                logging.info(
                    f"The hero {hero.get_name()} a makes his move. Please type 'help' to see the list of "
                    "available commands.")
                while True:
                    match input().strip().lower():
                        case "help":
                            logging.info('Write "move" to change position in game.\n'
                                         'Write "heal" to heal your hero by 1.\n'
                                         'Write "attack" to attack enemy in position.\n'
                                         'Write "take key" to take the key in position.\n'
                                         'Write "save" to save the game.\n'
                                         'Write "exit" to exit game.\n')
                        case "move":
                            self.move(hero)
                            break
                        case "heal":
                            if hero.use_healing():
                                break
                            logging.info(
                                f"The hero {hero.get_name()} makes his move again.")
                        case "attack":
                            if self.attack(hero):
                                break
                            logging.info(
                                f"The hero {hero.get_name()} makes his move again.")
                        case 'take key':
                            if self.maze.check_key() == (hero.coords, True):
                                hero.get_key()
                                self.maze.taking_key()
                                logging.info(f"Hero {hero.get_name()} take key")
                                break
                            else:
                                logging.info("Key isn't here or someone has already taken it.")
                        case 'save':
                            if is_save:
                                logging.info("The save will be made after the moves of all heroes. Please don't use "
                                             "this command.")
                            else:
                                is_save = True
                                logging.info("The save will be made after the moves of all heroes.")
                            logging.info(f"The hero {hero.get_name()} makes his move again.")
                        case 'exit':
                            logging.info('Game was closed.')
                            sys.exit()
                        case _:
                            logging.info(f"Unknown command. Please try again or type 'help' to see the list of "
                                         f"available commands.")
            if is_save:
                self.save_file()

    def attack(self, hero):
        """Attack another hero"""
        hero_here_list = []
        for h in self.heroes:
            if h != hero and h.coords == hero.coords:
                logging.info(f"Hero, {h.get_name()}, is here.")
                hero_here_list.append(h)
        if not hero_here_list:
            logging.info(f"Nobody is here to attack.")
            return False
        if len(hero_here_list) == 1:
            hero.attack(hero_here_list[0].get_name())
            hero_here_list[0].take_damage(DamageType.HERO)
            return True
        else:
            logging.info(f"Choose hero that you want to attack:")
            for i, h in enumerate(hero_here_list):
                logging.info(f"{i + 1}. {h.get_name()}", extra={"terminator": ""})
            while True:
                choice = input()
                if not choice.isdigit() or int(choice) not in range(1, len(hero_here_list) + 1):
                    logging.info("Invalid choice. Please enter the number of one of the listed heroes.")
                else:
                    target_hero = hero_here_list[int(choice) - 1]
                    target_hero.take_damage(DamageType.HERO)
                    hero.attack(target_hero.get_name())
                    return True

    def move(self, hero):
        """Move and event processing"""
        logging.info(f"Choose direction to move. Write 'help' to see a list of commands.")
        while True:
            match input().strip().lower():
                case "help":
                    logging.info('Write "right" to change position in game.\n'
                                 'Write "left" to heal your hero by 1.\n'
                                 'Write "up" to attack enemy in position.\n'
                                 'Write "down" to take the key in position.\n')
                case "right":
                    delta_x, delta_y = (1, 0)
                    break
                case "left":
                    delta_x, delta_y = (-1, 0)
                    break
                case "up":
                    delta_x, delta_y = (0, -1)
                    break
                case 'down':
                    delta_x, delta_y = (0, 1)
                    break
                case _:
                    logging.info(f"Unknown direction. Please try again or type 'help' to see the list of "
                                 f"available directions.")
        move_result = self.maze.get_position_status(hero.coords, (delta_x, delta_y))
        if move_result == "boss":
            if hero.have_key():
                logging.info(f"Hero {hero.get_name()} wins!")
                logging.info('End the game. Thanks for playing')
                sys.exit()
            else:
                logging.info(f"Hero {hero.get_name()} is killed by the golem. Game over.")
                self.remove_hero(hero)
        elif move_result == "fail":
            if not hero.is_alive():
                logging.info(f"Hero {hero.get_name()} die.")
                self.remove_hero(hero)
            else:
                hero.take_damage(DamageType.WALL)

        else:
            x, y = hero.coords
            hero.coords = x + delta_x, y + delta_y
            if hero.coords == hero.previous_coords:
                logging.info(f"The hero {hero.get_name()} got scared.")
                self.remove_hero(hero)
                return None
            if hero.coords not in self.maze.get_safe_positions() and (x, y) not in self.maze.get_safe_positions():
                hero.previous_coords = x, y
            logging.info(f"{hero.get_name()} moved to {hero.coords}.")
            if move_result == "heal":
                logging.info(f'Hero {hero.get_name()} heals.')
                hero.heal_cell()
            if self.maze.check_key() == (hero.coords, True):
                logging.info("A key is here.")
            for h in self.heroes:
                if h != hero and h.coords == hero.coords:
                    logging.info(f"Another hero, {h.get_name()}, is here.")
            if move_result == "burned":
                if not hero.is_alive():
                    logging.info(f"Hero {hero.get_name()} die.")
                    self.remove_hero(hero)
                hero.take_damage(DamageType.FIRE)

    def add_hero(self, name: str):
        """Add new hero in list of heroes"""
        for hero in self.heroes:
            if hero.get_name() == name.strip():
                logging.info(f"Hero {hero.get_name()} was added early.")
                break
        else:
            self.heroes.append(Hero(name))
            logging.info(f'Hero {name} was adding in game. Hero wait start the game.')

    def remove_hero(self, hero):
        """Remove hero from list of heroes"""
        if hero.have_key():
            self.maze.drop_key(hero.coords)
            logging.info(f"Key dropped at {hero.coords}")
        self.heroes.remove(hero)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    game = Game()
    game.game()
