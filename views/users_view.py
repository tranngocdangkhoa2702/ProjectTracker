import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox


ROLES = ["member", "leader", "admin"]


class UserDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa tài khoản người dùng."""

    def __init__(self, parent, on_save_callback, user=None):
        """Khởi tạo dialog theo mode tạo mới hoặc cập nhật user."""
        super().__init__(parent)
        self.title("Tài khoản")
        self.geometry("420x420")
        self.resizable(False, False)
        self.grab_set()
        self.user = user

        ctk.CTkLabel(self, text="Thêm tài khoản" if user is None else "Cập nhật tài khoản", font=("Segoe UI", 20, "bold")).pack(
            pady=(24, 8)
        )
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=32, pady=8)

        self.username_entry = ctk.CTkEntry(form, placeholder_text="Tên đăng nhập", height=40)
        self.username_entry.insert(0, user["username"] if user else "")
        self.username_entry.pack(fill="x", pady=10)

        password_placeholder = "Mật khẩu mới (bỏ trống nếu không đổi)" if user else "Mật khẩu"
        self.password_entry = ctk.CTkEntry(form, placeholder_text=password_placeholder, show="*", height=40)
        self.password_entry.pack(fill="x", pady=10)

        self.role_menu = ctk.CTkOptionMenu(form, values=ROLES)
        self.role_menu.set(user["role"] if user else "member")
        self.role_menu.pack(fill="x", pady=10)

        self.active_var = tk.BooleanVar(value=user["is_active"] if user else True)
        ctk.CTkSwitch(form, text="Tài khoản đang hoạt động", variable=self.active_var).pack(anchor="w", pady=10)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=32, pady=(18, 0))
        ctk.CTkButton(buttons, text="Hủy", fg_color="#3b3f45", hover_color="#4b5563", command=self.destroy).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        ctk.CTkButton(
            buttons,
            text="Lưu",
            fg_color="#16a34a",
            hover_color="#15803d",
            command=lambda: on_save_callback(
                self.username_entry.get(),
                self.password_entry.get(),
                self.role_menu.get(),
                self.active_var.get(),
                self,
                self.user,
            ),
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))


class UsersView(ctk.CTkFrame):
    """Màn hình quản trị tài khoản (admin)."""

    def __init__(self, master, auth_vm):
        """Khởi tạo view và nạp danh sách user."""
        super().__init__(master, fg_color="transparent")
        self.auth_vm = auth_vm
        self.users = []
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        """Dựng các thành phần UI quản lý tài khoản."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))
        ctk.CTkLabel(header, text="Quản lý tài khoản", font=("Segoe UI", 26, "bold")).pack(side="left")
        ctk.CTkButton(
            header, text="+ Thêm tài khoản", fg_color="#16a34a", hover_color="#15803d", width=150, command=self.open_add_dialog
        ).pack(side="right")

        tools = ctk.CTkFrame(self, fg_color="transparent")
        tools.pack(fill="x", padx=24, pady=(0, 12))
        self.search_entry = ctk.CTkEntry(tools, placeholder_text="Tìm theo tên đăng nhập hoặc quyền...", height=36)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh_table())
        self.count_label = ctk.CTkLabel(tools, text="", text_color="#94a3b8", width=120)
        self.count_label.pack(side="right", padx=(12, 0))

        self.table_container = ctk.CTkScrollableFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        self.table_container.pack(pady=(0, 24), padx=24, fill="both", expand=True)

    def refresh_table(self):
        """Render lại bảng user theo bộ lọc tìm kiếm."""
        for child in self.table_container.winfo_children():
            child.destroy()

        query = self.search_entry.get().lower().strip() if hasattr(self, "search_entry") else ""
        self.users = [user for user in self.auth_vm.list_users() if not query or query in user["username"].lower() or query in user["role"].lower()]
        self.count_label.configure(text=f"{len(self.users)} tài khoản")

        header = ctk.CTkFrame(self.table_container, fg_color=("#e5e7eb", "#242424"), corner_radius=8)
        header.pack(fill="x", pady=(0, 8), padx=4)
        columns = [("ID", 60), ("Tên đăng nhập", 230), ("Quyền", 120), ("Trạng thái", 120), ("Thao tác", 220)]
        for text, width in columns:
            ctk.CTkLabel(header, text=text, width=width, font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left", padx=8, pady=10)

        if not self.users:
            ctk.CTkLabel(self.table_container, text="Chưa có tài khoản phù hợp.", text_color="#94a3b8").pack(pady=40)
            return

        for index, user in enumerate(self.users):
            row_color = ("#ffffff", "#202020") if index % 2 == 0 else ("#f9fafb", "#1b1b1b")
            row = ctk.CTkFrame(self.table_container, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            role_color = "#f59e0b" if user["role"] == "admin" else ("#22c55e" if user["role"] == "leader" else "#2563eb")
            status_text = "Hoạt động" if user["is_active"] else "Đã khóa"
            status_color = "#22c55e" if user["is_active"] else "#ef4444"

            ctk.CTkLabel(row, text=str(user["id"]), width=60, anchor="w").pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=user["username"], width=230, anchor="w").pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=user["role"], width=120, anchor="w", text_color=role_color).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=status_text, width=120, anchor="w", text_color=status_color).pack(side="left", padx=8, pady=8)

            actions = ctk.CTkFrame(row, fg_color="transparent", width=220)
            actions.pack(side="left", padx=8, pady=6)
            ctk.CTkButton(
                actions, text="Sửa", width=58, height=28, fg_color="#52525b", hover_color="#3f3f46", command=lambda u=user: self.open_edit_dialog(u)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                actions, text="Xóa", width=58, height=28, fg_color="#dc2626", hover_color="#b91c1c", command=lambda user_id=user["id"]: self.delete_user(user_id)
            ).pack(side="left", padx=2)

    def open_add_dialog(self):
        """Mở dialog tạo user."""
        UserDialog(self, self.handle_save)

    def open_edit_dialog(self, user):
        """Mở dialog sửa user."""
        UserDialog(self, self.handle_save, user)

    def handle_save(self, username, password, role, is_active, dialog, original_user):
        """Lưu dữ liệu user từ dialog."""
        if original_user is None:
            success, message = self.auth_vm.create_user(username, password, role, is_active)
        else:
            success, message = self.auth_vm.update_user(original_user["id"], username, role, is_active)
            if success and password.strip():
                success, message = self.auth_vm.reset_password(original_user["id"], password)

        if success:
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Thành công", message)
        else:
            messagebox.showwarning("Thông báo", message)

    def delete_user(self, user_id):
        """Xóa tài khoản sau khi xác nhận."""
        if not messagebox.askyesno("Xác nhận", "Xóa tài khoản này?"):
            return
        success, message = self.auth_vm.delete_user(user_id)
        if success:
            self.refresh_table()
            messagebox.showinfo("Thành công", message)
        else:
            messagebox.showwarning("Thông báo", message)
