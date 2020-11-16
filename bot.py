import telebot
import vars
from telebot import types
from datetime import datetime
from selenium import webdriver

bot = telebot.TeleBot('1403672689:AAHZOWmQbfmOvyC28lcmap8XvUYdnhRQB_8', threaded=False)

if __name__ == '__main__':
    bot.send_message(270241310, "перезагрузился")
    file = open('users.txt')
    for line in file:
        tokens = line.split(";")
        chat = tokens[4].replace("\n", "")
        vars.users.append(vars.User(chat))
        vars.user_booleans.append(vars.UserBooleans(chat))
        vars.users[-1].username = tokens[0]
        vars.users[-1].password = tokens[1]
        vars.users[-1].course = tokens[2]
        vars.users[-1].group = tokens[3]
        vars.user_booleans[-1].registered = True
    file.close()


def find_user_by_chat(chat_id):
    counter = 0
    for user in vars.users:
        if user.chat_id == str(chat_id):
            return [user, vars.user_booleans[counter]]
        counter += 1
    return 404


def day_number(weekday):
    counter = 0
    for day in vars.weekdays:
        counter += 1
        if day == weekday:
            return counter
    return counter


def create_markup(message, this_user):
    try:
        data = open(this_user[0].course + "_" + this_user[0].group + ".txt")
        this_date = datetime.utcnow()
        this_day = this_date.weekday() + 1
        if this_day == 7 or this_day == 6:
            this_day = 0

        items = []
        items_str = []
        start_to_read = False
        for lines in data:
            string = lines.replace('\n', '')
            if string in vars.weekdays and day_number(string) == this_day + 2:
                data.close()
                break
            if start_to_read:
                items_str.append(string)
                items.append(types.KeyboardButton(string))
                continue
            if string in vars.weekdays and day_number(string) == this_day + 1:
                start_to_read = True

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        items.append(types.KeyboardButton("Готово"))
        markup.add(*items)
        this_user[0].subjects = items_str
        bot.send_message(message.chat.id, "Давай на пары за тебя схожу. Список пар появился у тебя внизу. Тыкни "
                                          'те, на которые мне сходить. Когда закончишь, нажми кнопку "Готово"',
                         reply_markup=markup)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "У меня пока нет файла с расписанием твоей группы, извини")


def try_to_login(message, user):
    dvr = webdriver.Firefox()
    dvr.get("https://edufpmi.bsu.by")
    main_url = dvr.current_url
    dvr.find_element_by_id("username").send_keys(user[0].username)
    dvr.find_element_by_id("password").send_keys(user[0].password)
    dvr.find_element_by_id("loginbtn").click()
    if dvr.current_url == main_url:
        bot.send_message(message.chat.id, "Неверный логин или пароль. Придётся подправить регистрационные данные. "
                                          "Введи логин")
        user[1].username = True
    else:
        bot.send_message(message.chat.id, "Вход на edu выполнен, можешь спать спокойно, с парами я разберусь")
        write_file = open("subjects_to_attend.txt", "a")
        write_file.write(user[0].username + ";" + user[0].password + "|")
        for subj in user[0].subjects_to_attend:
            if subj != user[0].subjects_to_attend[-1]:
                write_file.write(subj + ";")
            else:
                write_file.write(subj + "\n")
        write_file.close()
    dvr.quit()


@bot.message_handler(commands=['start'])
def start(message):
    if find_user_by_chat(message.chat.id) == 404:
        vars.users.append(vars.User(message.chat.id))
        vars.user_booleans.append(vars.UserBooleans(message.chat.id))
        bot.send_message(message.chat.id, "Привет, прогульщик. Кажется, мы ещё не знакомы. Введи свой логин с edufpmi")
        vars.user_booleans[-1].username = True


@bot.message_handler(commands=['plan'])
def plan(message):
    this_user = find_user_by_chat(message.chat.id)
    if this_user == 404:
        vars.users.append(vars.User(message.chat.id))
        vars.user_booleans.append(vars.UserBooleans(message.chat.id))
        bot.send_message(message.chat.id, "Сначала зарегистрируйся. Введи свой логин с edufpmi")
        vars.user_booleans[-1].username = True
        return

    if this_user[1].registered:
        create_markup(message, this_user)


@bot.message_handler(content_types=['text'])
def reply(message):
    this_user = find_user_by_chat(message.chat.id)
    if this_user == 404:
        vars.users.append(vars.User(message.chat.id))
        vars.user_booleans.append(vars.UserBooleans(message.chat.id))
        bot.send_message(message.chat.id, "Привет. А я тебя не знаю. Введи свой логин с edufpmi")
        vars.user_booleans[-1].username = True

    elif str(message.text) in this_user[0].subjects:
        this_user[0].subjects_to_attend.append(str(message.text))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        items = []
        this_user[0].subjects.remove(str(message.text))
        for subject in this_user[0].subjects:
            items.append(types.KeyboardButton(subject))
        items.append(types.KeyboardButton("Готово"))
        markup.add(*items)
        bot.send_message(message.chat.id, "Принял", reply_markup=markup)

    elif message.text == "Готово" and len(this_user[0].subjects_to_attend) != 0:
        try_to_login(message, this_user)

    elif this_user[1].username:
        this_user[1].username = False
        this_user[0].username = message.text
        bot.send_message(message.chat.id, "Принял. Теперь введи пароль. Я никому не скажу, обещаю")
        this_user[1].password = True

    elif this_user[1].password:
        this_user[1].password = False
        this_user[0].password = message.text
        bot.send_message(message.chat.id, "Принял. Теперь введи номер курса")
        this_user[1].course = True

    elif this_user[1].course:
        if (not message.text.is_digit()) or int(message.text) > 4 or int(message.text < 1):
            bot.send_message(message.chat.id, "Да введи ты нормально чо прикалываешься")
            return
        this_user[1].course = False
        this_user[0].course = message.text
        bot.send_message(message.chat.id, "Принял. Теперь введи номер группы")
        bot.send_message(message.chat.id, "Это чтобы получить твоё расписание, "
                                          "а не чтобы сдать тебя Гале")
        this_user[1].group = True

    elif this_user[1].group:
        if (not message.text.is_digit()) or int(message.text) > 14 or int(message.text < 1):
            bot.send_message(message.chat.id, "Да введи ты нормально чо прикалываешься")
            return
        this_user[1].group = False
        this_user[0].group = message.text
        data = open("users.txt", "a")
        data.write(this_user[0].username + ";" + this_user[0].password + ";" + this_user[0].course + ";" +
                   this_user[0].group + ";" + str(this_user[0].chat_id) + "\n")
        data.close()
        bot.send_message(message.chat.id, 'Регистрация завершена. Теперь, если захочешь поспать, так и напиши, '
                                          '"хочу завтра поспать", а я сделаю всё остальное')
        this_user[1].registered = True


bot.polling(none_stop=True)
