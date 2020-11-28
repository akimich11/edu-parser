import telebot
import vars
from telebot import types
from time import sleep
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


def login(driver, username, password):
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("loginbtn").click()
    print("Logged in.")


def try_to_login(message, user):
    user[0].dvr = webdriver.Firefox()
    user[0].dvr.implicitly_wait(10)
    user[0].dvr.get("https://edufpmi.bsu.by")
    main_url = user[0].dvr.current_url
    login(user[0].dvr, user[0].username, user[0].password)
    if user[0].dvr.current_url == main_url:
        error_code = str(user[0].dvr.find_element_by_class_name("alert alert-danger").text)
        if error_code == "Неверный логин или пароль, попробуйте заново.":
            bot.send_message(message.chat.id, "Неверный логин или пароль. Давай заново. Введи логин")
            user[1].username = True
        else:
            while user[0].dvr.current_url == main_url:
                login(user[0].dvr, user[0].username, user[0].password)
    sleep(2)
    return user[0].dvr.find_elements_by_xpath("//span[@class='multiline']")


def get_courses(message):
    this_user = find_user_by_chat(message.chat.id)
    if this_user == 404:
        vars.users.append(vars.User(message.chat.id))
        vars.user_booleans.append(vars.UserBooleans(message.chat.id))
        bot.send_message(message.chat.id, "А я тебя не знаю. Введи свой логин с edufpmi")
        vars.user_booleans[-1].username = True
    else:
        this_user[0].courses = try_to_login(message, this_user)
        if len(this_user[0].courses) != 0:
            s = ""
            k = 0
            markup = types.InlineKeyboardMarkup(row_width=4)
            items = []
            for course in this_user[0].courses:
                k += 1
                s += str(k) + ". " + course.text + "\n"
                items.append(types.InlineKeyboardButton(str(k), callback_data=k))
            markup.add(*items)
            bot.send_message(message.chat.id, 'Вот список курсов с твоего аккаунта:\n\n' + s)
            bot.send_message(message.chat.id, 'Тыкни тот, на который мне завтра зайти', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Войти получилось, а курсы не нашёл. Попробуй снова')
            this_user[0].dvr.quit()


@bot.message_handler(commands=['start'])
def command_handler(message):
    if find_user_by_chat(message.chat.id) == 404:
        vars.users.append(vars.User(message.chat.id))
        vars.user_booleans.append(vars.UserBooleans(message.chat.id))
        bot.send_message(message.chat.id, "Привет. Кажется, мы ещё не знакомы. Введи свой логин с edufpmi")
        vars.user_booleans[-1].username = True


@bot.message_handler(commands=['courses'])
def command_handler(message):
    bot.send_message(message.chat.id, "Идёт получение списка курсов. Это может занять до минуты")
    get_courses(message)


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
        this_user[1].registered = True
        bot.send_message(message.chat.id, 'Регистрация завершена. Пробую зайти на edu и получить список курсов...')
        get_courses(message)

    elif this_user[1].chooser:
        if str(message.text).isdigit():
            index = int(message.text) - 1
            f = open("tasks.csv")
            removed_line = get_line_by_id(f, this_user[0].username)
            f.close()
            f = open("tasks.csv")
            lines_to_save = remove_line_by_id(f, this_user[0].username)
            f.close()
            with open("tasks.csv", "w") as f:
                if removed_line != "":
                    f.write(lines_to_save + removed_line.replace('\n', '') + "," + this_user[0].links[index] + '\n')
                else:
                    f.write(lines_to_save + this_user[0].username + "," + this_user[0].password + "," +
                            this_user[0].links[index] + "\n")
            bot.send_message(message.chat.id, "Принял")


def get_line_by_id(f, u_id):
    for file_line in f:
        if file_line.split(",")[0] == u_id:
            return file_line
    return ""


def remove_line_by_id(f, u_id):
    lines_to_save = ""
    for file_line in f:
        if file_line.split(",")[0] != u_id:
            lines_to_save += file_line
    return lines_to_save


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    this_user = find_user_by_chat(call.message.chat.id)
    if this_user == 404:
        vars.users.append(vars.User(call.message.chat.id))
        vars.user_booleans.append(vars.UserBooleans(call.message.chat.id))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Кажется, я тебя не знаю. Введи свой логин с edufpmi", reply_markup=None)
        vars.user_booleans[-1].username = True
        return
    if call.message:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вывожу список пунктов", reply_markup=None)
        key = int(call.data) - 1
        this_user[0].courses[key].click()
        instances = this_user[0].dvr.find_elements_by_xpath("//span[@class='instancename']")
        if len(instances) != 0:
            s = ""
            k = 0
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
            this_user[0].links = []
            items = []
            for course in instances:
                this_user[0].links.append(course.find_element_by_xpath("./..").get_attribute("href"))
                k += 1
                course_text = str(course.text)
                if str(course.text).find("\n") != -1:
                    course_text = str(course.text).replace("\n", " (") + ")"
                s += str(k) + ". " + course_text + "\n"
                if k % 4 == 0:
                    s += "\n"
                items.append(types.KeyboardButton(str(k)))
            markup.add(*items)
            bot.send_message(call.message.chat.id, 'Вот что есть на выбранном курсе:\n\n' + s)
            bot.send_message(call.message.chat.id, 'Выбери пункты, на которые мне завтра тыкнуть', reply_markup=markup)
            this_user[1].chooser = True
        else:
            bot.send_message(call.message.chat.id, 'Кажется, выбранный курс пустой :(')


bot.polling(none_stop=True)
