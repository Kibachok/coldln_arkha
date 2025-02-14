#
# CLA_Loaders
#
# all the external file loaders for the game
#
import os
import csv
from pygame import image, mixer
import json


def audloader(localpathname):
    fullpathname = os.path.join(r'gamedata\aud', localpathname)
    # validates if it's here
    if not os.path.isfile(fullpathname):
        print(f'Path -- {fullpathname} audio not found)')
        return
    return mixer.Sound(fullpathname)


def csvloader(namepath):  # reads CSV as a dict and formats it in right way, used for locales and startup config
    # right-way format: <first column of current row's value as a dict>: <other columns of this row>,
    # for example: 'lvl_0_0': {'imseq': [0, 0, 0, 1, 1, 2]} from 'd_id': 'lvl_0_0', 'imseq': [0, 0, 0, 1, 1, 2]
    fullpathname = os.path.join(r'gamedata', namepath)
    if not os.path.isfile(fullpathname):
        print(f'Path -- {fullpathname} CSV not found')
        return None
    with open(fullpathname, mode='r', encoding='utf-8', newline='') as read:
        csvd = csv.DictReader(read, delimiter=';', quotechar='"')
        tfcsvd = {list(_.values())[0]: dict(list(_.items())[1:]) for _ in csvd}
    return tfcsvd


def imgloader(localpathname, colorkey=None):  # convenient func to load image already from gamedata\img
    # with validation of its existence and colorkey support
    fullpathname = os.path.join(r'gamedata\img', localpathname)
    # validates if it's here
    if not os.path.isfile(fullpathname):
        print(f'Path -- {fullpathname} image not found)')
        # otherwise returns doomkisser
        return image.load(r'doomkisser_V2_s.png')
    img = image.load(fullpathname)
    # colorkey
    if colorkey is not None and not -2:
        img = img.convert()
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)
    else:
        img = img.convert_alpha()
    return img


def lvlsreader():  # reads all the level jsons from levels folder, used only once as the game starts
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
    return lvls


def weapreader():  # reads weapons config
    weaps = []
    with open(r'gamedata\weaps.json') as wc:
        tmp = json.load(wc)
        try:
            for _ in tmp:
                weaps.append(_)
        except json.decoder.JSONDecodeError:
            print(f'Failed to read weap config')
    print(*weaps, sep='\n')
    return weaps


def dials_imgcat():
    return os.listdir(os.path.join(r'gamedata\img\game\dial'))
