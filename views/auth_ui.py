import customtkinter as ctk
from tkinter import messagebox


class AuthFrame(ctk.CTkFrame):
    def __init__(self, master, viewmodel, on_success):
        # Tạo khung Frame chính với bo góc và viền nhẹ
        super().__init__(master, corner_radius=20, fg_color=("#ebebeb", "#242424"))
        self.vm = viewmodel
        self.on_success = on_success
        self.show_login()

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_widgets()

        # Tiêu đề với font chữ hiện đại
        ctk.CTkLabel(self, text="PROJECT & TASK MANAGEMENT",
                     font=("Segoe UI", 26, "bold"),
                     text_color=("#3a7ebf", "#1f6aa5")).pack(pady=(40, 5))

        ctk.CTkLabel(self, text="Đăng nhập để tiếp tục quản lý đồ án",
                     font=("Segoe UI", 13),
                     text_color="gray").pack(pady=(0, 30))

        # Entry Username
        self.u_entry = ctk.CTkEntry(self, placeholder_text="Tên đăng nhập",
                                    width=320, height=45, corner_radius=10,
                                    border_width=2)
        self.u_entry.pack(pady=12)

        # Entry Password
        self.p_entry = ctk.CTkEntry(self, placeholder_text="Mật khẩu",
                                    show="*", width=320, height=45, corner_radius=10,
                                    border_width=2)
        self.p_entry.pack(pady=12)

        # Nút Quên mật khẩu căn lề phải nhẹ
        ctk.CTkButton(self, text="Quên mật khẩu?", font=("Segoe UI", 12),
                      fg_color="transparent", hover_color=None,
                      text_color=("#3a7ebf", "#1f6aa5"),
                      width=100, command=self.forgot_password).pack(pady=(0, 15))

        # Nút Đăng nhập chính
        ctk.CTkButton(self, text="ĐĂNG NHẬP", font=("Segoe UI", 14, "bold"),
                      width=320, height=45, corner_radius=10,
                      fg_color=("#3a7ebf", "#1f6aa5"),
                      hover_color=("#325d88", "#144870"),
                      command=self.handle_login).pack(pady=10)

        # Phân cách hoặc chuyển sang đăng ký
        ctk.CTkButton(self, text="Tạo tài khoản mới",
                      font=("Segoe UI", 13, "underline"),
                      fg_color="transparent", text_color="gray",
                      hover_color=None,
                      command=self.show_register).pack(pady=(10, 40))

    def show_register(self):
        self.clear_widgets()

        ctk.CTkLabel(self, text="TẠO TÀI KHOẢN",
                     font=("Segoe UI", 26, "bold"),
                     text_color=("#27ae60", "#2ecc71")).pack(pady=(30, 10))

        # Banner thông báo bảo mật
        info_frame = ctk.CTkFrame(self, fg_color=("#fcf3cf", "#3e361b"), corner_radius=8)
        info_frame.pack(pady=10, padx=40, fill="x")

        note = "🔒 Bảo mật: Chữ hoa đầu, số & ký tự đặc biệt (@)"
        ctk.CTkLabel(info_frame, text=note, font=("Segoe UI", 11),
                     text_color=("#a04000", "#f39c12")).pack(pady=8, padx=10)

        self.u_reg = ctk.CTkEntry(self, placeholder_text="Tên tài khoản mới",
                                  width=320, height=45, corner_radius=10)
        self.u_reg.pack(pady=10)

        self.p_reg = ctk.CTkEntry(self, placeholder_text="Mật khẩu bảo mật",
                                  show="*", width=320, height=45, corner_radius=10)
        self.p_reg.pack(pady=10)

        ctk.CTkButton(self, text="ĐĂNG KÝ NGAY", font=("Segoe UI", 14, "bold"),
                      fg_color=("#27ae60", "#2ecc71"),
                      hover_color=("#1e8449", "#27ae60"),
                      width=320, height=45, corner_radius=10,
                      command=self.handle_register).pack(pady=20)

        ctk.CTkButton(self, text="Quay lại đăng nhập",
                      font=("Segoe UI", 13),
                      fg_color="transparent", text_color="gray",
                      command=self.show_login).pack(pady=(0, 30))

    def forgot_password(self):
        messagebox.showinfo("Khôi phục truy cập",
                            "Vui lòng gửi Email cho Admin để được cấp lại mật khẩu:\n\n"
                            "📧 tranngocdangkhoa2702@gmail.com")

    def handle_register(self):
        success, msg = self.vm.register(self.u_reg.get(), self.p_reg.get())
        if success:
            messagebox.showinfo("Thành công", "Tài khoản của bạn đã được tạo!")
            self.show_login()
        else:
            messagebox.showwarning("Yêu cầu mật khẩu", msg)

    def handle_login(self):
        success, msg = self.vm.login(self.u_entry.get(), self.p_entry.get())
        if success:
            self.on_success()
        else:
            messagebox.showerror("Thất bại", msg)