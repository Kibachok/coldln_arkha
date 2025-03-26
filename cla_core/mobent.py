#
# CLA-MobEnt
#
# General classes for all mobile entities
#
# classes: Melee, Firearm, Raycast (sprite), Hitzone (sprite)
#

from math import sin, cos, radians
from random import randint
import cla_core.audio as aud
import pygame
from cla_core.screendata import X_CENTER, Y_CENTER, Y_SFAC, REL_SCALE, SCREENRES
import loaders as load


WEAPS = load.weapreader()[0]
CHARSCALE = 24  # player collision scale value
POFFSET_X = X_CENTER - Y_SFAC * CHARSCALE * 2
POFFSET_Y = Y_CENTER - Y_SFAC * CHARSCALE * 2


class Melee:
    def __init__(self, wid, attrange, delay, asndname=None):
        self.range, self.delay = attrange, delay
        self.vmid, self.asnd = wid, asndname
        self.timer, self.ctime = pygame.time.Clock(), 0
        self.weapicon = load.imgloader(r'game\items\ '[:-1] + self.vmid + '.png')
        self.weapicon = pygame.transform.scale(self.weapicon, (REL_SCALE * 32, REL_SCALE * 32))

    def attack(self, deg, pos, ppos):
        pos = [pos[0] * REL_SCALE + POFFSET_X + CHARSCALE * REL_SCALE // 2 - ppos[0] * REL_SCALE,
               pos[1] * REL_SCALE + POFFSET_Y + CHARSCALE * REL_SCALE // 2 - ppos[1] * REL_SCALE]
        self.ctime += self.timer.tick()
        if self.ctime >= self.delay:
            self.ctime = 0
            aud.aud_play(self.asnd)
            return Hitzone(deg, pos, self.range)


class Firearm:
    def __init__(self, wid, ammo, attrange, spread, projs, delay, rdelay, ssndname=None, rsndname=None):
        self.ammo, self.range, self.spread, self.projs, self.delay, self.rdelay = (ammo, attrange, spread, projs,
                                                                                   delay * 1000, rdelay * 1000)
        self.curammo = ammo  # current AMMOunt
        self.vmid, self.ssnd, self.rsnd = wid, ssndname, rsndname  # ViewModel ID and sounds to play when shot and rload
        self.timer, self.ctime = pygame.time.Clock(), 0
        self.weapicon = load.imgloader(r'game\items\ '[:-1] + self.vmid + '.png')
        self.weapicon = pygame.transform.scale(self.weapicon, (REL_SCALE * 32, REL_SCALE * 32))

    def attack(self, deg, pos, ppos):
        pos = [pos[0] * REL_SCALE + POFFSET_X + CHARSCALE * REL_SCALE // 2 - ppos[0] * REL_SCALE,
               pos[1] * REL_SCALE + POFFSET_Y + CHARSCALE * REL_SCALE // 2 - ppos[1] * REL_SCALE]
        self.ctime += self.timer.tick()
        if self.curammo > 0 and self.ctime >= self.delay:
            self.ctime = 0
            self.curammo -= 1
            aud.aud_play(self.ssnd)
            return [Raycast(deg, pos, self.range, self.spread) for _ in range(self.projs)]

    def reload(self):
        if self.curammo < self.ammo:
            self.ctime = self.delay - self.rdelay
            aud.aud_play(self.rsnd)
            self.curammo = self.ammo


class Raycast(pygame.sprite.Sprite):
    def __init__(self, deg, pos, a_range=1, spread=0, *group):
        super().__init__(*group)
        deg = ((deg * 45 + randint(-spread, spread)) + 360) % 360
        print(deg)
        print(sin(radians(deg)))
        print(cos(radians(deg)))
        surf_x = int(sin(radians(deg)) * a_range * REL_SCALE)
        surf_y = -int(cos(radians(deg)) * a_range * REL_SCALE)
        print(surf_x, surf_y)
        self.image = pygame.surface.Surface((abs(surf_x) if surf_x != 0 else 2, abs(surf_y) if surf_y != 0 else 2),
                                            pygame.SRCALPHA)
        pygame.draw.line(self.image, '#FF0000', (0 if surf_x >= 0 else abs(surf_x), 0 if surf_y >= 0 else abs(surf_y)),
                         (surf_x if surf_x >= 0 else 0, surf_y if surf_y >= 0 else 0), 2)
        self.rect = self.image.get_rect()
        self.rect.center = pos[0] + surf_x // 2, pos[1] + surf_y // 2
        self.mask = pygame.mask.from_surface(self.image)


class Hitzone(pygame.sprite.Sprite):
    def __init__(self, deg, pos, a_range=1, *group):
        super().__init__(*group)
        deg *= 45
        offset_x = sin(radians(deg)) * REL_SCALE * a_range // 2
        offset_y = cos(radians(deg)) * REL_SCALE * a_range // 2
        print(offset_x, offset_y, deg)
        attrange = REL_SCALE * a_range
        self.image = pygame.surface.Surface((attrange, attrange), pygame.SRCALPHA)  # debug purpose only
        pygame.draw.rect(self.image, '#FF0000', (0, 0, attrange, attrange), 5)
        self.rect = self.image.get_rect()
        self.rect.center = pos[0] + offset_x, pos[1] - offset_y
