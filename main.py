# DEMO WIP Build of game with basic game structure
#
# used to init the game
#
import cla_core.screendata as sd
import cla_core.pg_init as pg
import loaders as load
import database as db
import cla_core.locale as loc
import cla_core.s_graphics as graph
import cla_core.structure as struct
import cla_core.ui as ui
import pygame  # so-called piece of 'engine'


# \/ \/ \/ global used commands


# UPPERCASE = global used variable
# global used/required commands
pygame.mixer.init()

LVLS = load.lvlsreader()
WEAPS = load.weapreader()

LOCALES = ['en', 'ru']
CLOCALE = 'en'

pygame.mixer.music.set_volume(0.5)


print('Current scalefactors:', sd.X_SFAC, sd.Y_SFAC)
screen = pg.screen

FONT_2 = pygame.font.SysFont('comicsansms', int(sd.X_SFAC * 15))
FONT_2.set_bold(True)
FONT_3 = pygame.font.Font(None, int(sd.X_SFAC * 30))

pygame.display.set_caption("ColdLine Arkhangelsk")
pygame.display.set_icon(pygame.image.load(r"doomkisser_V2_s.png"))

STARTUP_CONF = load.csvloader('startupconfig.csv')
try:
    C_SAVE = STARTUP_CONF['last_save']['value']
except KeyError:
    C_SAVE = None
try:
    C_LVL = STARTUP_CONF['last_lvl']['value']
except KeyError:
    C_LVL = 0


def mmenu_imgs_init():
    clachr_size = 1024 * sd.Y_SFAC
    mmenuimg_0 = graph.ParallaxImage('MMENUIMG_0', r'mmenu\CLA_MM_BG_0.png', 0, 0, sd.Y_SFAC / 2 + 0.025,
                                     sd.Y_SFAC / 2 + 0.025)
    mmenuimg_1 = graph.ParallaxImage('MMENUIMG_1', r'mmenu\CLA_MM_BG_1.png', 0, 0, sd.Y_SFAC / 2, sd.Y_SFAC / 2,
                                     do_render=False)
    clachr = graph.ParallaxImage('CLA_CHR', r'mmenu\CLA_Chr__0003s_0004_HD_Obvod.png', sd.X_CENTER - clachr_size / 2,
                                 sd.SCREENRES.current_h - clachr_size + 50, sd.Y_SFAC / 2, sd.Y_SFAC / 2, 1.5,
                                 colorkey=-2)
    clachr_g = graph.ParallaxImage('CLA_CHR_G', r'mmenu\CLA_Chr__0003s_0001_HD_GS_Zakras.png', sd.X_CENTER - clachr_size
                                   / 2, sd.SCREENRES.current_h - clachr_size + 50, sd.Y_SFAC / 2, sd.Y_SFAC / 2, 1.5,
                                   colorkey=-2, do_render=False)
    clachr_bld = graph.ParallaxImage('CLA_CHR_BLD ', r'mmenu\CLA_Chr__0003s_0002_BLD.png', sd.X_CENTER - clachr_size
                                     / 2, sd.SCREENRES.current_h - clachr_size + 50, sd.Y_SFAC / 2, sd.Y_SFAC / 2, 1.5,
                                     colorkey=-2)
    clachr_col = graph.ParallaxImage('CLA_CHR_COL', r'mmenu\CLA_Chr__0003s_0003_HD_ColOL.png', sd.X_CENTER - clachr_size
                                     / 2, sd.SCREENRES.current_h - clachr_size + 50, sd.Y_SFAC / 2, sd.Y_SFAC / 2, 1.5,
                                     colorkey=-2)
    clachr_gno = graph.ParallaxImage('CLA_CHR_GNO', r'mmenu\CLA_Chr__0003s_0000_gno.png', sd.X_CENTER - 512 - 256 - 128,
                                     sd.SCREENRES.current_h - 512 - 256, 0.8, 0.8, 4, colorkey=-2)
    ttle = graph.ParallaxImage('TITLE', r'mmenu\CLA_Txt_0.png', sd.X_CENTER - 1024 * sd.Y_SFAC, 0, sd.Y_SFAC / 2,
                               sd.Y_SFAC / 2, 2.5, colorkey=-2)
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
    mmenu = struct.BaseScene()  # wip (subject to be properly organized probably)
    mmenu.add_img(*mmenu_imgs_init())  # wip (subject to be properly organized probably)
    # exit game button setup
    killgamebtn = ui.PushBtn('UI_BTN_KILLGAME', loc.BASELOCALE, x=sd.X_CENTER - 100, y=sd.Y_CENTER + 256,
                             txt="mmenu_killgame")
    killgamebtn.set_func(game_destroyer)
    # saveload window button setup
    savebtn = ui.PushBtn('UI_BTN_SAVELOAD', loc.BASELOCALE, w=450, x=sd.X_CENTER - 225, y=sd.Y_CENTER + 28,
                         txt="mmenu_saveloadgame")
    savebtn.set_func(mmenu_group_switch)
    sgbtn = ui.PushBtn('UI_BTN_STARTGAME', loc.BASELOCALE, w=450, x=sd.X_CENTER - 225, y=sd.Y_CENTER - 72,
                       txt="mmenu_startgame")
    sgbtn.set_func(mmenu_sgame_g_switch)
    version = ui.UIText('UI_TXT_VER', loc.BASELOCALE, x=sd.X_CENTER, y=sd.SCREENRES.current_h - 50, txt='cla_c_ver',
                        font=ui.FONT_1)
    version.recolor('col_txt', '#9D9DAF')
    locbtn = ui.PushBtn('UI_BTN_LOC', loc.BASELOCALE, w=50, x=sd.SCREENRES.current_w - 75,
                        y=sd.SCREENRES.current_h - 75, txt='mmenu_loc')
    expbtn = ui.PushBtn('UI_BTN_EXP', False, w=50, x=25, y=sd.SCREENRES.current_h - 75, txt='i')
    locbtn.set_func(mmenu_locsw)
    expbtn.set_func(mmenu_expnote_switch)
    mmenu.add_uie(killgamebtn, savebtn, sgbtn, locbtn, expbtn, ui.SaveloadMenu('UIG_SL'), mmenu_sgame_group_init(),
                  mmenu_claexp_init(), version)
    mmenu.set_music('dymyat_molcha.mp3')
    for _ in range(10):
        mmenu.add_s(graph.SnowflakeSprite)
    return mmenu


def mmenu_sgame_group_init():
    sgtxt = ui.UIText('UI_NGAME_TXT', loc.BASELOCALE, x=sd.X_CENTER, y=sd.Y_CENTER - 100, txt='mmenu_sgame_n',
                      font=ui.FONT_1)
    sgtxt_e = ui.UIText('UI_NGAME_E', loc.BASELOCALE, x=sd.X_CENTER, y=sd.Y_CENTER - 25, txt='n', font=ui.FONT_1)
    sgtxt_e.recolor('col_txt', 'red')
    sgtxt.recolor('col_txt', '#FFFFFF')
    sgprpt = ui.TextPrompt('UI_NGAME_PRPT', h=50, w=250, x=sd.X_CENTER - 125, y=sd.Y_CENTER)
    sgrp = ui.UIGroup('UIG_SGAME')
    sgbtn = ui.PushBtn('UI_SGAME_BTN', loc.BASELOCALE, h=50, w=250, x=sd.X_CENTER - 125, y=sd.Y_CENTER + 60,
                       txt='mmenu_sgame_s')
    sgbtn.set_func(mmenu_sgame)
    sgrp.add_elem(sgtxt, sgprpt, sgbtn, sgtxt_e)
    return sgrp


def mmenu_claexp_init():
    txt_t = ui.UIText('UI_CE_T', loc.BASELOCALE, x=sd.X_CENTER, y=160, txt='cla_exp_t', font=FONT_3)
    txt_t.recolor('col_txt', '#BFBFFF')
    txt_0 = ui.UIText('UI_CE_0', loc.BASELOCALE, x=sd.X_CENTER, y=220, txt='cla_exp_0', font=FONT_2)
    txt_0.recolor('col_txt', '#BFBFFF')
    txt_1 = ui.UIText('UI_CE_1', loc.BASELOCALE, x=sd.X_CENTER, y=255, txt='cla_exp_1', font=FONT_2)
    txt_1.recolor('col_txt', '#BFBFFF')
    txt_2 = ui.UIText('UI_CE_2', loc.BASELOCALE, x=sd.X_CENTER, y=300, txt='cla_exp_2', font=FONT_2)
    txt_2.recolor('col_txt', '#BFBFFF')
    txt_3 = ui.UIText('UI_CE_3', loc.BASELOCALE, x=sd.X_CENTER, y=350, txt='cla_exp_3', font=FONT_3)
    txt_3.recolor('col_txt', '#BFBFFF')
    txt_4 = ui.UIText('UI_CE_4', loc.BASELOCALE, x=sd.X_CENTER, y=390, txt='cla_exp_4', font=FONT_2)
    txt_4.recolor('col_txt', '#BFBFFF')
    txt_5 = ui.UIText('UI_CE_5', loc.BASELOCALE, x=sd.X_CENTER, y=420, txt='cla_exp_5', font=FONT_2)
    txt_5.recolor('col_txt', '#BFBFFF')
    txt_6 = ui.UIText('UI_CE_6', loc.BASELOCALE, x=sd.X_CENTER, y=450, txt='cla_exp_6', font=FONT_2)
    txt_6.recolor('col_txt', '#BFBFFF')
    txt_7 = ui.UIText('UI_CE_7', loc.BASELOCALE, x=sd.X_CENTER, y=480, txt='cla_exp_7', font=FONT_2)
    txt_7.recolor('col_txt', '#BFBFFF')
    txt_8 = ui.UIText('UI_CE_8', loc.BASELOCALE, x=sd.X_CENTER, y=510, txt='cla_exp_8', font=FONT_2)
    txt_8.recolor('col_txt', '#BFBFFF')
    txt_9 = ui.UIText('UI_CE_9', loc.BASELOCALE, x=sd.X_CENTER, y=560, txt='cla_exp_9', font=FONT_2)
    txt_9.recolor('col_txt', '#BFBFFF')
    txt_10 = ui.UIText('UI_CE_10', loc.BASELOCALE, x=sd.X_CENTER, y=590, txt='cla_exp_10', font=FONT_2)
    txt_10.recolor('col_txt', '#BFBFFF')
    txt_11 = ui.UIText('UI_CE_11', loc.BASELOCALE, x=sd.X_CENTER - 50, y=750, txt='cla_exp_11', font=FONT_2)
    txt_11.recolor('col_txt', '#BFBFFF')
    txt_12 = ui.UIText('UI_CE_12', loc.BASELOCALE, x=sd.X_CENTER, y=780, txt='cla_exp_12', font=FONT_2)
    txt_12.recolor('col_txt', '#BFBFFF')
    txt_13 = ui.UIText('UI_CE_13', loc.BASELOCALE, x=sd.X_CENTER, y=900, txt='cla_exp_13', font=FONT_2)
    txt_13.recolor('col_txt', '#BFBFFF')
    txt_14 = ui.UIText('UI_CE_14', loc.BASELOCALE, x=sd.X_CENTER, y=930, txt='cla_exp_14', font=FONT_2)
    txt_14.recolor('col_txt', '#BFBFFF')
    txt_15 = ui.UIText('UI_CE_15', loc.BASELOCALE, x=sd.X_CENTER, y=960, txt='cla_exp_15', font=FONT_2)
    txt_15.recolor('col_txt', '#BFBFFF')
    grp = ui.UIGroup('UIG_CLAEXP')
    grp.add_elem(txt_t, txt_0, txt_1, txt_2, txt_3, txt_4, txt_5, txt_6, txt_7, txt_8, txt_9, txt_10, txt_11, txt_12,
                 txt_13, txt_14, txt_15)
    return grp


def game_destroyer(log='Terminated manually'):
    global GAME_RUNNING
    GAME_RUNNING = False
    print(log)


def mmenu_group_switch():  # saveload window switch / переключатель меню загрузки
    mainmenu.set_prior(mainmenu.get_uie('UIG_SL').name)


def mmenu_expnote_switch():  # explanote switch: turns it on / переключатель пояснительной записки
    mainmenu.set_prior(mainmenu.get_uie('UIG_CLAEXP').name)


def mmenu_sgame_g_switch():  # new game window switch / переключатель меню создания игры
    mainmenu.set_prior(mainmenu.get_uie('UIG_SGAME').name)


def mmenu_sgame():  # new game creation / создание новой игры из главменю
    sname = mainmenu.get_prior().get_elem('UI_NGAME_PRPT').take_txt()
    if sname.strip():  # check if there's just anything in prompt, except for spaces
        # / проверка введено ли вообще что-либо кроме пробелов
        msg = db.db_executor(sceneslot.csave, sceneslot.clvl, 0, sname.lower())
        if msg:  # if db call returns anything - it's an error
            # бд вызов возвращает либо ошибку либо None
            mainmenu.get_prior().get_elem('UI_NGAME_E').set_txt(msg)
        else:
            # operational work / нормальная отработка
            mainmenu.get_prior().get_elem('UI_NGAME_E').set_txt('n')
            sceneslot.csave = sname.lower()
            sceneslot.clvl = 0
            sceneslot.lvl_load_current()
    else:  # if there's nothing / если ничего не введено
        mainmenu.get_prior().get_elem('UI_NGAME_E').set_txt('mmenu_sgame_e_e')


def mmenu_locsw():  # locale switcher / переключатель языка
    global sceneslot
    sceneslot.clocale = LOCALES[(LOCALES.index(sceneslot.clocale) + 1) % len(LOCALES)]


if __name__ == '__main__':
    GAME_RUNNING = True
    mainmenu = mmenu_obj_init()
    sceneslot = struct.SceneHolder(mainmenu, CLOCALE, C_SAVE, C_LVL)
    sceneslot.set_defscene(mainmenu)
    while GAME_RUNNING:
        sceneslot.const_parser(pygame.key.get_pressed())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_RUNNING = False
            else:
                sceneslot.event_parser(event)
        sceneslot.render(screen)
        pygame.display.flip()
