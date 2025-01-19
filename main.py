# DEMO WIP Build of game with main menu and some simple classes only
import os

import pygame
from random import randint, randrange, random


def imgloader(localpathname, colorkey=None):
    fullpathname = os.path.join('gamedata', localpathname)
    if not os.path.isfile(fullpathname):
        print(f'Path -- {fullpathname} image not found')
        return pygame.image.load(r'doomkisser_V2_s.png')
    img = pygame.image.load(fullpathname)
    if colorkey is not None and not -2:
        img = img.convert()
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)
    else:
        img = img.convert_alpha()
    return img


# UPPERCASE = global used variable
# global used/required commands
pygame.init()
pygame.mixer.init()
FONT_0 = pygame.font.Font(None, 35)
FONT_0.set_bold(True)
mtimer = pygame.time  # costill
pygame.mixer.music.load(r"gamedata\aud\mus\dymyat_molcha.mp3")  # MOVE IT TO SOME SCENE METHOD
pygame.mixer.music.play()  # test (look 30)
pygame.mixer.music.set_volume(1.0)  # test (look 30)
UI_CLICK = pygame.mixer.Sound(r"gamedata\aud\ui\button_click.wav")  # peaceding from tarkov
SCREENRES = pygame.display.Info()  # screen resolution required for some imgs to be properly set on canvas
screen = pygame.display.set_mode((SCREENRES.current_w, SCREENRES.current_h))
pygame.display.set_caption("ColdLine Arkhangelsk")
pygame.display.set_icon(pygame.image.load(r"doomkisser_V2_s.png"))
FADE_IMG = imgloader(r"img\ui\fade.png", -2)  # global used fade image
FADE_IMG = pygame.transform.scale(FADE_IMG, (SCREENRES.current_w, SCREENRES.current_h))


# global used commands - end
# -------------------------------------------------------
# \/ \/ \/ GRAPHIC ELS CLASSES START (НАЧАЛО ЗОНЫ КЛАССОВ ГРАФИКИ)


class RenderableImage:  # base image container made to be configurable
    # базовый контейнер изображения для рендера сделанный для удобной конфигурации
    def __init__(self, filepath, x, y, tw=0, th=0, colorkey=None, do_render=True):
        self.img = imgloader(filepath, colorkey)
        if not (tw <= 0 or th <= 0):
            self.img = pygame.transform.scale(self.img, (tw, th))
        self.scenepos = (x, y)  # local scene position for img
        self.do_render = do_render

    def switch_vis(self):
        self.do_render = not self.do_render

    def hide(self):
        self.do_render = False

    def show(self):
        self.do_render = True


class ParallaxImage(RenderableImage):  # container for image with all parallax (offset with the cursor) data about it
    # базовый контейнер рендер-изображения, дополненный данными для параллакса
    # справка::параллакс - эффект смещения, в данном контексте относительно курсора
    def __init__(self, filepath, x, y, tw=0, th=0, pm=1.0, colorkey=None, do_render=True):
        super().__init__(filepath, x, y, tw, th, colorkey, do_render)
        self.para_mul = pm  # parallax offset multiplier/множитель параллакс-смещения


class SnowflakeSprite(pygame.sprite.Sprite):  # main menu snowflake sprite / спрайт снежинки для главного меню
    sflake_0 = imgloader(r"img\mmenu\CLA_SDrop__0001s_0003_Snowdrop_0.png", -2)
    sflake_1 = imgloader(r"img\mmenu\CLA_SDrop__0001s_0002_Snowdrop_1.png", -2)
    sflake_2 = imgloader(r"img\mmenu\CLA_SDrop__0001s_0001_Snowdrop_2.png", -2)
    sflake_3 = imgloader(r"img\mmenu\CLA_Sdrop_3.png", -2)
    sflake_list = [sflake_0, sflake_1, sflake_2, sflake_3]  # a list of pngs for one of them being randomly selected
    # ^^^ список картинок снежинок, из которого одна будет выбрано случайно

    def __init__(self, *sgroup):
        super().__init__(*sgroup)
        simg = SnowflakeSprite.sflake_list[randint(0, 4) - 1]  # selection itself / выборка снежинки
        scale = (random() + 1) / 2
        simg = pygame.transform.scale(simg, (simg.get_width() * scale, simg.get_height() * scale))
        self.image = pygame.transform.rotate(simg, randrange(-181, 180))
        self.rect = self.image.get_rect()
        self.rect.x = randrange(SCREENRES.current_w)
        self.rect.y = randrange(SCREENRES.current_h)

    def update(self):
        if self.rect.y >= SCREENRES.current_h:
            self.rect.y = -50
        if self.rect.x < 0:
            self.rect.x = SCREENRES.current_w
        self.rect = self.rect.move((randrange(12) - 12, 5 + randrange(5)))


# ^^^ GRAPHIC ELS CLASSES END (КОНЕЦ ЗОНЫ КЛАССОВ ГРАФИКИ)
# ----------------------------------------------------------
# \/ \/ \/ UI CLASSES START (НАЧАЛО ЗОНЫ КЛАССОВ ИНТЕРФЕЙСА)


class UIElem:  # UI Element base class/базовый класс элемента интерфейса
    def __init__(self, x=0, y=0, w=0, h=0, txt='', font=None):
        global FONT_0
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.font = font
        self.txt = txt
        self.do_render = True

    def hide(self):
        self.do_render = False

    def show(self):
        self.do_render = True

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def text_render(self, col_txt='#202020'):
        try:
            return self.font.render(self.txt, False, col_txt)
        except TypeError:
            return FONT_0.render(self.txt, False, col_txt)
        except AttributeError:
            return FONT_0.render(self.txt, False, col_txt)


class UICanvas(UIElem):
    def __init__(self, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(x, y, w, h, txt, font)

    def render(self, screen, para=(0, 0), col_para='#AAAACF', col_0='#DFDFE8', col_koyma='#D0D0D8'):
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, col_para,
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        pygame.draw.rect(screen, col_0, (self.x, self.y, self.w, self.h), 0)
        pygame.draw.rect(screen, col_koyma, (self.x, self.y, self.w, self.h), 5)


class UIText(UIElem):
    def __init__(self, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(x, y, w, h, txt, font)

    def render(self, screen, para, col_txt='#202020'):
        text = self.text_render(col_txt)
        screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))


class UIInterElem(UIElem):  # interactive UI element (buttons, prompts ETC)
    def __init__(self, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(x, y, w, h, txt, font)
        self.active = True
        self.force_active = True  # do restore state after show() | восстанавливать ли состояние после show()
        self.status = 0  # 0 = idle (ожидание), 1 = pointed (наведённый курс.), 2 = active (активный (наж/редакт-ется))

    def hide(self):
        super().hide()
        self.active = False

    def show(self):
        super().show()
        if self.force_active:
            self.active = True

    def set_active(self, status, force=False):
        self.active = status
        if force:
            self.force_active = status

    def triggered(self):
        pass

    def proc_evt(self, event, click=False):
        pass


class PushBtn(UIInterElem):
    def __init__(self, x, y, w=200, h=50, txt='', font=None):
        super().__init__(x, y, w, h, txt, font)
        self.func = None

    def set_func(self, func):
        self.func = func

    def triggered(self):
        UI_CLICK.play()
        if self.func:
            self.func()

    def proc_evt(self, event, click=False):
        if self.active:
            if self.x <= event.pos[0] <= self.x + self.w and self.y <= event.pos[1] <= self.y + self.h and self.active:
                self.status = 1 if not click else 2
                if self.status == 2:
                    self.triggered()
            else:
                self.status = 0

    def render(self, screen, para=(0, 0), col_txt='#202020', col_para='#AAAACF', col_0='#DFDFE8', col_koyma='#D0D0D8',
               col_sel='#BBBBCC'):
        text = super().text_render(col_txt)
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, col_para,
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        if self.status == 0:
            pygame.draw.rect(screen, col_0, (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, col_koyma, (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))
        elif self.status == 1:
            pygame.draw.rect(screen, col_sel, (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, col_koyma, (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))
        else:
            pygame.draw.rect(screen, col_sel, (self.x + (offset / 2), self.y + (offset / 2), self.w, self.h), 0)
            pygame.draw.rect(screen, col_koyma, (self.x + (offset / 2), self.y + (offset / 2), self.w, self.h), 5)
            screen.blit(text, (self.x + (offset / 2), self.y + (offset / 2)))


class TextPrompt(UIInterElem):
    def __init__(self, x=0, y=0, w=0, h=0, font=None):
        super().__init__(x, y, w, h, font=font)

    def catching(self, event, breakevt=False):
        if event.type == pygame.KEYDOWN and not breakevt:
            print(event)
            if event.key == pygame.K_BACKSPACE:
                self.txt = self.txt[:-1]
            else:
                self.txt += f'{event.unicode}'
        elif breakevt:
            self.status = 0

    def proc_evt(self, event, click=False, scene_mode=0, scene=None):
        if self.active:
            if (self.x <= event.pos[0] <= self.x + self.w and self.y <= event.pos[1] <= self.y + self.h and self.active
                    and self.status != 2):
                if click:
                    self.status = 2
                    scene.scene_mode = 1
                    scene.catcher = self
                    print(scene)
                else:
                    self.status = 1
            else:
                self.status = 0

    def render(self, screen, para=(0, 0), col_txt='#202020', col_para='#AAAACF', col_0='#EFEFEF', col_koyma='#D0D0D8',
               col_sel='#BBBBCC'):
        text = super().text_render(col_txt)
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, col_para,
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        if self.status == 0:
            pygame.draw.rect(screen, col_0, (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, col_koyma, (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + 10, self.y + self.h / 2 - text.get_height() / 2))
        elif self.status == 1:
            pygame.draw.rect(screen, col_sel, (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, col_koyma, (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + 10, self.y + self.h / 2 - text.get_height() / 2))
        else:
            pygame.draw.rect(screen, col_sel, (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, col_koyma, (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + 15, self.y + self.h / 2 - text.get_height() / 2))


class UIGroup:
    def __init__(self):
        self.elems = []
        self.do_render = True
        self.active = True

    def add_elem(self, *elem):
        self.elems.extend(elem)

    def hide(self):
        self.do_render = False
        self.active = False
        for _ in self.elems:
            _.hide()

    def show(self):
        self.do_render = True
        self.active = True
        for _ in self.elems:
            _.show()

    def set_active(self, status):
        for _ in self.elems:
            if issubclass(type(_), UIInterElem):
                _.set_active(status, False)

    def proc_evt(self, event, click=False, scene_mode=0, scene=None):
        if self.active:
            for _ in self.elems:
                if issubclass(type(_), UIInterElem):
                    if isinstance(_, TextPrompt):
                        _.proc_evt(event, click, scene_mode, scene)
                    else:
                        _.proc_evt(event, click)

    def render(self, screen, para=(0, 0)):
        if self.do_render:
            for _ in self.elems:
                _.render(screen, para)


#  ^^^ UI CLASSES END (КОНЕЦ ЗОНЫ КЛАССОВ ИНТЕРФЕЙСА)
#  --------------------------------------------------------
#  \/ \/ \/ SCENE CLASSES START (НАЧАЛО ЗОНЫ КЛАССОВ СЦЕНЫ)


class BaseScene:  # scene class base: just a holder for scene content
    # базовый класс сцены - контейнера для содержимого на экране (хотя иногда и за его пределами) в данный м.вр.
    def __init__(self):
        self.para_l = (0, 0)  # parallax local offset
        self.imghld = []  # img - картинка
        self.uihld = []  # btn - кнопка
        self.sgroup = pygame.sprite.Group()  # s - спрайт
        self.entgroup = pygame.sprite.Group()  # ent - сущность (будь то NPC (враг) или окошко-тумбочка-кровать)
        self.scene_mode = 0
        self.catcher = None

    def __str__(self):
        return (f'{self.para_l}\n{self.imghld}\n{self.uihld}\n{self.sgroup}'
                f'\n{self.entgroup}\nscene_mode={self.scene_mode}\ncatcher={self.catcher}')

    def add_img(self, *imgs):  # add as many imgs as you want (1-"8 rotated by 90 degrees lol")
        self.imghld.extend(*imgs)

    def add_uie(self, *uies):  # add as many uielems as you want
        self.uihld.extend(uies)

    def add_s(self, *sprs):  # technically "s = ent" but i will probably make different group class for ent later
        for _ in sprs:
            _(self.sgroup)

    def add_ent(self, *ents):
        for _ in ents:
            _(self.entgroup)

    def ui_validator(self, event, click=False):
        for _ in self.uihld:
            if issubclass(type(_), UIInterElem) or isinstance(_, UIGroup):
                if isinstance(_, TextPrompt) or isinstance(_, UIGroup):
                    _.proc_evt(event, click, self.scene_mode, self)
                else:
                    _.proc_evt(event, click)

    def render(self, screen):
        for _ in self.imghld:
            if _.do_render:
                if type(_) == ParallaxImage:
                    screen.blit(_.img, (_.scenepos[0] - (self.para_l[0] * _.para_mul), _.scenepos[1]
                                        - (self.para_l[1] * _.para_mul)))
                else:
                    screen.blit(_.img, (_.scenepos[0], _.scenepos[1]))
        self.sgroup.draw(screen)
        self.sgroup.update()
        for _ in self.uihld:
            if _.do_render:
                _.render(screen, (self.para_l[0], self.para_l[1]))

    def get_para(self, x, y):
        self.para_l = (x, y)

    def sprite_event(self, event):
        self.sgroup.update()

    def proc_evt(self, event):
        if self.scene_mode == 0:
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:  # costill a little bit
                self.ui_validator(event)
                self.get_para(event.pos[0] / 50, event.pos[1] / 50)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui_validator(event, True)
        elif self.scene_mode == 1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == 13:
                    self.scene_mode = 0
                    self.catcher.catching(event, True)
                else:
                    self.catcher.catching(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.scene_mode = 0
                self.catcher.catching(event, True)
            elif event.type == pygame.MOUSEMOTION:
                self.get_para(event.pos[0] / 50, event.pos[1] / 50)


class GameScene(BaseScene):
    pass  # gonna make it later


class SceneHolder:
    def __init__(self, scene):
        self.scene = scene
        self.fade_timer = 0
        self.no_event = False

    def render(self, screen):
        if not self.no_event:
            screen.fill('#000000')
        else:
            self.render_fade(screen)
        self.scene.render(screen)

    def render_fade(self, screen):
        if self.fade_timer <= 255:
            screen.blit(FADE_IMG, (0, 0))
            self.fade_timer += 1
        else:
            self.no_event = False

    def funccall(self, name, *args):
        getattr(self.scene, name)(*args)

    def event_parser(self, event):
        self.scene.proc_evt(event)

    def switch_scene(self, scene_new):
        self.scene = scene_new
        self.fade_timer = 0
        self.no_event = True


# ^^^ SCENE CLASSES END (КОНЕЦ ЗОНЫ КЛАССОВ СЦЕНЫ)
# ------------------------------------------------------------
# \/ \/ \/ MAIN GAME LOOP AREA START (НАЧАЛО ЗОНЫ РАБОТЫ ИГРЫ)


def cla_mainmenu_draw(screen, xoffset=0, yoffset=0):  # REMOVE LATER
    doomerochek = pygame.image.load(r'doomkisser_V2_s.png').convert()
    doomerochek = pygame.transform.scale(doomerochek, (510, 510))
    # for _ in imgs:
    # screen.blit(_[0], (_[1][0] - (xoffset * _[2]), _[1][1] - (yoffset * _[2])))
    screen.blit(doomerochek, (0, 0))
    font = pygame.font.Font(None, 35)
    text = font.render("Cold Line :: Arkhangelsk (Dev-alpha)", False, '#CACAEF')
    screen.blit(text, (500 - text.get_width() - (500 - text.get_width()) / 2 - xoffset * 2, 50 - yoffset * 3))
    font = pygame.font.Font(None, 20)
    text = font.render("imagine good working main menu here", False, '#DDDDDD')
    screen.blit(text, (500 - text.get_width() - (500 - text.get_width()) / 2, 75))


def mmenu_imgs_init():
    clachr_size = int(SCREENRES.current_h * 0.9)
    mmenuimg_0 = ParallaxImage(r'img\mmenu\CLA_MM_BG_0.png', 0, 0,
                               SCREENRES.current_w + 40, int(SCREENRES.current_w / 2 * 1.25) + 50)
    mmenuimg_1 = ParallaxImage(r'img\mmenu\CLA_MM_BG_1.png', 0, 0,
                               SCREENRES.current_w + 40, int(SCREENRES.current_w / 2 * 1.25) + 50, do_render=False)
    clachr = ParallaxImage(r'img\mmenu\CLA_Chr__0003s_0004_HD_Obvod.png', SCREENRES.current_w / 2 - clachr_size / 2,
                           SCREENRES.current_h - clachr_size + 50, clachr_size, clachr_size, 1.5, -2)
    clachr_g = ParallaxImage(r'img\mmenu\CLA_Chr__0003s_0001_HD_GS_Zakras.png', SCREENRES.current_w / 2
                             - clachr_size / 2, SCREENRES.current_h - clachr_size + 50, clachr_size, clachr_size,
                             1.5, -2, False)
    clachr_bld = ParallaxImage(r'img\mmenu\CLA_Chr__0003s_0002_BLD.png', SCREENRES.current_w / 2 - clachr_size / 2,
                               SCREENRES.current_h - clachr_size + 50, clachr_size, clachr_size, 1.5, -2)
    clachr_col = ParallaxImage(r'img\mmenu\CLA_Chr__0003s_0003_HD_ColOL.png', SCREENRES.current_w / 2 - clachr_size
                               / 2, SCREENRES.current_h - clachr_size + 50, clachr_size, clachr_size, 1.5, -2)
    clachr_gno = ParallaxImage(r'img\mmenu\CLA_Chr__0003s_0000_gno.png',
                               SCREENRES.current_w / 2 - 512 - 256 - 128, SCREENRES.current_h - 512 - 256, 1024, 1024,
                               4, -2)
    ttle = ParallaxImage(r'img\mmenu\CLA_Txt_0.png', SCREENRES.current_w / 2 - 1024, 0, 2048, 512, 2.5, -2)
    return mmenuimg_0, mmenuimg_1, clachr, clachr_col, clachr_bld, ttle, clachr_gno, clachr_g


def mmenu_obj_init():
    mmenu = BaseScene()  # wip (subject to be properly organized probably)
    mmenu.add_img(mmenu_imgs_init())  # wip (subject to be properly organized probably)
    # pygame.mixer.music.fadeout(10000)
    killgamebtn = PushBtn(x=SCREENRES.current_w // 2 - 100, y=SCREENRES.current_h // 2 + 256, txt="kill program")
    killgamebtn.set_func(game_destroyer)
    mmenu.add_uie(killgamebtn)
    testbtn = PushBtn(w=450, x=SCREENRES.current_w // 2 - 225,
                      y=SCREENRES.current_h // 2 + 128, txt="Show a cute boykisser doomer UwU")  # AS WELL AS 161
    testbtn.set_func(doomkisser_enabler)  # SAME AS 162
    savebtn = PushBtn(w=450, x=SCREENRES.current_w // 2 - 225,
                      y=SCREENRES.current_h // 2 + 28, txt="Open save menu (load game)")
    savebtn.set_func(mmenu_group_switch)  # SAME AS 162
    mmenu.add_uie(testbtn, savebtn)
    mmenu.add_uie(mmenu_loadgame_group_init())
    for _ in range(10):
        mmenu.add_s(SnowflakeSprite)
    nmenu = BaseScene()  # multiscene game test remove it later!!!!!!!
    nmenu.add_uie(testbtn)
    return mmenu, nmenu


def mmenu_loadgame_group_init():
    canvas = UICanvas(h=700, w=800, x=SCREENRES.current_w // 2 - 400, y=SCREENRES.current_h // 2 - 350)
    testprompt = UIText(h=1, w=100, x=500, y=500, txt='testprompt')
    prpt_0 = TextPrompt(h=50, w=100, x=SCREENRES.current_w // 2 - 390, y=SCREENRES.current_h // 2 - 340)
    testgrp = UIGroup()
    testgrp.add_elem(canvas, testprompt, prpt_0)
    testgrp.hide()
    return testgrp


def music_controller():
    pygame.mixer.music.stop()
    pygame.mixer.music.play(start=1.8)
    return 1800


def game_destroyer():  # MAYBE FOR BUTTONS TEST
    global game_isactive
    game_isactive = False


def doomkisser_enabler():  # FOR BUTTONS TEST
    global do_render_pasxalko
    do_render_pasxalko = not do_render_pasxalko
    pygame.mixer.music.fadeout(5000)
    sceneslot.switch_scene(nmenu)


def mmenu_group_switch():
    if mmenu.uihld[3].do_render:
        mmenu.uihld[3].hide()
    else:
        mmenu.uihld[3].show()


if __name__ == '__main__':
    game_isactive = True
    do_render_pasxalko = False  # VERY TEST
    mmenu, nmenu = mmenu_obj_init()
    sceneslot = SceneHolder(mmenu)
    dtime = 0  # costill
    while game_isactive:
        if (mtimer.get_ticks() + dtime) % 170000 >= 169995:  # nowayroyatnee costill (subject to be removed)
            dtime += music_controller()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_isactive = False
            else:
                sceneslot.event_parser(event)
        sceneslot.render(screen)
        if do_render_pasxalko:
            cla_mainmenu_draw(screen, xoffset=0, yoffset=0)
        pygame.display.flip()
