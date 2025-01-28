# DEMO WIP Build of game with main menu and some simple classes only
import os

import pygame
import csv
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


def lvlloader():  # wip do not use | используется для загрузки уровней (скорее всего через CSV будет а не через JSON)
    # потому что условия для оценивания проекта, НЕ ТРОГАТЬ пока что
    pass


def db_executor():  # можно в передаваемые аргументы записать если что SQL запрос
    # весь код для взаимодействия с СУБД возможно наверно я не знаю
    pass


# UPPERCASE = global used variable
# global used/required commands
pygame.init()
pygame.mixer.init()
DIALS = csvloader(f'dials/dials.csv')
BASELOCALE = csvloader('locals/basegame.csv')
LOCALES = ['en', 'ru']
CLOCALE = 'en'
FONT_0 = pygame.font.Font(None, 35)
FONT_0.set_bold(True)
FONT_1 = pygame.font.Font(None, 50)
FONT_1.set_bold(True)
UI_PALETTE = {'col_txt': '#202020', 'col_para': '#AAAACF', 'col_koyma': '#D0D0D8', 'col_sel': '#BBBBCC',
              'col_0': '#DFDFE8'}
mtimer = pygame.time  # costill
pygame.mixer.music.load(r"gamedata\aud\mus\belye_dnee.mp3")  # MOVE IT TO SOME SCENE METHOD
pygame.mixer.music.play()  # test (look 30)
pygame.mixer.music.set_volume(1.0)  # test (look 30)
UI_CLICK = pygame.mixer.Sound(r"gamedata\aud\ui\button_click.wav")  # peaceding from tarkov
UI_ESCAPE = pygame.mixer.Sound(r"gamedata\aud\ui\menu_escape.wav")  # peaceding from tarkov
SCREENRES = pygame.display.Info()  # screen resolution required for some imgs to be properly set on canvas
X_CENTER = SCREENRES.current_w // 2  # just a separate coord of screen center value to not repeat the code
Y_CENTER = SCREENRES.current_h // 2  # same as X_CENTER
X_SFAC = SCREENRES.current_w // 250 / 4
Y_SFAC = SCREENRES.current_h // 250 / 4
print(X_SFAC, Y_SFAC)
screen = pygame.display.set_mode((SCREENRES.current_w, SCREENRES.current_h))
pygame.display.set_caption("ColdLine Arkhangelsk")
pygame.display.set_icon(pygame.image.load(r"doomkisser_V2_s.png"))
FADE_IMG = imgloader(r"ui\fade.png", -2)  # global used fade image
FADE_IMG = pygame.transform.scale(FADE_IMG, (SCREENRES.current_w, SCREENRES.current_h))
DARKEN_IMG = imgloader(r"ui\darken.png", -2)  # global used darken image
DARKEN_IMG = pygame.transform.scale(DARKEN_IMG, (SCREENRES.current_w, SCREENRES.current_h))


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
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=0.0, th=0.0, colorkey=None, do_render=True):
        self.name = name
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
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=0.0, th=0.0, pm=1.0, colorkey=None, do_render=True):
        super().__init__(name, filepath, x, y, tw, th, colorkey, do_render)
        self.para_mul = pm  # parallax offset multiplier/множитель параллакс-смещения

    def render(self, screen, *params):
        screen.blit(self.img, (self.scenepos[0] - (self.para_mul * params[0]), self.scenepos[1]
                               - (self.para_mul * params[1])))


class PlayerOffsetImage(RenderableImage):  # container for image with support of relative to player offset
    # базовый контейнер рендер-изображения с поддержкой относительного к игроку смещения
    def __init__(self, name, filepath, x=0.0, y=0.0, tw=0.0, th=0.0, colorkey=None, do_render=True):
        super().__init__(name, filepath, x, y, tw, th, colorkey, do_render)

    def render(self, screen, *params):
        screen.blit(self.img, (self.scenepos[0] - params[0], self.scenepos[1] - params[1]))


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
        sequence = pygame.transform.scale(sequence, (Y_SFAC * 512, Y_SFAC * 256))
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
        self.image = pygame.transform.scale(imgloader(filename), (Y_SFAC * 256, Y_SFAC * 256))
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.cdg = 0

    def update(self, deg):
        if self.cdg != deg:
            self.rotate(deg)

    def rotate(self, deg):
        self.image = pygame.transform.rotate(self.image, (deg - self.cdg) * 45)
        self.cdg = deg
        self.rect = self.image.get_rect(center=self.rect.center)


class PlayerRotatableFramedSprite(BaseFramedSprite):
    def __init__(self, filename, f_x=1, f_y=1, x=0, y=0, frate=10, *sgroup):
        super().__init__(filename, f_x, f_y, x, y, frate, *sgroup)
        self.image = self.image = pygame.transform.scale(self.image, (Y_SFAC * 256, Y_SFAC * 256))
        self.cdg = 0

    def update(self, *deg):
        super().update()
        if self.cdg != deg:
            self.rotate(*deg)

    def rotate(self, deg):
        deltadeg = (deg - self.cdg) * 45
        self.image = pygame.transform.rotate(self.image, deltadeg)
        self.imgset = [pygame.transform.rotate(_, deltadeg) for _ in self.imgset]
        self.cdg = deg
        self.rect = self.image.get_rect(center=self.rect.center)


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
    def __init__(self, name, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(name, None, x, y, w, h, txt, font=font)
        self.palette['col_0'] = '#EFEFEF'

    def catching(self, event, breakevt=False):
        if event.type == pygame.KEYDOWN and not breakevt:
            if event.key == pygame.K_BACKSPACE:
                self.txt = self.txt[:-1]
            else:
                self.txt += f'{event.unicode}'
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


def dial_icons_init():
    charicons = []
    paths = os.listdir(os.path.join(r'gamedata\img\game\dial'))
    for i in paths:
        if i[-3:] == 'png' or i[-3:] == 'jpg':
            charicons.append(RenderableImage(i, f'game/dial/{i}', x=SCREENRES.current_w - (512 * Y_SFAC) - 50,
                                             y=SCREENRES.current_h - (512 * Y_SFAC) - 50, tw=Y_SFAC, th=Y_SFAC))
    return charicons


class DialSeq:
    dial_img = RenderableImage('IMG_DIAL', r'ui\dial_window.png')
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
        return self.d_id

    def imgetter(self):
        try:
            print(self.imgseq)
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


class CharSpritemap:
    m0g, m1g, m2g = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_0.png', X_CENTER, Y_CENTER, m0g)
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_0_w0.png', X_CENTER, Y_CENTER, m0g)
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_run_0.png', X_CENTER, Y_CENTER, m1g)
    PlayerRotatableSprite(r'game\char\bkiss\cla_bkiss_sprite_dead_0.png', X_CENTER, Y_CENTER, m2g)
    PlayerRotatableFramedSprite(r'game\char\bkiss\cla_bkiss_sprite_run_0_w0.png', 2, 1, X_CENTER, Y_CENTER, 6, m1g)

    def __init__(self):
        self.sgs = [CharSpritemap.m0g, CharSpritemap.m1g, CharSpritemap.m2g]

    def render(self, screen, status, deg):
        try:
            self.sgs[status].update(deg)
            self.sgs[status].draw(screen)
        except IndexError:
            self.sgs[0].update(deg)
            self.sgs[0].draw(screen)


class Player:
    orients = {(0, -1): 0, (1, -1): 1, (1, 0): 2, (1, 1): 3, (0, 1): 4, (-1, 1): 5, (-1, 0): 6, (-1, -1): 7}

    def __init__(self):
        self.char_spritemap = CharSpritemap()
        self.orient = (0, 0)
        self.deg = 0
        self.coords = [0, 0]
        self.vels = [0, 0, 0, 0]  # velocities / скорости (0=up,1=down,2=right,3=left)
        self.clip = None
        self.weap = 0
        self.status = 0
        self.cf = False  # cycle flag; represents one event cycle
        self.orient_l = []

    def proc_evt(self, event, keys):
        if self.status != 2:
            self.calc_orient(keys)
            if self.status != 0:
                if self.orient == (0, 0):
                    self.status = 0
            else:
                if self.orient != (0, 0):
                    self.status = 1

    def calc_orient(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if keys[pygame.K_d] or keys[pygame.K_LEFT]:
                self.set_orient((1, -1))
            elif keys[pygame.K_a] or keys[pygame.K_RIGHT]:
                self.set_orient((-1, -1))
            else:
                self.set_orient((0, -1))
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if keys[pygame.K_d] or keys[pygame.K_LEFT]:
                self.set_orient((1, 1))
            elif keys[pygame.K_a] or keys[pygame.K_RIGHT]:
                self.set_orient((-1, 1))
            else:
                self.set_orient((0, 1))
        else:
            if keys[pygame.K_d] or keys[pygame.K_LEFT]:
                self.set_orient((1, 0))
            elif keys[pygame.K_a] or keys[pygame.K_RIGHT]:
                self.set_orient((-1, 0))
            else:
                self.set_orient((0, 0))

    def set_orient(self, orient):
        if orient != (0, 0) or orient != self.orient:
            self.orient = orient
            try:
                self.deg = Player.orients[orient]
            except KeyError:
                pass

    def render(self, screen):
        self.char_spritemap.render(screen, self.status, self.deg)


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

        self.catcher = None  # catching prompt (while scenemode = 1)
        self.prior_uig = None  # UI group to render

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
        self.get_prior().hide()
        self.prior_uig = None
        UI_ESCAPE.play()

    def set_holder(self, hld):
        self.holder = hld

    # 'parsers' / 'парсеры' (обработчики)

    def ui_validator(self, event, click=False):
        if not self.prior_uig:
            for _ in self.uihld.values():
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
                self.ui_validator(event, True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.prior_uig:
                        self.unset_prior()
                    else:
                        game_destroyer()
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

    def render(self, screen):
        # rendering images
        for _ in self.imghld.values():
            if _.do_render:
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

    def __init__(self, mmenu):
        super().__init__()
        self.mmenu = mmenu
        self.add_uie(GameScene.pausemenu)
        self.get_uie('UIG_PAUSE').get_elem('UI_BTN_PMENU_R').set_func(self.unpause)
        self.dial_sequences = {}  # 'dialog sequences'
        self.dial = None
        self.player = Player()

    def set_holder(self, hld):
        super().set_holder(hld)
        if self.holder:
            self.get_uie('UIG_PAUSE').get_elem('UI_BTN_PMENU_E').set_func(self.holder.swto_defscene)

    def add_dsq(self, *dsqs):
        for _ in dsqs:
            self.dial_sequences[f'{_}'] = _

    def get_dsq(self, name):
        try:
            return self.dial_sequences[name]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {name} not in <current scene>'s dial sequences")

    def pause(self):
        self.set_prior('UIG_PAUSE')

    def unpause(self):
        self.unset_prior()

    def start_dial(self, dial):
        self.scene_mode = 2
        self.dial = self.get_dsq(dial).set(self)

    def render(self, screen):
        # rendering images
        for _ in self.imghld.values():
            if _.do_render:
                if isinstance(_, PlayerOffsetImage):
                    _.render(screen, -self.player.coords[0], -self.player.coords[1])
                else:
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
        if self.dial:
            self.dial.render(screen)
        self.player.render(screen)

    def ui_validator(self, event, click=False):
        if self.dial:
            self.dial.proc_evt(event, click)
        else:
            super().ui_validator(event, click)

    def proc_evt(self, event, **kwargs):
        self.get_para(event)
        self.player.proc_evt(event, pygame.key.get_pressed())
        if self.scene_mode == 0:
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.ui_validator(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui_validator(event, True)
            elif event.type == pygame.KEYDOWN:
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


class SceneHolder:
    def __init__(self, scene):
        self.defscene = None
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
        if self.scene:
            self.scene.unset_prior()
            self.scene.set_holder(None)
        self.scene = scene_new
        if self.scene:
            self.scene.set_holder(self)
        self.fade_timer = 0
        self.no_event = True

    def set_defscene(self, ds):
        self.defscene = ds

    def swto_defscene(self):
        self.switch_scene(self.defscene)


# ^^^ SCENE CLASSES END (КОНЕЦ ЗОНЫ КЛАССОВ СЦЕНЫ)
# ------------------------------------------------------------
# \/ \/ \/ MAIN GAME LOOP AREA START (НАЧАЛО ЗОНЫ РАБОТЫ ИГРЫ)


def cla_mainmenu_draw(screen, xoffset=0, yoffset=0):  # REMOVE LATER
    doomerochek = pygame.image.load(r'doomkisser_V2_s.png').convert()
    doomerochek = pygame.transform.scale(doomerochek, (510, 510))
    screen.blit(doomerochek, (0, 0))
    font = pygame.font.Font(None, 35)
    text = font.render("Cold Line :: Arkhangelsk (Dev-alpha)", False, '#CACAEF')
    screen.blit(text, (500 - text.get_width() - (500 - text.get_width()) / 2 - xoffset * 2, 50 - yoffset * 3))
    font = pygame.font.Font(None, 20)
    text = font.render("imagine good working main menu here", False, '#DDDDDD')
    screen.blit(text, (500 - text.get_width() - (500 - text.get_width()) / 2, 75))


def mmenu_imgs_init():
    clachr_size = 1024 * Y_SFAC
    mmenuimg_0 = ParallaxImage('MMENUIMG_0', r'mmenu\CLA_MM_BG_0.png', 0, 0,
                               Y_SFAC / 2 + 0.025, Y_SFAC / 2 + 0.025)
    mmenuimg_1 = ParallaxImage('MMENUIMG_1', r'mmenu\CLA_MM_BG_1.png', 0, 0,
                               Y_SFAC / 2, Y_SFAC / 2, do_render=False)
    clachr = ParallaxImage('CLA_CHR', r'mmenu\CLA_Chr__0003s_0004_HD_Obvod.png',
                           X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                           Y_SFAC / 2, Y_SFAC / 2, 1.5, -2)
    clachr_g = ParallaxImage('CLA_CHR_G', r'mmenu\CLA_Chr__0003s_0001_HD_GS_Zakras.png',
                             X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                             Y_SFAC / 2, Y_SFAC / 2, 1.5, -2, False)
    clachr_bld = ParallaxImage('CLA_CHR_BLD ', r'mmenu\CLA_Chr__0003s_0002_BLD.png',
                               X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                               Y_SFAC / 2, Y_SFAC / 2, 1.5, -2)
    clachr_col = ParallaxImage('CLA_CHR_COL', r'mmenu\CLA_Chr__0003s_0003_HD_ColOL.png',
                               X_CENTER - clachr_size / 2, SCREENRES.current_h - clachr_size + 50,
                               Y_SFAC / 2, Y_SFAC / 2, 1.5, -2)
    clachr_gno = ParallaxImage('CLA_CHR_GNO', r'mmenu\CLA_Chr__0003s_0000_gno.png',
                               X_CENTER - 512 - 256 - 128, SCREENRES.current_h - 512 - 256, 0.8, 0.8,
                               4, -2)
    ttle = ParallaxImage('TITLE', r'mmenu\CLA_Txt_0.png', X_CENTER - 1024, 0, Y_SFAC / 2, Y_SFAC / 2, 2.5, -2)
    return mmenuimg_0, mmenuimg_1, clachr, clachr_col, clachr_bld, ttle, clachr_gno, clachr_g


def mmenu_obj_init():
    mmenu = BaseScene()  # wip (subject to be properly organized probably)
    mmenu.add_img(*mmenu_imgs_init())  # wip (subject to be properly organized probably)
    # exit game button setup
    killgamebtn = PushBtn('UI_BTN_KILLGAME', BASELOCALE, x=X_CENTER - 100, y=Y_CENTER + 256, txt="mmenu_killgame")
    killgamebtn.set_func(game_destroyer)
    # TEST button setup
    testbtn = PushBtn('UI_BTN_BKISS_BTN', BASELOCALE, w=450, x=X_CENTER - 225, y=Y_CENTER + 128, txt="mmenu_roflo")
    testbtn.set_func(doomkisser_enabler)
    # saveload window button setup
    savebtn = PushBtn('UI_BTN_SAVELOAD', BASELOCALE, w=450, x=X_CENTER - 225, y=Y_CENTER + 28, txt="mmenu_saveloadgame")
    savebtn.set_func(mmenu_group_switch)
    sgbtn = PushBtn('UI_BTN_STARTGAME', BASELOCALE, w=450, x=X_CENTER - 225, y=Y_CENTER - 72, txt="mmenu_startgame")
    sgbtn.set_func(mmenu_sgame_g_switch)
    locbtn = PushBtn('UI_BTN_LOC', BASELOCALE, w=50, x=SCREENRES.current_w - 75, y=SCREENRES.current_h - 75,
                     txt='mmenu_loc')
    locbtn.set_func(mmenu_locsw)
    mmenu.add_uie(killgamebtn, testbtn, savebtn, sgbtn, locbtn, mmenu_loadgame_group_init(), mmenu_sgame_group_init())
    for _ in range(10):
        mmenu.add_s(SnowflakeSprite)
    nmenu = BaseScene()  # multiscene game test remove it later!!!!!!!
    nmenu.add_uie(testbtn)
    return mmenu, nmenu


def mmenu_loadgame_group_init():
    canvas = UICanvas('CANVAS', h=700, w=800, x=X_CENTER - 400, y=Y_CENTER - 350)
    testprompt = UIText('UI_TXT_TEST', False, h=1, w=100, x=500, y=500, txt='testprompt')
    prpt_0 = TextPrompt('UI_PRPT_TEST', h=50, w=100, x=X_CENTER - 390, y=Y_CENTER - 340)
    testgrp = UIGroup('UIG_TEST')
    testgrp.add_elem(canvas, testprompt, prpt_0)
    return testgrp


def mmenu_sgame_group_init():
    sgtxt = UIText('UI_NGAME_TXT', BASELOCALE, x=X_CENTER, y=Y_CENTER - 100, txt='mmenu_sgame_n', font=FONT_1)
    sgtxt.recolor('col_txt', '#FFFFFF')
    sgprpt = TextPrompt('UI_NGAME_PRPT', h=50, w=250, x=X_CENTER - 125, y=Y_CENTER)
    sgrp = UIGroup('UIG_SGAME')
    sgbtn = PushBtn('UI_SGAME_BTN', BASELOCALE, h=50, w=250, x=X_CENTER - 125, y=Y_CENTER + 60, txt='mmenu_sgame_s')
    sgbtn.set_func(mmenu_sgame)
    sgrp.add_elem(sgtxt, sgprpt, sgbtn)
    return sgrp


def music_controller():
    pygame.mixer.music.stop()
    pygame.mixer.music.play(start=1.8)
    return 1800


def game_destroyer():  # MAYBE FOR BUTTONS TEST
    global GAME_RUNNING
    GAME_RUNNING = False


def doomkisser_enabler():  # FOR BUTTONS TEST
    global do_render_pasxalko
    do_render_pasxalko = not do_render_pasxalko
    pygame.mixer.music.fadeout(5000)
    sceneslot.switch_scene(nmenu)


def mmenu_group_switch():
    mmenu.set_prior(mmenu.get_uie('UIG_TEST').name)


def mmenu_sgame_g_switch():
    mmenu.set_prior(mmenu.get_uie('UIG_SGAME').name)


def mmenu_sgame():
    sname = mmenu.get_prior().get_elem('UI_NGAME_PRPT').take_txt()
    print(sname)
    # пиши код базы данных сдеся
    sceneslot.switch_scene(gscene_init())


def mmenu_locsw():
    global CLOCALE
    CLOCALE = LOCALES[(LOCALES.index(CLOCALE) + 1) % len(LOCALES)]


def gscene_init():
    global mmenu
    scene = GameScene(mmenu)
    scene.add_img(PlayerOffsetImage('SCENE', r'game\scene\1-335as.jpg', tw=Y_SFAC * 4, th=Y_SFAC * 4))
    scene.add_dsq(DialSeq('lvl_0_0'))
    scene.start_dial('lvl_0_0')
    return scene


if __name__ == '__main__':
    GAME_RUNNING = True
    do_render_pasxalko = False  # VERY TEST
    mmenu, nmenu = mmenu_obj_init()
    sceneslot = SceneHolder(mmenu)
    sceneslot.set_defscene(mmenu)
    dtime = 0  # costill
    while GAME_RUNNING:
        if (mtimer.get_ticks() + dtime) % 170000 >= 169995:  # nowayroyatnee costill (subject to be removed)
            dtime += music_controller()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_RUNNING = False
            else:
                sceneslot.event_parser(event)
        sceneslot.render(screen)
        if do_render_pasxalko:
            cla_mainmenu_draw(screen, xoffset=0, yoffset=0)
        pygame.display.flip()
