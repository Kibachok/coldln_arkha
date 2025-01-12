# DEMO WIP Build of game with main menu and some simple classes only
import pygame


class RenderableImage:  # base image container made to be configurable
    # базовый контейнер изображения для рендера сделанный для удобной конфигурации
    def __init__(self, filepath, x, y, isalpha=False, do_render=True):
        if isalpha:
            self.img = pygame.image.load(filepath).convert_alpha()
        else:
            self.img = pygame.image.load(filepath).convert()
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
    def __init__(self, filepath, x, y, pm=1.0, isalpha=False, do_render=True):
        super().__init__(filepath, x, y, isalpha, do_render)
        self.para_mul = pm  # parallax offset multiplier/множитель параллакс-смещения


class PushBtn:  # PUSHBuTtoN class: pushable/класс нажимаемой кнопки
    def __init__(self, btntxt='', font='', w=200, h=50, x=0, y=0):
        global font_0
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.func = False
        self.status = 0
        self.active = True
        self.font = font
        self.btntxt = btntxt
        self.do_render = True
        # self.pressed_delay = False

    def set_func(self, func):
        self.func = func

    def set_active(self, status):
        self.active = status

    def hide(self):
        self.do_render = False
        self.active = False

    def show(self):
        self.do_render = True

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def pressed(self):
        if self.func:
            self.func()

    def render(self, screen, para):
        try:
            text = self.font.render(self.btntxt, False, '#202020')
        except TypeError:
            text = font_0.render(self.btntxt, False, '#202020')
        except AttributeError:
            text = font_0.render(self.btntxt, False, '#202020')
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, '#AAAACF',
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        if self.status == 0:
            pygame.draw.rect(screen, '#DFDFE8', (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, '#D0D0D8', (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))
        elif self.status == 1:
            pygame.draw.rect(screen, '#BBBBCC', (self.x, self.y, self.w, self.h), 0)
            pygame.draw.rect(screen, '#D0D0D8', (self.x, self.y, self.w, self.h), 5)
            screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))
        else:
            pygame.draw.rect(screen, '#BBBBCC', (self.x + (offset / 2), self.y + (offset / 2), self.w, self.h), 0)
            pygame.draw.rect(screen, '#D0D0D8', (self.x + (offset / 2), self.y + (offset / 2), self.w, self.h), 5)
            screen.blit(text, (self.x + (offset / 2), self.y + (offset / 2)))

    def status_check(self, event, click=False):
        if self.active:
            if self.x <= event.pos[0] <= self.x + self.w and self.y <= event.pos[1] <= self.y + self.h and self.active:
                self.status = 1 if not click else 2
                if self.status == 2:
                    self.pressed()
            else:
                self.status = 0


class BaseScene:  # scene class base: just a holder for scene content
    # базовый класс сцены - контейнера для содержимого на экране (хотя иногда и за его пределами) в данный м.вр.
    def __init__(self):
        self.imghld = []
        self.btnhld = []

    def append_img(self, img):
        self.imghld.append(img)

    def extend_img(self, imgs):
        self.imghld.extend(imgs)

    def append_btn(self, btn):
        self.btnhld.append(btn)

    def extend_btn(self, btns):
        self.btnhld.extend(btns)

    def btn_validator(self, event, click=False):
        for _ in self.btnhld:
            _.status_check(event, click)


class ParallaxScene(BaseScene):  # parallax-supported scene/сцена с поддержкой параллакса
    def __init__(self):
        super().__init__()

    def render(self, screen, xoffset, yoffset):
        for _ in self.imghld:
            if _.do_render:
                screen.blit(_.img, (_.scenepos[0] - (xoffset * _.para_mul), _.scenepos[1] - (yoffset * _.para_mul)))
        for _ in self.btnhld:
            if _.do_render:
                _.render(screen, (xoffset, yoffset))


class SceneHolder:
    def __init__(self, scene):
        self.scene = scene
        self.fade_timer = 0
        self.no_event = False

    def render(self, screen, *params):
        self.scene.render(screen, *params)

    def render_fade(self, screen):
        if self.fade_timer <= 255:
            screen.blit(FADE_IMG, (0, 0))
            self.fade_timer += 1
        else:
            self.no_event = False

    def funccall(self, name, *args):
        getattr(self.scene, name)(*args)

    def switch_scene(self, scene_new):
        self.scene = scene_new
        # pygame.draw.rect(screen, '#000000', (0, 0, SCREENRES.current_w, SCREENRES.current_h))
        self.fade_timer = 0
        self.no_event = True


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
    mmenuimg = ParallaxImage(r'gamedata\img\mmenu\CLA_MM_BG_0.png', 0, 0)
    mmenuimg.img = pygame.transform.scale(mmenuimg.img, (SCREENRES.current_w, SCREENRES.current_w / 2 * 1.25))
    clachr = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0004_HD_Obvod.png', SCREENRES.current_w / 2 - 512,
                           SCREENRES.current_h - 974, 1.5, True)
    clachr.img = pygame.transform.scale(clachr.img, (1024, 1024))
    clachr_g = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0001_HD_GS_Zakras.png',
                             SCREENRES.current_w / 2 - 512, SCREENRES.current_h - 974, 1.5, True, False)
    clachr_g.img = pygame.transform.scale(clachr_g.img, (1024, 1024))
    clachr_bld = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0002_BLD.png',
                               SCREENRES.current_w / 2 - 512, SCREENRES.current_h - 974, 1.5, True)
    clachr_bld.img = pygame.transform.scale(clachr_bld.img, (1024, 1024))
    clachr_col = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0003_HD_ColOL.png',
                               SCREENRES.current_w / 2 - 512, SCREENRES.current_h - 974, 1.5, True)
    clachr_col.img = pygame.transform.scale(clachr_col.img, (1024, 1024))
    clachr_gno = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0000_gno.png',
                               SCREENRES.current_w / 2 - 512 - 256 - 128, SCREENRES.current_h - 512 - 256, 4, True)
    clachr_gno.img = pygame.transform.scale(clachr_gno.img, (1024, 1024))
    ttle = ParallaxImage(r'gamedata\img\mmenu\CLA_Txt_0.png', SCREENRES.current_w / 2 - 1024, 0, 2.5, True)
    ttle.img = pygame.transform.scale(ttle.img, (2048, 512))
    return mmenuimg, clachr, clachr_col, clachr_bld, ttle, clachr_gno, clachr_g


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
    ui_click.play()
    sceneslot.switch_scene(nmenu)


pygame.init()
pygame.mixer.init()  # test
mtimer = pygame.time  # costill
pygame.mixer.music.load(r"gamedata\aud\mus\svdetelstvo_polko_privet.mp3")  # test (change it later like move to separate
# def or class idk)
pygame.mixer.music.play()  # test (look 124)
pygame.mixer.music.set_volume(1.0)  # test (look 124)
ui_click = pygame.mixer.Sound(r"gamedata\aud\ui\button_click.wav")  # peaceding from tarkov
SCREENRES = pygame.display.Info()  # screen resolution var required for some imgs to be properly set on canvas
screen = pygame.display.set_mode((SCREENRES.current_w, SCREENRES.current_h))
FADE_IMG = pygame.image.load(r"gamedata\img\ui\fade.png").convert_alpha()
FADE_IMG = pygame.transform.scale(FADE_IMG, (SCREENRES.current_w, SCREENRES.current_h))
pygame.display.set_caption("ColdLine Arkhangelsk")
pygame.display.set_icon(pygame.image.load(r"doomkisser_V2_s.png"))
game_isactive = True
do_render_pasxalko = False
font_0 = pygame.font.Font(None, 35)  # font
font_0.set_bold(True)
mmenu = ParallaxScene()  # wip (subject to be properly organized probably)
mmenu.extend_img(mmenu_imgs_init())  # wip (subject to be properly organized probably)
# pygame.mixer.music.fadeout(10000)
testbtn = PushBtn(x=SCREENRES.current_w // 2 - 100, y=SCREENRES.current_h // 2 + 256, btntxt="kill program")
# NAME SAYS FOR THE THING ITSELF
testbtn.set_func(game_destroyer)  # FUNC-BUTTON SETTER TEST
mmenu.append_btn(testbtn)
testbtn2 = PushBtn(w=450, x=SCREENRES.current_w // 2 - 225, y=SCREENRES.current_h // 2 + 128,
                   btntxt="Show a cute boykisser doomer UwU")  # AS WELL AS 161
testbtn2.set_func(doomkisser_enabler)  # SAME AS 162
mmenu.append_btn(testbtn2)
nmenu = ParallaxScene()  # wip (subject to be properly organized probably)
nmenu.append_btn(testbtn2)
sceneslot = SceneHolder(mmenu)
dtime = 0  # costill
while game_isactive:
    if (mtimer.get_ticks() + dtime) % 170000 >= 169995:  # nowayroyatnee costill (subject to be removed)
        dtime += music_controller()
    if sceneslot.no_event:
        sceneslot.render_fade(screen)
        sceneslot.render(screen, 0, 0)
        pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_isactive = False
        if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:  # costill a little bit
            # mmenu.btn_validator(event)
            # mmenu.render(screen, xoffset=event.pos[0] / 50, yoffset=event.pos[1] / 50)
            sceneslot.funccall('btn_validator', event)
            sceneslot.render(screen, event.pos[0] / 50, event.pos[1] / 50)
            if do_render_pasxalko:
                cla_mainmenu_draw(screen, xoffset=event.pos[0] / 50, yoffset=event.pos[1] / 50)
            pygame.display.flip()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # mmenu.btn_validator(event, True)
            # mmenu.render(screen, xoffset=event.pos[0] / 50, yoffset=event.pos[1] / 50)
            sceneslot.funccall('btn_validator', event, True)
            sceneslot.render(screen, event.pos[0] / 50, event.pos[1] / 50)
            pygame.display.flip()
