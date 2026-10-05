import pygame

from pygame_ui.theme import Theme
from superfarmer.game import Game
from superfarmer.player import Player
from superfarmer.species import Species


def test_players_start_with_empty_herd():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    theme = Theme()

    try:
        game = Game(players=(Player("A"), Player("B")))

        for player in game.players:
            for species in Species:
                assert player.herd.get_animal_count(species) == 0
    finally:
        pygame.quit()
