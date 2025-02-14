#
# CLA-PGInit
#
# pygame initer, so graphics-related things can be drawn while the game being initialised
#
import pygame

import cla_core.screendata as sd


pygame.init()
screen = pygame.display.set_mode((sd.SCREENRES.current_w, sd.SCREENRES.current_h))
