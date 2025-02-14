#
# CLA-DB
#
# database interactions
#
import sqlite3


DB = sqlite3.connect(r'savedata\savedata.sqlite3')


def db_executor(csave, clvl, exectype, *data):  # type - type of SQL request; 0 = new game, 1 = get games,
    # 2 = delete save, 3 = change save's level, 4 = load save
    cs = DB.cursor()
    if exectype == 0:
        if cs.execute('''SELECT savename FROM saves WHERE savename=?''', (*data, )).fetchall():
            return 'mmenu_sgame_e_ae'
        try:
            cs.execute('''INSERT INTO saves(savename, lvl) VALUES(?, 0)''', (*data, )).fetchall()
            DB.commit()
            return
        except sqlite3.OperationalError:
            return 'mmenu_sgame_e_ws'
    elif exectype == 1:
        try:
            return cs.execute('''SELECT savename FROM saves''').fetchall()
        except sqlite3.OperationalError:
            return False
    elif exectype == 2:
        try:
            cs.execute('''DELETE FROM saves WHERE savename=?''', (*data, )).fetchall()
            DB.commit()
            return
        except sqlite3.OperationalError:
            return False
    elif exectype == 3:
        try:
            cs.execute('''UPDATE saves
                            SET lvl=?
                            WHERE savename=?''', (clvl, csave)).fetchall()
        except sqlite3.OperationalError:
            cs.execute('''INSERT INTO saves(savename, lvl) VALUES(?, ?)''', (clvl, csave)).fetchall()
        DB.commit()
    elif exectype == 4:
        csave, clvl = cs.execute('''SELECT savename, lvl FROM saves WHERE savename=?''', (*data, )).fetchall(
        )[0]
        return csave, int(clvl)
