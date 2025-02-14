#
# CLA-StaticGraphics
#
# all the graphics that are minimally controlled by events or not controlled at all
#
# classes: RenderableImage -> ParallaxImage, PlayerOffsetImage; SnowflakeSprite (sprite);
# BaseFramedSprite (sprite) -> PlayerRotatableFramedSprite; PlayerRotatableSprite (sprite)
#
import pygame

import os
from random import randint, randrange, random

import cla_core.screendata as sd
import loaders as load
import cla_core.audio as aud
import cla_core.player as player


FADE_IMG = load.imgloader(r"ui\fade.png", -2)  # global used fade image
FADE_IMG = pygame.transform.scale(FADE_IMG, (sd.SCREENRES.current_w, sd.SCREENRES.current_h))
DARKEN_IMG = load.imgloader(r"ui\darken.png", -2)  # global used darken image
DARKEN_IMG = pygame.transform.scale(DARKEN_IMG, (sd.SCREENRES.current_w, sd.SCREENRES.current_h))


class RenderableImage:  # base image container made to be configurable
    # базовый контейнер изображения для рендера сделанный для удобной конфигурации
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=0.0, th=0.0, overlay=False, colorkey=None, do_render=True):
        self.name = name
        self.overlay = overlay
        self.img = load.imgloader(filepath, colorkey)
        if not (tw <= 0.0 or th <= 0.0):  # tw, th - transform width and transform height - multipliers
            print(f'Image: {self.name}, Width: {self.img.get_width() * tw}, Height: {self.img.get_height() * th}')
            self.img = pygame.transform.scale(self.img, (self.img.get_width() * tw, self.img.get_height() * th))
        self.scenepos = (x, y)  # local scene position for img
        self.do_render = do_render

    def __str__(self):
        return self.name

    def switch_vis(self):
        self.do_render = not self.do_render

    def hide(self):
        self.do_render = False

    def show(self):
        self.do_render = True

    def render(self, screen, *params):
        screen.blit(self.img, (self.scenepos[0], self.scenepos[1]))


class ParallaxImage(RenderableImage):  # container for image with all parallax (offset with the cursor) data about it
    # базовый контейнер рендер-изображения, дополненный данными для параллакса
    # справка::параллакс - эффект смещения, в данном контексте относительно курсора
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=0.0, th=0.0, pm=1.0, overlay=False, colorkey=None,
                 do_render=True):
        super().__init__(name, filepath, x, y, tw, th, overlay, colorkey, do_render)
        self.para_mul = pm  # parallax offset multiplier/множитель параллакс-смещения

    def render(self, screen, *params):
        screen.blit(self.img, (self.scenepos[0] - (self.para_mul * params[0]), self.scenepos[1]
                               - (self.para_mul * params[1])))


class PlayerOffsetImage(RenderableImage):  # container for image with support of relative to player offset
    # базовый контейнер рендер-изображения с поддержкой относительного к игроку смещения
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=sd.REL_SCALE, th=sd.REL_SCALE, overlay=False, colorkey=None,
                 do_render=True):
        super().__init__(name, filepath, x, y, tw, th, overlay, colorkey, do_render)

    def render(self, screen, *params):
        screen.blit(self.img, (self.scenepos[0] - params[0] * sd.REL_SCALE + player.POFFSET_X, self.scenepos[1]
                               - params[1] * sd.REL_SCALE + player.POFFSET_Y))


def sflake_init():
    sflake_0 = load.imgloader(r"mmenu\CLA_SDrop__0001s_0003_Snowdrop_0.png", -2)
    sflake_1 = load.imgloader(r"mmenu\CLA_SDrop__0001s_0002_Snowdrop_1.png", -2)
    sflake_2 = load.imgloader(r"mmenu\CLA_SDrop__0001s_0001_Snowdrop_2.png", -2)
    sflake_3 = load.imgloader(r"mmenu\CLA_Sdrop_3.png", -2)
    return sflake_0, sflake_1, sflake_2, sflake_3


class SnowflakeSprite(pygame.sprite.Sprite):  # main menu snowflake sprite / спрайт снежинки для главного меню
    sflake_list = sflake_init()  # a list of pngs for one of them being randomly selected

    # ^^^ список картинок снежинок, из которого одна будет выбрано случайно

    def __init__(self, *sgroup):
        super().__init__(*sgroup)
        simg = SnowflakeSprite.sflake_list[randint(0, 4) - 1]  # selection itself / выборка снежинки
        scale = (random() + 1) / 2
        simg = pygame.transform.scale(simg, (simg.get_width() * scale, simg.get_height() * scale))
        self.image = pygame.transform.rotate(simg, randrange(-181, 180))
        self.rect = self.image.get_rect()
        self.rect.x = randrange(sd.SCREENRES.current_w)
        self.rect.y = randrange(sd.SCREENRES.current_h)

    def update(self):
        if self.rect.y >= sd.SCREENRES.current_h:
            self.rect.y = -50
        if self.rect.x < 0:
            self.rect.x = sd.SCREENRES.current_w
        self.rect = self.rect.move((randrange(12) - 12, 5 + randrange(5)))


class BaseFramedSprite(pygame.sprite.Sprite):  # animated sprite
    def __init__(self, filename, f_x=1, f_y=1, x=0, y=0, frate=10, *sgroup):
        super().__init__(*sgroup)
        sequence = load.imgloader(filename)
        sequence = pygame.transform.scale(sequence, (sd.REL_SCALE * sequence.get_width(), sd.REL_SCALE
                                                     * sequence.get_height()))
        self.frame = 0
        self.framerate = (1 / frate) * 1000
        self.time = 0
        self.clock = pygame.time.Clock()
        self.rect = pygame.Rect(0, 0, sequence.get_width() // f_x, sequence.get_height() // f_y)
        self.rect.center = x, y
        self.imgset = [sequence.subsurface(pygame.Rect((self.rect.w * x, self.rect.h * y), self.rect.size)) for x
                       in range(f_x) for y in range(f_y)]
        self.framecount = len(self.imgset)
        self.image = self.imgset[self.frame]

    def update(self):
        self.time += self.clock.tick()
        if self.time >= self.framerate:
            self.frame = (self.frame + 1) % self.framecount
            self.image = self.imgset[self.frame]
            self.time = self.time % self.framerate


class PlayerRotatableSprite(pygame.sprite.Sprite):
    def __init__(self, filename, x=0, y=0, *sgroup):
        super().__init__(*sgroup)
        self.image_nonrotated = pygame.transform.scale(load.imgloader(filename), (sd.REL_SCALE * 64,
                                                                                  sd.REL_SCALE * 64))
        self.image_45drotated = pygame.transform.rotate(self.image_nonrotated, -45)
        self.image = self.image_nonrotated
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.cdg = 0

    def update(self, deg):
        if self.cdg != deg:
            self.rotate(deg)

    def rotate(self, deg):
        self.image = pygame.transform.rotate(self.image_45drotated if deg % 2 != 0 else self.image_nonrotated,
                                             (deg - 1) * -45 if deg % 2 != 0 else deg * -45)
        self.cdg = deg
        self.rect = self.image.get_rect(center=self.rect.center)


class PlayerRotatableFramedSprite(BaseFramedSprite):
    def __init__(self, filename, f_x=1, f_y=1, x=0, y=0, frate=10, *sgroup):
        super().__init__(filename, f_x, f_y, x, y, frate, *sgroup)
        self.imgset_nonrotated = self.imgset
        self.imgset_45drotated = list(map(lambda _: pygame.transform.rotate(_, -45), self.imgset_nonrotated))
        self.image = self.image = pygame.transform.scale(self.image, (sd.Y_SFAC * 256, sd.Y_SFAC * 256))
        self.cdg = 0
        self.pf = 0

    def update(self, *deg):
        super().update()
        if self.frame != self.pf:
            self.pf = self.frame
            aud.aud_play(aud.WALK[randint(0, 2)])
        if self.cdg != deg[0]:
            self.rotate(*deg)

    def rotate(self, deg):
        self.imgset = [pygame.transform.rotate(_, (deg - 1) * -45 if deg % 2 != 0 else deg * -45) for _ in
                       (self.imgset_45drotated if deg % 2 != 0 else self.imgset_nonrotated)]
        self.image = self.imgset[self.frame]
        self.cdg = deg
        self.rect = self.imgset[0].get_rect(center=self.rect.center)


class CharSpritemap:  # character sprites container logically sorted by player statuses
    m0g, m1g, m2g = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

    # m[0, 1, 2]g - static sprites groups: sprites that depend on player status only (not animated and not weapon:
    # head, dead character)

    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_0.png', sd.X_CENTER, sd.Y_CENTER, m0g)
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_run_0.png', sd.X_CENTER, sd.Y_CENTER, m1g)
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_dead_0.png', sd.X_CENTER, sd.Y_CENTER, m2g)

    ldir = os.listdir(r'gamedata\img\game\char\bkiss')  # reads all the character images

    m0wg, m1wg = [], []  # WeaponGroup lists: containers for spritegroups of each weapon type,
    # num is player status respectively
    for _ in list(filter(lambda x: 'sprite_0_w' in x, sorted(ldir))):
        locgr = pygame.sprite.Group()
        PlayerRotatableSprite(r'game\char\bkiss\ '[:-1] + _, sd.X_CENTER, sd.Y_CENTER, locgr)
        m0wg.append(locgr)
    for _ in list(filter(lambda x: 'sprite_run_0_w' in x, sorted(ldir))):
        locgr = pygame.sprite.Group()
        PlayerRotatableFramedSprite(r'game\char\bkiss\ '[:-1] + _, 2, 1, sd.X_CENTER, sd.Y_CENTER, 5, locgr)
        m1wg.append(locgr)

    def __init__(self):
        self.sgs = [CharSpritemap.m0g, CharSpritemap.m1g, CharSpritemap.m2g]
        self.wsgs = [CharSpritemap.m0wg, CharSpritemap.m1wg]

    def render(self, screen, status, deg, weap):
        # 'weapon' sprites rendering
        if status != 2:
            try:
                self.wsgs[status][weap].update(deg)
                self.wsgs[status][weap].draw(screen)
            except IndexError:
                self.wsgs[0][0].update(deg)
                self.wsgs[0][0].draw(screen)
        # 'static' sprites rendering
        try:
            self.sgs[status].update(deg)
            self.sgs[status].draw(screen)
        except IndexError:
            self.sgs[0].update(deg)
            self.sgs[0].draw(screen)
