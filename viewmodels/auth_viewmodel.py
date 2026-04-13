import re
from models.user_model import UserModel


class AuthViewModel:
    def __init__(self):
        self.model = UserModel()

    def validate_password(self, password):
        """
        Ràng buộc: Ít nhất 8 ký tự, 1 chữ hoa đầu, 1 số, 1 ký tự đặc biệt.
        """
        if len(password) < 8:
            return False, "Mật khẩu phải ít nhất 8 ký tự!"
        if not password[0].isupper():
            return False, "Chữ cái đầu tiên phải viết hoa!"
        if not re.search(r"[0-9]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 chữ số!"
        if not re.search(r"[@$!%*?&]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (@$!%*?&)"
        return True, ""

    def register(self, username, password):
        if not username:
            return False, "Vui lòng nhập tên tài khoản!"

        # Kiểm tra ràng buộc mật khẩu trước khi lưu
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg

        return self.model.add_user(username, password)

    def login(self, username, password):
        if self.model.authenticate(username, password):
            return True, "Thành công"
        return False, "Sai tài khoản hoặc mật khẩu!"