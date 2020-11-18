from time import sleep
from selenium import webdriver


# собственно вход
def login(driver, username, password):
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("loginbtn").click()


# конкретно тут я пробовал входить на одну из лекций на своём курсе ДМиМЛа, получилось
def enter_conference(driver, course_url):
    driver.get(course_url)
    driver.find_element_by_xpath('//*[@id="module-2658"]/div/div/div[2]/div/a').click()
    driver.find_element_by_id("join_button_input").click()
    driver.switch_to.window(driver.window_handles[-1])
    sleep(15)
    driver.find_element_by_xpath("//span[text()='Только слушать']").click()


if "__main__" == __name__:
    file = open("subjects_to_attend.txt")
    for line in file:
        data = line.replace("\n", "").split("|")
        usr, pwd = data[0].split(";")
        subjects = data[1].split(";")

        # попытка входа
        dvr = webdriver.Chrome()
        dvr.implicitly_wait(7)

        dvr.get("https://edufpmi.bsu.by")
        main_url = dvr.current_url
        login(dvr, usr, pwd)
        if dvr.current_url == main_url:
            login(dvr, usr, pwd)
        # получение списка курсов
        courses = dvr.find_elements_by_xpath("//span[@class='multiline']")

        for i in range(len(courses)):
            courses[i].click()  # open course
            linked_image = dvr.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                      "/attendance/1604991493/icon']")
            for x in range(len(linked_image)):
                attendance = linked_image[x]
                attendance.click()
                send_link = dvr.find_elements_by_link_text("Отправить посещаемость")
                if len(send_link) != 0:
                    send_link[-1].click()
                    dvr.find_element_by_xpath("//span[text()='Присутствовал']").click()
                    dvr.find_element_by_id("id_submitbutton").click()
                    dvr.back()
                    dvr.back()
                    # dvr.back()
                dvr.back()
                linked_image = dvr.find_elements_by_xpath("//img[@src='https://edufpmi.bsu.by/theme/image.php/moove"
                                                          "/attendance/1604991493/icon']")
            dvr.back()
            courses = dvr.find_elements_by_xpath("//span[@class='multiline']")
