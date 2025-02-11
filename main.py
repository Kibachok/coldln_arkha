# DEMO WIP Build of game with main menu and some simple classes only
import os

import pygame
import csv
import sqlite3
import json
from random import randint, randrange, random


def csvloader(namepath):
    fullpathname = os.path.join(r'gamedata', namepath)
    if not os.path.isfile(fullpathname):
        print(f'Path -- {fullpathname} CSV not found')
        return None
    with open(fullpathname, mode='r', encoding='utf-8', newline='') as read:
        csvd = csv.DictReader(read, delimiter=';', quotechar='"')
        tfcsvd = dict(map(lambda x: (list(x.values())[0], x), csvd))
    return tfcsvd


def imgloader(localpathname, colorkey=None):  # use this to load imgs | использовать для загрузки картинок
    fullpathname = os.path.join(r'gamedata\img', localpathname)
    if not os.path.isfile(fullpathname):
        print(f'Path -- {fullpathname} image not found)')
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


def lvlreader():
    lvls = []
    for _ in os.listdir(r"gamedata\levels"):
        with open(r'gamedata\levels\ '[:-1] + _, mode='r', encoding="utf-8") as lc:
            try:
                tmp = json.load(lc)
                lvls.append(tmp)
                print(tmp[0]["start_coord"], tmp[0]["music"], tmp[0]["imgs"], tmp[0]["uies"], tmp[0]["dials"],
                      tmp[0]["ents"], sep='\n')
            except json.decoder.JSONDecodeError as jde:
                print(f'Failed to read level config: {jde}')
    print(lvls)
    return lvls


# UPPERCASE = global used variable
# global used/required commands
pygame.init()
pygame.mixer.init()

DB = sqlite3.connect(r'savedata\savedata.sqlite3')
LVLS = lvlreader()
DIALS = csvloader(f'dials/dials.csv')

BASELOCALE = csvloader('locals/basegame.csv')
WLOCALE = csvloader('locals/weaps.csv')
LOCALES = ['en', 'ru']
CLOCALE = 'en'

pygame.mixer.music.set_volume(0.8)

UI_CLICK = pygame.mixer.Sound(r"gamedata\aud\ui\button_click.wav")  # peaceding from tarkov
UI_ESCAPE = pygame.mixer.Sound(r"gamedata\aud\ui\menu_escape.wav")  # peaceding from tarkov
WEAP_PICKUP = pygame.mixer.Sound(r"gamedata\aud\ui\weap_pickup.wav")  # peaceding from tarkov
DEATH_SND = pygame.mixer.Sound(r"gamedata\aud\ui\death.wav")  # peaceding from hl2
WALK = [pygame.mixer.Sound(r"gamedata\aud\game\walk_0.wav"), pygame.mixer.Sound(r"gamedata\aud\game\walk_1.wav"),
        pygame.mixer.Sound(r"gamedata\aud\game\walk_2.wav")]  # peaceding from tarkov

SCREENRES = pygame.display.Info()  # screen resolution required for some imgs to be properly set on canvas
X_CENTER = SCREENRES.current_w // 2  # just a separate coord of screen center value to not repeat the code
Y_CENTER = SCREENRES.current_h // 2  # same as X_CENTER
X_SFAC = SCREENRES.current_w // 125 / 8
Y_SFAC = SCREENRES.current_h // 125 / 8
REL_SCALE = Y_SFAC * 4  # relational scale for scenes
PSCALE = 24  # player collision scale value
POFFSET_X = X_CENTER - Y_SFAC * PSCALE * 2
POFFSET_Y = Y_CENTER - Y_SFAC * PSCALE * 2
print(X_SFAC, Y_SFAC)
screen = pygame.display.set_mode((SCREENRES.current_w, SCREENRES.current_h))

FONT_0 = pygame.font.Font(None, 35)
FONT_0.set_bold(True)
FONT_1 = pygame.font.Font(None, 50)
FONT_1.set_bold(True)
FONT_2 = pygame.font.Font(None, int(X_SFAC * 20))
FONT_2.set_bold(True)
FONT_3 = pygame.font.Font(None, int(X_SFAC * 30))
FONT_3.set_bold(True)

UI_PALETTE = {'col_txt': '#202020', 'col_para': '#AAAACF', 'col_koyma': '#D0D0D8', 'col_sel': '#BBBBCC',
              'col_0': '#DFDFE8'}

pygame.display.set_caption("ColdLine Arkhangelsk")
pygame.display.set_icon(pygame.image.load(r"doomkisser_V2_s.png"))

FADE_IMG = imgloader(r"ui\fade.png", -2)  # global used fade image
FADE_IMG = pygame.transform.scale(FADE_IMG, (SCREENRES.current_w, SCREENRES.current_h))
DARKEN_IMG = imgloader(r"ui\darken.png", -2)  # global used darken image
DARKEN_IMG = pygame.transform.scale(DARKEN_IMG, (SCREENRES.current_w, SCREENRES.current_h))

STARTUP_CONF = csvloader('startupconfig.csv')
try:
    C_SAVE = STARTUP_CONF['last_save']['value']
except KeyError:
    C_SAVE = None
try:
    C_LVL = STARTUP_CONF['last_lvl']['value']
except KeyError:
    C_LVL = 0


def lvlloader(lvlid, sh):  # wip do not use | используется для загрузки уровней
    global LVLS
    clconf = LVLS[lvlid][0]
    LVLS = lvlreader()
    # init part
    try:
        lvl = GameScene(clconf['start_coord'])
    except KeyError:
        print(f'Level {lvlid}: no start coords given - setting to 0, 0')
        lvl = GameScene([0, 0])
    lvl.set_holder(sh)
    try:
        lvl.set_music(clconf['music'])
    except KeyError:
        pass
    try:
        for _ in clconf['imgs']:
            try:
                _['filepath'] = _['filepath'].replace("/", r"\ "[:-1])
                imgtype = _.pop('type')
                if imgtype == 'playeroffset':
                    lvl.add_img(PlayerOffsetImage(**_))
                elif imgtype == 'parallax':
                    lvl.add_img(ParallaxImage(**_))
                else:
                    lvl.add_img(RenderableImage(**_))
            except KeyError:
                print(f'Level {lvlid}: incorrect image format - rejecting it')
    except KeyError:
        print(f'Level {lvlid}: no images given')
    try:
        lvl.add_dsq(*clconf['dials'])
    except KeyError:
        print(f'Level {lvlid}: no dials given')
    try:
        for _ in clconf['ents']:
            lvl.add_ent(_)
    except KeyError:
        print(f'Level {lvlid}: no entities given')
    return lvl


def lvlsaver():
    pass


def db_executor(exectype=0, *data):  # type - type of SQL request; 0 = new game, 1 = get games
    global C_SAVE, C_LVL
    cs = DB.cursor()
    if exectype == 0:
        if cs.execute('''SELECT savename FROM saves WHERE savename=?''', (*data, )).fetchall():
            return 'mmenu_sgame_e_ae'
        try:
            cs.execute('''INSERT INTO saves(savename, lvl) VALUES(?, 0)''', (*data, )).fetchall()
            DB.commit()
            return
        except sqlite3.OperationalError:
            return 'mmenu_sgame_e_ws'
    elif exectype == 1:
        try:
            return cs.execute('''SELECT savename FROM saves''').fetchall()
        except sqlite3.OperationalError:
            return False
    elif exectype == 2:
        try:
            cs.execute('''DELETE FROM saves WHERE savename=?''', (*data, )).fetchall()
            DB.commit()
            return
        except sqlite3.OperationalError:
            return False
    elif exectype == 3:
        try:
            cs.execute('''UPDATE saves
                            SET lvl=?
                            WHERE savename=?''', (C_LVL, C_SAVE)).fetchall()
        except sqlite3.OperationalError:
            cs.execute('''INSERT INTO saves(savename, lvl) VALUES(?, ?)''', (C_LVL, C_SAVE)).fetchall()
        DB.commit()
    elif exectype == 4:
        C_SAVE, C_LVL = cs.execute('''SELECT savename, lvl FROM saves WHERE savename=?''',
                                   (*data, )).fetchall()[0]


def locgetter(loc, key):
    global CLOCALE
    try:
        return loc[key][CLOCALE]
    except KeyError as ke:
        print(f'({ke}) MKW: The keyword is missing in current locale ({loc}), returning it')
    except TypeError as te:
        print(f'({te}) NL: No locale in the UI class, returning locale key')
    return key


def dialgetter(key):
    global DIALS
    try:
        return list(map(lambda x: int(x), filter(lambda y: y.isdigit(), DIALS[key]['imseq'])))
    except KeyError as ke:
        print(f'({ke}) MKW: The keyword is missing in dials, returning [0]')
    except TypeError as te:
        print(f'({te}) NS: No sequence in dials, returning [0]')
    return [0]


# global used commands - end
# -------------------------------------------------------
# \/ \/ \/ GRAPHIC ELS CLASSES START (НАЧАЛО ЗОНЫ КЛАССОВ ГРАФИКИ)


class RenderableImage:  # base image container made to be configurable
    # базовый контейнер изображения для рендера сделанный для удобной конфигурации
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=0.0, th=0.0, overlay=False, colorkey=None, do_render=True):
        self.name = name
        self.overlay = overlay
        self.img = imgloader(filepath, colorkey)
        if not (tw <= 0.0 or th <= 0.0):
            print(self.img.get_width() * tw, self.img.get_height() * th, self.name)
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
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=0.0, th=0.0, pm=1.0, overlay=False, colorkey=None, do_render=True):
        super().__init__(name, filepath, x, y, tw, th, overlay, colorkey, do_render)
        self.para_mul = pm  # parallax offset multiplier/множитель параллакс-смещения

    def render(self, screen, *params):
        screen.blit(self.img, (self.scenepos[0] - (self.para_mul * params[0]), self.scenepos[1]
                               - (self.para_mul * params[1])))


class PlayerOffsetImage(RenderableImage):  # container for image with support of relative to player offset
    # базовый контейнер рендер-изображения с поддержкой относительного к игроку смещения
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=REL_SCALE, th=REL_SCALE, overlay=False, colorkey=None, do_render=True):
        super().__init__(name, filepath, x, y, tw, th, overlay, colorkey, do_render)

    def render(self, screen, *params):
        screen.blit(self.img, (self.scenepos[0] - params[0] * REL_SCALE + POFFSET_X, self.scenepos[1] - params[1]
                               * REL_SCALE + POFFSET_Y))


def sflake_init():
    sflake_0 = imgloader(r"mmenu\CLA_SDrop__0001s_0003_Snowdrop_0.png", -2)
    sflake_1 = imgloader(r"mmenu\CLA_SDrop__0001s_0002_Snowdrop_1.png", -2)
    sflake_2 = imgloader(r"mmenu\CLA_SDrop__0001s_0001_Snowdrop_2.png", -2)
    sflake_3 = imgloader(r"mmenu\CLA_Sdrop_3.png", -2)
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
        self.rect.x = randrange(SCREENRES.current_w)
        self.rect.y = randrange(SCREENRES.current_h)

    def update(self):
        if self.rect.y >= SCREENRES.current_h:
            self.rect.y = -50
        if self.rect.x < 0:
            self.rect.x = SCREENRES.current_w
        self.rect = self.rect.move((randrange(12) - 12, 5 + randrange(5)))


class BaseFramedSprite(pygame.sprite.Sprite):
    def __init__(self, filename, f_x=1, f_y=1, x=0, y=0, frate=10, *sgroup):
        super().__init__(*sgroup)
        sequence = imgloader(filename)
        sequence = pygame.transform.scale(sequence, (REL_SCALE * sequence.get_width(), REL_SCALE
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
        self.image_nonrotated = pygame.transform.scale(imgloader(filename), (REL_SCALE * 64, REL_SCALE * 64))
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
        self.image = self.image = pygame.transform.scale(self.image, (Y_SFAC * 256, Y_SFAC * 256))
        self.cdg = 0
        self.pf = 0

    def update(self, *deg):
        super().update()
        if self.frame != self.pf:
            self.pf = self.frame
            WALK[randint(0, 2)].play()
        if self.cdg != deg[0]:
            self.rotate(*deg)

    def rotate(self, deg):
        self.imgset = [pygame.transform.rotate(_, (deg - 1) * -45 if deg % 2 != 0 else deg * -45) for _ in
                       (self.imgset_45drotated if deg % 2 != 0 else self.imgset_nonrotated)]
        self.image = self.imgset[self.frame]
        self.cdg = deg
        self.rect = self.imgset[0].get_rect(center=self.rect.center)


# ^^^ GRAPHIC ELS CLASSES END (КОНЕЦ ЗОНЫ КЛАССОВ ГРАФИКИ)
# ----------------------------------------------------------
# \/ \/ \/ UI CLASSES START (НАЧАЛО ЗОНЫ КЛАССОВ ИНТЕРФЕЙСА)


class UIElem:  # UI Element base class/базовый класс элемента интерфейса
    def __init__(self, name, loc, x=0, y=0, w=0, h=0, txt='', font=None):
        global FONT_0
        global UI_PALETTE
        self.loc = loc
        self.palette = dict(UI_PALETTE)
        self.name = name
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.font = font
        self.txt = txt
        self.do_render = True

    def __str__(self):
        return self.name

    def hide(self):
        self.do_render = False

    def show(self):
        self.do_render = True

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def set_txt(self, text):
        self.txt = text

    def recolor(self, cid, col):
        try:
            self.palette[cid] = col
        except KeyError as ke:
            print(f'({ke}) NC: No color of this name in the palette')

    def text_render(self):
        if self.loc:
            try:
                return self.font.render(locgetter(self.loc, self.txt), False, self.palette['col_txt'])
            except TypeError:
                return FONT_0.render(locgetter(self.loc, self.txt), False, self.palette['col_txt'])
            except AttributeError:
                return FONT_0.render(locgetter(self.loc, self.txt), False, self.palette['col_txt'])
        else:
            try:
                return self.font.render(self.txt, False, self.palette['col_txt'])
            except TypeError:
                return FONT_0.render(self.txt, False, self.palette['col_txt'])
            except AttributeError:
                return FONT_0.render(self.txt, False, self.palette['col_txt'])


class UICanvas(UIElem):
    def __init__(self, name, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(name, None, x, y, w, h, txt, font)

    def render(self, screen, para=(0, 0)):
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, self.palette['col_para'],
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        pygame.draw.rect(screen, self.palette['col_0'], (self.x, self.y, self.w, self.h), 0)
        pygame.draw.rect(screen, self.palette['col_koyma'], (self.x, self.y, self.w, self.h), 5)


class UIText(UIElem):
    def __init__(self, name, loc, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(name, loc, x, y, w, h, txt, font)

    def render(self, screen, *params):
        text = self.text_render()
        screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))


class UIInterElem(UIElem):  # interactive UI element (buttons, prompts ETC)
    def __init__(self, name, loc, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(name, loc, x, y, w, h, txt, font)
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
    def __init__(self, name, loc, x=0, y=0, w=200, h=50, txt='', font=None):
        super().__init__(name, loc, x, y, w, h, txt, font)
        self.func = None
        self.fpars = []

    def set_func(self, func):
        self.func = func

    def add_fps(self, *fpars):
        self.fpars.extend(fpars)

    def triggered(self):
        UI_CLICK.play()
        if self.func:
            if self.fpars:
                self.func(self.fpars)
            else:
                self.func()

    def proc_evt(self, event, click=False):
        if self.active:
            if self.x <= event.pos[0] <= self.x + self.w and self.y <= event.pos[1] <= self.y + self.h and self.active:
                self.status = 1 if not click else 2
                if self.status == 2:
                    self.triggered()
            else:
                self.status = 0

    def render(self, screen, para=(0, 0)):
        text = super().text_render()
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, self.palette['col_para'],
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        if self.status == 0:
            pygame.draw.rect(screen, self.palette['col_0'], (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, self.palette['col_koyma'], (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))
        elif self.status == 1:
            pygame.draw.rect(screen, self.palette['col_sel'], (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, self.palette['col_koyma'], (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))
        else:
            pygame.draw.rect(screen, self.palette['col_sel'], (self.x + (offset / 2), self.y + (offset / 2), self.w,
                                                               self.h), 0)
            pygame.draw.rect(screen, self.palette['col_koyma'], (self.x + (offset / 2), self.y + (offset / 2), self.w,
                                                                 self.h), 5)
            screen.blit(text, (self.x + (offset / 2), self.y + (offset / 2)))


class TextPrompt(UIInterElem):
    def __init__(self, name, x=0, y=0, w=0, h=0, txt='', font=None, maxl=32):
        super().__init__(name, None, x, y, w, h, txt, font=font)
        self.palette['col_0'] = '#EFEFEF'
        self.maxl = maxl

    def catching(self, event, breakevt=False):
        if event.type == pygame.KEYDOWN and not breakevt:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                self.txt = self.txt[:-1]
            else:
                print(event.key)
                self.txt += f'{event.unicode}'
                if len(self.txt) > self.maxl:
                    self.txt = self.txt[:-1]
        elif breakevt:
            self.status = 0

    def take_txt(self):
        ttxt = self.txt
        self.txt = ''
        return ttxt

    def proc_evt(self, event, click=False, scene_mode=0, scene=None):
        if self.active:
            if (self.x <= event.pos[0] <= self.x + self.w and self.y <= event.pos[1] <= self.y + self.h and self.active
                    and self.status != 2):
                if click:
                    self.status = 2
                    scene.scene_mode = 1
                    scene.catcher = self
                else:
                    self.status = 1
            else:
                self.status = 0

    def text_render(self):
        try:
            return self.font.render(self.txt, False, self.palette['col_txt'])
        except TypeError:
            return FONT_0.render(self.txt, False, self.palette['col_txt'])
        except AttributeError:
            return FONT_0.render(self.txt, False, self.palette['col_txt'])

    def render(self, screen, para=(0, 0)):
        text = self.text_render()
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, self.palette['col_para'],
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        if self.status == 0:
            pygame.draw.rect(screen, self.palette['col_0'], (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, self.palette['col_koyma'], (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + 10, self.y + self.h / 2 - text.get_height() / 2))
        elif self.status == 1:
            pygame.draw.rect(screen, self.palette['col_sel'], (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, self.palette['col_koyma'], (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + 10, self.y + self.h / 2 - text.get_height() / 2))
        else:
            pygame.draw.rect(screen, self.palette['col_sel'], (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, self.palette['col_koyma'], (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + 15, self.y + self.h / 2 - text.get_height() / 2))


class UIGroup:
    def __init__(self, name):
        self.name = name
        self.elems = {}
        self.do_render = False
        self.active = False

    def __str__(self):
        return self.name

    def add_elem(self, *elem):
        for _ in elem:
            self.elems[f'{_}'] = _

    def hide(self):
        self.do_render = False
        self.active = False
        for _ in self.elems.values():
            _.hide()

    def show(self):
        self.do_render = True
        self.active = True
        for _ in self.elems.values():
            _.show()

    def set_active(self, status):
        for _ in self.elems.values():
            if issubclass(type(_), UIInterElem):
                _.set_active(status, False)

    def get_elem(self, name):
        try:
            return self.elems[name]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {name} not in {self.name}'s elements")

    def proc_evt(self, event, click=False, scene_mode=0, scene=None):
        if self.active:
            for _ in self.elems.values():
                if issubclass(type(_), UIInterElem):
                    if isinstance(_, TextPrompt):
                        _.proc_evt(event, click, scene_mode, scene)
                    else:
                        _.proc_evt(event, click)

    def render(self, screen, para=(0, 0)):
        if self.do_render:
            for _ in self.elems.values():
                _.render(screen, para)


class SaveloadMenu(UIGroup):
    canvas = UICanvas("CANVAS", X_CENTER - 300, Y_CENTER - 300, 600, 600)
    namefields, btnslist, dbtns = [], [], []
    for _ in range(5):
        nf = PushBtn(f'SN_{_}', False, X_CENTER - 250, Y_CENTER - 200 + 75 * _, 200, 50, '')
        nf.recolor('col_1', '#d5d5d5')
        nf.set_active(False, True)
        namefields.append(nf)
        pb = PushBtn(f'PB_{_}', BASELOCALE, X_CENTER - 25, Y_CENTER - 200 + 75 * _, 150, 50, 'mmenu_slmenu_p')
        pb.add_fps((_,))
        pb.set_active(False)
        btnslist.append(pb)
        dpb = PushBtn(f'DB_{_}', BASELOCALE, X_CENTER + 150, Y_CENTER - 200 + 75 * _, 80, 50, 'mmenu_slmenu_d')
        dpb.add_fps((_,))
        dpb.recolor('col_txt', '#FF0000')
        dpb.set_active(False)
        dbtns.append(dpb)
    txt = UIText('SLTXT', BASELOCALE, X_CENTER, Y_CENTER - 225, 0, 0, 'mmenu_slmenu_label', FONT_1)
    button_prev = PushBtn('B_PREV', False, X_CENTER - 120, Y_CENTER + 225, 50, 50, '<')
    button_next = PushBtn('B_NEXT', False, X_CENTER + 75, Y_CENTER + 225, 50, 50, '>')

    def __init__(self, name):
        super().__init__(name)
        self.hld = None
        self.page = 0
        self.saves = []
        self.load_saves()
        self.pbtn = SaveloadMenu.button_prev
        self.nbtn = SaveloadMenu.button_next
        self.pbtn.set_func(self.page_prev)
        self.nbtn.set_func(self.page_next)
        self.lbtns = SaveloadMenu.btnslist
        lbtns = SaveloadMenu.btnslist
        dbtns = SaveloadMenu.dbtns
        for _ in lbtns:
            _.set_func(self.load_save)
        for _ in dbtns:
            _.set_func(self.del_save)
        self.add_elem(SaveloadMenu.canvas, SaveloadMenu.txt, self.pbtn, self.nbtn, *SaveloadMenu.namefields,
                      *lbtns, *dbtns)

    def set_holder(self, hld):
        self.hld = hld

    def load_saves(self):
        self.saves = db_executor(1)

    def show(self):
        super().show()
        self.page = 0
        self.load_saves()
        self.set_values()

    def page_prev(self):
        if self.page > 0:
            self.page -= 1
        else:
            self.page = (len(self.saves) // 5 + (1 if len(self.saves) % 5 > 0 else 0)) - 1
        self.set_values()

    def page_next(self):
        if self.page >= (len(self.saves) // 5 + (1 if len(self.saves) % 5 > 0 else 0)) - 1:
            self.page = 0
        else:
            self.page += 1
        self.set_values()

    def set_values(self):
        for _ in range(5):
            self.get_elem(f'SN_{_}').set_txt('')
            self.get_elem(f'PB_{_}').set_active(False, True)
            self.get_elem(f'DB_{_}').set_active(False, True)
        if self.saves:
            if (self.page + 1) * 5 > len(self.saves):
                for _ in range(len(self.saves) % 5):
                    self.get_elem(f'SN_{_}').set_txt(self.saves[self.page * 5 + _][0])
                    self.get_elem(f'PB_{_}').set_active(True, True)
                    self.get_elem(f'DB_{_}').set_active(True, True)
            else:
                for _ in range(5):
                    self.get_elem(f'SN_{_}').set_txt(self.saves[self.page * 5 + _][0])
                    self.get_elem(f'PB_{_}').set_active(True, True)
                    self.get_elem(f'DB_{_}').set_active(True, True)

    def del_save(self, *bid):
        db_executor(2, self.saves[self.page * 5 + bid[0][0][0]][0])
        self.load_saves()
        self.set_values()

    def load_save(self, *bid):
        db_executor(4, self.saves[self.page * 5 + bid[0][0][0]][0])
        self.hld.lvl_load_current()


def dial_icons_init():
    charicons = []
    paths = os.listdir(os.path.join(r'gamedata\img\game\dial'))
    for i in paths:
        if i[-3:] == 'png' or i[-3:] == 'jpg':
            charicons.append(RenderableImage(i, f'game/dial/{i}', x=SCREENRES.current_w - (512 * Y_SFAC) - 50,
                                             y=SCREENRES.current_h - (512 * Y_SFAC) - 50, tw=Y_SFAC, th=Y_SFAC))
    return charicons


class DialSeq:
    dial_img = RenderableImage('IMG_DIAL', r'ui\dial_window.png', tw=Y_SFAC, th=Y_SFAC)
    char_imgs = dial_icons_init()
    zaglush_img = RenderableImage('doomkisser', '', x=SCREENRES.current_w - 512 * Y_SFAC - 50,
                                  y=SCREENRES.current_h - 512 * Y_SFAC - 50, th=Y_SFAC / 4, tw=Y_SFAC / 4)
    next_btn = PushBtn('UI_BTN_DIAL_NEXT', False, SCREENRES.current_w - 75, SCREENRES.current_h - 75, 50, 50, '>')

    def __init__(self, d_id):
        self.d_id = d_id
        self.scene = None
        path = r'locals\lvls\dials\''
        self.loc = csvloader(path[:-1] + d_id + '.csv')
        self.imgseq = dialgetter(d_id)
        self.sptr = 0
        self.txtcut = 0
        self.cimg = self.imgetter()
        self.ctxt = locgetter(self.loc, f'msg_{self.sptr}')
        self.uitxt = UIText('UI_DIAL_TXT', False, X_CENTER, SCREENRES.current_h - 64, txt='', font=FONT_1)
        self.uitxt.recolor('col_txt', '#ffffff')
        self.btn_local = DialSeq.next_btn
        self.btn_local.set_func(self.update)

    def __str__(self):
        return f'{self.d_id}, {self.scene}, {self.imgseq}'

    def imgetter(self):
        try:
            return DialSeq.char_imgs[self.imgseq[self.sptr]]
        except IndexError:
            try:
                return DialSeq.char_imgs[0]
            except IndexError:
                return DialSeq.zaglush_img

    def update(self):
        self.sptr += 1
        if not self.sptr >= len(self.imgseq):
            self.txtcut = 0
            self.cimg = self.imgetter()
            self.ctxt = locgetter(self.loc, f'msg_{self.sptr}')
            self.uitxt.set_txt('')
        else:
            self.scene.dial = None
            self.scene.scene_mode = 0
            self.scene = None
            self.sptr = 0

    def proc_evt(self, event, click=False):
        self.btn_local.proc_evt(event, click)

    def render(self, screen, para=(0, 0)):
        DialSeq.dial_img.render(screen)
        self.cimg.render(screen)
        if not self.txtcut < len(self.ctxt) * 5 + 1:
            self.uitxt.render(screen)
        else:
            self.uitxt.render(screen)
            self.uitxt.set_txt(self.ctxt[:self.txtcut // 5])
            self.txtcut += 1
        self.btn_local.render(screen, para)

    def set(self, scene):
        self.scene = scene
        return self


#  ^^^ UI CLASSES END (КОНЕЦ ЗОНЫ КЛАССОВ ИНТЕРФЕЙСА)
#  --------------------------------------------------------
#  \/ \/ \/ SCENE CLASSES START (НАЧАЛО ЗОНЫ КЛАССОВ СЦЕНЫ)


class PlayerClip(pygame.sprite.Sprite):
    PCG = pygame.sprite.Group()

    def __init__(self):
        super().__init__(PlayerClip.PCG)
        self.image = pygame.Surface((REL_SCALE * PSCALE, REL_SCALE * PSCALE), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('green'), (0, 0, REL_SCALE * PSCALE, REL_SCALE * PSCALE), 5)
        self.rect = pygame.Rect(POFFSET_X, POFFSET_Y, REL_SCALE * PSCALE, REL_SCALE * PSCALE)


class Entity(pygame.sprite.Sprite):  # base entity for scene, init it with gamescene ONLY
    def __init__(self, pcoord, x=0, y=0, w=0, h=0, *sg):
        super().__init__(*sg)
        self.x, self.y = x, y
        self.rect = pygame.Rect(x * REL_SCALE + POFFSET_X - pcoord[0] * REL_SCALE, y * REL_SCALE + POFFSET_Y - pcoord[1]
                                * REL_SCALE, REL_SCALE * w, REL_SCALE * h)

    def update(self, pcoord, scene, *args, **kwargs):  # basically an "entity mover" in this specific case
        self.rect.update(self.x * REL_SCALE + POFFSET_X - pcoord[0] * REL_SCALE, self.y * REL_SCALE + POFFSET_Y -
                         pcoord[1] * REL_SCALE, self.rect.width, self.rect.height)


class TriggerClip(Entity):
    def __init__(self, pcoord, x=0, y=0, w=0, h=0, func=None, once=False, *tcg):
        super().__init__(pcoord, x, y, w, h, *tcg)
        self.image = pygame.Surface((w * REL_SCALE, h * REL_SCALE), pygame.SRCALPHA, 32)
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
        if pygame.sprite.spritecollideany(self, PlayerClip.PCG):
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
        rel32 = REL_SCALE * 32
        self.name = name
        img = imgloader(img)
        self.image = pygame.transform.scale(img, (rel32, rel32))

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, PlayerClip.PCG):
            scene.get_uie('UI_TXT_IPCK').set_txt(f'{locgetter(BASELOCALE, 'item_pckp')}{self.name}')
        else:
            scene.get_uie('UI_TXT_IPCK').set_txt('')


class DropWeap(Entity):
    def __init__(self, pcoord, x=0, y=0, wid=1, *icg):
        super().__init__(pcoord, x, y, 32, 32, *icg)
        rel32 = REL_SCALE * 32
        self.wid = wid
        self.image = pygame.transform.scale(self.load_weap(), (rel32, rel32))

    def load_weap(self):
        if os.path.isfile(r'gamedata\img\game\items\w_' + str(self.wid) + '.png'):
            return imgloader(r'game\items\w_' + str(self.wid) + '.png')
        else:
            return imgloader(r'game\items\w_1.png')

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, PlayerClip.PCG):
            scene.get_uie('UI_TXT_IPCK').set_txt(f'{locgetter(BASELOCALE, 'item_pckp')}'
                                                 f'{locgetter(WLOCALE, 'w_' + str(self.wid))}'
                                                 f'{(' ' + '(' + locgetter(WLOCALE, 'w_' + str(scene.player.weap)) 
                                                     + locgetter(BASELOCALE, 'item_drop')) 
                                                 if scene.player.weap != 0 else ''}')
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
        self.image = pygame.Surface((w * REL_SCALE, h * REL_SCALE), pygame.SRCALPHA, 32)
        self.prev_pos = None
        pygame.draw.rect(self.image, '#00ff00', (0, 0, self.rect.w, self.rect.h), 5)  # debug

    def static_collide(self, pcoord, scene):
        scene.player.revert()
        super().groups()[0].update(scene.player.coords, scene, True)
        if (self.x + self.w / 2 - PSCALE < pcoord[0] < self.x + self.w and
                (not (pcoord[1] + PSCALE - 1 < self.y) and not (pcoord[1] > self.y + self.h - 1))):
            scene.player.vel[0] = 0
        elif self.x + self.w / 2 > pcoord[0] + PSCALE > self.x and (not (pcoord[1] + PSCALE - 1 < self.y) and
                                                                    not (pcoord[1] > self.y + self.h - 1)):
            scene.player.vel[0] = 0
        elif self.y + self.h / 2 - PSCALE < pcoord[1] < self.y + self.h:
            scene.player.vel[1] = 0
        elif self.y + self.h / 2 > pcoord[1] + PSCALE > self.y:
            scene.player.vel[1] = 0

    def dynamic_collide_player(self, pcoord, scene):
        if (self.x + self.w // 2 - PSCALE < pcoord[0] < self.x + self.w and
                (not (pcoord[1] + PSCALE - 1 < self.y) and not (pcoord[1] > self.y + self.h - 1))):
            self.direction = 0
            self.vel = scene.player.sl * self.drag
            if self.drag < 1:
                scene.player.vel[0] *= self.drag
        elif self.x + self.w // 2 > pcoord[0] + PSCALE > self.x and (not (pcoord[1] + PSCALE - 1 < self.y)
                                                                     and not (pcoord[1] > self.y + self.h - 1)):
            self.direction = 1
            self.vel = scene.player.sl * self.drag
            if self.drag < 1:
                scene.player.vel[0] *= self.drag
        elif self.y + self.h // 2 - PSCALE < pcoord[1] < self.y + self.h:
            self.direction = 2
            self.vel = scene.player.sl * self.drag
            if self.drag < 1:
                scene.player.vel[1] *= self.drag
        elif self.y + self.h // 2 > pcoord[1] + PSCALE > self.y:
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
        rel32 = REL_SCALE * 32
        img = imgloader(img)
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
            isplayerclip = pygame.sprite.spritecollideany(self, PlayerClip.PCG)
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
                        if pygame.sprite.spritecollideany(self, PlayerClip.PCG):
                            super().static_collide(pcoord, scene)
                    elif issceneclip:
                        super().dynamic_collide_obj(scene)
                        if pygame.sprite.spritecollideany(self, PlayerClip.PCG):
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
        if pygame.sprite.spritecollideany(self, PlayerClip.PCG):
            super().static_collide(pcoord, scene)


class TestEnemy(Entity):
    def __init__(self, pcoord, x=0, y=0, *esg):
        super().__init__(pcoord, x, y, PSCALE, PSCALE, *esg)
        self.image = imgloader(r"game\char\bkiss\cla_bkiss_sprite_0.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * REL_SCALE,
                                                         self.image.get_height() * REL_SCALE))

    def update(self, pcoord, scene, *args, **kwargs):
        super().update(pcoord, scene, *args, **kwargs)
        if pygame.sprite.spritecollideany(self, scene.Pshots) or pygame.sprite.spritecollideany(self, scene.enemshots):
            self.death()

    def death(self):
        self.image = imgloader(r"game\char\bkiss\cla_bkiss_sprite_dead_0.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * REL_SCALE,
                                                         self.image.get_height() * REL_SCALE))


class Shot(pygame.sprite.Sprite):
    image = imgloader(r"game\effects\Shot.png")
    image = pygame.transform.scale(image, (image.get_width() * 2.5, image.get_height() * 2.5))

    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = Shot.image
        self.rect = Shot.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def die(self):
        self.kill()


class CharSpritemap:
    m0g, m1g, m2g = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_0.png', X_CENTER, Y_CENTER, m0g)
    # PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_0_w0.png', X_CENTER, Y_CENTER, m0g)
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_run_0.png', X_CENTER, Y_CENTER, m1g)
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_dead_0.png', X_CENTER, Y_CENTER, m2g)
    # PlayerRotatableFramedSprite(r'game\char\bkiss\cla_bkiss_sprite_run_0_w0.png', 2, 1, X_CENTER, Y_CENTER, 5, m1g)
    ldir = os.listdir(r'gamedata\img\game\char\bkiss')
    m0wg, m1wg = [], []
    for _ in list(filter(lambda x: 'sprite_0_w' in x, sorted(ldir))):
        locgr = pygame.sprite.Group()
        PlayerRotatableSprite(r'game\char\bkiss\ '[:-1] + _, X_CENTER, Y_CENTER, locgr)
        m0wg.append(locgr)
    for _ in list(filter(lambda x: 'sprite_run_0_w' in x, sorted(ldir))):
        locgr = pygame.sprite.Group()
        PlayerRotatableFramedSprite(r'game\char\bkiss\ '[:-1] + _, 2, 1, X_CENTER, Y_CENTER, 5, locgr)
        m1wg.append(locgr)

    def __init__(self):
        self.sgs = [CharSpritemap.m0g, CharSpritemap.m1g, CharSpritemap.m2g]
        self.wsgs = [CharSpritemap.m0wg, CharSpritemap.m1wg]

    def render(self, screen, status, deg, weap):
        if status != 2:
            try:
                self.wsgs[status][weap].update(deg)
                self.wsgs[status][weap].draw(screen)
            except IndexError:
                self.wsgs[0][0].update(deg)
                self.wsgs[0][0].draw(screen)
        try:
            self.sgs[status].update(deg)
            self.sgs[status].draw(screen)
        except IndexError:
            self.sgs[0].update(deg)
            self.sgs[0].draw(screen)


class Player:
    orients = {(0, -1): 0, (1, -1): 1, (1, 0): 2, (1, 1): 3, (0, 1): 4, (-1, 1): 5, (-1, 0): 6, (-1, -1): 7}

    def __init__(self, startpos):
        self.char_spritemap = CharSpritemap()
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
        WEAP_PICKUP.play()
        return weap_old

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


class BaseScene:  # scene class base: just a holder for scene content
    # базовый класс сцены - контейнера для содержимого на экране (хотя иногда и за его пределами) в данный м.вр.
    def __init__(self, support_para=True):
        self.holder = None  # current scene holder (used for some subclasses to work)

        self.scene_mode = 0  # 0 - scene's proper work; 1 - prompt catching; 2 - cutscene mode

        self.support_para = support_para  # do calculate parallax every update / высчитывать параллакс
        self.para_l = (0, 0)  # parallax local offset / локальный показатель смещения

        self.imghld = {}  # img - картинка
        self.uihld = {}  # ui - интерфейс
        self.sgroup = pygame.sprite.Group()  # s - спрайт
        self.entgroup = pygame.sprite.Group()  # ent - сущность (будь то NPC (враг) или окошко-тумбочка-кровать)

        self.music = None

        self.catcher = None  # catching prompt (while scenemode = 1)
        self.prior_uig = None  # UI group to render

        self.debug = True

    def __str__(self):
        return (f'{self.para_l}\n{self.imghld}\n{self.uihld}\n{self.sgroup}'
                f'\n{self.entgroup}\nscene_mode={self.scene_mode}\ncatcher={self.catcher}')

    # 'adders' / 'добавители' (добавлять элементы в контейнеры для объектов сцены)

    def add_img(self, *imgs):  # add as many imgs as you want (1-"8 rotated by 90 degrees lol")
        for _ in imgs:
            self.imghld[f'{_}'] = _

    def add_uie(self, *uies):  # add as many uielems as you want
        for _ in uies:
            self.uihld[f'{_}'] = _

    def add_s(self, *sprs):  # technically "s = ent" but i will probably make different group class for ent later
        for _ in sprs:
            _(self.sgroup)

    def add_ent(self, *ents):
        for _ in ents:
            _(self.entgroup)

    # getters / геттеры (получатели: возвращают значения из контейнеров)

    def get_para(self, event):
        if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
            self.para_l = (event.pos[0] / 50, event.pos[1] / 50)

    def get_img(self, name):
        try:
            return self.imghld[name]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {name} not in <current scene>'s image elements")

    def get_uie(self, name):
        try:
            return self.uihld[name]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {name} not in <current scene>'s UI elements")

    def get_prior(self):
        if self.prior_uig:
            return self.get_uie(self.prior_uig)

    # setters / сеттеры (устанавливают значения)

    def set_prior(self, name):
        self.prior_uig = self.get_uie(name).name
        self.get_prior().show()

    def unset_prior(self):
        if self.prior_uig:
            self.get_prior().hide()
        self.prior_uig = None
        UI_ESCAPE.play()

    def set_holder(self, hld):
        self.holder = hld
        for _ in self.uihld.values():
            if isinstance(_, SaveloadMenu):
                _.set_holder(self.holder)

    def set_music(self, name):
        if name:
            mp = os.path.join(r'gamedata\aud\mus', name)
            if os.path.isfile(mp):
                self.music = mp

    # 'parsers' / 'парсеры' (обработчики)

    def ui_validator(self, event, click=False):
        if not self.prior_uig:
            for _ in self.uihld.values():
                if self.prior_uig != _.name:
                    if issubclass(type(_), UIInterElem) or isinstance(_, UIGroup):
                        if isinstance(_, TextPrompt) or isinstance(_, UIGroup):
                            _.proc_evt(event, click, self.scene_mode, self)
                        else:
                            _.proc_evt(event, click)
        else:
            self.get_uie(self.prior_uig).proc_evt(event, click, self.scene_mode, self)

    def sprite_event(self, event):
        self.sgroup.update()

    def proc_evt(self, event, *params):
        self.get_para(event)
        if self.scene_mode == 0:
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.ui_validator(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(self.uihld)
                print(self.prior_uig)
                self.ui_validator(event, True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.prior_uig:
                        self.unset_prior()
                    else:
                        game_destroyer()
        elif self.scene_mode == 1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == 13 or event.key == pygame.K_TAB:
                    self.scene_mode = 0
                    self.catcher.catching(event, True)
                else:
                    self.catcher.catching(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.scene_mode = 0
                self.catcher.catching(event, True)

    def const_update(self, *args):
        pass

    def render(self, screen):
        # rendering images
        for _ in self.imghld.values():
            if _.do_render and not _.overlay:
                _.render(screen, self.para_l[0], self.para_l[1])
        # rendering and moving independent sprites
        self.sgroup.draw(screen)
        self.sgroup.update()
        # rendering UIEs
        for _ in self.uihld.values():
            if _.do_render:
                _.render(screen, (self.para_l[0], self.para_l[1]))
        # rendering prior UIGroup
        if self.prior_uig:
            screen.blit(DARKEN_IMG, (0, 0))
            self.get_uie(self.prior_uig).render(screen, (self.para_l[0], self.para_l[1]))


class GameScene(BaseScene):
    pmenu_txt = UIText('UI_TXT_PMENU', BASELOCALE, X_CENTER, Y_CENTER - 150, txt='pmenu_txt')
    pmenu_resume = PushBtn('UI_BTN_PMENU_R', BASELOCALE, X_CENTER - 150, Y_CENTER - 50, w=300, txt='pmenu_resume')
    pmenu_exit = PushBtn('UI_BTN_PMENU_E', BASELOCALE, X_CENTER - 200, Y_CENTER + 50, w=400, txt='pmenu_exit')
    pausemenu = UIGroup('UIG_PAUSE')
    pausemenu.add_elem(pmenu_txt, pmenu_resume, pmenu_exit)
    dmenu_txt = UIText('UI_TXT_DMENU', BASELOCALE, X_CENTER, Y_CENTER // 2, txt='dmenu_txt', font=FONT_1)
    dmenu_restart = PushBtn('UI_BTN_DMENU_R', BASELOCALE, X_CENTER - 225, Y_CENTER - 50, w=450, txt='dmenu_restart')
    deathmenu = UIGroup('UIG_DEATH')
    deathmenu.add_elem(dmenu_txt, dmenu_restart, pmenu_exit)
    itempck = UIText('UI_TXT_IPCK', None, X_CENTER, 100)
    # itempck.recolor('col_txt', '#d8d8ff')
    bg = ParallaxImage('BG', r'game\scene\BG_Sky.png', tw=Y_SFAC * 1.25, th=Y_SFAC * 1.25)

    def __init__(self, startpos):
        super().__init__()
        self.add_uie(GameScene.pausemenu, GameScene.deathmenu)
        self.get_uie('UIG_PAUSE').get_elem('UI_BTN_PMENU_R').set_func(self.unpause)
        self.add_uie(GameScene.itempck)
        self.add_img(GameScene.bg)
        self.dial_sequences = {}  # 'dialog sequences'
        self.dial = None
        self.player = Player(startpos)
        self.trigs, self.items, self.props, self.sclips = (pygame.sprite.Group(), pygame.sprite.Group(),
                                                           pygame.sprite.Group(), pygame.sprite.Group())
        self.enems = pygame.sprite.Group()
        self.Pshots = pygame.sprite.Group()
        self.enemshots = pygame.sprite.Group()
        self.enemy = TestEnemy(self.player.coords, 128, 128, self.enems)
        self.tic = 0
        self.bullet = False
        self.delay = 0
        self.timer = pygame.time.Clock()

    def set_holder(self, hld):
        super().set_holder(hld)
        if self.holder:
            self.get_uie('UIG_PAUSE').get_elem('UI_BTN_PMENU_E').set_func(self.holder.swto_defscene)
            self.get_uie('UIG_DEATH').get_elem('UI_BTN_PMENU_E').set_func(self.holder.swto_defscene)
            self.get_uie('UIG_DEATH').get_elem('UI_BTN_DMENU_R').set_func(self.holder.lvl_reload)

    def add_dsq(self, *dsqs):
        for _ in dsqs:
            self.dial_sequences[f'{_}'] = DialSeq(_)

    def get_dsq(self, name):
        try:
            print(self.dial_sequences)
            print(name)
            return self.dial_sequences[name]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {name} not in <current scene>'s dial sequences")

    def add_ent(self, *kws):
        for _ in kws:
            ent_type = _.pop('type')
            if ent_type == 'TriggerClip':
                new_trig = TriggerClip(self.player.coords, **_)
                try:
                    if _["func"] == "lvl_next" or "lvl_next" in _["func"]:
                        new_trig.set_func(self.holder.lvl_load_next)
                    elif "start_dial" in _["func"]:
                        if self.get_dial_by_did(_["func"][1]):
                            new_trig.set_funcdata((self.get_dial_by_did(_["func"][1]), ))
                            new_trig.set_func(self.start_dial)
                except KeyError:
                    print('No func for trigger')
                self.trigs.add(new_trig)
            elif ent_type == 'DropItem':
                self.items.add(DropItem(self.player.coords, **_))
            elif ent_type == 'DropWeap':
                self.items.add(DropWeap(self.player.coords, **_))
            elif ent_type == 'Prop':
                self.props.add(Prop(self.player.coords, **_))
            elif ent_type == 'SceneCollision':
                self.sclips.add(SceneCollision(self.player.coords, **_))
            elif ent_type == 'Enemy':
                self.enems.add(TestEnemy(self.player.coords, **_))

    def pause(self):
        self.set_prior('UIG_PAUSE')

    def unpause(self):
        self.unset_prior()

    def get_dial_by_did(self, did):
        try:
            return list(self.dial_sequences.keys())[did]
        except IndexError:
            return False

    def start_dial(self, dial):
        self.scene_mode = 2
        self.dial = self.get_dsq(dial).set(self)

    def render(self, screen):
        # rendering images
        for _ in self.imghld.values():
            if _.do_render and not _.overlay:
                if isinstance(_, PlayerOffsetImage):
                    _.render(screen, self.player.coords[0], self.player.coords[1])
                else:
                    _.render(screen, self.para_l[0], self.para_l[1])
        # rendering and moving independent sprites
        self.sgroup.draw(screen)
        self.sgroup.update()
        self.items.draw(screen)
        self.props.draw(screen)
        self.enems.draw(screen)
        self.Pshots.draw(screen)
        self.enemshots.draw(screen)
        # rendering UIEs
        for _ in self.uihld.values():
            if _.do_render:
                _.render(screen, (self.para_l[0], self.para_l[1]))
        # rendering prior UIGroup
        self.player.render(screen)
        if self.prior_uig:
            screen.blit(DARKEN_IMG, (0, 0))
            self.get_uie(self.prior_uig).render(screen, (self.para_l[0], self.para_l[1]))
        if self.dial:
            self.dial.render(screen)
        if self.debug:
            self.trigs.draw(screen)
            PlayerClip.PCG.draw(screen)
        for _ in self.imghld.values():
            if _.do_render and _.overlay:
                if isinstance(_, PlayerOffsetImage):
                    _.render(screen, self.player.coords[0], self.player.coords[1])
                else:
                    _.render(screen, self.para_l[0], self.para_l[1])

    def ui_validator(self, event, click=False):
        if self.dial:
            self.dial.proc_evt(event, click)
        else:
            super().ui_validator(event, click)

    def proc_evt(self, event, **kwargs):
        self.get_para(event)
        if self.scene_mode == 0:
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.ui_validator(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui_validator(event, True)
                self.atc()
            elif event.type == pygame.KEYDOWN:
                self.player.interaction_proc(event)
                if event.key == pygame.K_ESCAPE:
                    if self.prior_uig:
                        self.unset_prior()
                    else:
                        self.pause()
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
        elif self.scene_mode == 2:
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.ui_validator(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui_validator(event, True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.dial.update()

    def const_update(self, keys):
        if self.scene_mode == 0:
            self.player.proc_evt(keys)
            if self.player.status == 2 and not self.player.did_died:
                if self.player.weap != 0:
                    self.items.add(DropWeap(self.player.coords[0] + (random() - 0.5) * 64, self.player.coords[1] +
                                      (random() - 0.5) * 64, self.player.weap))
                self.set_prior('UIG_DEATH')
                self.player.did_died = True
            self.sclips.update(self.player.coords, self)
            self.props.update(self.player.coords, self)
            self.trigs.update(self.player.coords, self)
            self.items.update(self.player.coords, self)
            self.enems.update(self.player.coords, self)
            self.player.interact_request = False
            if self.tic >= self.delay and self.bullet:
                self.bullet.die()
                self.bullet = False
                self.tic = 0
            elif self.bullet:
                self.tic += self.timer.tick()

    def save_state(self):
        pass

    def load_state(self):
        pass

    def atc(self):
        if self.player.weap == 1:
            self.bullet = Shot(X_CENTER - 150, Y_CENTER - 50, self.Pshots)
            self.tic = 0
            self.timer = pygame.time.Clock()
            self.delay = 1000


class SceneHolder:
    def __init__(self, scene):
        self.defscene = None
        self.scene = None
        self.switch_scene(scene)
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

    def const_parser(self, keys):
        self.scene.const_update(keys)

    def switch_scene(self, scene_new):
        if self.scene:
            self.scene.unset_prior()
            self.scene.set_holder(None)
        self.scene = scene_new
        if self.scene:
            self.scene.set_holder(self)
            self.music_play()
        self.fade_timer = 0
        self.no_event = True

    def set_defscene(self, ds):
        self.defscene = ds
        self.music_play()

    def swto_defscene(self):
        self.switch_scene(self.defscene)

    def music_play(self):
        if self.scene.music:
            pygame.mixer.music.load(self.scene.music)
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.fadeout(10000)

    def lvl_reload(self):
        self.switch_scene(lvlloader(C_LVL, self))

    def lvl_load_next(self):
        global C_LVL
        C_LVL += 1
        db_executor(3)
        try:
            self.switch_scene(lvlloader(C_LVL, self))
        except IndexError:
            self.swto_defscene()

    def lvl_load(self, lvlid):
        global C_LVL
        C_LVL = lvlid
        db_executor(3)
        try:
            self.switch_scene(lvlloader(C_LVL, self))
        except IndexError:
            self.swto_defscene()

    def lvl_load_current(self):
        global C_LVL
        try:
            self.switch_scene(lvlloader(C_LVL, self))
        except IndexError:
            self.swto_defscene()


# ^^^ SCENE CLASSES END (КОНЕЦ ЗОНЫ КЛАССОВ СЦЕНЫ)
# ------------------------------------------------------------
# \/ \/ \/ MAIN GAME LOOP AREA START (НАЧАЛО ЗОНЫ РАБОТЫ ИГРЫ)


def mmenu_imgs_init():
    clachr_size = 1024 * Y_SFAC
    mmenuimg_0 = ParallaxImage('MMENUIMG_0', r'mmenu\CLA_MM_BG_0.png', 0, 0,
                               Y_SFAC / 2 + 0.025, Y_SFAC / 2 + 0.025)
    mmenuimg_1 = ParallaxImage('MMENUIMG_1', r'mmenu\CLA_MM_BG_1.png', 0, 0,
                               Y_SFAC / 2, Y_SFAC / 2, do_render=False)
    clachr = ParallaxImage('CLA_CHR', r'mmenu\CLA_Chr__0003s_0004_HD_Obvod.png',
                           X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                           Y_SFAC / 2, Y_SFAC / 2, 1.5, colorkey=-2)
    clachr_g = ParallaxImage('CLA_CHR_G', r'mmenu\CLA_Chr__0003s_0001_HD_GS_Zakras.png',
                             X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                             Y_SFAC / 2, Y_SFAC / 2, 1.5, colorkey=-2, do_render=False)
    clachr_bld = ParallaxImage('CLA_CHR_BLD ', r'mmenu\CLA_Chr__0003s_0002_BLD.png',
                               X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                               Y_SFAC / 2, Y_SFAC / 2, 1.5, colorkey=-2)
    clachr_col = ParallaxImage('CLA_CHR_COL', r'mmenu\CLA_Chr__0003s_0003_HD_ColOL.png',
                               X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                               Y_SFAC / 2, Y_SFAC / 2, 1.5, colorkey=-2)
    clachr_gno = ParallaxImage('CLA_CHR_GNO', r'mmenu\CLA_Chr__0003s_0000_gno.png',
                               X_CENTER - 512 - 256 - 128, SCREENRES.current_h - 512 - 256, 0.8, 0.8,
                               4, colorkey=-2)
    ttle = ParallaxImage('TITLE', r'mmenu\CLA_Txt_0.png', X_CENTER - 1024 * Y_SFAC, 0, Y_SFAC / 2, Y_SFAC / 2, 2.5,
                         colorkey=-2)
    print(C_LVL)
    if int(C_LVL) == 1:
        clachr_bld.show()
        clachr_g.hide()
        clachr_col.show()
        mmenuimg_1.show()
        mmenuimg_0.hide()
    elif int(C_LVL) == 0:
        clachr_bld.hide()
        clachr_g.show()
        clachr_col.hide()
        mmenuimg_1.hide()
        mmenuimg_0.show()
    else:
        mmenuimg_1.hide()
        mmenuimg_0.hide()
    return mmenuimg_0, mmenuimg_1, clachr, clachr_col, clachr_bld, ttle, clachr_gno, clachr_g


def mmenu_obj_init():
    mmenu = BaseScene()  # wip (subject to be properly organized probably)
    mmenu.add_img(*mmenu_imgs_init())  # wip (subject to be properly organized probably)
    # exit game button setup
    killgamebtn = PushBtn('UI_BTN_KILLGAME', BASELOCALE, x=X_CENTER - 100, y=Y_CENTER + 256, txt="mmenu_killgame")
    killgamebtn.set_func(game_destroyer)
    # saveload window button setup
    savebtn = PushBtn('UI_BTN_SAVELOAD', BASELOCALE, w=450, x=X_CENTER - 225, y=Y_CENTER + 28, txt="mmenu_saveloadgame")
    savebtn.set_func(mmenu_group_switch)
    sgbtn = PushBtn('UI_BTN_STARTGAME', BASELOCALE, w=450, x=X_CENTER - 225, y=Y_CENTER - 72, txt="mmenu_startgame")
    sgbtn.set_func(mmenu_sgame_g_switch)
    version = UIText('UI_TXT_VER', BASELOCALE, x=X_CENTER, y=SCREENRES.current_h - 50, txt='cla_c_ver', font=FONT_1)
    version.recolor('col_txt', '#9D9DAF')
    locbtn = PushBtn('UI_BTN_LOC', BASELOCALE, w=50, x=SCREENRES.current_w - 75, y=SCREENRES.current_h - 75,
                     txt='mmenu_loc')
    expbtn = PushBtn('UI_BTN_EXP', False, w=50, x=25, y=SCREENRES.current_h - 75, txt='i')
    locbtn.set_func(mmenu_locsw)
    expbtn.set_func(mmenu_expnote_switch)
    mmenu.add_uie(killgamebtn, savebtn, sgbtn, locbtn, expbtn, SaveloadMenu('UIG_SL'), mmenu_sgame_group_init(),
                  mmenu_claexp_init(), version)
    mmenu.set_music('dymyat_molcha.mp3')
    for _ in range(10):
        mmenu.add_s(SnowflakeSprite)
    return mmenu


def mmenu_sgame_group_init():
    sgtxt = UIText('UI_NGAME_TXT', BASELOCALE, x=X_CENTER, y=Y_CENTER - 100, txt='mmenu_sgame_n', font=FONT_1)
    sgtxt_e = UIText('UI_NGAME_E', BASELOCALE, x=X_CENTER, y=Y_CENTER - 25, txt='n', font=FONT_1)
    sgtxt_e.recolor('col_txt', 'red')
    sgtxt.recolor('col_txt', '#FFFFFF')
    sgprpt = TextPrompt('UI_NGAME_PRPT', h=50, w=250, x=X_CENTER - 125, y=Y_CENTER)
    sgrp = UIGroup('UIG_SGAME')
    sgbtn = PushBtn('UI_SGAME_BTN', BASELOCALE, h=50, w=250, x=X_CENTER - 125, y=Y_CENTER + 60, txt='mmenu_sgame_s')
    sgbtn.set_func(mmenu_sgame)
    sgrp.add_elem(sgtxt, sgprpt, sgbtn, sgtxt_e)
    return sgrp


def mmenu_claexp_init():
    txt_t = UIText('UI_CE_T', BASELOCALE, x=X_CENTER, y=160, txt='cla_exp_t', font=FONT_3)
    txt_t.recolor('col_txt', '#BFBFFF')
    txt_0 = UIText('UI_CE_0', BASELOCALE, x=X_CENTER, y=220, txt='cla_exp_0', font=FONT_2)
    txt_0.recolor('col_txt', '#BFBFFF')
    txt_1 = UIText('UI_CE_1', BASELOCALE, x=X_CENTER, y=255, txt='cla_exp_1', font=FONT_2)
    txt_1.recolor('col_txt', '#BFBFFF')
    txt_2 = UIText('UI_CE_2', BASELOCALE, x=X_CENTER, y=300, txt='cla_exp_2', font=FONT_2)
    txt_2.recolor('col_txt', '#BFBFFF')
    txt_3 = UIText('UI_CE_3', BASELOCALE, x=X_CENTER, y=350, txt='cla_exp_3', font=FONT_3)
    txt_3.recolor('col_txt', '#BFBFFF')
    txt_4 = UIText('UI_CE_4', BASELOCALE, x=X_CENTER, y=390, txt='cla_exp_4', font=FONT_2)
    txt_4.recolor('col_txt', '#BFBFFF')
    txt_5 = UIText('UI_CE_5', BASELOCALE, x=X_CENTER, y=420, txt='cla_exp_5', font=FONT_2)
    txt_5.recolor('col_txt', '#BFBFFF')
    txt_6 = UIText('UI_CE_6', BASELOCALE, x=X_CENTER, y=450, txt='cla_exp_6', font=FONT_2)
    txt_6.recolor('col_txt', '#BFBFFF')
    txt_7 = UIText('UI_CE_7', BASELOCALE, x=X_CENTER, y=480, txt='cla_exp_7', font=FONT_2)
    txt_7.recolor('col_txt', '#BFBFFF')
    txt_8 = UIText('UI_CE_8', BASELOCALE, x=X_CENTER, y=510, txt='cla_exp_8', font=FONT_2)
    txt_8.recolor('col_txt', '#BFBFFF')
    txt_9 = UIText('UI_CE_9', BASELOCALE, x=X_CENTER, y=560, txt='cla_exp_9', font=FONT_2)
    txt_9.recolor('col_txt', '#BFBFFF')
    txt_10 = UIText('UI_CE_10', BASELOCALE, x=X_CENTER, y=590, txt='cla_exp_10', font=FONT_2)
    txt_10.recolor('col_txt', '#BFBFFF')
    txt_11 = UIText('UI_CE_11', BASELOCALE, x=X_CENTER - 50, y=750, txt='cla_exp_11', font=FONT_2)
    txt_11.recolor('col_txt', '#BFBFFF')
    txt_12 = UIText('UI_CE_12', BASELOCALE, x=X_CENTER, y=780, txt='cla_exp_12', font=FONT_2)
    txt_12.recolor('col_txt', '#BFBFFF')
    txt_13 = UIText('UI_CE_13', BASELOCALE, x=X_CENTER, y=900, txt='cla_exp_13', font=FONT_2)
    txt_13.recolor('col_txt', '#BFBFFF')
    txt_14 = UIText('UI_CE_14', BASELOCALE, x=X_CENTER, y=930, txt='cla_exp_14', font=FONT_2)
    txt_14.recolor('col_txt', '#BFBFFF')
    txt_15 = UIText('UI_CE_15', BASELOCALE, x=X_CENTER, y=960, txt='cla_exp_15', font=FONT_2)
    txt_15.recolor('col_txt', '#BFBFFF')
    grp = UIGroup('UIG_CLAEXP')
    grp.add_elem(txt_t, txt_0, txt_1, txt_2, txt_3, txt_4, txt_5, txt_6, txt_7, txt_8, txt_9, txt_10, txt_11, txt_12,
                 txt_13, txt_14, txt_15)
    return grp


def game_destroyer():
    global GAME_RUNNING
    GAME_RUNNING = False


def mmenu_group_switch():
    mmenu.set_prior(mmenu.get_uie('UIG_SL').name)


def mmenu_expnote_switch():
    mmenu.set_prior(mmenu.get_uie('UIG_CLAEXP').name)


def mmenu_sgame_g_switch():
    mmenu.set_prior(mmenu.get_uie('UIG_SGAME').name)


def mmenu_sgame():  # new game creation / создание новой игры из главменю
    global C_LVL
    global C_SAVE
    sname = mmenu.get_prior().get_elem('UI_NGAME_PRPT').take_txt()
    if sname.strip():
        msg = db_executor(0, sname.lower())
        if msg:
            mmenu.get_prior().get_elem('UI_NGAME_E').set_txt(msg)
        else:
            mmenu.get_prior().get_elem('UI_NGAME_E').set_txt('n')
            C_SAVE = sname.lower()
            C_LVL = 0
            sceneslot.lvl_load_current()
    else:
        mmenu.get_prior().get_elem('UI_NGAME_E').set_txt('mmenu_sgame_e_e')


def mmenu_locsw():  # locale switcher / переключатель языка
    global CLOCALE
    CLOCALE = LOCALES[(LOCALES.index(CLOCALE) + 1) % len(LOCALES)]


if __name__ == '__main__':
    GAME_RUNNING = True
    mmenu = mmenu_obj_init()
    sceneslot = SceneHolder(mmenu)
    sceneslot.set_defscene(mmenu)
    while GAME_RUNNING:
        sceneslot.const_parser(pygame.key.get_pressed())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_RUNNING = False
            else:
                sceneslot.event_parser(event)
        sceneslot.render(screen)
        pygame.display.flip()
