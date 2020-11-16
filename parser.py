from time import sleep
from selenium import webdriver


def register(user):
    file = open("users.txt")
    username = "user"
    password = "password"
    for line in file:
        tokens = line.split(':')
        if tokens[0] == user:
            username = tokens[1]
            password = tokens[2]
            break
    return [username, password]


def login(driver, username, password):
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("loginbtn").click()


def get_timetable():
    return ["Вычислительные методы алгебры", "Программирование"]


def translate(subject):
    string, time = str(subject).split(" ")
    if string == "МА":
        string = "анализ"
    elif string == "ДУ":
        string = "дифф"
    elif string == "ВМА":
        string = "алгебр"
    elif string == "Прога":
        string = "прогр"
    elif string == "Экономика":
        string = "эконом"
    elif string == "Физра":
        string = "физическ"
    elif string == "ДМиМЛ":
        string = "дискретн"

    return [string, time]


def enter_conference(driver, course_url):
    driver.get(course_url)
    driver.find_element_by_xpath('//*[@id="module-2658"]/div/div/div[2]/div/a').click()
    driver.find_element_by_id("join_button_input").click()
    driver.switch_to.window(driver.window_handles[1])
    sleep(15)
    driver.find_element_by_xpath("//span[text()='Только слушать']").click()


def find_course(courses_list, subject):
    for list_item in courses_list:
        course_name = str(list_item.text)
        if course_name.lower().find(subject) != -1:
            return list_item
    return 404


if __name__ == "__main__":
    usr, pwd = register("Аким Малыщик")
    dvr = webdriver.Firefox()
    dvr.get("https://edufpmi.bsu.by")
    main_url = dvr.current_url
    login(dvr, usr, pwd)
    if dvr.current_url == main_url:
        print("Wrong username or password, fix the input file...")

    sleep(5)
    courses = dvr.find_elements_by_xpath("//span[@class='multiline']")
