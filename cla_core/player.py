#
# CLA-Player
#
# player-related classes and player (for the game scene) itself
#
# classes: PlayerClip (sprite), Raycast (sprite), Player
#
import pygame

import cla_core.screendata as sd
import cla_core.s_graphics as graph
import cla_core.audio as aud


PSCALE = 24  # player collision scale value
POFFSET_X = sd.X_CENTER - sd.Y_SFAC * PSCALE * 2
POFFSET_Y = sd.Y_CENTER - sd.Y_SFAC * PSCALE * 2


class PlayerClip(pygame.sprite.Sprite):
    PCG = pygame.sprite.Group()

    def __init__(self):
        super().__init__(PlayerClip.PCG)
        self.image = pygame.Surface((sd.REL_SCALE * PSCALE, sd.REL_SCALE * PSCALE), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('green'), (0, 0, sd.REL_SCALE * PSCALE, sd.REL_SCALE * PSCALE), 5)
        self.rect = pygame.Rect(POFFSET_X, POFFSET_Y, sd.REL_SCALE * PSCALE, sd.REL_SCALE * PSCALE)


class Raycast(pygame.sprite.Sprite):
    def __init__(self, deg, pos, a_range=1, spread=0, *group):
        super().__init__(*group)
        self.image = pygame.surface.Surface((2 * a_range * PSCALE, 2 * a_range * PSCALE), pygame.SRCALPHA, 32)
        pygame.draw.line(self.image, '#FF0000', (self.image.get_width() / 2, self.image.get_height() / 2),
                         (0, 0), 2)
        # self.image = pygame.transform.rotate(self.image, -(deg * 45 + randrange(-spread, spread)))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.mask = pygame.mask.from_surface(self.image)


class Player:
    orients = {(0, -1): 0, (1, -1): 1, (1, 0): 2, (1, 1): 3, (0, 1): 4, (-1, 1): 5, (-1, 0): 6, (-1, -1): 7}

    def __init__(self, startpos):
        self.char_spritemap = graph.CharSpritemap()
        # space positioning properties
        self.orient = (0, 0)
        self.deg = 0
        self.coords = startpos
        self.prev_coors = None
        self.vel = [0, 0]  # velocities / скорости (0=down,1=right)
        self.acc = 720  # acceleration, in pix/sec
        self.decc = 960  # deceleration, in pix/sec
        self.sl = 240  # speed limit, in pix/sec
        # collision
        self.clip = PlayerClip()
        # current data
        self.weap = 0
        self.status = 0
        self.did_died = False
        self.interact_request = False
        self.timedelta = pygame.time.Clock()
        self.d_td = 0  # means debug timedelta

    def proc_evt(self, keys):
        if self.status != 2:
            if keys:
                self.calc_orient(keys)
            self.move()
            if self.status != 0:
                if self.orient == (0, 0):
                    self.status = 0
            else:
                if self.orient != (0, 0):
                    self.status = 1

    def interaction_proc(self, event):
        if self.interact_request:
            self.interact_request = False
        if event.key == pygame.K_e:
            self.interact_request = True

    def weap_exchange(self, weap_new):
        weap_old = self.weap
        self.weap = weap_new
        aud.aud_play(aud.WEAP_PICKUP)
        return weap_old

    def attack_event(self, scene):
        if self.weap == 1:
            scene.pshots.add(list(map(lambda x: Raycast(self.deg, (sd.X_CENTER, sd.Y_CENTER), 64, 60), range(1))))
            aud.aud_play(aud.W1_SHOOT)

    def death_event(self):
        self.status = 2
        aud.aud_play(aud.DEATH_SND)

    def calc_orient(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.set_orient((-1, -1))
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.set_orient((1, -1))
            else:
                self.set_orient((0, -1))
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.set_orient((-1, 1))
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.set_orient((1, 1))
            else:
                self.set_orient((0, 1))
        else:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.set_orient((-1, 0))
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.set_orient((1, 0))
            else:
                self.set_orient((0, 0))

    def move(self):
        self.prev_coors = self.coords[:]
        td = self.timedelta.tick() / 1000
        self.d_td += td
        # coord debug
        if self.d_td > 5:
            self.d_td %= 5
            print(self.coords)
        # reducing diagonal speed
        self.coords[0] -= self.vel[0] * td * (1 if (self.orient[0] != 0 and self.orient[1] == 0
                                                    or self.orient[1] != 0 and self.orient[0] == 0) else 0.71)
        self.coords[1] -= self.vel[1] * td * (1 if (self.orient[0] != 0 and self.orient[1] == 0
                                                    or self.orient[1] != 0 and self.orient[0] == 0) else 0.71)
        if self.orient[0] != 0:
            if self.orient[0] == -1:
                if self.vel[0] + self.acc * td <= self.sl:
                    self.vel[0] += self.acc * td
                else:
                    self.vel[0] = self.sl
            else:
                if self.vel[0] - self.acc * td >= -self.sl:
                    self.vel[0] -= self.acc * td
                else:
                    self.vel[0] = -self.sl
        else:
            if self.vel[0] > 0:
                if self.vel[0] - self.decc * td >= 0:
                    self.vel[0] -= self.decc * td
                else:
                    self.vel[0] = 0
            else:
                if self.vel[0] + self.decc * td <= 0:
                    self.vel[0] += self.decc * td
                else:
                    self.vel[0] = 0
        if self.orient[1] != 0:
            if self.orient[1] == -1:
                if self.vel[1] + self.acc * td <= self.sl:
                    self.vel[1] += self.acc * td
                else:
                    self.vel[1] = self.sl
            else:
                if self.vel[1] - self.acc * td >= -self.sl:
                    self.vel[1] -= self.acc * td
                else:
                    self.vel[1] = -self.sl
        else:
            if self.vel[1] < 0:
                if self.vel[1] + self.decc * td <= 0:
                    self.vel[1] += self.decc * td
                else:
                    self.vel[1] = 0
            else:
                if self.vel[1] - self.decc * td >= 0:
                    self.vel[1] -= self.decc * td
                else:
                    self.vel[1] = 0
        if self.coords[0] < 0:
            self.coords[0] = 0
            self.vel[0] = 0
        if self.coords[1] < 0:
            self.coords[1] = 0
            self.vel[1] = 0
        # self.clip.update(self.coords)

    def set_orient(self, orient):
        if orient != (0, 0) or orient != self.orient:
            self.orient = orient
            try:
                self.deg = Player.orients[orient]
            except KeyError:
                pass

    def revert(self):
        if self.prev_coors:
            print('-----')
            print(self.prev_coors)
            print('-----')
            print(self.coords)
            print('-----')
            self.coords = self.prev_coors[:]

    def render(self, screen):
        self.char_spritemap.render(screen, self.status, self.deg, self.weap)
