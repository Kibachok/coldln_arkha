#
# CLA-Locale
#
# localization related things (locale files and locale getter)
#
import loaders as load

BASELOCALE = load.csvloader('locals/basegame.csv')
WLOCALE = load.csvloader('locals/weaps.csv')


def locgetter(loc, key, clang):  # locale getter, gets locale ID and returns the translated text
    # according to current locale
    try:
        return loc[key][clang]
    except KeyError as ke:
        print(f'({ke}) MKW: The keyword is missing in current locale ({loc}), returning it')
    except TypeError as te:
        print(f'({te}) NL: No locale in the UI class, returning locale key')
    return key
