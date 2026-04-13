import customtkinter as ctk
from viewmodels.auth_viewmodel import AuthViewModel
from views.auth_ui import AuthFrame
from views.projects_view import ProjectsView
from views.tasks_view import TasksView
from views.matrix_view import MatrixView


class ProjectManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Đồ Án - HUIT")
        self.geometry("500x600")

        self.auth_vm = AuthViewModel()
        self.show_auth_screen()

    def show_auth_screen(self):
        self.auth_frame = AuthFrame(self, self.auth_vm, self.show_main_dashboard)
        self.auth_frame.pack(fill="both", expand=True, padx=40, pady=40)

    def show_main_dashboard(self):
        # 1. Xóa giao diện đăng nhập cũ
        if self.auth_frame:
            self.auth_frame.destroy()
        self.geometry("1000x700")  # Mở rộng cửa sổ một chút để dễ nhìn

        # 2. Layout Giao diện chính (giữ nguyên cấu trúc cũ)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Thanh menu bên trái (Sidebar)
        sidebar = ctk.CTkFrame(self.main_container, width=220, corner_radius=0, fg_color="#1f1f1f")
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="PROJECT TRACKER", font=("Arial", 20, "bold"), text_color="#3a7ebf").pack(pady=25)

        # ---------------------------------------------------------
        # 3. Cập nhật các nút chức năng MỚI dựa trên Đề Bài (Ảnh 2)
        # ---------------------------------------------------------

        # Nút 1: Quản lý Dự án (tương ứng bảng Projects)
        btn_projects = ctk.CTkButton(sidebar,
                                     text="📁 Quản lý Dự án",
                                     font=("Arial", 14),
                                     anchor="w",  # Căn lề trái cho chữ
                                     corner_radius=8,
                                     fg_color="transparent",  # Màu nền trong suốt khi không chọn
                                     text_color="gray90",
                                     hover_color="#2c2c2c",
                                     command=self.show_projects_view)  # Sẽ viết hàm này sau
        btn_projects.pack(pady=10, padx=15, fill="x")

        # Nút 2: Quản lý Công việc (tương ứng bảng Tasks)
        btn_tasks = ctk.CTkButton(sidebar,
                                  text="✅ Quản lý Công việc",
                                  font=("Arial", 14),
                                  anchor="w",
                                  corner_radius=8,
                                  fg_color="transparent",
                                  text_color="gray90",
                                  hover_color="#2c2c2c",
                                  command=self.show_tasks_view)  # Sẽ viết hàm này sau
        btn_tasks.pack(pady=10, padx=15, fill="x")

        # Nút 3: Ma trận Eisenhower (Phân loại tự động)
        btn_matrix = ctk.CTkButton(sidebar,
                                   text="📊 Ma trận Eisenhower",
                                   font=("Arial", 14),
                                   anchor="w",
                                   corner_radius=8,
                                   fg_color="transparent",
                                   text_color="gray90",
                                   hover_color="#2c2c2c",
                                   command=self.show_matrix_view)  # Sẽ viết hàm này sau
        btn_matrix.pack(pady=10, padx=15, fill="x")

        # Nút 4: Thống kê (Giữ lại để đồ án hoàn thiện hơn)
        btn_stats = ctk.CTkButton(sidebar,
                                  text="📈 Thống kê báo cáo",
                                  font=("Arial", 14),
                                  anchor="w",
                                  corner_radius=8,
                                  fg_color="transparent",
                                  text_color="gray90",
                                  hover_color="#2c2c2c",
                                  command=self.show_stats_view)  # Sẽ viết hàm này sau
        btn_stats.pack(pady=10, padx=15, fill="x")

        # Nút Đăng xuất (Thêm vào cuối menu)
        ctk.CTkButton(sidebar, text="🚪 Đăng xuất", fg_color="#c0392b", hover_color="#e74c3c",
                      command=self.show_auth_screen).pack(side="bottom", pady=20, padx=15, fill="x")

        # ---------------------------------------------------------
        # 4. Khu vực hiển thị nội dung bên phải (giữ nguyên)
        # ---------------------------------------------------------
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="#101010", corner_radius=10)
        self.content_area.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.welcome_label = ctk.CTkLabel(self.content_area, text="Chào mừng bạn đến với Project Tracker!",
                                          font=("Arial", 18), text_color="gray")
        self.welcome_label.pack(pady=100)

    # 5. Định nghĩa các hàm trống để tránh lỗi khi bấm nút (Sẽ viết nội dung sau)
    # Hàm tiện ích để xóa nội dung cũ (viết vào trong class ProjectManagerApp)
    def clear_content_area(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # Cập nhật các hàm điều hướng (trong class ProjectManagerApp)
    def show_projects_view(self):
        self.clear_content_area()  # Xóa chữ chào mừng
        # Hiển thị ProjectsView vào vùng content_area
        projects_page = ProjectsView(self.content_area)
        projects_page.pack(fill="both", expand=True)

    def show_tasks_view(self):
        self.clear_content_area()
        tasks_page = TasksView(self.content_area)
        tasks_page.pack(fill="both", expand=True)

    def show_matrix_view(self):
        self.clear_content_area()
        matrix_page = MatrixView(self.content_area)
        matrix_page.pack(fill="both", expand=True)

    def show_stats_view(self):
        self.clear_content_area()
        ctk.CTkLabel(self.content_area, text="Màn hình Thống kê đang phát triển...", font=("Arial", 16)).pack(pady=100)


if __name__ == "__main__":
    app = ProjectManagerApp()
    app.mainloop()