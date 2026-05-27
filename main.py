import customtkinter as ctk

from viewmodels.auth_viewmodel import AuthViewModel
from viewmodels.project_manager_viewmodel import ProjectViewModel
from viewmodels.task_mananger_viewmodel import TaskViewModel
from views.audit_logs_view import AuditLogsView
from views.auth_ui import AuthFrame
from views.matrix_view import EisenhowerView
from views.projects_view import ProjectsView
from views.system_tools_view import SystemToolsView
from views.tasks_view import TasksView
from views.timeline_view import TimelineView
from views.users_view import UsersView


class ProjectManagerApp(ctk.CTk):
    """
    Mục đích:
    - Điều phối toàn bộ giao diện chính của ứng dụng.
    - Điều hướng giữa các màn theo quyền người dùng.

    Input:
    - Không có tham số đầu vào từ bên ngoài khi khởi tạo.

    Output:
    - Một cửa sổ ứng dụng CustomTkinter đã sẵn sàng chạy.

    Luồng xử lý chính:
    - Khởi tạo auth viewmodel.
    - Hiển thị màn xác thực.
    - Sau khi đăng nhập, dựng dashboard theo role.
    """

    def __init__(self):
        """Khởi tạo cửa sổ ứng dụng và điều hướng vào màn auth."""
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Hệ thống Quản lý Đồ án - HUIT")
        self.geometry("500x620")
        self.minsize(500, 580)

        self.auth_vm = AuthViewModel()
        self.auth_frame = None
        self.main_container = None
        self.content_area = None
        self.sidebar_buttons = {}
        self._logout_after_id = None
        self.tasks_page = None

        self.show_auth_screen()

    def clear_window(self):
        """Xóa toàn bộ widget trên cửa sổ hiện tại."""
        if self._logout_after_id is not None:
            self.after_cancel(self._logout_after_id)
            self._logout_after_id = None
        for widget in self.winfo_children():
            widget.destroy()

    def show_auth_screen(self):
        """Hiển thị màn đăng nhập/đăng ký."""
        self.auth_vm.logout()
        self.clear_window()
        self.geometry("500x620")
        self.minsize(500, 580)

        shell = ctk.CTkFrame(self, fg_color=("#eef2ff", "#111827"))
        shell.pack(fill="both", expand=True)
        self.auth_frame = AuthFrame(shell, self.auth_vm, self.show_main_dashboard)
        self.auth_frame.pack(fill="both", expand=True, padx=46, pady=46)

    def show_main_dashboard(self):
        """
        Mục đích:
        - Dựng màn dashboard sau khi đăng nhập.

        Input:
        - Không nhận tham số trực tiếp.

        Output:
        - Sidebar + vùng nội dung được render theo role hiện tại.

        Luồng xử lý chính:
        - Xóa giao diện cũ.
        - Tạo sidebar với menu phù hợp quyền.
        - Mở view mặc định là Dự án.
        """
        self.clear_window()
        self.geometry("1240x780")
        self.minsize(1040, 680)

        self.main_container = ctk.CTkFrame(self, fg_color=("#f8fafc", "#0f172a"))
        self.main_container.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(self.main_container, width=260, corner_radius=0, fg_color=("#ffffff", "#111827"))
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="Project Tracker", font=("Segoe UI", 22, "bold"), text_color=("#1d4ed8", "#60a5fa")).pack(
            pady=(28, 4), padx=18, anchor="w"
        )
        ctk.CTkLabel(sidebar, text="HUIT workspace", font=("Segoe UI", 12), text_color="#94a3b8").pack(
            pady=(0, 18), padx=18, anchor="w"
        )
        self.create_user_badge(sidebar)

        nav_items = [
            ("projects", "Dự án", self.show_projects_view),
            ("tasks", "Công việc", self.show_tasks_view),
            ("matrix", "Ma trận", self.show_matrix_view),
            ("timeline", "Timeline", self.show_timeline_view),
            ("stats", "Thống kê", self.show_stats_view),
        ]
        if self.auth_vm.is_leader_or_admin():
            nav_items.append(("logs", "Nhật ký", self.show_logs_view))
            nav_items.append(("tools", "Công cụ", self.show_tools_view))
        if self.auth_vm.is_admin():
            nav_items.append(("users", "Tài khoản", self.show_users_view))

        self.sidebar_buttons = {}
        for key, text, command in nav_items:
            button = self.create_sidebar_button(sidebar, text, lambda k=key, cmd=command: self.navigate(k, cmd))
            button.pack(pady=5, padx=14, fill="x")
            self.sidebar_buttons[key] = button

        ctk.CTkButton(
            sidebar, text="Đăng xuất", fg_color="#dc2626", hover_color="#b91c1c", height=38, command=self.start_logout_flow
        ).pack(side="bottom", pady=22, padx=14, fill="x")

        self.content_area = ctk.CTkFrame(self.main_container, fg_color=("#ffffff", "#111111"), corner_radius=14)
        self.content_area.pack(side="right", fill="both", expand=True, padx=18, pady=18)

        self.navigate("projects", self.show_projects_view)

    def current_actor(self):
        """Lấy username hiện tại để ghi audit log."""
        user = self.auth_vm.current_user or {}
        return user.get("username", "system")

    def create_user_badge(self, parent):
        """Hiển thị thông tin user đang đăng nhập ở sidebar."""
        user = self.auth_vm.current_user or {}
        role_map = {"admin": "Admin", "leader": "Leader", "member": "Member"}
        role = role_map.get(user.get("role"), "Member")
        badge = ctk.CTkFrame(parent, fg_color=("#f1f5f9", "#1f2937"), corner_radius=10)
        badge.pack(fill="x", padx=14, pady=(0, 18))
        ctk.CTkLabel(badge, text=user.get("username", "guest"), font=("Segoe UI", 14, "bold"), anchor="w").pack(
            fill="x", padx=12, pady=(10, 0)
        )
        ctk.CTkLabel(badge, text=role, text_color=("#2563eb", "#93c5fd"), font=("Segoe UI", 12), anchor="w").pack(
            fill="x", padx=12, pady=(0, 10)
        )

    def create_sidebar_button(self, parent, text, command):
        """Factory tạo button sidebar cùng style chung."""
        return ctk.CTkButton(
            parent,
            text=text,
            font=("Segoe UI", 14, "bold"),
            anchor="w",
            corner_radius=8,
            height=40,
            fg_color="transparent",
            text_color=("#334155", "#e5e7eb"),
            hover_color=("#e5e7eb", "#1f2937"),
            command=command,
        )

    def navigate(self, active_key, command):
        """Đổi trạng thái active của menu và render view tương ứng."""
        for key, button in self.sidebar_buttons.items():
            if key == active_key:
                button.configure(fg_color=("#dbeafe", "#1e3a8a"), text_color=("#1d4ed8", "#ffffff"))
            else:
                button.configure(fg_color="transparent", text_color=("#334155", "#e5e7eb"))
        command()

    def clear_content_area(self):
        """Xóa vùng nội dung bên phải trước khi chuyển view."""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_projects_view(self):
        """
        Mục đích:
        - Mở màn quản lý dự án.

        Input:
        - Dùng actor hiện tại và quyền quản lý từ auth_vm.

        Output:
        - Render ProjectsView vào content area.

        Luồng xử lý chính:
        - Xóa content cũ.
        - Khởi tạo ProjectsView với context quyền.
        - Pack view vào vùng nội dung.
        """
        self.clear_content_area()
        ProjectsView(self.content_area, actor=self.current_actor(), can_manage=self.auth_vm.can_manage_work()).pack(fill="both", expand=True)

    def show_tasks_view(self):
        """
        Mục đích:
        - Mở màn quản lý công việc.

        Input:
        - Dùng actor hiện tại và quyền quản lý từ auth_vm.

        Output:
        - Render TasksView và lưu tham chiếu self.tasks_page.

        Luồng xử lý chính:
        - Xóa content cũ.
        - Khởi tạo TasksView theo quyền.
        - Pack view vào vùng nội dung.
        """
        self.clear_content_area()
        self.tasks_page = TasksView(self.content_area, actor=self.current_actor(), can_manage=self.auth_vm.can_manage_work())
        self.tasks_page.pack(fill="both", expand=True)

    def show_matrix_view(self):
        """Mở màn ma trận Eisenhower."""
        self.clear_content_area()
        all_tasks = self.tasks_page.view_model.all_tasks if self.tasks_page else TaskViewModel(actor=self.current_actor(), can_manage=False).all_tasks
        EisenhowerView(self.content_area, all_tasks).pack(fill="both", expand=True)

    def show_timeline_view(self):
        """Mở màn timeline dạng Gantt mini."""
        self.clear_content_area()
        TimelineView(self.content_area, actor=self.current_actor()).pack(fill="both", expand=True)

    def show_stats_view(self):
        """Mở màn thống kê tổng quan."""
        self.clear_content_area()
        StatsView(self.content_area).pack(fill="both", expand=True)

    def show_logs_view(self):
        """Mở màn nhật ký hệ thống."""
        self.clear_content_area()
        AuditLogsView(self.content_area, actor=self.current_actor()).pack(fill="both", expand=True)

    def show_tools_view(self):
        """Mở màn công cụ hệ thống (export/backup)."""
        self.clear_content_area()
        SystemToolsView(self.content_area, actor=self.current_actor()).pack(fill="both", expand=True)

    def show_users_view(self):
        """Mở màn quản lý tài khoản (admin)."""
        self.clear_content_area()
        UsersView(self.content_area, self.auth_vm).pack(fill="both", expand=True)

    def start_logout_flow(self):
        """
        Mục đích:
        - Hiển thị màn đăng xuất có tiến trình trước khi về login.

        Input:
        - Không nhận tham số trực tiếp.

        Output:
        - Màn hình trung gian đăng xuất + progress bar.

        Luồng xử lý chính:
        - Xóa giao diện dashboard.
        - Dựng panel đăng xuất.
        - Bắt đầu animate progress và kết thúc bằng show_auth_screen.
        """
        self.clear_window()
        self.geometry("500x620")
        self.minsize(500, 580)

        shell = ctk.CTkFrame(self, fg_color=("#eef2ff", "#111827"))
        shell.pack(fill="both", expand=True)
        panel = ctk.CTkFrame(shell, corner_radius=18, fg_color=("#ffffff", "#202020"))
        panel.pack(fill="both", expand=True, padx=46, pady=46)

        ctk.CTkLabel(panel, text="Đang đăng xuất...", font=("Segoe UI", 26, "bold"), text_color=("#1d4ed8", "#60a5fa")).pack(
            pady=(110, 10)
        )
        ctk.CTkLabel(
            panel, text="Hệ thống đang kết thúc phiên làm việc, vui lòng chờ.", font=("Segoe UI", 13), text_color="#94a3b8"
        ).pack(pady=(0, 22))

        self.logout_progress = ctk.CTkProgressBar(panel, width=340, height=14)
        self.logout_progress.set(0)
        self.logout_progress.pack(pady=(0, 12))
        self.logout_percent_label = ctk.CTkLabel(panel, text="0%", font=("Segoe UI", 13, "bold"), text_color="#60a5fa")
        self.logout_percent_label.pack()

        self._animate_logout_progress(0)

    def _animate_logout_progress(self, value):
        """Animate progress đăng xuất và kết thúc phiên."""
        self.logout_progress.set(value / 100)
        self.logout_percent_label.configure(text=f"{value}%")
        if value >= 100:
            self._logout_after_id = None
            self.show_auth_screen()
            return
        next_value = min(100, value + 10)
        self._logout_after_id = self.after(55, lambda: self._animate_logout_progress(next_value))


class StatsView(ctk.CTkFrame):
    """View thống kê số liệu dự án/công việc."""

    def __init__(self, master):
        """Khởi tạo dữ liệu thống kê để render dashboard."""
        super().__init__(master, fg_color="transparent")
        self.project_vm = ProjectViewModel(can_manage=False)
        self.task_vm = TaskViewModel(can_manage=False)
        self.setup_ui()

    def setup_ui(self):
        """Dựng các nhóm thống kê: card, tiến độ, ưu tiên, deadline."""
        ctk.CTkLabel(self, text="Thống kê tổng quan", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=24, pady=(24, 14))
        stats = self.task_vm.get_stats()
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(0, 18))

        self.create_card(cards, "Dự án", len(self.project_vm.all_projects), "#2563eb").pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.create_card(cards, "Công việc", stats["total"], "#7c3aed").pack(side="left", fill="x", expand=True, padx=8)
        self.create_card(cards, "Đang làm", stats["todo"], "#f59e0b").pack(side="left", fill="x", expand=True, padx=8)
        self.create_card(cards, "Hoàn thành", stats["done"], "#16a34a").pack(side="left", fill="x", expand=True, padx=(8, 0))

        progress_frame = ctk.CTkFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        progress_frame.pack(fill="x", padx=24, pady=(0, 18))
        ctk.CTkLabel(progress_frame, text=f"Tiến độ hoàn thành: {stats['progress']}%", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=18, pady=(16, 8)
        )
        progress = ctk.CTkProgressBar(progress_frame, height=14)
        progress.set(stats["progress"] / 100 if stats["total"] else 0)
        progress.pack(fill="x", padx=18, pady=(0, 18))

        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        lower.grid_columnconfigure((0, 1), weight=1, uniform="stats")
        lower.grid_rowconfigure(0, weight=1)

        priority_frame = ctk.CTkFrame(lower, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        priority_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(priority_frame, text="Phân bổ ưu tiên", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(16, 10))
        for priority, count in stats["priorities"].items():
            row = ctk.CTkFrame(priority_frame, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=6)
            ctk.CTkLabel(row, text=priority, width=55, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, height=12)
            bar.set(count / stats["total"] if stats["total"] else 0)
            bar.pack(side="left", fill="x", expand=True, padx=12)
            ctk.CTkLabel(row, text=str(count), width=40).pack(side="right")

        deadline_frame = ctk.CTkFrame(lower, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        deadline_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(deadline_frame, text="Theo dõi deadline", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            deadline_frame, text=f"Quá hạn: {stats['overdue']}  |  Sắp tới 7 ngày: {stats['upcoming']}", text_color="#94a3b8"
        ).pack(anchor="w", padx=18, pady=(0, 12))

        urgent_tasks = self.task_vm.get_deadline_insights(limit=6)
        if not urgent_tasks:
            ctk.CTkLabel(deadline_frame, text="Không có công việc cần nhắc deadline.", text_color="#94a3b8").pack(pady=30)
            return

        for task, label, color in urgent_tasks:
            row = ctk.CTkFrame(deadline_frame, fg_color=("#ffffff", "#202020"), corner_radius=8)
            row.pack(fill="x", padx=18, pady=5)
            ctk.CTkLabel(row, text=task.name, anchor="w", font=("Segoe UI", 12, "bold"), wraplength=320).pack(fill="x", padx=12, pady=(8, 0))
            ctk.CTkLabel(row, text=f"{task.task_id} - {task.deadline or '-'} - {label}", anchor="w", text_color=color).pack(
                fill="x", padx=12, pady=(0, 8)
            )

    def create_card(self, parent, label, value, color):
        """Tạo card số liệu dùng lại trong khu vực thống kê."""
        card = ctk.CTkFrame(parent, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        ctk.CTkLabel(card, text=label, text_color="#94a3b8", font=("Segoe UI", 13)).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkLabel(card, text=str(value), text_color=color, font=("Segoe UI", 30, "bold")).pack(anchor="w", padx=16, pady=(0, 14))
        return card


if __name__ == "__main__":
    app = ProjectManagerApp()
    app.mainloop()
