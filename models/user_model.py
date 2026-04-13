import sqlite3

class UserModel:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             username TEXT UNIQUE, password TEXT)''')
            conn.commit()

    def add_user(self, username, password):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
            return True, "Đăng ký thành công!"
        except sqlite3.IntegrityError:
            return False, "Tên đăng nhập đã tồn tại!"

    def authenticate(self, username, password):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            return cursor.fetchone() is not None