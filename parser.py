from time import sleep

import selenium
from selenium import webdriver
from selenium import common
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


MAX_TIMEOUT = 10
MIN_TIMEOUT = 2


def login(driver, username, password):
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("loginbtn").click()
    print("Logged in.")


def try_to_click(element):
    while True:
        try:
            element.click()
            return
        except common.exceptions.WebDriverException:
            pass


def attendance_clicker(driver, courses):
    for i in range(len(courses)):
        try_to_click(courses[i])
        driver.implicitly_wait(MIN_TIMEOUT)
        print('Зашёл на курс ' + str(i))
        linked_image = driver.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                     "/attendance/1604991493/icon']")
        for x in range(len(linked_image)):
            attendance = linked_image[x]
            attendance.click()
            send_link = driver.find_elements_by_link_text("Отправить посещаемость")
            if len(send_link) != 0:
                send_link[-1].click()
                try:
                    driver.find_element_by_xpath("//span[text()='Присутствовал']").click()
                    driver.find_element_by_id("id_submitbutton").click()
                except selenium.common.exceptions.NoSuchElementException:
                    print("Кнопка 'присутствовал' не найдена")
                sleep(5)
                driver.back()
                driver.back()
                driver.back()
                driver.back()
                print('Посещаемость отмечена на курсе ' + str(i))
                return i
            driver.back()
            print('Посещаемость на курсе ' + str(i) + ' не отмечена')
            linked_image = driver.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                         "/attendance/1604991493/icon']")
        driver.back()
        driver.implicitly_wait(MAX_TIMEOUT)
        courses = driver.find_elements_by_xpath("//span[@class='multiline']")
    return -1


def search_in_course(driver, course):
    try_to_click(course)
    driver.implicitly_wait(MIN_TIMEOUT)
    linked_image = driver.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                 "/bigbluebuttonbn/1604991493/icon']")
    for x in range(len(linked_image)):
        conference = linked_image[x]
        conference.click()
        control_panel = driver.find_element_by_id("control_panel_div")
        print('Проверяю конференцию... ', end="")
        if str(control_panel.text).find("Этот сеанс начался") != -1:
            driver.find_element_by_id("join_button_input").click()
            print('Влетаю на конференцию на курсе... ', end="")
            driver.switch_to.window(driver.window_handles[-1])
            WebDriverWait(driver, timeout=180).until(lambda d:
                                                    d.find_element_by_xpath("//span[text()='Только слушать']"))
            driver.find_element_by_xpath("//span[text()='Только слушать']").click()
            print("Влетел")
            return True
        print('Она пустая')
        driver.back()
        linked_image = driver.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                     "/bigbluebuttonbn/1604991493/icon']")
    driver.back()
    return False


def conference_clicker(driver, courses, number):
    if number != -1:
        search_in_course(driver, courses[number])
    else:
        for i in range(len(courses)):
            was_found = search_in_course(driver, courses[i])
            if was_found:
                return True
            driver.implicitly_wait(MAX_TIMEOUT)
            courses = driver.find_elements_by_xpath("//span[@class='multiline']")
    return False


if "__main__" == __name__:
    file = open("subjects_to_attend.txt")
    for line in file:
        data = line.replace("\n", "").split("|")
        usr, pwd = data[0].split(";")

        # options = Options()
        # options.headless = True
        # dvr = webdriver.Firefox(options=options)

        ua = dict(DesiredCapabilities.PHANTOMJS)
        ua["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 "
            "Safari/537.36")
        dvr = webdriver.PhantomJS(desired_capabilities=ua)
        dvr.set_window_size(1280, 720)

        dvr.implicitly_wait(MAX_TIMEOUT)

        dvr.get("https://edufpmi.bsu.by")
        main_url = dvr.current_url
        login(dvr, usr, pwd)
        if dvr.current_url == main_url:
            login(dvr, usr, pwd)

        course_number = attendance_clicker(dvr, dvr.find_elements_by_xpath("//span[@class='multiline']"))
        if not conference_clicker(dvr, dvr.find_elements_by_xpath("//span[@class='multiline']"), course_number):
            dvr.quit()
        dvr.quit()
