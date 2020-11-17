import telebot
import vars
from telebot import types
from selenium import webdriver

bot = telebot.TeleBot('1403672689:AAHZOWmQbfmOvyC28lcmap8XvUYdnhRQB_8', threaded=False)

if __name__ == '__main__':
    bot.send_message(270241310, "перезагрузился")
    file = open('users.txt')
    for line in file:
        tokens = line.split(";")
        chat = int(tokens[2].replace("\n", ""))
        vars.users.append(vars.User(chat))
        vars.user_booleans.append(vars.UserBooleans(chat))
        vars.users[-1].username = tokens[0]
        vars.users[-1].password = tokens[1]
        vars.user_booleans[-1].registered = True
    file.close()


def find_user_by_chat(chat_id):
    counter = 0
    for user in vars.users:
        if user.chat_id == chat_id:
            return [user, vars.user_booleans[counter]]
        counter += 1
    return 404


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
    output = open("subjects_to_attend.txt", "a")
    output.write(user[0].username + ";" + user[0].password + "|")
    for time in user[0].times_to_attend:
        if time != user[0].times_to_attend[-1]:
            output.write(time + ";")
        else:
            output.write(time + "\n")
    user[0].times_to_attend = []
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
        this_user[0].times = vars.buttons
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*vars.buttons)
        bot.send_message(message.chat.id, 'Давай на пары за тебя схожу. Тыкни время, когда мне за тебя отметиться или '
                                          'войти в конференцию. Когда закончишь, нажми кнопку "Готово"',
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def reply(message):
    this_user = find_user_by_chat(message.chat.id)
    if this_user == 404:
        vars.users.append(vars.User(message.chat.id))
        vars.user_booleans.append(vars.UserBooleans(message.chat.id))
        bot.send_message(message.chat.id, "Привет. А я тебя не знаю. Введи свой логин с edufpmi")
        vars.user_booleans[-1].username = True

    elif this_user[1].username:
        this_user[1].username = False
        this_user[0].username = message.text
        bot.send_message(message.chat.id, "Принял. Теперь введи пароль. Я никому не скажу, обещаю")
        this_user[1].password = True

    elif this_user[1].password:
        this_user[1].password = False
        this_user[0].password = message.text
        data = open("users.txt", "a")
        data.write(this_user[0].username + ";" + this_user[0].password + ";" + str(this_user[0].chat_id) + "\n")
        data.close()
        bot.send_message(message.chat.id, 'Регистрация завершена. Теперь, если захочешь поспать, напиши '
                                          '/plan, а я сделаю всё остальное')
        this_user[1].registered = True

    elif message.text == "Готово":
        try_to_login(message, this_user)

    elif str(message.text) in vars.buttons:
        this_user[0].times_to_attend.append(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        this_user[0].times.remove(str(message.text))
        markup.add(*this_user[0].times)
        bot.send_message(message.chat.id, "Принял", reply_markup=markup)


bot.polling(none_stop=True)
