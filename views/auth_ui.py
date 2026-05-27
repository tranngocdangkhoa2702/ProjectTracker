import customtkinter as ctk
from tkinter import messagebox


class AuthFrame(ctk.CTkFrame):
    """UI đăng nhập/đăng ký + animation tiến trình đăng nhập."""

    def __init__(self, master, viewmodel, on_success):
        """Khởi tạo frame auth và hiển thị form login."""
        super().__init__(master, corner_radius=18, fg_color=("#ffffff", "#202020"))
        self.vm = viewmodel
        self.on_success = on_success
        self._login_after_id = None
        self.show_login()

    def clear_widgets(self):
        """Xóa toàn bộ widget trên frame auth."""
        if self._login_after_id is not None:
            self.after_cancel(self._login_after_id)
            self._login_after_id = None
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        """Hiển thị form đăng nhập."""
        self.clear_widgets()

        ctk.CTkLabel(
            self,
            text="Project Tracker",
            font=("Segoe UI", 30, "bold"),
            text_color=("#1d4ed8", "#60a5fa"),
        ).pack(pady=(46, 6))
        ctk.CTkLabel(
            self,
            text="Đăng nhập để quản lý dự án, công việc và tiến độ đồ án.",
            font=("Segoe UI", 13),
            text_color="#94a3b8",
        ).pack(pady=(0, 8))
        ctk.CTkLabel(
            self,
            text="Admin mặc định: Admin / Admin@123",
            font=("Segoe UI", 11),
            text_color=("#64748b", "#9ca3af"),
        ).pack(pady=(0, 20))

        self.u_entry = ctk.CTkEntry(self, placeholder_text="Tên đăng nhập", width=330, height=44, corner_radius=10)
        self.u_entry.pack(pady=10)
        self.p_entry = ctk.CTkEntry(self, placeholder_text="Mật khẩu", show="*", width=330, height=44, corner_radius=10)
        self.p_entry.pack(pady=10)
        self.p_entry.bind("<Return>", lambda _event: self.handle_login())

        ctk.CTkButton(
            self,
            text="Đăng nhập",
            font=("Segoe UI", 14, "bold"),
            width=330,
            height=44,
            corner_radius=10,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.handle_login,
        ).pack(pady=(18, 8))

        ctk.CTkButton(
            self,
            text="Tạo tài khoản người dùng",
            font=("Segoe UI", 13),
            fg_color="transparent",
            hover_color=("#e5e7eb", "#2b2b2b"),
            text_color=("#1d4ed8", "#60a5fa"),
            command=self.show_register,
        ).pack(pady=4)

        ctk.CTkButton(
            self,
            text="Quên mật khẩu?",
            font=("Segoe UI", 12),
            fg_color="transparent",
            hover_color=("#e5e7eb", "#2b2b2b"),
            text_color="#94a3b8",
            command=self.forgot_password,
        ).pack(pady=(0, 32))

    def show_register(self):
        """Hiển thị form đăng ký tài khoản."""
        self.clear_widgets()

        ctk.CTkLabel(
            self,
            text="Tạo tài khoản",
            font=("Segoe UI", 30, "bold"),
            text_color=("#15803d", "#4ade80"),
        ).pack(pady=(40, 8))

        info_frame = ctk.CTkFrame(self, fg_color=("#fef3c7", "#2c2411"), corner_radius=10)
        info_frame.pack(pady=(4, 20), padx=42, fill="x")
        ctk.CTkLabel(
            info_frame,
            text="Mật khẩu: chữ đầu viết hoa, ít nhất 8 ký tự, có số và ký tự đặc biệt.",
            font=("Segoe UI", 11),
            text_color=("#92400e", "#fbbf24"),
            wraplength=300,
        ).pack(pady=10, padx=12)

        self.u_reg = ctk.CTkEntry(self, placeholder_text="Tên tài khoản mới", width=330, height=44, corner_radius=10)
        self.u_reg.pack(pady=10)
        self.p_reg = ctk.CTkEntry(self, placeholder_text="Mật khẩu", show="*", width=330, height=44, corner_radius=10)
        self.p_reg.pack(pady=10)
        self.p_reg.bind("<Return>", lambda _event: self.handle_register())

        ctk.CTkButton(
            self,
            text="Đăng ký",
            font=("Segoe UI", 14, "bold"),
            fg_color="#16a34a",
            hover_color="#15803d",
            width=330,
            height=44,
            corner_radius=10,
            command=self.handle_register,
        ).pack(pady=(18, 8))

        ctk.CTkButton(
            self,
            text="Quay lại đăng nhập",
            font=("Segoe UI", 13),
            fg_color="transparent",
            hover_color=("#e5e7eb", "#2b2b2b"),
            text_color="#94a3b8",
            command=self.show_login,
        ).pack(pady=(0, 30))

    def show_login_progress(self):
        """Hiển thị màn hình trung gian khi đang đăng nhập."""
        self.clear_widgets()

        ctk.CTkLabel(
            self,
            text="Đang đăng nhập...",
            font=("Segoe UI", 26, "bold"),
            text_color=("#1d4ed8", "#60a5fa"),
        ).pack(pady=(90, 10))
        ctk.CTkLabel(
            self,
            text="Hệ thống đang xác thực tài khoản, vui lòng chờ.",
            font=("Segoe UI", 13),
            text_color="#94a3b8",
        ).pack(pady=(0, 22))

        self.login_progress = ctk.CTkProgressBar(self, width=340, height=14)
        self.login_progress.set(0)
        self.login_progress.pack(pady=(0, 12))
        self.login_percent_label = ctk.CTkLabel(self, text="0%", font=("Segoe UI", 13, "bold"), text_color="#60a5fa")
        self.login_percent_label.pack()

        self._animate_login_progress(0)

    def _animate_login_progress(self, value):
        """Chạy progress bar đăng nhập và chuyển dashboard khi hoàn tất."""
        self.login_progress.set(value / 100)
        self.login_percent_label.configure(text=f"{value}%")

        if value >= 100:
            self._login_after_id = None
            self.on_success()
            return

        next_value = min(100, value + 8)
        self._login_after_id = self.after(60, lambda: self._animate_login_progress(next_value))

    def forgot_password(self):
        """Hiển thị thông tin liên hệ admin để cấp lại mật khẩu."""
        messagebox.showinfo(
            "Khôi phục truy cập",
            "Vui lòng liên hệ Admin để được cấp lại mật khẩu:\n\ntranngocdangkhoa2702@gmail.com",
        )

    def handle_register(self):
        """Xử lý submit đăng ký."""
        success, msg = self.vm.register(self.u_reg.get(), self.p_reg.get())
        if success:
            messagebox.showinfo("Thành công", "Tài khoản người dùng đã được tạo!")
            self.show_login()
        else:
            messagebox.showwarning("Thông báo", msg)

    def handle_login(self):
        """Xử lý submit đăng nhập."""
        success, msg = self.vm.login(self.u_entry.get(), self.p_entry.get())
        if success:
            self.show_login_progress()
        else:
            messagebox.showerror("Thất bại", msg)
