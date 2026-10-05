import pygame

from superfarmer.species import Species


class Assets:
    def __init__(self):
        self.player_farm_background = pygame.image.load("assets/landscape2.jpg")

        self.animal_images_roll = {
            Species.RABBIT: pygame.image.load("assets/rabbit128.png"),
            Species.SHEEP: pygame.image.load("assets/sheep128.png"),
            Species.PIG: pygame.image.load("assets/pig128.png"),
            Species.COW: pygame.image.load("assets/cow128.png"),
            Species.HORSE: pygame.image.load("assets/horse128.png"),
            Species.FOX: pygame.image.load("assets/fox128.png"),
            Species.WOLF: pygame.image.load("assets/wolf128.png"),
        }

        self.animal_images_herd = {
            Species.RABBIT: pygame.image.load("assets/rabbit32.png"),
            Species.SHEEP: pygame.image.load("assets/sheep32.png"),
            Species.PIG: pygame.image.load("assets/pig32.png"),
            Species.COW: pygame.image.load("assets/cow32.png"),
            Species.HORSE: pygame.image.load("assets/horse32.png"),
            Species.SMALL_DOG: pygame.image.load("assets/smalldog32.png"),
            Species.BIG_DOG: pygame.image.load("assets/bigdog32.png"),
        }

        self.dice_icon = pygame.image.load("assets/dice.png")
        self.dice_sound = pygame.mixer.Sound("sounds/diceroll.mp3")

        self.pricelist_img = pygame.image.load("assets/pricelist.jpg")

        self.win_sound = pygame.mixer.Sound("sounds/fanfare.mp3")
