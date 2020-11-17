from time import sleep
from selenium import webdriver


# собственно вход
def login(driver, username, password):
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("loginbtn").click()


# перевод названий предметов из файла в слова для поиска среди курсов на сайте
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


# конкретно тут я пробовал входить на одну из лекций на своём курсе ДМиМЛа, получилось
def enter_conference(driver, course_url):
    driver.get(course_url)
    driver.find_element_by_xpath('//*[@id="module-2658"]/div/div/div[2]/div/a').click()
    driver.find_element_by_id("join_button_input").click()
    driver.switch_to.window(driver.window_handles[1])
    sleep(15)
    driver.find_element_by_xpath("//span[text()='Только слушать']").click()


# поиск курса в списке
def find_course(courses_list, subject):
    for list_item in courses_list:
        course_name = str(list_item.text)
        if course_name.lower().find(subject) != -1:
            return list_item
    return 404


# works only if there is only two tabs
def get_other_window_handle(dvr, handle):
    for element in dvr.window_handles:
        if (element != handle):
            return element


if "__main__" == __name__:
    file = open("subjects_to_attend.txt")
    for line in file:
        data = line.replace("\n", "").split("|")
        usr, pwd = data[0].split(";")
        subjects = data[1].split(";")

        # попытка входа
        dvr = webdriver.Firefox()
        dvr.get("https://edufpmi.bsu.by")
        main_url = dvr.current_url
        login(dvr, usr, pwd)
        if dvr.current_url == main_url:
            login(dvr, usr, pwd)
        sleep(5)
        # получение списка курсов
        courses = dvr.find_elements_by_xpath("//span[@class='multiline']")

        windowHandlers = dvr.window_handles
        for i in range(len(courses)):
            element = courses[i]
            old_handle = dvr.current_window_handle
            element.click()  # open course in current tab to get it's URL
            sleep(3)  # todo: change it to the dynamic version
            newTabURL = dvr.current_url  # get course's URL
            dvr.back()  # go back to the menu page
            dvr.execute_script("window.open('" + newTabURL + "')")  # open new tab with the course
            dvr.switch_to.window(get_other_window_handle(dvr, dvr.current_window_handle))

            linked_image = dvr.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                      "/attendance/1604991493/icon']");

            for x in linked_image:
                x.click()
                # find empty radiobutton (with 'prisutstvoval' value)
                # click it
                # dvr.back()

            dvr.close()
            dvr.switch_to.window(old_handle)
            sleep(3)  # todo: change it to the dynamic version
            courses = dvr.find_elements_by_xpath("//span[@class='multiline']")
