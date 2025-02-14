#
# CLA-Screendata
#
# a convenient separate display info source
#
import pygame


pygame.init()


SCREENRES = pygame.display.Info()  # screen resolution required for some imgs to be properly set on canvas
X_CENTER = SCREENRES.current_w // 2  # just a separate coord of screen center value to not repeat the code
Y_CENTER = SCREENRES.current_h // 2  # same as X_CENTER
X_SFAC = SCREENRES.current_w // 125 / 8
Y_SFAC = SCREENRES.current_h // 125 / 8
REL_SCALE = Y_SFAC * 4  # relational scale for scenes
