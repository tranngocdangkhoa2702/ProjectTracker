import hashlib
import sqlite3
from pathlib import Path


class UserModel:
    """Quản lý dữ liệu người dùng trong SQLite."""

    def __init__(self, db_name="database.db"):
        """Khởi tạo model và đảm bảo bảng users đã sẵn sàng."""
        self.db_name = Path(__file__).resolve().parents[1] / db_name
        self._create_table()

    def _create_table(self):
        """Tạo/migrate cấu trúc bảng users."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT DEFAULT 'member',
                    is_active INTEGER DEFAULT 1)"""
            )
            cursor.execute("PRAGMA table_info(users)")
            columns = {row[1] for row in cursor.fetchall()}
            if "role" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'member'")
            if "is_active" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")

            # Đồng bộ dữ liệu cũ: role='user' -> role='member'
            cursor.execute("UPDATE users SET role='member' WHERE role='user' OR role IS NULL OR role=''")
            conn.commit()
        self.ensure_admin_account()

    def _hash_password(self, password):
        """Hash mật khẩu bằng SHA-256 trước khi lưu."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _to_user_dict(self, user_id, username, role, is_active):
        return {
            "id": user_id,
            "username": username,
            "role": role or "member",
            "is_active": bool(is_active),
        }

    def ensure_admin_account(self):
        """Đảm bảo luôn có tài khoản Admin mặc định hoạt động."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            admin_password = self._hash_password("Admin@123")
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND is_active=1")
            if cursor.fetchone()[0] > 0:
                return

            cursor.execute("SELECT id FROM users WHERE username=?", ("Admin",))
            admin_row = cursor.fetchone()
            if admin_row:
                cursor.execute(
                    "UPDATE users SET role='admin', is_active=1 WHERE id=?",
                    (admin_row[0],),
                )
                conn.commit()
                return

            cursor.execute("SELECT id FROM users WHERE username=? COLLATE NOCASE", ("admin",))
            old_admin_row = cursor.fetchone()
            if old_admin_row:
                cursor.execute(
                    "UPDATE users SET username='Admin', password=?, role='admin', is_active=1 WHERE id=?",
                    (admin_password, old_admin_row[0]),
                )
            else:
                cursor.execute(
                    "INSERT INTO users (username, password, role, is_active) VALUES (?, ?, 'admin', 1)",
                    ("Admin", admin_password),
                )
            conn.commit()

    def add_user(self, username, password, role="member", is_active=True):
        """Thêm tài khoản mới."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role, is_active) VALUES (?, ?, ?, ?)",
                    (username, self._hash_password(password), role, int(is_active)),
                )
                conn.commit()
            return True, "Đăng ký thành công!"
        except sqlite3.IntegrityError:
            return False, "Tên đăng nhập đã tồn tại!"

    def authenticate(self, username, password):
        """Xác thực tài khoản và trả về thông tin user nếu hợp lệ."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password, role, is_active FROM users WHERE username=?", (username,))
            row = cursor.fetchone()

        if row is None:
            return None

        user_id, stored_username, stored_password, role, is_active = row
        if not is_active:
            return None

        hashed_password = self._hash_password(password)
        if stored_password == hashed_password:
            return self._to_user_dict(user_id, stored_username, role, is_active)
        # Tương thích dữ liệu cũ lưu mật khẩu raw-text.
        if stored_password == password:
            self._upgrade_password(username, hashed_password)
            return self._to_user_dict(user_id, stored_username, role, is_active)
        return None

    def _upgrade_password(self, username, hashed_password):
        """Nâng cấp mật khẩu cũ sang dạng hash."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
            conn.commit()

    def list_users(self):
        """Lấy danh sách tài khoản để hiển thị quản trị."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, is_active FROM users ORDER BY role='admin' DESC, role, username")
            return [self._to_user_dict(*row) for row in cursor.fetchall()]

    def list_active_users(self):
        """Lay danh sach tai khoan dang hoat dong."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, is_active FROM users WHERE is_active=1 ORDER BY username")
            return [self._to_user_dict(*row) for row in cursor.fetchall()]

    def get_user(self, user_id):
        """Lấy một tài khoản theo id."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, is_active FROM users WHERE id=?", (user_id,))
            row = cursor.fetchone()
        return self._to_user_dict(*row) if row else None

    def count_active_admins(self):
        """Đếm số admin đang hoạt động để tránh xóa/hạ quyền toàn bộ."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND is_active=1")
            return cursor.fetchone()[0]

    def update_user(self, user_id, username, role, is_active):
        """Cập nhật thông tin tài khoản."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET username=?, role=?, is_active=? WHERE id=?",
                    (username, role, int(is_active), user_id),
                )
                conn.commit()
            return True, "Cập nhật tài khoản thành công."
        except sqlite3.IntegrityError:
            return False, "Tên đăng nhập đã tồn tại!"

    def reset_password(self, user_id, new_password):
        """Reset mật khẩu tài khoản."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=? WHERE id=?", (self._hash_password(new_password), user_id))
            conn.commit()
        return True, "Đã cấp lại mật khẩu."

    def delete_user(self, user_id):
        """Xóa tài khoản khỏi hệ thống."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()
        return True, "Đã xóa tài khoản."
