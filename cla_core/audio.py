#
# CLA-Audio
#
# all game's sounds and player function with validation of audio's existence
#
from pygame import mixer

import loaders as load


mixer.init()


UI_CLICK = load.audloader(r"ui\button_click.wav")  # peaceding from tarkov
UI_ESCAPE = load.audloader(r"ui\menu_escape.wav")  # peaceding from tarkov
WEAP_PICKUP = load.audloader(r"ui\weap_pickup.wav")  # peaceding from tarkov
DEATH_SND = load.audloader(r"ui\death.wav")  # peaceding from hl2
WALK = [load.audloader(r"game\walk_0.wav"), load.audloader(r"gamedata\aud\game\walk_1.wav"),
        load.audloader(r"game\walk_2.wav")]  # peaceding from tarkov
W1_SHOOT = load.audloader(r"game\weap\weap_1_atc.ogg")  # peaceding from tarkov


def aud_play(audio):
    if audio:
        audio.play()
