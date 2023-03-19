# -*- coding: utf-8 -*-
import logging
from time import time

import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from regexp import *
from support import *


TOKEN = "YOUR TOKEN"

bot = telebot.TeleBot(TOKEN, parse_mode=None)
telebot.apihelper.RETRY_ON_ERROR = True

CWB2 = 408101137


def send_msg(id, text, reply_m=None, parse_m=None):
    try:
        bot.send_message(id, text, reply_markup = reply_m, parse_mode = parse_m)
    except Exception as e:
       logging.exception(e)
       send_msg(id, text, parse_m = parse_m, reply_m = reply_m)


def forward_msg(chat_id, mci, msg_id):
    try:
        bot.forward_message(chat_id, mci, msg_id)
    except Exception as e:
        logging.exception(e)
        forward_msg(chat_id, mci, msg_id)


def delete_msg(mci: int, msg_id: int):
    try:
        bot.delete_message(mci, msg_id)
    except ApiTelegramException as e:
        logging.exception(e)
        return
    except Exception as e:
        logging.exception(e)
        delete_msg(mci ,msg_id)


def class_sms(message: Message, DB: DB, resp="", cont=0, val=False):
    mci = message.chat.id

    if re_map.search(message.text):
        DB.restart_upda()
        xmap = ""

        for match in iter_re_map_protected.finditer(message.text):
            DB.state_map(match.group('name'), int(match.group('level')), produce = "YES")
            if match.group('wasattack') is None:
                xmap += emojize(':sleeping_face:')
            else:
                if match.group('quality') == 'closely protected':
                    xmap += emojize(':trident_emblem:')
                elif match.group('quality') == 'easily protected':
                    xmap += emojize(':OK_hand:')
                else:
                    xmap += emojize(':shield:')
            xmap += f" {match.group('name')} lvl.{match.group('level')}\n"
        xmap += "\n"

        for match2 in iter_re_map_belongs.finditer(message.text):
            DB.state_map(match2.group('name'), int(match2.group('level')), owner = match2.group('alliance'), produce = "NO")
            if match2.group('quality') == ' Easy win:':
                xmap += emojize(':smiling_face_with_sunglasses:')
            elif match2.group('quality') == ' Massacre:':
                xmap += emojize(':high_voltage:')
            else:
                xmap += emojize(':crossed_swords:')
            xmap += f" {match2.group('name')} lvl.{match2.group('level')}\n╰ {emojize(':handshake:')}{match2.group('alliance')}\n"
        delete_msg(mci, message.message_id)
        send_msg(mci, xmap)

    elif message.text is not None and re_location.search(message.text):
        local = re_location.match(message.text)
        x = DB.save_loc(local.group('code'), local.group('name'), local.group('level'), time())
        if x == 0 and message.chat.type != 'private':
            delete_msg(mci, message.message_id)
        else:
            send_msg(mci, '⚠️New Location⚠️')

    elif message.text is not None and re_headquarter.search(message.text):
        local = re_headquarter.match(message.text)
        x = DB.save_hq(local.group('code'), local.group('name'), time())
        if x == 0 and message.chat.type != 'private':
            delete_msg(mci, message.message_id)
        else:
            send_msg(mci, '⚠️New Headquarter⚠️')
    
    elif re_guild.search(message.text) and message.forward_from and message.forward_from.id == CWB2:
        regex = re_guild.search(message.text)
        guilds_tag[regex.group('name')] = regex.group('tag')
        with open("guilds_tag.json", "w") as f:
            json.dump(guilds_tag, f, indent=4)

    elif re_ga.search(message.text) and message.forward_from and message.forward_from.id == CWB2:
        regex = re_ga.search(message.text)
        guilds, players = int(regex.group('guilds')), int(regex.group('players'))
        pay_x_hour = players * guilds * 0.1
        pay_x_week = pay_x_hour * 24 * 7
        pay_x_guild = pay_x_week / guilds
        pay_x_player = pay_x_week / players

        msg = f"""Guilds: {guilds} Players: {players}
Pago x Hora: {emojize(':money_bag:')}{pay_x_hour:.2f}
Pago x Semana: {emojize(':clutch_bag:')}{pay_x_week / 146:.2f}
Pago x Gremio {emojize(':clutch_bag:')}{pay_x_guild / 146:.2f}
Pago x Jugador: {emojize(':clutch_bag:')}{pay_x_player / 146:.2f}"""

        bot.send_message(mci, msg)

    elif message.forward_from and message.forward_from.id == CWB2 and message.chat.type == 'private':

        if re_roster.search(message.text):
            guild_name = re_roster.match(message.text).group('guild_name')
            DB.roster(guild_name)
            for match in iter_re_roster.finditer(message.text):
                DB.set_roster(guild_name ,match.group('player'), demojize(match.group('pclass')), demojize(match.group('sclass')), match.group('level'))
            send_msg(mci, emojize(':busts_in_silhouette:Su Roster ha sido aceptado'))

        
        elif re_me.match(message.text):
            DB.profile(message.from_user.id, message.from_user.first_name, message.from_user.username, re_me.search(message.text), time())
        

        elif re_atklist.search(message.text):
            aod = 'attack'
            guild_name = re_atklist.match(message.text).group('guild_name')
            castle = demojize(re_atklist.match(message.text).group('castle'))
            try:
                for match in iter_re_list.finditer(message.text):
                    DB.at_df_list(guild_name, aod, match)
                send_msg(mci, DB.sms_stats(castle))
                send_msg(settings['war_room_id'], f"{emojize(castle)}{guild_name} attack update")

            except Exception as e: 
                send_msg(mci, emojize("Sorry. Debe actualizar su :busts_in_silhouette:Roster"))


        elif re_deflist.search(message.text):

            aod = 'defence'
            guild_name = re_deflist.match(message.text).group('guild_name')
            castle = demojize(re_deflist.match(message.text).group('castle'))
            
            try:
                for match in iter_re_list.finditer(message.text):
                    DB.at_df_list(guild_name, aod, match)
                send_msg(mci, DB.sms_stats(castle))
                send_msg(settings['war_room_id'], f"{emojize(castle)}{guild_name} defence update")
            
            except Exception as e:
                send_msg(mci, emojize("Sorry. Debe actualizar su :busts_in_silhouette:Roster"))


@bot.message_handler(commands=['start'])
def inicio(message):
    DB.user_registro(message)
    bot.send_message(message.chat.id , f"Welcome to {settings['ga_name']}")


@bot.message_handler(commands=['me'])
def profile(message: Message):
    msg = message.reply_to_message
    DB.profile(msg.from_user.id, msg.from_user.first_name, msg.from_user.username, re_me.search(msg.text), time())


@bot.message_handler(commands=['set_admin'])
def set_admin(message: Message):
    if message.from_user.id in admins_dict.values():
        DB.user_registro(message)
        admins_dict[message.reply_to_message.from_user.username] = message.reply_to_message.from_user.id
        with open("admins.json", "w") as f:
            json.dump(admins_dict, f, indent=4)

@bot.message_handler(commands=['del_admin'])
def del_admin(message):
    if message.from_user.id in admins_dict.values():
        DB.user_registro(message)
        del admins_dict[message.reply_to_message.text[1:]]
        with open("admins.json", "w") as f:
            json.dump(admins_dict, f, indent=4)

@bot.message_handler(commands=['admin_list'])
def admin_list(message):
    if message.from_user.id in admins_dict.values():
        DB.user_registro(message)
        respond = ''
        for user, id in admins_dict.items():
            respond += f'{id} - @{user}\n'

        bot.send_message(message.chat.id, respond)
        

@bot.message_handler(commands=['set_wr'])
def set_wr(message):
    if message.from_user.id in admins_dict.values():
        DB.user_registro(message)
        settings['war_room_id'] = message.chat.id
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)



@bot.message_handler(commands=['id'])
def majaid(message):
    mci = message.chat.id
    DB.user_registro(message)
    if message.reply_to_message:
        send_msg(mci, f"User ID: {message.reply_to_message.from_user.id}")
    else:
        send_msg(mci, f"User ID: {message.from_user.id}")

@bot.message_handler(commands=['chat_id'])
def get_chat_id(message):
    mci = message.chat.id
    DB.user_registro(message)
    send_msg(mci, f"Chat ID: {message.chat.id}")


@bot.message_handler(commands=['gass'])
def ga_stats(message):
    mci = message.chat.id
    DB.user_registro(message)
    sms = f"{settings['ga_name']}🤝\n-----------------------\n{DB.ga_stats('attack')}\n-----------------------\n{DB.ga_stats('defence')}"
    if message.from_user.id in admins_dict.values():
        send_msg(mci, sms)


@bot.message_handler(commands=['group'])
def ga_stats_gro(message):
    mci = message.chat.id
    DB.user_registro(message)
    tlista = message.text.split()
    if len(tlista) != 1:
        lista = list(map(lambda s: s.upper(), tlista[1:]))
        sms = "🤝"
        for i in range(len(lista)):
            if i % 2 == 0 and i != 0:
                sms += "\n🤝"
            sms += f"[{lista[i]}]🤝"

        sms += f"\n-----------------------\n{DB.ga_stats_group('attack', lista)}\n-----------------------\n{DB.ga_stats_group('defence', lista)}"
    else:
        return
    if message.from_user.id in admins_dict.values():
        send_msg(mci, sms)

@bot.message_handler(commands=['gasc'])
def ga_sclass(message):
    mci = message.chat.id
    DB.user_registro(message)
    sms = f"{settings['ga_name']}🤝\n-----------------------\n{DB.ga_sclass(19, 41)}-----------------------\n{DB.ga_sclass(40, 61)}-----------------------\n{DB.ga_sclass(60, 90)}"
    if message.from_user.id in admins_dict.values():
        send_msg(mci, sms)


@bot.message_handler(commands=['gss'])
def gs_stats(message):
    mci = message.chat.id
    DB.user_registro(message)
    sms = DB.guilds_stats()
    if message.from_user.id in admins_dict.values():
        send_msg(mci, sms)

@bot.message_handler(commands=['gssr'])
def gs_stats_rank(message: Message):
    mci = message.chat.id
    DB.user_registro(message)
    sms = DB.guilds_stats_rank()
    if message.from_user.id in admins_dict.values():
        send_msg(mci, sms)
       


@bot.message_handler(commands=['topa'])
def top(message):
    mci = message.chat.id
    DB.user_registro(message)
    if message.from_user.id in admins_dict.values():
        send_msg(mci, DB.ga_top('attack'), parse_m = "HTML")


@bot.message_handler(commands=['topd'])
def top(message):
    mci = message.chat.id
    DB.user_registro(message)
    if message.from_user.id in admins_dict.values():
        send_msg(mci, DB.ga_top('defence'), parse_m = "HTML")


@bot.message_handler(commands=['demo'])
def demoji(message):
    mci = message.chat.id
    x = demojize(message.reply_to_message.text)
    send_msg(mci, x)


@bot.message_handler(commands=['orden'])
def orden(message: Message):
    DB.user_registro(message)
    mci = message.chat.id
    try:
        title = iter_re_orden.split(message.reply_to_message.text)[0]
        o_markup = InlineKeyboardMarkup(row_width = 1)
        for match in iter_re_orden.finditer(message.reply_to_message.text):
            oButton = InlineKeyboardButton(f"{match.group('orden')}", url = f"http://t.me/share/url?url={match.group('link')}")
            o_markup.add(oButton)
        send_msg(mci, f"{title}", reply_m = o_markup)
    except:
        send_msg(mci, "Me quieres explotar =(")


@bot.message_handler(commands=['buttons'])
def buttons(message):
    mci = message.chat.id
    try:
        title = iter_re_andy.split(message.reply_to_message.text)[0]
        o_markup = InlineKeyboardMarkup(row_width = 1)
        for match in iter_re_andy.finditer(message.reply_to_message.text):
            oButton = InlineKeyboardButton(f"{match.group('texto')}", url = f"http://t.me/share/url?url={match.group('link')}")
            o_markup.add(oButton)
        send_msg(mci, f"{title}", reply_m = o_markup)
    except:
        send_msg(mci, "Me quieres explotar =(")


@bot.message_handler(commands=['send'])
def send_orden(message):
    DB.user_registro(message)
    if message.from_user.id in admins_dict.values():
        lista = message.text.split()
        if len(lista) != 1:
            for i in range(1, len(message.text.split())):
                if f"[{lista[i].upper()}]" in squads_dict:
                    forward_msg(squads_dict[f"[{lista[i].upper()}]"], message.chat.id, message.reply_to_message.id)
        else:
            for j in squads_dict.values():
                forward_msg(j, message.chat.id, message.reply_to_message.id) 


@bot.message_handler(commands=['nosend'])
def nosend_orden(message):

    DB.user_registro(message)
    if message.from_user.id in admins_dict.values():
        lista_tem = message.text.split()
        lista_tem = list(map(lambda t: f"[{t}]".upper(), lista_tem))
        try:
            for j in squads_dict.keys():
                if j in lista_tem:
                    continue
                forward_msg(squads_dict[j], message.chat.id, message.reply_to_message.message_id)
        except:
            send_msg(message.chat.id , "Mmm...?!") 


@bot.message_handler(commands=['showmap'])
def mostrar_map(message: Message):
    mci = message.chat.id; lista = []
    DB.user_registro(message)
    if message.from_user.id in admins_dict.values():
        if message.reply_to_message:
            temp = message.reply_to_message.text.split()
            [lista.append(int(i)) for i in temp]
            send_msg(mci, DB.show_map(time(), lista=lista), parse_m="HTML")
        else:
            send_msg(mci, DB.show_map(time()), parse_m="HTML")


@bot.message_handler(commands=['showhq'])
def mostrar_quater(message: Message):
    mci = message.chat.id
    DB.user_registro(message)
    if message.from_user.username in admins_dict:
        send_msg(mci, DB.show_hq(), parse_m="HTML")


@bot.message_handler(commands=['delete_loc']) 
def delete_loc(message: Message):
    if message.from_user.id in admins_dict.values():
        code = message.text.split('delete_loc ' )[1]
        send_msg(message.chat.id, f"Are you sure?\n\n/delete_loc_confirm_{code}")


@bot.message_handler(regexp=r'/delete_loc_confirm_\w{6}') 
def delete_loc_confirm(message):
    if message.from_user.id in admins_dict.values():
        code = message.text.split('delete_loc_confirm_' )[1]
        DB.delete_location(code)


@bot.message_handler(commands=['delete_ga_confirm'])
def delete_ga(message: Message):
    if message.from_user.id == 929349801:

        DB.delete_rosters()
        send_msg(message.chat.id, "Ha borrado los rosters")


@bot.message_handler(commands=['delete_map_confirm']) 
def delete_map(message):
    if message.from_user.id == 929349801:

        DB.delete_all_loc()
        send_msg(message.chat.id, "Uff. Bye map")


@bot.message_handler(commands=['disable'])
def desactive_hq(message):
    DB.user_registro(message)
    if message.from_user.id in admins_dict.values():
        try:
            status = message.text.split('disable ')
            DB.active_on_off(status[1], "NO")
            send_msg(message.chat.id, f"{status[1]} ❌")
        except Exception as e:
            print(e) 


@bot.message_handler(commands=['enable'])
def active_hq(message: Message):
    DB.user_registro(message)
    if message.from_user.id in admins_dict.values():
        try:
            status = message.text.split('enable ')
            DB.active_on_off(status[1], "YES")
            send_msg(message.chat.id, f"{status[1]} ✅")
        except:
            pass    


@bot.message_handler(commands=['wd'])
def withdraw(message):
    mci = message.chat.id

    DB.user_registro(message)

    w_markup = InlineKeyboardMarkup(row_width = 1)

    url = "http://t.me/share/url?url=/g_withdraw%20"

    sms_new = ""

    count, i = 0, 1
    
    try:
        sms_new = url
        for match in iter_re_stock.finditer(message.reply_to_message.text):
            sms_new += f"{match.group('code')}%20{match.group('cant')}%20"
            count += 1
            if count == 9:
                wButton = InlineKeyboardButton(f"Cadena {i}", url = sms_new)
                w_markup.add(wButton)
                sms_new = url
                count = 0
                i += 1
        if count != 0:
            wButton = InlineKeyboardButton(f"Cadena {i}", url = sms_new)
            w_markup.add(wButton)
        send_msg(mci, "Withdraw", reply_m = w_markup)
    
    except Exception as e:
        print(e)


@bot.channel_post_handler(func=lambda channel_post: True)
def chan_loc(channel_post):
    mci = channel_post.chat.id

    if channel_post.text is not None and re.match("/add_squad \w{2,3}", channel_post.text):
        
        delete_msg(mci, channel_post.message_id)
        
        tag = "[{}]".format(re.match('/add_squad (?P<tag>\w{2,3})', channel_post.text).group('tag').upper())
        
        squads_dict[tag] = channel_post.chat.id
        
        send_msg(settings['war_room_id'], f"New Squad --> {tag[1:-1]}")
        
        with open("squads.json", "w") as f:
        
            json.dump(squads_dict, f, indent=4 )


@bot.message_handler(func=lambda message: True)
def all_sms(message: Message):
    new_user = DB()
    DB.user_registro(message)

    if message.text is not None:
        class_sms(message, new_user)


@bot.callback_query_handler(func=lambda callback_query: True)
def acciones(callback_query):
    test = callback_query.data
    return


bot.polling()
