import customtkinter as ctk
from tkinter import messagebox


class AuthFrame(ctk.CTkFrame):
    def __init__(self, master, viewmodel, on_success):
        super().__init__(master)
        self.vm = viewmodel
        self.on_success = on_success
        self.show_login()

    def clear_widgets(self):
        for widget in self.winfo_children(): widget.destroy()

    def show_login(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="ĐĂNG NHẬP", font=("Arial", 24, "bold")).pack(pady=20)

        self.u_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.u_entry.pack(pady=10)
        self.p_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.p_entry.pack(pady=10)

        ctk.CTkButton(self, text="Đăng nhập", command=self.handle_login).pack(pady=15)

        # Nút Quên mật khẩu
        ctk.CTkButton(self, text="Quên mật khẩu?", fg_color="transparent",
                      text_color="gray", command=self.forgot_password).pack()

        ctk.CTkButton(self, text="Chưa có tài khoản? Đăng ký", fg_color="transparent",
                      command=self.show_register).pack(pady=5)

    def show_register(self):
        self.clear_widgets()
        ctk.CTkLabel(self, text="TẠO TÀI KHOẢN", font=("Arial", 24, "bold")).pack(pady=20)

        # Ghi chú ràng buộc cho người dùng thấy
        note = "Mật khẩu: Viết hoa đầu, có số & ký tự đặc biệt ví dụ (@)"
        ctk.CTkLabel(self, text=note, font=("Arial", 11), text_color="orange").pack()

        self.u_reg = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.u_reg.pack(pady=10)
        self.p_reg = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.p_reg.pack(pady=10)

        ctk.CTkButton(self, text="Đăng ký ngay", fg_color="green", command=self.handle_register).pack(pady=20)
        ctk.CTkButton(self, text="Quay lại", fg_color="transparent", command=self.show_login).pack()

    def forgot_password(self):
        # Trong đồ án thực tế, chỗ này thường gửi mã OTP về Email.
        # Ở đây chúng ta làm thông báo hướng dẫn.
        messagebox.showinfo("Quên mật khẩu", "Vui lòng liên hệ Admin (tranngocdangkhoa2702@gmail.com hoặc datdesign256@gmail.com) để khôi phục mật khẩu!")

    def handle_register(self):
        success, msg = self.vm.register(self.u_reg.get(), self.p_reg.get())
        if success:
            messagebox.showinfo("Thành công", msg)
            self.show_login()
        else:
            messagebox.showwarning("Lưu ý", msg)  # Hiện cảnh báo nếu mật khẩu yếu

    def handle_login(self):
        success, msg = self.vm.login(self.u_entry.get(), self.p_entry.get())
        if success:
            self.on_success()
        else:
            messagebox.showerror("Lỗi", msg)

    def clear_widgets(self):
        for widget in self.winfo_children(): widget.destroy()