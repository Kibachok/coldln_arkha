#
# CLA-Entities
#
# all the game's entities for the game levels, actually just a sprites controlled by the game logic
#
import pygame

import os
from random import random

import loaders as load
import cla_core.screendata as sd
import cla_core.locale as loc
import cla_core.player as player


class Entity(pygame.sprite.Sprite):  # base entity for scene, init it with gamescene ONLY
    def __init__(self, pcoord, x=0, y=0, w=0, h=0, *sg):
        super().__init__(*sg)
        self.x, self.y = x, y
        self.rect = pygame.Rect(x * sd.REL_SCALE + player.POFFSET_X - pcoord[0] * sd.REL_SCALE, y * sd.REL_SCALE
                                + player.POFFSET_Y - pcoord[1] * sd.REL_SCALE, sd.REL_SCALE * w, sd.REL_SCALE * h)

    def update(self, pcoord, scene, *args, **kwargs):  # basically an "entity mover" in this specific case
        self.rect.update(self.x * sd.REL_SCALE + player.POFFSET_X - pcoord[0] * sd.REL_SCALE, self.y * sd.REL_SCALE
                         + player.POFFSET_Y - pcoord[1] * sd.REL_SCALE, self.rect.width, self.rect.height)


class TriggerClip(Entity):
    def __init__(self, pcoord, x=0, y=0, w=0, h=0, func=None, once=False, *tcg):
        super().__init__(pcoord, x, y, w, h, *tcg)
        self.image = pygame.Surface((w * sd.REL_SCALE, h * sd.REL_SCALE), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, '#00ff00', (0, 0, self.rect.w, self.rect.h), 5)  # debug
        self.once = once
        self.func = func
        self.func_data = []

    def set_func(self, func):
        self.func = func

    def set_funcdata(self, *funcdata):
        self.func_data.extend(*funcdata)

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, player.PlayerClip.PCG):
            if self.func:
                if self.func_data:
                    self.func(*self.func_data)
                else:
                    self.func()
            if self.once:
                self.kill()


class DropItem(Entity):
    def __init__(self, pcoord, name, img, x=0, y=0, *icg):
        super().__init__(pcoord, x, y, 32, 32, *icg)
        rel32 = sd.REL_SCALE * 32
        self.name = name
        img = load.imgloader(img)
        self.image = pygame.transform.scale(img, (rel32, rel32))

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, player.PlayerClip.PCG):
            scene.get_uie('UI_TXT_IPCK').set_txt(f'''{loc.locgetter(loc.BASELOCALE, 'item_pckp', scene.holder.clocale)}
                                                 {self.name}''')
        else:
            scene.get_uie('UI_TXT_IPCK').set_txt('')


class DropWeap(Entity):
    def __init__(self, pcoord, x=0, y=0, wid=1, *icg):
        super().__init__(pcoord, x, y, 32, 32, *icg)
        rel32 = sd.REL_SCALE * 32
        self.wid = wid
        self.image = pygame.transform.scale(self.load_weap(), (rel32, rel32))

    def load_weap(self):
        if os.path.isfile(r'gamedata\img\game\items\w_' + str(self.wid) + '.png'):
            return load.imgloader(r'game\items\w_' + str(self.wid) + '.png')
        else:
            return load.imgloader(r'game\items\w_1.png')

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, player.PlayerClip.PCG):
            scene.get_uie('UI_TXT_IPCK').set_txt(
                f'''{loc.locgetter(loc.BASELOCALE, "item_pckp", scene.holder.clocale)}{loc.locgetter(
                    loc.WLOCALE, "w_" + str(self.wid), scene.holder.clocale)}{(
                        " " + "(" + loc.locgetter(loc.WLOCALE, "w_" + str(scene.player.weap), scene.holder.clocale) 
                        + loc.locgetter(loc.BASELOCALE, 
                                        'item_drop', scene.holder.clocale)) if scene.player.weap != 0 else ''}''')
            if scene.player.interact_request:
                self.replicate(scene.player.weap_exchange(self.wid), scene)
                self.kill()
        else:
            scene.get_uie('UI_TXT_IPCK').set_txt('')

    def replicate(self, new_weap, scene):
        if new_weap != 0:
            self.groups()[0].add(DropWeap(scene.player.coords, scene.player.coords[0] + (random() - 0.5) * 64,
                                          scene.player.coords[1] + (random() - 0.5) * 64, new_weap))


class CollisionEntity(Entity):
    def __init__(self, pcoord, x=0, y=0, w=0, h=0, *csg):
        super().__init__(pcoord, x, y, w, h, *csg)
        self.w, self.h = w, h
        self.image = pygame.Surface((w * sd.REL_SCALE, h * sd.REL_SCALE), pygame.SRCALPHA, 32)
        self.prev_pos = None
        pygame.draw.rect(self.image, '#00ff00', (0, 0, self.rect.w, self.rect.h), 5)  # debug

    def static_collide(self, pcoord, scene):
        scene.player.revert()
        super().groups()[0].update(scene.player.coords, scene, True)
        if (self.x + self.w / 2 - player.PSCALE < pcoord[0] < self.x + self.w and
                (not (pcoord[1] + player.PSCALE - 1 < self.y) and not (pcoord[1] > self.y + self.h - 1))):
            scene.player.vel[0] = 0
        elif self.x + self.w / 2 > pcoord[0] + player.PSCALE > self.x and (not (pcoord[1] + player.PSCALE - 1 < self.y)
                                                                           and not (pcoord[1] > self.y + self.h - 1)):
            scene.player.vel[0] = 0
        elif self.y + self.h / 2 - player.PSCALE < pcoord[1] < self.y + self.h:
            scene.player.vel[1] = 0
        elif self.y + self.h / 2 > pcoord[1] + player.PSCALE > self.y:
            scene.player.vel[1] = 0

    def dynamic_collide_player(self, pcoord, scene):
        if (self.x + self.w // 2 - player.PSCALE < pcoord[0] < self.x + self.w and
                (not (pcoord[1] + player.PSCALE - 1 < self.y) and not (pcoord[1] > self.y + self.h - 1))):
            self.direction = 0
            self.vel = scene.player.sl * self.drag
            if self.drag < 1:
                scene.player.vel[0] *= self.drag
        elif self.x + self.w // 2 > pcoord[0] + player.PSCALE > self.x and (not (pcoord[1] + player.PSCALE - 1 < self.y)
                                                                            and not (pcoord[1] > self.y + self.h - 1)):
            self.direction = 1
            self.vel = scene.player.sl * self.drag
            if self.drag < 1:
                scene.player.vel[0] *= self.drag
        elif self.y + self.h // 2 - player.PSCALE < pcoord[1] < self.y + self.h:
            self.direction = 2
            self.vel = scene.player.sl * self.drag
            if self.drag < 1:
                scene.player.vel[1] *= self.drag
        elif self.y + self.h // 2 > pcoord[1] + player.PSCALE > self.y:
            self.direction = 3
            self.vel = scene.player.sl * self.drag
            if self.drag < 1:
                scene.player.vel[1] *= self.drag

    def dynamic_collide_obj(self, scene):
        if self.prev_pos:
            self.x, self.y = self.prev_pos[:]
        super().groups()[0].update(scene.player.coords, scene, True)


class Prop(CollisionEntity):
    def __init__(self, pcoord, img, x=0, y=0, w=0, h=0, dynamic=False, drag=1, *mecg):
        super().__init__(pcoord, x, y, w, h, *mecg)
        rel32 = sd.REL_SCALE * 32
        img = load.imgloader(img)
        self.image = pygame.transform.scale(img, (rel32, rel32))
        self.dynamic = dynamic
        self.drag = drag
        self.vel = 0
        self.direction = 0
        self.decc = 960
        self.timedelta = pygame.time.Clock()

    def update(self, pcoord, scene, reloc_only=False, *args, **kwargs):
        if not reloc_only:
            self.prev_pos = self.x, self.y
            td = self.timedelta.tick() / 1000
            if self.direction == 0:
                self.x -= self.vel * td
            elif self.direction == 1:
                self.x += self.vel * td
            elif self.direction == 2:
                self.y -= self.vel * td
            elif self.direction == 3:
                self.y += self.vel * td
            if self.vel - self.decc * td >= 0:
                self.vel -= self.decc * td
            else:
                self.vel = 0
        super().update(pcoord, scene, *args, **kwargs)
        if not reloc_only:
            isplayerclip = pygame.sprite.spritecollideany(self, player.PlayerClip.PCG)
            issceneclip = pygame.sprite.spritecollideany(self, scene.sclips)
            pseudogroup = pygame.sprite.Group(self.groups()[0])
            pseudogroup.remove(self)
            isselfclip = pygame.sprite.spritecollideany(self, pseudogroup)
            if isplayerclip or issceneclip:
                if not self.dynamic:
                    super().static_collide(pcoord, scene)
                else:
                    if isselfclip:
                        super().dynamic_collide_obj(scene)
                        if pygame.sprite.spritecollideany(self, player.PlayerClip.PCG):
                            super().static_collide(pcoord, scene)
                    elif issceneclip:
                        super().dynamic_collide_obj(scene)
                        if pygame.sprite.spritecollideany(self, player.PlayerClip.PCG):
                            super().static_collide(pcoord, scene)
                    elif isplayerclip:
                        super().dynamic_collide_player(pcoord, scene)


class SceneCollision(CollisionEntity):
    def __init__(self, pcoord, x=0, y=0, w=0, h=0, *ccg):
        super().__init__(pcoord, x, y, w, h, *ccg)
        self.w = w
        self.h = h
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        pygame.draw.rect(self.image, '#5a5a5a', self.rect)

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, player.PlayerClip.PCG):
            super().static_collide(pcoord, scene)


class TestEnemy(Entity):
    def __init__(self, pcoord, x=0, y=0, *esg):
        super().__init__(pcoord, x, y, player.PSCALE, player.PSCALE, *esg)
        self.image = load.imgloader(r"game\char\bkiss\cla_bkiss_sprite_0.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * sd.REL_SCALE,
                                                         self.image.get_height() * sd.REL_SCALE))

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, scene.pshots) or pygame.sprite.spritecollideany(self, scene.enemshots):
            self.death()

    def death(self):
        self.image = load.imgloader(r"game\char\bkiss\cla_bkiss_sprite_dead_0.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * sd.REL_SCALE,
                                                         self.image.get_height() * sd.REL_SCALE))
