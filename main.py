import customtkinter as ctk
from viewmodels.auth_viewmodel import AuthViewModel
from views.auth_ui import AuthFrame
from views.projects_view import ProjectsView
from views.tasks_view import TasksView
from views.matrix_view import EisenhowerView


class ProjectManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Đồ Án - HUIT")
        self.geometry("500x600")

        self.auth_vm = AuthViewModel()
        # Khai báo các biến để quản lý giao diện
        self.auth_frame = None
        self.main_container = None

        self.show_auth_screen()

    def clear_window(self):
        """Hàm dọn dẹp sạch sẽ cửa sổ trước khi chuyển màn hình"""
        for widget in self.winfo_children():
            widget.destroy()

    def show_auth_screen(self):
        # 1. Dọn dẹp cửa sổ (Xóa Dashboard nếu có)
        self.clear_window()
        self.geometry("500x600")

        # 2. Hiển thị màn hình đăng nhập
        self.auth_frame = AuthFrame(self, self.auth_vm, self.show_main_dashboard)
        self.auth_frame.pack(fill="both", expand=True, padx=40, pady=40)

    def show_main_dashboard(self):
        # 1. Xóa màn hình đăng nhập
        self.clear_window()
        self.geometry("1100x750")  # Tăng kích thước cho thoải mái

        # 2. Tạo Container chính chứa Sidebar và Content
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Thanh menu bên trái (Sidebar)
        sidebar = ctk.CTkFrame(self.main_container, width=220, corner_radius=0, fg_color="#1f1f1f")
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="PROJECT TRACKER", font=("Arial", 20, "bold"), text_color="#3a7ebf").pack(pady=25)

        # Nút 1: Quản lý Dự án
        self.create_sidebar_button(sidebar, "📁 Quản lý Dự án", self.show_projects_view).pack(pady=10, padx=15, fill="x")

        # Nút 2: Quản lý Công việc
        self.create_sidebar_button(sidebar, "✅ Quản lý Công việc", self.show_tasks_view).pack(pady=10, padx=15,
                                                                                              fill="x")

        # Nút 3: Ma trận Eisenhower
        self.create_sidebar_button(sidebar, "📊 Ma trận Eisenhower", self.show_matrix_view).pack(pady=10, padx=15,
                                                                                                fill="x")

        # Nút 4: Thống kê
        self.create_sidebar_button(sidebar, "📈 Thống kê báo cáo", self.show_stats_view).pack(pady=10, padx=15, fill="x")

        # Nút Đăng xuất (Dùng hàm show_auth_screen đã có lệnh xóa sạch window)
        ctk.CTkButton(sidebar, text="🚪 Đăng xuất", fg_color="#c0392b", hover_color="#e74c3c",
                      command=self.show_auth_screen).pack(side="bottom", pady=20, padx=15, fill="x")

        # 3. Khu vực hiển thị nội dung bên phải
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="#101010", corner_radius=10)
        self.content_area.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.welcome_label = ctk.CTkLabel(self.content_area, text="Chào mừng bạn đến với Project Tracker!",
                                          font=("Arial", 18), text_color="gray")
        self.welcome_label.pack(pady=100)

    def create_sidebar_button(self, parent, text, command):
        """Hàm phụ trợ tạo nút menu nhanh hơn"""
        return ctk.CTkButton(parent, text=text, font=("Arial", 14), anchor="w",
                             corner_radius=8, fg_color="transparent", text_color="gray90",
                             hover_color="#2c2c2c", command=command)

    def clear_content_area(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_projects_view(self):
        self.clear_content_area()
        projects_page = ProjectsView(self.content_area)
        projects_page.pack(fill="both", expand=True)

    def show_tasks_view(self):
        self.clear_content_area()
        self.tasks_page = TasksView(self.content_area)  # Lưu vào self để Eisenhower dùng
        self.tasks_page.pack(fill="both", expand=True)

    def show_matrix_view(self):
        self.clear_content_area()
        all_tasks = []
        if hasattr(self, 'tasks_page'):
            # Lấy list công việc từ ViewModel của trang Tasks
            all_tasks = self.tasks_page.view_model.all_tasks

        matrix_page = EisenhowerView(self.content_area, all_tasks)
        matrix_page.pack(fill="both", expand=True)

    def show_stats_view(self):
        self.clear_content_area()
        ctk.CTkLabel(self.content_area, text="Màn hình Thống kê đang phát triển...", font=("Arial", 16)).pack(pady=100)


if __name__ == "__main__":
    app = ProjectManagerApp()
    app.mainloop()