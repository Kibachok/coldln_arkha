#
# CLA-Audio
#
# all game's sounds and player function with validation of audio's existence
#
import loaders as load


UI_CLICK = load.audloader(r"ui\button_click.wav")  # peaceding from tarkov
UI_ESCAPE = load.audloader(r"ui\menu_escape.wav")  # peaceding from tarkov
WEAP_PICKUP = load.audloader(r"ui\weap_pickup.wav")  # peaceding from tarkov
DEATH_SND = load.audloader(r"ui\death.wav")  # peaceding from hl2
WALK = [load.audloader(r"game\walk_0.wav"), load.audloader(r"gamedata\aud\game\walk_1.wav"),
        load.audloader(r"game\walk_2.wav")]  # peaceding from tarkov
BUCKSHOT_SHOOT = load.audloader(r"game\weap\weap_1_atc.ogg")  # peaceding from tarkov
BUCKSHOT_RELOAD = load.audloader(r"game\weap\weap_1_rld.wav")  # peaceding from gayturned


AUDIOS = {
    'UI_CLICK': UI_CLICK,
    'UI_ESCAPE': UI_ESCAPE,
    'WEAP_PICKUP': WEAP_PICKUP,
    'DEATH_SND': DEATH_SND,
    'WALK': WALK,
    'BUCKSHOT_SHOOT': BUCKSHOT_SHOOT,
    'BUCKSHOT_RELOAD': BUCKSHOT_RELOAD
}


def aud_play(audio):
    if audio:
        if isinstance(audio, str):
            try:
                AUDIOS[audio].play()
            except KeyError:
                pass
        else:
            try:
                audio.play()
            except AttributeError:
                pass
