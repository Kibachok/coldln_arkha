#
# CLA-UI
#
# all the UI elements' classes
#
# classes: UIElem -> UICanvas, UIText, [UIInterElem -> TextPrompt, PushBtn]; UIGroup -> SaveloadMenu; DialSeq
#
import pygame

import cla_core.screendata as sd
import loaders as load
import database as db
import cla_core.locale as loc
import cla_core.audio as aud
import cla_core.s_graphics as graph


pygame.init()


FONT_0 = pygame.font.Font(None, 35)
FONT_0.set_bold(True)
FONT_1 = pygame.font.Font(None, 50)
FONT_1.set_bold(True)

UI_PALETTE = {'col_txt': '#202020', 'col_para': '#AAAACF', 'col_koyma': '#D0D0D8', 'col_sel': '#BBBBCC',
              'col_0': '#DFDFE8'}


class UIElem:  # UI Element base class/базовый класс элемента интерфейса
    def __init__(self, name, lloc, x=0, y=0, w=0, h=0, txt='', font=None):
        global FONT_0
        global UI_PALETTE
        self.loc = lloc
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

    def text_render(self, locale):
        if self.loc:
            try:
                return self.font.render(loc.locgetter(self.loc, self.txt, locale), False, self.palette['col_txt'])
            except TypeError:
                return FONT_0.render(loc.locgetter(self.loc, self.txt, locale), False, self.palette['col_txt'])
            except AttributeError:
                return FONT_0.render(loc.locgetter(self.loc, self.txt, locale), False, self.palette['col_txt'])
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

    def render(self, screen, locale, para=(0, 0)):
        offset = sd.SCREENRES.current_w // 1000 * 5
        pygame.draw.rect(screen, self.palette['col_para'],
                         (self.x + offset - (para[0] * 0.8), self.y + offset - (para[1] * 0.8), self.w, self.h), 0)
        pygame.draw.rect(screen, self.palette['col_0'], (self.x, self.y, self.w, self.h), 0)
        pygame.draw.rect(screen, self.palette['col_koyma'], (self.x, self.y, self.w, self.h), 5)


class UIText(UIElem):
    def __init__(self, name, lloc, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(name, lloc, x, y, w, h, txt, font)

    def render(self, screen, locale, *args):
        text = self.text_render(locale)
        screen.blit(text, (self.x + self.w / 2 - text.get_width() / 2, self.y + self.h / 2 - text.get_height() / 2))


class UIInterElem(UIElem):  # interactive UI element (buttons, prompts ETC)
    def __init__(self, name, lloc, x=0, y=0, w=0, h=0, txt='', font=None):
        super().__init__(name, lloc, x, y, w, h, txt, font)
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
    def __init__(self, name, lloc, x=0, y=0, w=200, h=50, txt='', font=None):
        super().__init__(name, lloc, x, y, w, h, txt, font)
        self.func = None
        self.fpars = []

    def set_func(self, func):
        self.func = func

    def add_fps(self, *fpars):
        self.fpars.extend(fpars)

    def triggered(self):
        aud.aud_play(aud.UI_CLICK)
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

    def render(self, screen, locale, para=(0, 0)):
        text = super().text_render(locale)
        offset = sd.SCREENRES.current_w // 1000 * 5
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

    def text_render(self, locale):
        try:
            return self.font.render(self.txt, False, self.palette['col_txt'])
        except TypeError:
            return FONT_0.render(self.txt, False, self.palette['col_txt'])
        except AttributeError:
            return FONT_0.render(self.txt, False, self.palette['col_txt'])

    def render(self, screen, locale, para=(0, 0)):
        text = self.text_render(locale)
        offset = sd.SCREENRES.current_w // 1000 * 5
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

    def render(self, screen, locale, para=(0, 0)):
        if self.do_render:
            for _ in self.elems.values():
                _.render(screen, locale, para)


class SaveloadMenu(UIGroup):
    canvas = UICanvas("CANVAS", sd.X_CENTER - 300, sd.Y_CENTER - 300, 600, 600)
    namefields, btnslist, dbtns = [], [], []
    for _ in range(5):
        nf = PushBtn(f'SN_{_}', False, sd.X_CENTER - 250, sd.Y_CENTER - 200 + 75 * _, 200, 50, '')
        nf.recolor('col_1', '#d5d5d5')
        nf.set_active(False, True)
        namefields.append(nf)
        pb = PushBtn(f'PB_{_}', loc.BASELOCALE, sd.X_CENTER - 25, sd.Y_CENTER - 200 + 75 * _, 150, 50,
                     'mmenu_slmenu_p')
        pb.add_fps((_,))
        pb.set_active(False)
        btnslist.append(pb)
        dpb = PushBtn(f'DB_{_}', loc.BASELOCALE, sd.X_CENTER + 150, sd.Y_CENTER - 200 + 75 * _, 80, 50,
                      'mmenu_slmenu_d')
        dpb.add_fps((_,))
        dpb.recolor('col_txt', '#FF0000')
        dpb.set_active(False)
        dbtns.append(dpb)
    txt = UIText('SLTXT', loc.BASELOCALE, sd.X_CENTER, sd.Y_CENTER - 225, 0, 0, 'mmenu_slmenu_label', FONT_1)
    button_prev = PushBtn('B_PREV', False, sd.X_CENTER - 120, sd.Y_CENTER + 225, 50, 50, '<')
    button_next = PushBtn('B_NEXT', False, sd.X_CENTER + 75, sd.Y_CENTER + 225, 50, 50, '>')

    def __init__(self, name):
        super().__init__(name)
        self.hld = None
        self.page = 0
        self.saves = []
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
        self.load_saves()

    def load_saves(self):
        self.saves = db.db_executor(self.hld.csave, self.hld.clvl, 1)

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
        db.db_executor(self.hld.csave, self.hld.clvl, 2, self.saves[self.page * 5 + bid[0][0][0]][0])
        self.load_saves()
        self.set_values()

    def load_save(self, *bid):
        db.db_executor(self.hld.csave, self.hld.clvl, 4, self.saves[self.page * 5 + bid[0][0][0]][0])
        self.hld.lvl_load_current()


DIALS = load.csvloader(f'dials/dials.csv')


def dial_icons_init():
    charicons = []
    paths = load.dials_imgcat()
    for i in paths:
        if i[-3:] == 'png' or i[-3:] == 'jpg':
            charicons.append(graph.RenderableImage(i, f'game/dial/{i}',
                                                   x=sd.SCREENRES.current_w - (512 * sd.Y_SFAC) - 50,
                                                   y=sd.SCREENRES.current_h - (512 * sd.Y_SFAC) - 50,
                                                   tw=sd.Y_SFAC, th=sd.Y_SFAC))
    return charicons


def dialgetter(key):  # gets the dial images sequence from global dials var
    # dial == dialogue
    global DIALS
    try:
        return list(map(lambda x: int(x), filter(lambda y: y.isdigit(), DIALS[key]['imseq'])))
    except KeyError as ke:
        print(f'({ke}) MKW: The keyword is missing in dials, returning [0]')
    except TypeError as te:
        print(f'({te}) NS: No sequence in dials, returning [0]')
    return [0]


class DialSeq:
    dial_img = graph.RenderableImage('IMG_DIAL', r'ui\dial_window.png', tw=sd.Y_SFAC, th=sd.Y_SFAC)
    char_imgs = dial_icons_init()
    zaglush_img = graph.RenderableImage('doomkisser', '', x=sd.SCREENRES.current_w - 512 * sd.Y_SFAC - 50,
                                        y=sd.SCREENRES.current_h - 512 * sd.Y_SFAC - 50, th=sd.Y_SFAC / 4,
                                        tw=sd.Y_SFAC / 4)
    next_btn = PushBtn('UI_BTN_DIAL_NEXT', False, sd.SCREENRES.current_w - 75, sd.SCREENRES.current_h - 75, 50, 50,
                       '>')

    def __init__(self, d_id):
        self.d_id = d_id
        self.scene = None
        path = r'locals\lvls\dials\''
        self.loc = load.csvloader(path[:-1] + d_id + '.csv')
        self.imgseq = dialgetter(d_id)
        self.sptr = 0
        self.txtcut = 0
        self.cimg = self.imgetter()
        self.ctxt = None
        self.uitxt = UIText('UI_DIAL_TXT', False, sd.X_CENTER, sd.SCREENRES.current_h - 64, txt='', font=FONT_1)
        self.uitxt.recolor('col_txt', '#ffffff')
        self.btn_local = DialSeq.next_btn
        self.btn_local.set_func(self.update)

    def __str__(self):
        return f'{self.d_id}'

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
            self.ctxt = loc.locgetter(self.loc, f'msg_{self.sptr}', self.scene.holder.clocale)
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
            self.uitxt.render(screen, self.scene.holder.clocale)
        else:
            self.uitxt.render(screen, self.scene.holder.clocale)
            self.uitxt.set_txt(self.ctxt[:self.txtcut // 5])
            self.txtcut += 1
        self.btn_local.render(screen, para)

    def set(self, scene):
        self.scene = scene
        self.ctxt = loc.locgetter(self.loc, f'msg_{self.sptr}', self.scene.holder.clocale)
        return self
