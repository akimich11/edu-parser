class User:
    def __init__(self, chat_id):
        self.username = "null"
        self.password = "null"
        self.course = "null"
        self.group = "null"
        self.chat_id = chat_id
        self.subjects = []
        self.subjects_to_attend = []


class UserBooleans:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.username = False
        self.password = False
        self.course = False
        self.group = False
        self.registered = False


users = []
user_booleans = []
weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
