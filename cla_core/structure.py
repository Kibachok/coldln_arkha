#
# CLA-structure
#
# all the game's base structural objects: scenes and "scene holder"
#
# classes: SceneHolder, BaseScene -> GameScene
#
import pygame

import os
import sys
from random import random

import cla_core.screendata as sd
import cla_core.ui as ui
import cla_core.s_graphics as graph
import cla_core.audio as aud
import cla_core.locale as loc
import loaders as load
import database as db
import cla_core.player as player
import cla_core.entities as ent


LVLS = load.lvlsreader()


def lvlloader(lvlid, sh, *lvls):  # creates a gamescene from level's json format
    print(int(lvlid), type(lvlid))
    clconf = lvls[int(lvlid)][0]
    # init part
    try:
        lvl = GameScene(list(clconf['start_coord']))
    except KeyError:
        print(f'Level {lvlid}: no start coords given - setting to 0, 0')
        lvl = GameScene([0, 0])
    lvl.set_holder(sh)
    # reading music: dead silence if not specified or audio file doesn't exist
    try:
        lvl.set_music(clconf['music'])
    except KeyError:
        pass
    except FileNotFoundError:
        pass
    # images reader
    try:
        for _ in clconf['imgs']:
            try:
                _ = dict(_)
                _['filepath'] = _['filepath'].replace("/", r"\ "[:-1])
                _['filepath'] = _['filepath'].replace(r"\\", r"\ "[:-1])
                imgtype = _.pop('type')
                # selects a container type
                if imgtype == 'playeroffset':
                    lvl.add_img(graph.PlayerOffsetImage(**_))
                elif imgtype == 'parallax':
                    lvl.add_img(graph.ParallaxImage(**_))
                else:
                    lvl.add_img(graph.RenderableImage(**_))
            except KeyError:
                print(f'Level {lvlid}: incorrect image format - rejecting it')
    except KeyError:
        print(f'Level {lvlid}: no images given')
    # dials reader
    try:
        lvl.add_dsq(*clconf['dials'])
    except KeyError:
        print(f'Level {lvlid}: no dials given')
    # entities reader
    try:
        for _ in clconf['ents']:
            _ = dict(_)
            print(_)
            lvl.add_ent(_)
    except KeyError:
        print(f'Level {lvlid}: no entities given')
    return lvl


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

        self.debug = True  # debug mode, manual switching only for now

    def __str__(self):
        return (f'{self.para_l}\n{self.imghld}\n{self.uihld}\n{self.sgroup}'
                f'\n{self.entgroup}\nscene_mode={self.scene_mode}\ncatcher={self.catcher}')

    # 'adders' / 'добавители' (добавлять элементы в контейнеры для объектов сцены)

    def add_img(self, *imgs):  # add as many imgs to the scene's img dict as you want
        # formatted like - <image container's 'name' field>: <image container itself>
        for _ in imgs:
            self.imghld[f'{_}'] = _

    def add_uie(self, *uies):  # add as many uielems to the scene's uies dict as you want
        # formatted like - <UIE's 'name' field>: <UIE itself>
        for _ in uies:
            self.uihld[f'{_}'] = _

    def add_s(self, *sprs):  # adds independent sprites (independent - constantly updated without any specific event)
        for _ in sprs:
            _(self.sgroup)

    def add_ent(self, *ents):  # unused
        for _ in ents:
            _(self.entgroup)

    # getters / геттеры (получатели: возвращают значения из контейнеров)

    def get_para(self, event):  # calculates the current 'parallax' values using mouse pos
        if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
            self.para_l = (event.pos[0] / 50, event.pos[1] / 50)

    def get_img(self, name):  # returns specific image container using its name if it's in scene's images dict
        try:
            return self.imghld[name]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {name} not in <current scene>'s image elements")

    def get_uie(self, name):  # returns specific ui elem using its name if it's in scene's uies dict
        try:
            return self.uihld[name]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {name} not in <current scene>'s UI elements")

    def get_prior(self):  # returns the current prior ui group
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
        aud.aud_play(aud.UI_ESCAPE)

    def set_holder(self, hld):
        self.holder = hld
        if self.holder:
            for _ in self.uihld.values():
                if isinstance(_, ui.SaveloadMenu):
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
                    if issubclass(type(_), ui.UIInterElem) or isinstance(_, ui.UIGroup):
                        if isinstance(_, ui.TextPrompt) or isinstance(_, ui.UIGroup):
                            _.proc_evt(event, click, self.scene_mode, self)
                        else:
                            _.proc_evt(event, click)
        else:
            self.get_uie(self.prior_uig).proc_evt(event, click, self.scene_mode, self)

    def sprite_event(self):
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
                        self.holder.tf('Terminated manually (using given func of sys.exit)')
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
                _.render(screen, self.holder.clocale, (self.para_l[0], self.para_l[1]))
        # rendering prior UIGroup
        if self.prior_uig:
            screen.blit(graph.DARKEN_IMG, (0, 0))
            self.get_uie(self.prior_uig).render(screen, self.holder.clocale, (self.para_l[0], self.para_l[1]))


class GameScene(BaseScene):
    pmenu_txt = ui.UIText('UI_TXT_PMENU', loc.BASELOCALE, sd.X_CENTER, sd.Y_CENTER - 150, txt='pmenu_txt')
    pmenu_resume = ui.PushBtn('UI_BTN_PMENU_R', loc.BASELOCALE, sd.X_CENTER - 150, sd.Y_CENTER - 50, w=300,
                              txt='pmenu_resume')
    pmenu_exit = ui.PushBtn('UI_BTN_PMENU_E', loc.BASELOCALE, sd.X_CENTER - 200, sd.Y_CENTER + 50, w=400,
                            txt='pmenu_exit')
    pausemenu = ui.UIGroup('UIG_PAUSE')
    pausemenu.add_elem(pmenu_txt, pmenu_resume, pmenu_exit)
    dmenu_txt = ui.UIText('UI_TXT_DMENU', loc.BASELOCALE, sd.X_CENTER, sd.Y_CENTER // 2, txt='dmenu_txt',
                          font=ui.FONT_1)
    dmenu_restart = ui.PushBtn('UI_BTN_DMENU_R', loc.BASELOCALE, sd.X_CENTER - 225, sd.Y_CENTER - 50, w=450,
                               txt='dmenu_restart')
    deathmenu = ui.UIGroup('UIG_DEATH')
    deathmenu.add_elem(dmenu_txt, dmenu_restart, pmenu_exit)
    itempck = ui.UIText('UI_TXT_IPCK', None, sd.X_CENTER, 100)
    # itempck.recolor('col_txt', '#d8d8ff')
    bg = graph.ParallaxImage('BG', r'game\scene\BG_Sky.png', tw=sd.Y_SFAC * 1.25, th=sd.Y_SFAC * 1.25)

    def __init__(self, startpos):
        super().__init__()
        self.add_uie(GameScene.pausemenu, GameScene.deathmenu)
        self.get_uie('UIG_PAUSE').get_elem('UI_BTN_PMENU_R').set_func(self.unpause)
        self.add_uie(GameScene.itempck)
        self.add_img(GameScene.bg)
        self.dial_sequences = {}  # 'dialog sequences'
        self.dial = None
        self.player = player.Player(startpos)
        self.trigs, self.items, self.props, self.sclips = (pygame.sprite.Group(), pygame.sprite.Group(),
                                                           pygame.sprite.Group(), pygame.sprite.Group())
        self.enems = pygame.sprite.Group()
        self.pshots = pygame.sprite.Group()
        self.enemshots = pygame.sprite.Group()
        self.enemy = ent.TestEnemy(self.player.coords, 128, 128, self.enems)
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

    # 'adders'

    def add_dsq(self, *dsqs):
        for _ in dsqs:
            self.dial_sequences[f'{_}'] = ui.DialSeq(_)

    def add_ent(self, *kws):  # adds entities to the scene, specifically made for .json initialisation
        for _ in kws:
            # try - except passes entity addition process if there's no "type" given
            try:
                ent_type = _.pop('type')
                # selects entity and group based on the ent_type field
                if ent_type == 'TriggerClip':
                    new_trig = ent.TriggerClip(self.player.coords, **_)
                    try:
                        if _["func"] == "lvl_next" or "lvl_next" in _["func"]:
                            new_trig.set_func(self.holder.lvl_load_next)
                        elif _["func"] == "kill" or "kill" in _["func"]:
                            new_trig.set_func(self.player.death_event)
                        elif "start_dial" in _["func"]:
                            if self.get_dial_by_did(_["func"][1]):
                                new_trig.set_funcdata((self.get_dial_by_did(_["func"][1]),))
                                new_trig.set_func(self.start_dial)
                    except KeyError:
                        print('No func for trigger')
                    self.trigs.add(new_trig)
                elif ent_type == 'DropItem':
                    self.items.add(ent.DropItem(self.player.coords, **_))
                elif ent_type == 'DropWeap':
                    self.items.add(ent.DropWeap(self.player.coords, **_))
                elif ent_type == 'Prop':
                    self.props.add(ent.Prop(self.player.coords, **_))
                elif ent_type == 'SceneCollision':
                    self.sclips.add(ent.SceneCollision(self.player.coords, **_))
                elif ent_type == 'Enemy':
                    self.enems.add(ent.TestEnemy(self.player.coords, **_))
            except KeyError:
                pass

    # pause-unpause

    def pause(self):
        self.set_prior('UIG_PAUSE')

    def unpause(self):
        self.unset_prior()

    # getters

    def get_dial_by_did(self, did):  # gets dialogue from scene's dials using its ID, used in trigger entity setter
        try:
            return list(self.dial_sequences.keys())[did]
        except IndexError:
            return False

    def get_dsq(self, d_id):  # gets dial sequence (from local scope, scene's list) using its dial_id
        # used in start_dial
        try:
            return self.dial_sequences[d_id]
        except KeyError as ke:
            print(f"({ke}) ME: Missing element -- {d_id} not in <current scene>'s dial sequences")

    def start_dial(self, d_id):  # sets scene in dialogue mode and current dial using its dial_id
        self.scene_mode = 2
        self.dial = self.get_dsq(d_id).set(self)

    # operations (render, event parsing etc.)

    def render(self, screen):
        # rendering images
        for _ in self.imghld.values():
            if _.do_render and not _.overlay:
                if isinstance(_, graph.PlayerOffsetImage):
                    _.render(screen, self.player.coords[0], self.player.coords[1])
                else:
                    _.render(screen, self.para_l[0], self.para_l[1])
        # rendering and moving independent sprites
        self.sgroup.draw(screen)
        self.sgroup.update()
        # rendering entity sprites
        self.items.draw(screen)
        self.props.draw(screen)
        self.enems.draw(screen)
        self.pshots.draw(screen)
        self.enemshots.draw(screen)
        # rendering player
        self.player.render(screen)
        # rendering UIEs
        for _ in self.uihld.values():
            if _.do_render:
                _.render(screen, self.holder.clocale, (self.para_l[0], self.para_l[1]))
        # rendering prior UIGroup
        if self.prior_uig:
            screen.blit(graph.DARKEN_IMG, (0, 0))
            self.get_uie(self.prior_uig).render(screen, self.holder.clocale, (self.para_l[0], self.para_l[1]))
        # rendering dial
        if self.dial:
            self.dial.render(screen)
        # rendering debug data
        if self.debug:
            self.trigs.draw(screen)
            player.PlayerClip.PCG.draw(screen)
        # rendering overlay images
        for _ in self.imghld.values():
            if _.do_render and _.overlay:
                if isinstance(_, graph.PlayerOffsetImage):
                    _.render(screen, self.player.coords[0], self.player.coords[1])
                else:
                    _.render(screen, self.para_l[0], self.para_l[1])

    def ui_validator(self, event, click=False):  # ui elements' event processing
        if self.dial:
            self.dial.proc_evt(event, click)
        else:
            super().ui_validator(event, click)

    def proc_evt(self, event, **kwargs):  # regular event processor (when they are)
        self.get_para(event)
        if self.scene_mode == 0:  # regular
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.ui_validator(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui_validator(event, True)
                if not self.prior_uig and not self.player.did_died:
                    self.player.attack_event(self)
            elif event.type == pygame.KEYDOWN:
                self.player.interaction_proc(event)
                if event.key == pygame.K_ESCAPE:
                    if self.prior_uig:
                        self.unset_prior()
                    else:
                        self.pause()
                elif event.key == pygame.K_SPACE:
                    self.player.attack_event(self)
        elif self.scene_mode == 1:  # text prompt capture (override from base scene)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == 13:
                    self.scene_mode = 0
                    self.catcher.catching(event, True)
                else:
                    self.catcher.catching(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.scene_mode = 0
                self.catcher.catching(event, True)
        elif self.scene_mode == 2:  # dialogue mode
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                self.ui_validator(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui_validator(event, True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.dial.update()

    def const_update(self, keys):  # constantly validates and updates things
        if self.scene_mode == 0:
            self.pshots.remove(self.pshots)
            self.player.proc_evt(keys)
            # checks if player died and program hasn't parsed it yet
            if self.player.status == 2 and not self.player.did_died:
                # if player had weapon when died
                if self.player.weap != 0:
                    self.add_ent({'x': self.player.coords[0] + (random() - 0.5) * 64,
                                  'y': self.player.coords[1] + (random() - 0.5) * 64,
                                  'wid': self.player.weap})
                self.set_prior('UIG_DEATH')  # sets the death screen
                self.player.did_died = True  # svidetelstvo o smerti
            # entities parse order
            self.sclips.update(self.player.coords, self)
            self.props.update(self.player.coords, self)
            self.trigs.update(self.player.coords, self)
            self.items.update(self.player.coords, self)
            self.enems.update(self.player.coords, self)
            self.player.interact_request = False

    def save_state(self):  # unused
        pass

    def load_state(self):  # unused
        pass


class SceneHolder:  # main class of the game
    def __init__(self, scene, cloc, cs, clvl, terminatorf=sys.exit):
        self.clocale = cloc
        self.csave = cs
        self.clvl = clvl
        self.defscene = None  # "default scene" (main menu)
        self.scene = None
        self.switch_scene(scene)
        self.fade_timer = 0  # idk it's probably unused
        self.no_event = False
        self.tf = terminatorf

    def render(self, screen):
        if not self.no_event:
            screen.fill('#000000')
        else:
            self.render_fade(screen)
        self.scene.render(screen)

    def render_fade(self, screen):
        if self.fade_timer <= 255:
            screen.blit(graph.FADE_IMG, (0, 0))
            self.fade_timer += 1
        else:
            self.no_event = False

    def funccall(self, name, *args):
        getattr(self.scene, name)(*args)

    def event_parser(self, event):  # processes events if they are
        self.scene.proc_evt(event)

    def const_parser(self, keys):  # processess events constantly (keys in this case)
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
        self.clvl = int(self.clvl)
        self.switch_scene(lvlloader(self.clvl, self, *LVLS))

    def lvl_load_next(self):
        self.clvl = int(self.clvl)
        self.clvl += 1
        db.db_executor(self.csave, self.clvl, 3)
        try:
            self.switch_scene(lvlloader(self.clvl, self, *LVLS))
        except IndexError:
            self.swto_defscene()

    def lvl_load(self, lvlid):
        self.clvl = int(self.clvl)
        self.clvl = lvlid
        db.db_executor(self.csave, self.clvl, 3)
        try:
            self.switch_scene(lvlloader(self.clvl, self, *LVLS))
        except IndexError:
            self.swto_defscene()

    def lvl_load_current(self):
        self.clvl = int(self.clvl)
        try:
            self.switch_scene(lvlloader(self.clvl, self, *LVLS))
        except IndexError:
            self.swto_defscene()
