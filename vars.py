class User:
    def __init__(self, chat_id):
        self.username = "null"
        self.password = "null"
        self.chat_id = chat_id
        self.courses = []
        self.items = []
        self.dvr = "null"


class UserBooleans:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.username = False
        self.password = False
        self.registered = False
        self.chooser = False


users = []
user_booleans = []
buttons = ["8:15", "9:45", "11:15", "13:00", "14:30", "Готово"]
