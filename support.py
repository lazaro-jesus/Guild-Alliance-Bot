# import pandas as pd
import sqlite3
from emoji import emojize, demojize
import json

# Leer o crear .json necesarios 
def load_json(file):
    try:
        with open(f"{file}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(f"{file}.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
            return {}

# Configuraciones .json
admins_dict = load_json("admins")
squads_dict = load_json("squads")
settings = load_json("settings")
guilds_tag = load_json("guilds_tag")
blocked_list = load_json("blocked")["block"]

tag = lambda gname: guilds_tag[gname]


class jugador:
    def __init__(self, name, aod, level, pclass, sclass, gname):
        self.aod = 0
        self.name = name
        self.level = level
        self.pclass = pclass
        self.sclass = sclass
        self.gname = tag(gname)
        self.aim(aod)

    def aim(self, aod):
        if self.pclass == ":bow_and_arrow:":
            if self.level > 64:
                x = aod + aod * (0.66 + 0.02 * ((self.level - 65) // 5))
                self.aod = int(x)
            elif self.level > 59:
                x = aod + (aod * 0.62)
                self.aod = int(x)
            elif self.level > 54:
                x = aod + (aod * 0.57)
                self.aod = int(x)
            elif self.level > 49:
                x = aod + (aod * 0.54)
                self.aod = int(x)
            else:
                y = aod + (aod * 0.5)
                self.aod = int(y)

        elif self.sclass == ":bow_and_arrow:":
            if self.level > 59:
                x = aod + (aod * 0.62)
                self.aod = int(x)
            elif self.level > 54:
                x = aod + (aod * 0.57)
                self.aod = int(x)
            elif self.level > 49:
                x = aod + (aod * 0.54)
                self.aod = int(x)
            else:
                y = aod + (aod * 0.5)
                self.aod = int(y)
        else:
            self.aod = aod


class DB:
    def __init__(self):
        pass

    @staticmethod
    def user_registro(message):
        Id = message.from_user.id
        fname = demojize(message.from_user.first_name)
        if message.from_user.username:
            uname = "@" + message.from_user.username
        else:
            uname = fname
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(
            'CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, admin TEXT DEFAULT "NO")')
        punt.execute(
            f'INSERT OR IGNORE INTO Users(id, first_name, username, admin) VALUES("{Id}", "{fname}", "{uname}", "NO")')
        punt.execute(f'UPDATE Users SET first_name = "{fname}", username = "{uname}" WHERE id = "{Id}"')
        conn.commit()
        punt.close()
        conn.close()

    @staticmethod
    def permisos(Id):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(f'UPDATE Users SET admin = "YES" WHERE id = "{Id}"')
        conn.commit()
        punt.close()
        conn.close()

    @staticmethod
    def show_users():
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        user_list = conn.execute(f'SELECT id, username FROM Users').fetchall()
        conn.commit()
        punt.close()
        conn.close()
        msg = [f"{j} - {i}" for i, j in user_list]
        return "\n".join(msg)

    def delete_guild(self, guild):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(f'DROP table IF EXISTS "{guild}"')
        conn.commit()
        punt.close()
        conn.close()

    def roster(self, guild):
        self.delete_guild(guild)
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(
            f'CREATE TABLE IF NOT EXISTS "{guild}"(player TEXT PRIMARY KEY, pclass TEXT, sclass TEXT, level INTEGER, attack INTEGER DEFAULT 0, defence INTEGER DEFAULT 0)')
        conn.commit()
        punt.close()
        conn.close()

    def set_roster(self, guild, player, pclass, sclass, lvl):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(
            f'INSERT OR REPLACE INTO "{guild}" (player, pclass, sclass, level) VALUES ("{player}", "{pclass}", "{sclass}", "{lvl}")')
        conn.commit()
        punt.close()
        conn.close()

    @classmethod
    def delete_rosters(self):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        a = [t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()]
        for i in a:
            if i in blocked_list:
                continue
            self.delete_guild(i)
        conn.commit()
        conn.close()

    def at_df_list(self, guild, aod, match):
        self.aod = aod
        self.guild =  guild
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(f'UPDATE "{guild}" SET "{aod}" = "{match.group("stat")}" WHERE player = "{match.group("player")}"')
        conn.commit()
        punt.close()
        conn.close()

    def sms_stats(self, castle):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        x = [q[0] for q in conn.execute(f'SELECT {self.aod} FROM "{self.guild}" WHERE level > 60').fetchall()]
        y = [w[0] for w in
             conn.execute(f'SELECT {self.aod} FROM "{self.guild}" WHERE level > 40 AND level < 61').fetchall()]
        z = [e[0] for e in
             conn.execute(f'SELECT {self.aod} FROM "{self.guild}" WHERE level > 19 AND level < 41').fetchall()]
        conn.commit()
        punt.close()
        conn.close()
        if self.aod == "attack":
            AD = '⚔Ataque'
        else:
            AD = '🛡Defensa'
        return f'{emojize(castle)}{self.guild}\n{AD} total: {sum(x + y + z)}\n🥇Rango Alto: {sum(x)}\n🥈Rango Medio: {sum(y)}\n🥉Rango Bajo: {sum(z)}'

    @staticmethod
    def guilds_stats():
        sms = "-------Guides Stats-------\n\n"
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        a = [t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()]
        for i in a:
            b = list
            c = list
            if i in blocked_list:
                continue
            b = sum([q[0] for q in conn.execute(f'SELECT attack FROM "{i}"').fetchall()])
            c = sum([q[0] for q in conn.execute(f'SELECT defence FROM "{i}"').fetchall()])
            n = conn.execute(f'SELECT count(*) FROM "{i}"').fetchall()[0][0]
            if b + c != 0:
                sms += emojize(f"{tag(i)}  ⚔{b} | 🛡{c} | :busts_in_silhouette: {n}\n\n")
        return sms

    @staticmethod
    def guilds_stats_rank():
        sms = "-------Guides Stats-------\n\n"
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        a = [t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()]
        for i in a:
            b = list
            c = list
            if i in blocked_list:
                continue
            ha = [q[0] for q in conn.execute(f'SELECT attack FROM "{i}" WHERE level > 60').fetchall()]
            ma = [q[0] for q in conn.execute(f'SELECT attack FROM "{i}" WHERE level > 40 AND level < 61').fetchall()]
            la = [q[0] for q in conn.execute(f'SELECT attack FROM "{i}" WHERE level > 19 AND level < 41').fetchall()]
            hd = [q[0] for q in conn.execute(f'SELECT defence FROM "{i}" WHERE level > 60').fetchall()]
            md = [q[0] for q in conn.execute(f'SELECT defence FROM "{i}" WHERE level > 40 AND level < 61').fetchall()]
            ld = [q[0] for q in conn.execute(f'SELECT defence FROM "{i}" WHERE level > 19 AND level < 41').fetchall()]

            n = len(ha+ma+la)
            if sum(ha+ma+la+hd+md+ld) != 0:
                sms += emojize(f"""{tag(i)}  ⚔{sum(ha+ma+la)} | 🛡{sum(hd+md+ld)} | :busts_in_silhouette: {n}
--H--> ⚔{sum(ha)} | 🛡{sum(hd)} | :busts_in_silhouette: {len(ha)}
--M--> ⚔{sum(ma)} | 🛡{sum(md)} | :busts_in_silhouette: {len(ma)}
--L--> ⚔{sum(la)} | 🛡{sum(ld)} | :busts_in_silhouette: {len(la)}\n\n""")
        
        return sms

    @staticmethod
    def ga_stats(aod):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        low, mid, high = 0, 0, 0
        a = [t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()]
        for i in a:
            if i in blocked_list:
                continue
            high += sum([q[0] for q in conn.execute(f'SELECT {aod} FROM "{i}" WHERE level > 60').fetchall()])
            mid += sum([w[0] for w in conn.execute(f'SELECT {aod} FROM "{i}" WHERE level > 40 AND level < 61').fetchall()])
            low += sum([e[0] for e in conn.execute(f'SELECT {aod} FROM "{i}" WHERE level > 19 AND level < 41').fetchall()])
        conn.commit()
        punt.close()
        conn.close()
        if aod == "attack":
            AD = '⚔Ataque'
        else:
            AD = '🛡Defensa'
        return emojize(f'''{AD} total: {low + mid + high}
:1st_place_medal:Rango Alto: {high}
:2nd_place_medal:Rango Medio: {mid}
:3rd_place_medal:Rango Bajo: {low}''')


    @staticmethod
    def ga_stats_group(aod, group):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        low, mid, high = 0, 0, 0
        for i in guilds_tag.items():
            if i[1][1:-1] in group:
                high += sum([q[0] for q in conn.execute(f'SELECT {aod} FROM "{i[0]}" WHERE level > 60').fetchall()])
                mid += sum([w[0] for w in conn.execute(f'SELECT {aod} FROM "{i[0]}" WHERE level > 40 AND level < 61').fetchall()])
                low += sum([e[0] for e in conn.execute(f'SELECT {aod} FROM "{i[0]}" WHERE level > 19 AND level < 41').fetchall()])
        conn.commit()
        punt.close()
        conn.close()
        if aod == "attack":
            AD = '⚔Ataque'
        else:
            AD = '🛡Defensa'
        return emojize(f'''{AD} total: {low + mid + high}
:1st_place_medal:Rango Alto: {high}
:2nd_place_medal:Rango Medio: {mid}
:3rd_place_medal:Rango Bajo: {low}''')

    @staticmethod
    def ga_sclass(min, max):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        sms, AD = "", ''
        count = [0, 0, 0, 0, 0, 0]
        a = [t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()]

        if min == 60:
            rag = f'{emojize(":1st_place_medal:")}Rango Alto'
        elif min == 40:
            rag = f'{emojize(":2nd_place_medal:")}Rango Medio'
        else:
            rag = f'{emojize(":3rd_place_medal:")}Rango Bajo'
        sms += f'{rag}\n'

        for aod in ['attack', 'defence']:
            b, c, d, e, f, g, h, o = [], [], [], [], [], [], [], []
            if aod == "attack":
                AD = 'Ataque'  
            else:
                AD = 'Defensa'
            sms += f'{AD} total: '

            for i in a:
                if i in blocked_list:
                    continue
                b += [q[0] for q in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":crossed_swords:" AND level > "{min}" AND level < "{max}"').fetchall()]
                c += [w[0] for w in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":bow_and_arrow:" AND level > "{min}" AND level < "{max}"').fetchall()]
                d += [h[0] for h in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":shield:" AND level > "{min}" AND level < "{max}"').fetchall()]
                e += [j[0] for j in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":package:" AND level > "{min}" AND level < "{max}"').fetchall()]
                f += [k[0] for k in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":alembic:" AND level > "{min}" AND level < "{max}"').fetchall()]
                g += [l[0] for l in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":hammer_and_pick:" AND level > "{min}" AND level < "{max}"').fetchall()]
                h += [m[0] for m in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":drop_of_blood:" AND level > "{min}" AND level < "{max}"').fetchall()]
                o += [n[0] for n in conn.execute(
                    f'SELECT {aod} FROM "{i}" WHERE pclass = ":top_hat:" AND level > "{min}" AND level < "{max}"').fetchall()]

            sms += (f'''{sum(b + c + d + e + f + g + h)}
{emojize(":crossed_swords:")}: {sum(b)}
{emojize(":bow_and_arrow:")}: {sum(c)}
{emojize(":shield:")}: {sum(d)}
{emojize(":package:")}: {sum(e)}
{emojize(":alembic:")}: {sum(f)}
{emojize(":hammer_and_pick:")}: {sum(g)}
{emojize(":drop_of_blood:")}: {sum(h)}
{emojize(":top_hat:")}: {sum(o)}\n''')
        sms += '\n'
        conn.commit()
        punt.close()
        conn.close()
        return sms

    @staticmethod
    def ga_top(aod):
        d = []
        if aod == "attack":
            e = "⚔"
        else:
            e = "🛡"
        sms = f'🏆<b>TOP {aod.upper()}</b>🏆\n\n{emojize(":1st_place_medal:")}<b>RANGO ALTO</b>\n'
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        a = [t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type = "table"').fetchall()]
        for i in a:
            if i in blocked_list: 
                continue
            b = conn.execute(f'SELECT player, {aod}, level, pclass, sclass FROM "{i}"').fetchall()
            conn.commit()
            for j in b:
                d.append(jugador(j[0], j[1], j[2], j[3], j[4], i))
        punt.close()
        conn.close()
        c1, c2, c3 = 0, 0, 0
        c = sorted(d, key=lambda d: d.aod, reverse=True)
        for k in range(len(c)):
            if c[k].level > 60 and c1 < 5:
                sms += f'{emojize(c[k].pclass)}{c[k].level} {c[k].gname}{c[k].name} {e}{c[k].aod}\n'
                c1 += 1
        sms += f'\n{emojize(":2nd_place_medal:")}<b>RANGO MEDIO</b>\n'
        for k in range(len(c)):
            if 61 > c[k].level > 40 and c2 < 5:
                sms += f'{emojize(c[k].pclass)}{c[k].level} {c[k].gname}{c[k].name} {e}{c[k].aod}\n'
                c2 += 1
        sms += f'\n{emojize(":3rd_place_medal:")}<b>RANGO BAJO</b>\n'
        for k in range(len(c)):
            if 19 < c[k].level < 41 and c3 < 5:
                sms += f'{emojize(c[k].pclass)}{c[k].level} {c[k].gname}{c[k].name} {e}{c[k].aod}\n'
                c3 += 1
        return sms


    def save_loc(self, code, name, level, time):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(
            f'CREATE TABLE IF NOT EXISTS Locations (code TEXT PRIMARY KEY, name TEXT, level INTEGER, time REAL, owner TEXT, produce TEXT DEFAULT "NO", upda TEXT DEFAULT "NO")')
        punt.execute(f'DELETE FROM Locations WHERE "{time}" - time > 999999')
        if not conn.execute(f'SELECT * FROM Locations WHERE code = "{code}"').fetchall():
            punt.execute(
                f'INSERT INTO Locations VALUES ("{code}", "{name}", "{level}", "{time}", "unknown", "NO", "NO")')
            conn.commit()
            punt.close()
            conn.close()
            return 1
        else:
            conn.commit()
            punt.close()
            conn.close()
            return 0

    def save_hq(self, code, name, time):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(
            f'CREATE TABLE IF NOT EXISTS Headquarters (code TEXT PRIMARY KEY, name TEXT, active TEXT DEFAULT "YES")')
        try:
            punt.execute(f'DELETE FROM Locations WHERE "{time}" - time > 999999')
        except sqlite3.OperationalError:
            pass
        if not conn.execute(f'SELECT * FROM Headquarters WHERE code = "{code}"').fetchall():
            punt.execute(f'INSERT INTO Headquarters VALUES ("{code}", "{name}", "YES")')
            conn.commit()
            punt.close()
            conn.close()
            return 1
        else:
            conn.commit()
            punt.close()
            conn.close()
            return 0

    @staticmethod
    def show_map(time, lista=None):
        sms = ''
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        X = conn.execute(f'SELECT name, level, code, time, upda FROM Locations ORDER BY "level"').fetchall()
        for i in range(len(X)):
            exst = ''
            if time - X[i][3] < 86400:
                exst = emojize(':sparkles:')
            elif time - X[i][3] > 320400 and X[i][4] == "NO":
                exst = emojize(':cross_mark:')
            if lista != None:
                if i + 1 in lista:
                    sms += f'''{X[i][0]} lvl.{X[i][1]}{exst}
<a href ="http://t.me/share/url?url=/ga_atk_{X[i][2]}">⚔</a>     <a href ="http://t.me/share/url?url=/ga_def_{X[i][2]}">🛡</a>     <a href ="http://t.me/share/url?url=/delete_loc%20{X[i][2]}">🚫</a>\n\n'''
            else:
                sms += f'''{i + 1}.  {X[i][0]} lvl.{X[i][1]}{exst}
     <a href ="http://t.me/share/url?url=/ga_atk_{X[i][2]}">⚔</a>     <a href ="http://t.me/share/url?url=/ga_def_{X[i][2]}">🛡</a>     <a href ="http://t.me/share/url?url=/delete_loc%20{X[i][2]}">🚫</a>\n\n'''
        conn.commit()
        punt.close()
        conn.close()
        return sms

    @staticmethod
    def show_hq():
        sms = ''
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        x = conn.execute(f'SELECT name, code FROM Headquarters WHERE active = "YES" ORDER BY "name" ASC').fetchall()
        for quater in x:
            y = conn.execute(
                f'SELECT name, level, produce, upda FROM Locations WHERE owner = "{quater[0]}" ORDER BY "level"').fetchall()
            sms += f'<a href ="http://t.me/share/url?url=/ga_atk_{quater[1]}">{quater[0]}\n</a>'
            if y:
                for loc in y:
                    if loc[3] == "NO":
                        produce = emojize(':cross_mark:')
                    elif loc[2] == "YES":
                        produce = emojize(':gem_stone:')
                    else:
                        produce = emojize(':stopwatch:')
                    sms += f'{loc[0]} lvl. {loc[1]} {produce}\n'
            sms += '\n'
        conn.commit()
        punt.close()
        conn.close()
        return sms

    @staticmethod
    def delete_all_loc():
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute('DROP table IF EXISTS "Locations"')
        conn.commit()
        punt.close()
        conn.close()

    @staticmethod
    def delete_location(code):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(f'DELETE FROM Locations WHERE code = "{code}"')
        conn.commit()
        punt.close()
        conn.close()

    @staticmethod
    def active_on_off(name, active):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(f'UPDATE Headquarters SET active = "{active}" WHERE name = "{name}"')
        conn.commit()
        punt.close()
        conn.close()

    def state_map(self, name, level, owner=None, produce=None):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        if conn.execute(
                f'SELECT name, level FROM Locations WHERE name = "{name}" AND level = "{level}"').fetchall():
            if produce == "NO":
                punt.execute(
                    f'UPDATE Locations SET owner = "{owner}", produce = "NO", upda = "YES" WHERE name = "{name}" AND level = "{level}"')
            else:
                punt.execute(
                    f'UPDATE Locations SET produce = "YES", upda = "YES" WHERE name = "{name}" AND level = "{level}"')
            conn.commit()
            punt.close()
            conn.close()

    def restart_upda(self):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.execute(f'UPDATE Locations SET upda = "NO"')
        conn.commit()
        punt.close()
        conn.close()

    # Cambiar a pandas
    def profile(ID, fname, uname, match, t_update):
        conn = sqlite3.connect("data_base.db")
        punt = conn.cursor()
        punt.executescript('''CREATE TABLE IF NOT EXISTS Profiles(
            ID INTEGER PRIMARY KEY, fname TEXT, uname TEXT,  
            castle TEXT, g_emoji TEXT, guild TEXT, name TEXT, class TEXT,
            level INTEGER, attack INTEGER, defence INTEGER,
            exp_current INTEGER, exp_needed INTEGER, hp INTEGER, hp_max INTEGER,
            stamina_current INTEGER, stamina_max INTEGER, time_remaining INTEGER,
            mana INTEGER, mana_max INTEGER, gold INTEGER, pouch INTEGER, gem INTEGER,
            eq_attack INTEGER DEFAULT 0, eq_defence INTEGER DEFAULT 0, bag_current INTEGER DEFAULT 0,
            pet TEXT, pet_level INTEGER, state TEXT, last_update REAL
            )''')
        punt.executescript(f'''INSERT OR REPLACE INTO Profiles VALUES("{ID}", "{demojize(fname)}", "{uname}",
        "{demojize(match.group(1))}", "{match.group(2)}", "{match.group(3)}", "{match.group(4)}", "{match.group(5)}",
        "{match.group(6)}", "{match.group(7)}", "{match.group(8)}", "{match.group(9)}", "{match.group(10)}",
        "{match.group(11)}", "{match.group(12)}", "{match.group(13)}", "{match.group(14)}", "{match.group(15)}",
        "{match.group(16)}", "{match.group(17)}", "{match.group(18)}", "{match.group(19)}", "{match.group(20)}",
        "{match.group(21)}", "{match.group(22)}", "{match.group(23)}", "{match.group(24)}", "{match.group(25)}", 
        "{demojize(match.group(26))}", "{t_update}")''')
        conn.commit()
        punt.close()
        conn.close()

    @staticmethod
    def show_guild(name):
        boolean = False
        for key, value in guilds_tag:
            if name == key:
                boolean = True
                break
            elif name == value:
                boolean = True
                name = key
        if not boolean:
            return "No Encontrado"
