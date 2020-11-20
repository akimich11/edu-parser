from time import sleep
from selenium import webdriver
from selenium import common
from selenium.webdriver.support.ui import WebDriverWait


# собственно вход
def login(driver, username, password):
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("loginbtn").click()


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
        driver.implicitly_wait(1)
        linked_image = driver.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                     "/attendance/1604991493/icon']")
        for x in range(len(linked_image)):
            attendance = linked_image[x]
            attendance.click()
            send_link = driver.find_elements_by_link_text("Отправить посещаемость")
            if len(send_link) != 0:
                send_link[-1].click()
                driver.find_element_by_xpath("//span[text()='Присутствовал']").click()
                driver.find_element_by_id("id_submitbutton").click()
                sleep(5)
                driver.quit()
                return i
            driver.back()
            linked_image = driver.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                         "/attendance/1604991493/icon']")
        driver.back()
        driver.implicitly_wait(7)
        courses = driver.find_elements_by_xpath("//span[@class='multiline']")
    return -1


def search_in_course(driver, course):
    try_to_click(course)
    driver.implicitly_wait(1)
    linked_image = driver.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                 "/bigbluebuttonbn/1604991493/icon']")
    for x in range(len(linked_image)):
        conference = linked_image[x]
        conference.click()
        control_panel = driver.find_element_by_id("control_panel_div")
        if str(control_panel.text).find("Этот сеанс начался") != -1:
            driver.find_element_by_id("join_button_input").click()
            driver.switch_to.window(driver.window_handles[-1])
            WebDriverWait(driver, timeout=15).until(lambda d:
                                                    d.find_element_by_xpath("//span[text()='Только слушать']"))
            driver.find_element_by_xpath("//span[text()='Только слушать']").click()
            return True
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
            driver.implicitly_wait(7)
            courses = driver.find_elements_by_xpath("//span[@class='multiline']")
    return False


if "__main__" == __name__:
    file = open("subjects_to_attend.txt")
    for line in file:
        data = line.replace("\n", "").split("|")
        usr, pwd = data[0].split(";")

        dvr = webdriver.Firefox()
        dvr.implicitly_wait(7)

        dvr.get("https://edufpmi.bsu.by")
        main_url = dvr.current_url
        login(dvr, usr, pwd)
        if dvr.current_url == main_url:
            login(dvr, usr, pwd)

        course_number = attendance_clicker(dvr, dvr.find_elements_by_xpath("//span[@class='multiline']"))
        if not conference_clicker(dvr, dvr.find_elements_by_xpath("//span[@class='multiline']"), course_number):
            dvr.quit()
