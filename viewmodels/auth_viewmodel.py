import re

from models.audit_log_model import AuditLogModel
from models.user_model import UserModel


class AuthViewModel:
    """Xử lý đăng nhập, đăng ký và phân quyền người dùng."""

    def __init__(self):
        self.model = UserModel()
        self.audit = AuditLogModel()
        self.current_user = None

    def validate_password(self, password):
        if len(password) < 8:
            return False, "Mật khẩu phải có ít nhất 8 ký tự."
        if not password[0].isupper():
            return False, "Chữ cái đầu tiên của mật khẩu phải viết hoa."
        if not re.search(r"[0-9]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 chữ số."
        if not re.search(r"[@$!%*?&]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (@$!%*?&)."
        return True, ""

    def register(self, username, password):
        username = username.strip()
        if not username:
            return False, "Vui lòng nhập tên tài khoản."

        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg

        success, message = self.model.add_user(username, password, "member", False)
        if success:
            self.audit.log("guest", "register", "user", username, "self register - pending approval")
            return True, "Đăng ký thành công. Vui lòng chờ quản trị viên kích hoạt tài khoản."
        return success, message

    def login(self, username, password):
        user = self.model.authenticate(username.strip(), password)
        if user:
            self.current_user = user
            self.audit.log(user["username"], "login", "session", user["id"], "login success")
            return True, "Thành công."
        return False, "Sai tài khoản, mật khẩu hoặc tài khoản đã bị khóa."

    def logout(self):
        if self.current_user:
            self.audit.log(self.current_user["username"], "logout", "session", self.current_user["id"], "manual logout")
        self.current_user = None

    def user_role(self):
        return (self.current_user or {}).get("role", "member")

    def is_admin(self):
        return self.user_role() == "admin"

    def is_leader_or_admin(self):
        return self.user_role() in ("admin", "leader")

    def can_manage_work(self):
        return self.is_leader_or_admin()

    def list_users(self):
        if not self.is_admin():
            return []
        return self.model.list_users()

    def list_active_users(self):
        if not self.is_leader_or_admin():
            return []
        return self.model.list_active_users()

    def list_active_usernames(self):
        return [user["username"] for user in self.list_active_users()]

    def create_user(self, username, password, role, is_active=True):
        if not self.is_admin():
            return False, "Bạn không có quyền quản lý tài khoản."
        username = username.strip()
        if not username:
            return False, "Vui lòng nhập tên tài khoản."
        if role not in ("admin", "leader", "member"):
            return False, "Quyền tài khoản không hợp lệ."

        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg
        success, message = self.model.add_user(username, password, role, is_active)
        if success:
            self.audit.log(self.current_user["username"], "create_user", "user", username, f"role={role}")
        return success, message

    def update_user(self, user_id, username, role, is_active):
        if not self.is_admin():
            return False, "Bạn không có quyền quản lý tài khoản."
        username = username.strip()
        if not username:
            return False, "Vui lòng nhập tên tài khoản."
        if role not in ("admin", "leader", "member"):
            return False, "Quyền tài khoản không hợp lệ."

        target = self.model.get_user(user_id)
        if not target:
            return False, "Không tìm thấy tài khoản."
        if self.current_user and self.current_user["id"] == user_id and not is_active:
            return False, "Không thể khóa chính tài khoản đang đăng nhập."
        if target["role"] == "admin" and (role != "admin" or not is_active) and self.model.count_active_admins() <= 1:
            return False, "Cần giữ lại ít nhất một tài khoản quản trị đang hoạt động."

        success, message = self.model.update_user(user_id, username, role, is_active)
        if success:
            self.audit.log(self.current_user["username"], "update_user", "user", user_id, f"username={username}, role={role}, active={is_active}")
            if self.current_user and self.current_user["id"] == user_id:
                self.current_user.update({"username": username, "role": role, "is_active": is_active})
        return success, message

    def reset_password(self, user_id, new_password):
        if not self.is_admin():
            return False, "Bạn không có quyền quản lý tài khoản."

        is_valid, msg = self.validate_password(new_password)
        if not is_valid:
            return False, msg
        success, message = self.model.reset_password(user_id, new_password)
        if success:
            self.audit.log(self.current_user["username"], "reset_password", "user", user_id, "password reset")
        return success, message

    def delete_user(self, user_id):
        if not self.is_admin():
            return False, "Bạn không có quyền quản lý tài khoản."
        if self.current_user and self.current_user["id"] == user_id:
            return False, "Không thể xóa chính tài khoản đang đăng nhập."
        target = self.model.get_user(user_id)
        if not target:
            return False, "Không tìm thấy tài khoản."
        if target["role"] == "admin" and self.model.count_active_admins() <= 1:
            return False, "Cần giữ lại ít nhất một tài khoản quản trị đang hoạt động."

        success, message = self.model.delete_user(user_id)
        if success:
            self.audit.log(self.current_user["username"], "delete_user", "user", user_id, target["username"])
        return success, message
