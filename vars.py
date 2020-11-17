class User:
    def __init__(self, chat_id):
        self.username = "null"
        self.password = "null"
        self.chat_id = chat_id
        self.subjects = times
        self.subjects_to_attend = []


class UserBooleans:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.username = False
        self.password = False
        self.registered = False


users = []
user_booleans = []
weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
times = ["8:15", "9:45", "11:15", "13:00", "14:30", "Готово"]
