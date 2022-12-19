from telebot import types
import re
import time
import sqlite3
import asyncio
from telebot.async_telebot import AsyncTeleBot

TOKEN = ''

bot = AsyncTeleBot(TOKEN)

hm = '''Привет!
Этот бот предназначен для манипуляций с мемберами в твоем чате, для его использования просто добавь его в чат.
Чтобы вызвать команду, связанную с человеком, напишите команду в реплай к его сообщению или напишите /{команда} @{юзернейм}
Вот список команд:
/help - выводит это собщение
/prom - сделать человека админом
/unprom - отнять админку
/ban - забанить человека в чате
/unban - разбанить человека в чате
/readonly - дать человеку ридонли
/unreadonly - снять с человека ридонли
/stat - вывести статистику по чату
/leave - убрать бота из чата
'''

CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message"]


def sel(username):
    conn = sqlite3.connect("db.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS data (
      username text PRIMARY KEY NOT NULL,
      id integer NOT NULL)
    """)
    c.execute("SELECT id FROM data WHERE username=(?)", (username,))
    ans = c.fetchone()
    conn.close()
    if ans is None:
        return None
    else:
        return ans[0]


def add(username, id):
    conn = sqlite3.connect("db.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS data (
      username text PRIMARY KEY NOT NULL,
      id integer NOT NULL)
    """)
    c.execute("INSERT INTO data VALUES (?, ?)", (username, id,))
    conn.commit()
    conn.close()


pattern = re.compile(r'(\s*)(/.*) (@\w+)(\s*)')


async def check_admin(chat, user):
    return (await bot.get_chat_member(chat, user)).status == "administrator" or (await bot.get_chat_member(chat,
                                                                                                           user)).status == "creator"


def get_promer(message):
    promer = re.findall(pattern, message.text)
    if len(promer) != 0:
        promer = re.sub(pattern, r'\3', message.text)
    else:
        promer = ''
    if message.reply_to_message is not None:
        promer2 = message.reply_to_message.from_user.id
        if sel('@' + message.reply_to_message.from_user.username) is None:
            add('@' + message.reply_to_message.from_user.username, promer2)
    else:
        promer2 = None
    if promer2 is None and promer == '':
        return 'noth'
    if promer2 is not None:
        promer_id = promer2
    elif sel(promer) is None:
        return 'unk'
    else:
        promer_id = sel(promer)
    return promer_id


@bot.message_handler(commands=['help'])
async def help_message(message):
    await bot.send_message(message.chat.id, hm)
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)


@bot.message_handler(commands=['start'])
async def hello_message(message):
    await help_message(message)
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)


@bot.message_handler(commands=['prom'])
async def prom_message(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    user = message.from_user.id
    if not await check_admin(chat, user):
        await bot.send_message(message.chat.id, "Вы не админ, вы не можете админить людей")
        return

    try:
        promer_id = get_promer(message)
        if promer_id == 'noth':
            await bot.send_message(message.chat.id, "Вы не указали человека, которого хотите заадминить")
            return
        elif promer_id == 'unk':
            await bot.send_message(message.chat.id, "Я не знаю такого человека, пусть он хоть напишет что-нибудь")
            return

        if (await bot.get_chat_member(chat, promer_id)).status == 'creator':
            await bot.send_message(message.chat.id, "Его уже некуда повышать")
            return

        await bot.promote_chat_member(chat, promer_id,
                                      can_manage_chat=True,
                                      can_post_messages=True,
                                      can_edit_messages=True,
                                      can_delete_messages=True,
                                      can_manage_video_chats=True,
                                      can_restrict_members=True,
                                      can_promote_members=True,
                                      can_change_info=True,
                                      can_invite_users=True,
                                      can_pin_messages=True)
        await bot.send_message(message.chat.id, "Встречаем нового админа!")
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
        await bot.send_message(message.chat.id,
                               "Что-то пошло не так, возможно у меня нет нужных прав или вы пытаетесь забанить меня самого (я же не дурак так делать)")


@bot.message_handler(commands=['unprom'])
async def unprom_message(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    user = message.from_user.id
    if not await check_admin(chat, user):
        await bot.send_message(message.chat.id, "Вы не админ, вы не можете отбирать админки")
        return

    try:
        promer_id = get_promer(message)
        if promer_id == 'noth':
            await bot.send_message(message.chat.id, "Вы не указали человека, которого хотите заадминить")
            return
        elif promer_id == 'unk':
            await bot.send_message(message.chat.id, "Я не знаю такого человека, пусть он хоть напишет что-нибудь")
            return

        if (await bot.get_chat_member(chat, promer_id)).status == 'creator':
            await bot.send_message(message.chat.id, "Ты куда на батьку полез???")
            await bot.promote_chat_member(chat, user,
                                          can_manage_chat=False,
                                          can_post_messages=False,
                                          can_edit_messages=False,
                                          can_delete_messages=False,
                                          can_manage_video_chats=False,
                                          can_restrict_members=False,
                                          can_promote_members=False,
                                          can_change_info=False,
                                          can_invite_users=False,
                                          can_pin_messages=False)
            return

        await bot.promote_chat_member(chat, promer_id,
                                      can_manage_chat=False,
                                      can_post_messages=False,
                                      can_edit_messages=False,
                                      can_delete_messages=False,
                                      can_manage_video_chats=False,
                                      can_restrict_members=False,
                                      can_promote_members=False,
                                      can_change_info=False,
                                      can_invite_users=False,
                                      can_pin_messages=False)
        await bot.send_message(message.chat.id, "Прости, ты был хорошим админом :'(")
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
        await bot.send_message(message.chat.id,
                               "Что-то пошло не так, возможно у меня нет нужных прав или вы пытаетесь забанить меня самого (я же не дурак так делать)")


@bot.message_handler(commands=['ban'])
async def ban_message(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    user = message.from_user.id
    if not await check_admin(chat, user):
        await bot.send_message(message.chat.id, "Вы не админ, вы не можете банить людей")
        return

    try:
        promer_id = get_promer(message)
        if promer_id == 'noth':
            await bot.send_message(message.chat.id, "Вы не указали человека, которого хотите заадминить")
            return
        elif promer_id == 'unk':
            await bot.send_message(message.chat.id, "Я не знаю такого человека, пусть он хоть напишет что-нибудь")
            return

        if (await bot.get_chat_member(chat, promer_id)).status == 'creator':
            await bot.send_message(message.chat.id, "Ты куда на батьку полез???")
            await bot.ban_chat_member(chat, user, until_date=int(time.time()) + 60, revoke_messages=False)
            return

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text='На минуту',
                                           callback_data='1 1 {!s} {!s} {!s}'.format(promer_id, user, chat))
        item2 = types.InlineKeyboardButton(text='На час',
                                           callback_data='1 2 {!s} {!s} {!s}'.format(promer_id, user, chat))
        item3 = types.InlineKeyboardButton(text='На день',
                                           callback_data='1 3 {!s} {!s} {!s}'.format(promer_id, user, chat))
        item4 = types.InlineKeyboardButton(text='Навсегда!',
                                           callback_data='1 4 {!s} {!s} {!s}'.format(promer_id, user, chat))
        markup.add(item1, item2, item3, item4)
        await bot.send_message(message.chat.id, "Выберите время", reply_markup=markup)
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
        await bot.send_message(message.chat.id,
                               "Что-то пошло не так, возможно у меня нет нужных прав или вы пытаетесь забанить меня самого (я же не дурак так делать)")


@bot.message_handler(commands=['unban'])
async def unban_message(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    user = message.from_user.id
    if not await check_admin(chat, user):
        await bot.send_message(message.chat.id, "Вы не админ, вы не можете разбанить людей")
        return

    try:
        promer_id = get_promer(message)
        if promer_id == 'noth':
            await bot.send_message(message.chat.id, "Вы не указали человека, которого хотите заадминить")
            return
        elif promer_id == 'unk':
            await bot.send_message(message.chat.id, "Я не знаю такого человека, пусть он хоть напишет что-нибудь")
            return

        await bot.unban_chat_member(chat, promer_id, only_if_banned=True)
        await bot.send_message(message.chat.id, "Вы разбанили деда:O")
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))


@bot.message_handler(commands=['readonly'])
async def ro_message(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    user = message.from_user.id
    if not await check_admin(chat, user):
        await bot.send_message(message.chat.id, "Вы не админ, вы не можете раздавать ридонли")
        return

    try:
        promer_id = get_promer(message)
        if promer_id == 'noth':
            await bot.send_message(message.chat.id, "Вы не указали человека, которого хотите заридонлить")
            return
        elif promer_id == 'unk':
            await bot.send_message(message.chat.id, "Я не знаю такого человека, пусть он хоть напишет что-нибудь")
            return

        if (await bot.get_chat_member(chat, promer_id)).status == 'creator':
            await bot.send_message(message.chat.id, "Ты куда на батьку полез???")
            await bot.restrict_chat_member(chat, user,
                                           can_send_messages=False,
                                           can_send_media_messages=False,
                                           can_send_polls=False,
                                           can_send_other_messages=False,
                                           can_add_web_page_previews=False,
                                           can_change_info=False,
                                           can_invite_users=False,
                                           can_pin_messages=False,
                                           until_date=int(time.time()) + 60)
            return

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text='На минуту',
                                           callback_data='2 1 {!s} {!s} {!s}'.format(promer_id, user, chat))
        item2 = types.InlineKeyboardButton(text='На час',
                                           callback_data='2 2 {!s} {!s} {!s}'.format(promer_id, user, chat))
        item3 = types.InlineKeyboardButton(text='На день',
                                           callback_data='2 3 {!s} {!s} {!s}'.format(promer_id, user, chat))
        item4 = types.InlineKeyboardButton(text='Навсегда!',
                                           callback_data='2 4 {!s} {!s} {!s}'.format(promer_id, user, chat))
        markup.add(item1, item2, item3, item4)
        await bot.send_message(message.chat.id, "Выберите время", reply_markup=markup)
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
        await bot.send_message(message.chat.id,
                               "Что-то пошло не так, возможно у меня нет нужных прав или вы пытаетесь забанить меня самого (я же не дурак так делать)")


@bot.message_handler(commands=['unreadonly'])
async def unro_message(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    user = message.from_user.id
    if not await check_admin(chat, user):
        await bot.send_message(message.chat.id, "Вы не админ, вы не можете снять ридонли")
        return

    try:
        promer_id = get_promer(message)
        if promer_id == 'noth':
            await bot.send_message(message.chat.id, "Вы не указали человека, у которого хотите снять ридонли")
            return
        elif promer_id == 'unk':
            await bot.send_message(message.chat.id, "Я не знаю такого человека, пусть он хоть напишет что-нибудь")
            return

        await bot.restrict_chat_member(chat, promer_id,
                                       can_send_messages=True,
                                       can_send_media_messages=True,
                                       can_send_polls=True,
                                       can_send_other_messages=True,
                                       can_add_web_page_previews=True,
                                       can_change_info=True,
                                       can_invite_users=True,
                                       can_pin_messages=True,
                                       until_date=0)
        await bot.send_message(message.chat.id, "Ура, снова можно писать")
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
        await bot.send_message(message.chat.id,
                               "Что-то пошло не так, возможно у меня нет нужных прав или вы пытаетесь забанить меня самого (я же не дурак так делать)")


@bot.callback_query_handler(func=lambda call: True)
async def callback(query):
    if sel('@' + query.from_user.username) is None:
        add('@' + query.from_user.username, query.from_user.id)
    ans = query.data.split()
    try:
        if int(ans[0]) == 1:
            if query.from_user.id != int(ans[3]):
                await bot.send_message(int(ans[4]), "Выбрать время может только забанивший человек")
            else:
                if int(ans[1]) == 1:
                    await bot.ban_chat_member(int(ans[4]), int(ans[2]), until_date=int(time.time()) + 60,
                                              revoke_messages=False)
                    await bot.send_message(int(ans[4]), "Человек забанен на минуту")
                elif int(ans[1]) == 2:
                    await bot.ban_chat_member(int(ans[4]), int(ans[2]), until_date=int(time.time()) + 3600,
                                              revoke_messages=False)
                    await bot.send_message(int(ans[4]), "Человек забанен на час")
                elif int(ans[1]) == 3:
                    await bot.ban_chat_member(int(ans[4]), int(ans[2]), until_date=int(time.time()) + 86400,
                                              revoke_messages=False)
                    await bot.send_message(int(ans[4]), "Человек забанен на день")
                elif int(ans[1]) == 4:
                    await bot.ban_chat_member(int(ans[4]), int(ans[2]), until_date=0, revoke_messages=False)
                    await bot.send_message(int(ans[4]), "Человек забанен навсегда")
                elif int(ans[1]) == 0:
                    await bot.send_message(int(ans[4]), "Хорошо, не баним")
        if int(ans[0]) == 2:
            if query.from_user.id != int(ans[3]):
                await bot.send_message(int(ans[4]), "Выбрать время может только забанивший человек")
            else:
                if int(ans[1]) == 1:
                    await bot.restrict_chat_member(int(ans[4]), int(ans[2]),
                                                   can_send_messages=False,
                                                   can_send_media_messages=False,
                                                   can_send_polls=False,
                                                   can_send_other_messages=False,
                                                   can_add_web_page_previews=False,
                                                   can_change_info=False,
                                                   can_invite_users=False,
                                                   can_pin_messages=False,
                                                   until_date=int(time.time()) + 60)
                    await bot.send_message(int(ans[4]), "Дал ридонли на минуту")
                elif int(ans[1]) == 2:
                    await bot.restrict_chat_member(int(ans[4]), int(ans[2]),
                                                   can_send_messages=False,
                                                   can_send_media_messages=False,
                                                   can_send_polls=False,
                                                   can_send_other_messages=False,
                                                   can_add_web_page_previews=False,
                                                   can_change_info=False,
                                                   can_invite_users=False,
                                                   can_pin_messages=False,
                                                   until_date=int(time.time()) + 3600)
                    await bot.send_message(int(ans[4]), "Дал ридонли на час")
                elif int(ans[1]) == 3:
                    await bot.restrict_chat_member(int(ans[4]), int(ans[2]),
                                                   can_send_messages=False,
                                                   can_send_media_messages=False,
                                                   can_send_polls=False,
                                                   can_send_other_messages=False,
                                                   can_add_web_page_previews=False,
                                                   can_change_info=False,
                                                   can_invite_users=False,
                                                   can_pin_messages=False,
                                                   until_date=int(time.time()) + 86400)
                    await bot.send_message(int(ans[4]), "Дал ридонли на день")
                elif int(ans[1]) == 4:
                    await bot.restrict_chat_member(int(ans[4]), int(ans[2]),
                                                   can_send_messages=False,
                                                   can_send_media_messages=False,
                                                   can_send_polls=False,
                                                   can_send_other_messages=False,
                                                   can_add_web_page_previews=False,
                                                   can_change_info=False,
                                                   can_invite_users=False,
                                                   can_pin_messages=False,
                                                   until_date=0)
                    await bot.send_message(int(ans[4]), "Дал ридонли навсегда")
                elif int(ans[1]) == 0:
                    await bot.send_message(int(ans[4]), "Хорошо, не баним")
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
        await bot.send_message(int(ans[4]),
                               "Что-то пошло не так, возможно у меня нет нужных прав или вы пытаетесь забанить меня самого (я же не дурак так делать)")


@bot.message_handler(commands=['stat'])
async def stat_message(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    try:
        await bot.send_message(message.chat.id,
                               "В чате {!s} людей и {!s} админов".format(await bot.get_chat_member_count(chat),
                                                                         len(await bot.get_chat_administrators(
                                                                             chat))))
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
        await bot.send_message(message.chat.id,
                               "Что-то пошло не так, возможно у меня нет нужных прав или вы пытаетесь забанить меня самого (я же не дурак так делать)")


@bot.message_handler(commands=['leave'])
async def leave(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    chat = message.chat.id
    user = message.from_user.id
    if not await check_admin(chat, user):
        await bot.send_message(message.chat.id, "Вы не админ, вы не можете кикнуть бота")
        return

    try:
        await bot.leave_chat(message.chat.id)
    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))


@bot.message_handler(content_types=CONTENT_TYPES)
async def message_reply(message):
    if sel('@' + message.from_user.username) is None:
        add('@' + message.from_user.username, message.from_user.id)
    if message.new_chat_members is not None:
        for i in message.new_chat_members:
            if sel('@' + i.username) is None:
                add('@' + i.username, i.id)
            await bot.send_message(message.chat.id, "{!s}, признавайся. Кто убил Марка???".format('@' + i.username))
            await bot.send_photo(message.chat.id,
                                 'https://drive.google.com/file/d/1mbWM5rclbxHcdesNGLgfuU95pS0JS2wh/view?usp=sharing')


async def main():
    await asyncio.gather(bot.infinity_polling())


if __name__ == '__main__':
    asyncio.run(main())
