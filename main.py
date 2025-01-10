# DEMO WIP Build of game with main menu and some simple classes only
import pygame


class ParallaxImage:  # container for image with all parallax (offset with the cursor) data about it
    def __init__(self, filepath, x, y, pm=1.0, isalpha=False):
        if isalpha:
            self.img = pygame.image.load(filepath).convert_alpha()
        else:
            self.img = pygame.image.load(filepath).convert()
        self.scenepos = (x, y)  # local scene position for img
        self.para_mul = pm  # parallax offset multiplier


class PushBtn:  # PUSHBuTtoN class: pushable
    def __init__(self, w=200, h=50, x=0, y=0):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.func = False
        self.status = 0
        self.active = True
        # self.pressed_delay = False

    def set_func(self, func):
        self.func = func

    def set_active(self, status):
        self.active = status

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def pressed(self):
        if self.func:
            self.func()

    def render(self, screen):
        offset = SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, '#CCCCDD', (self.x, self.y, self.w, self.h), 0)
        if self.status == 0:
            pygame.draw.rect(screen, '#DFDFE8', (self.x + offset, self.y + offset, self.w, self.h), 0)
        elif self.status == 1:
            pygame.draw.rect(screen, '#BBBBCC', (self.x + offset, self.y + offset, self.w, self.h), 0)
        else:
            pygame.draw.rect(screen, '#BBBBCC', (self.x + (offset / 2), self.y + (offset / 2), self.w, self.h), 0)

    def status_check(self, event, click=False):
        if self.x <= event.pos[0] <= self.x + self.w and self.y <= event.pos[1] <= self.y + self.h and self.active:
            self.status = 1 if not click else 2
            if self.status == 2:
                self.pressed()
        else:
            self.status = 0


class BaseScene:  # scene class base: just a holder for scene content
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


class ParallaxScene(BaseScene):
    def __init__(self):
        super().__init__()

    def render(self, screen, xoffset, yoffset):
        for _ in self.imghld:
            screen.blit(_.img, (_.scenepos[0] - (xoffset * _.para_mul), _.scenepos[1] - (yoffset * _.para_mul)))
        for _ in self.btnhld:
            _.render(screen)


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
                             SCREENRES.current_w / 2 - 512, SCREENRES.current_h - 974, 1.5, True)
    clachr_g.img = pygame.transform.scale(clachr_g.img, (1024, 1024))
    clachr_bld = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0002_BLD.png',
                               SCREENRES.current_w / 2 - 512, SCREENRES.current_h - 974, 1.5, True)
    clachr_bld.img = pygame.transform.scale(clachr_bld.img, (1024, 1024))
    clachr_col = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0003_HD_ColOL.png',
                               SCREENRES.current_w / 2 - 512, SCREENRES.current_h - 974, 1.5, True)
    clachr_col.img = pygame.transform.scale(clachr_col.img, (1024, 1024))
    clachr_gno = ParallaxImage(r'gamedata\img\mmenu\CLA_Chr__0003s_0000_gno.png',
                               SCREENRES.current_w / 2 - 512 - 256 - 128, SCREENRES.current_h - 512 - 256, 3, True)
    clachr_gno.img = pygame.transform.scale(clachr_gno.img, (1024, 1024))
    ttle = ParallaxImage(r'gamedata\img\mmenu\CLA_Txt_0.png', SCREENRES.current_w / 2 - 1024, 0, 2, True)
    ttle.img = pygame.transform.scale(ttle.img, (2048, 512))
    return mmenuimg, clachr, clachr_col, clachr_bld, ttle, clachr_gno


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


pygame.init()
pygame.mixer.init()  # test
mtimer = pygame.time  # costill
pygame.mixer.music.load(r"gamedata\aud\mus\dymyat_molcha.mp3")  # test (change it later like move to separate
# def or class idk)
pygame.mixer.music.play()  # test (look 124)
pygame.mixer.music.set_volume(0.8)  # test (look 124)
ui_click = pygame.mixer.Sound(r"gamedata\aud\ui\button_click.wav")  # peaceding from tarkov
SCREENRES = pygame.display.Info()  # screen resolution var required for some imgs to be properly set on canvas
screen = pygame.display.set_mode((SCREENRES.current_w, SCREENRES.current_h))
pygame.display.set_caption("ColdLine Arkhangelsk")
imgslist = mmenu_imgs_init()  # wip (subject to be properly organized probably)
game_isactive = True
do_render_pasxalko = False
mmenu = ParallaxScene()  # wip (subject to be properly organized probably)
mmenu.extend_img(imgslist)  # wip (subject to be properly organized probably)
# pygame.mixer.music.fadeout(10000)
testbtn = PushBtn(x=SCREENRES.current_w // 2 - 100, y=SCREENRES.current_h // 2 + 256)  # NAME SAYS FOR THE THING ITSELF
testbtn.set_func(game_destroyer)  # FUNC-BUTTON SETTER TEST
mmenu.append_btn(testbtn)
testbtn2 = PushBtn(x=SCREENRES.current_w // 2 - 100, y=SCREENRES.current_h // 2 + 128)  # AS WELL AS 161
testbtn2.set_func(doomkisser_enabler)  # SAME AS 162
mmenu.append_btn(testbtn2)
dtime = 0  # costill
while game_isactive:
    if (mtimer.get_ticks() + dtime) % 170000 >= 169995:  # nowayroyatnee costill (subject to be removed)
        dtime += music_controller()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_isactive = False
        if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:  # costill a little bit
            mmenu.btn_validator(event)
            mmenu.render(screen, xoffset=event.pos[0] / 50, yoffset=event.pos[1] / 50)
            if do_render_pasxalko:
                cla_mainmenu_draw(screen, xoffset=event.pos[0] / 50, yoffset=event.pos[1] / 50)
            pygame.display.flip()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mmenu.btn_validator(event, True)
            mmenu.render(screen, xoffset=event.pos[0] / 50, yoffset=event.pos[1] / 50)
            pygame.display.flip()
