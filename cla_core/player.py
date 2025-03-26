#
# CLA-Player
#
# player-related classes and player (for the game scene) itself
#
# classes: PlayerClip (sprite), Player
#
import pygame

import cla_core.screendata as sd
import cla_core.s_graphics as graph
import cla_core.audio as aud
import cla_core.mobent as mobent
import loaders as load


class PlayerClip(pygame.sprite.Sprite):
    PCG = pygame.sprite.Group()

    def __init__(self):
        super().__init__(PlayerClip.PCG)
        self.image = pygame.Surface((sd.REL_SCALE * mobent.CHARSCALE, sd.REL_SCALE * mobent.CHARSCALE),
                                    pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('green'), (0, 0, sd.REL_SCALE * mobent.CHARSCALE, sd.REL_SCALE
                                                             * mobent.CHARSCALE), 5)
        self.rect = pygame.Rect(mobent.POFFSET_X, mobent.POFFSET_Y, sd.REL_SCALE * mobent.CHARSCALE, sd.REL_SCALE * mobent.CHARSCALE)


class Player:
    orients = {(0, -1): 0, (1, -1): 1, (1, 0): 2, (1, 1): 3, (0, 1): 4, (-1, 1): 5, (-1, 0): 6, (-1, -1): 7}

    def __init__(self, startpos):
        self.char_spritemap = graph.CharSpritemap('bkiss')
        # space positioning properties
        self.orient = (0, 0)
        self.deg = 0
        self.coords = startpos
        self.prev_coors = None
        self.vel = [0, 0]  # velocities / скорости (0=down,1=right)
        self.acc = 960  # acceleration, in pix/sec
        self.decc = 1440  # deceleration, in pix/sec
        self.sl = 240  # speed limit, in pix/sec
        # collision
        self.clip = PlayerClip()
        # current data
        self.weap = None
        self.weap_request('empty')
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
        if event.key == pygame.K_r:
            self.reload_event()

    #
    # weap interactions
    #

    def weap_exchange(self, weap_new):
        weap_old = self.weap
        self.weap_request(weap_new)
        self.char_spritemap.weap_get(weap_new)
        aud.aud_play(aud.WEAP_PICKUP)
        return weap_old.vmid

    def weap_request(self, wid):
        try:
            weap_local = dict(mobent.WEAPS[wid])
            wtype = weap_local.pop('type').lower()
            if wtype == 'melee':
                self.weap = mobent.Melee(wid, **weap_local)
            elif wtype == 'firearm':
                self.weap = mobent.Firearm(wid, **weap_local)
            else:
                self.weap = mobent.Melee('empty', attrange=28, delay=0.25)
        except KeyError:
            self.weap = mobent.Melee('empty', attrange=28, delay=0.25)

    def attack_event(self, scene):
        if self.weap:
            projectiles = self.weap.attack(self.deg, self.coords, self.coords)
            if projectiles:
                scene.pshots.add(projectiles)

    def reload_event(self):
        if isinstance(self.weap, mobent.Firearm):
            self.weap.reload()

    #
    # death event
    #

    def death_event(self):
        self.status = 2
        aud.aud_play(aud.DEATH_SND)

    #
    # movement
    #

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

    #
    # render
    #

    def render(self, screen):
        self.char_spritemap.render(screen, self.status, self.deg)
        screen.blit(self.weap.weapicon, (sd.SCREENRES.current_w - 50 - sd.REL_SCALE * 32, sd.SCREENRES.current_h - 50
                                         - sd.REL_SCALE * 32))
