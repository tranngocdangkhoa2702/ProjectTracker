import tkinter as tk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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
    """Class chính dùng để điều khiển các màn hình của chương trình."""

    def __init__(self):
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
        """Xóa các widget đang có trên cửa sổ."""
        if self._logout_after_id is not None:
            self.after_cancel(self._logout_after_id)
            self._logout_after_id = None
        for widget in self.winfo_children():
            widget.destroy()

    def show_auth_screen(self):
        """Mở màn hình đăng nhập."""
        self.auth_vm.logout()
        self.clear_window()
        self.geometry("500x620")
        self.minsize(500, 580)

        shell = ctk.CTkFrame(self, fg_color=("#eef2ff", "#111827"))
        shell.pack(fill="both", expand=True)
        self.auth_frame = AuthFrame(shell, self.auth_vm, self.show_main_dashboard)
        self.auth_frame.pack(fill="both", expand=True, padx=46, pady=46)

    def show_main_dashboard(self):
        """Hiển thị giao diện chính sau khi đăng nhập thành công."""
        self.clear_window()
        self.tasks_page = None
        self.geometry("1240x780")
        self.minsize(1040, 680)

        self.main_container = ctk.CTkFrame(self, fg_color=("#f8fafc", "#0f172a"))
        self.main_container.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(self.main_container, width=260, corner_radius=0, fg_color=("#ffffff", "#111827"))
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="Theo dõi đồ án", font=("Segoe UI", 22, "bold"), text_color=("#1d4ed8", "#60a5fa")).pack(
            pady=(28, 4), padx=18, anchor="w"
        )
        ctk.CTkLabel(sidebar, text="Nhóm 6_Đề Tài 15_Project Tracker", font=("Segoe UI", 12), text_color="#94a3b8").pack(
            pady=(0, 18), padx=18, anchor="w"
        )
        self.create_user_badge(sidebar)

        nav_items = [
            ("projects", "Dự án", self.show_projects_view),
            ("tasks", "Công việc", self.show_tasks_view),
            ("matrix", "Ma trận", self.show_matrix_view),
            ("timeline", "Dòng thời gian", self.show_timeline_view),
            ("stats", "Thống kê", self.show_stats_view),
        ]
        if self.auth_vm.is_admin():
            nav_items.append(("logs", "Nhật ký", self.show_logs_view))
            nav_items.append(("tools", "Công cụ", self.show_tools_view))
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
        """Lấy tên user hiện tại để ghi log."""
        user = self.auth_vm.current_user or {}
        return user.get("username", "system")

    def current_role(self):
        """Lay role hien tai de truyen xuong lop nghiep vu."""
        return self.auth_vm.user_role()

    def create_user_badge(self, parent):
        """Hiển thị thông tin tài khoản trên sidebar."""
        user = self.auth_vm.current_user or {}
        role_map = {"admin": "Quản trị viên", "leader": "Trưởng nhóm", "member": "Thành viên"}
        role = role_map.get(user.get("role"), "Thành viên")
        badge = ctk.CTkFrame(parent, fg_color=("#f1f5f9", "#1f2937"), corner_radius=10)
        badge.pack(fill="x", padx=14, pady=(0, 18))
        ctk.CTkLabel(badge, text=user.get("username", "guest"), font=("Segoe UI", 14, "bold"), anchor="w").pack(
            fill="x", padx=12, pady=(10, 0)
        )
        ctk.CTkLabel(badge, text=role, text_color=("#2563eb", "#93c5fd"), font=("Segoe UI", 12), anchor="w").pack(
            fill="x", padx=12, pady=(0, 10)
        )

    def create_sidebar_button(self, parent, text, command):
        """Tạo nút menu bên trái."""
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
        """Chuyển màn hình theo nút menu được chọn."""
        for key, button in self.sidebar_buttons.items():
            if key == active_key:
                button.configure(fg_color=("#dbeafe", "#1e3a8a"), text_color=("#1d4ed8", "#ffffff"))
            else:
                button.configure(fg_color="transparent", text_color=("#334155", "#e5e7eb"))
        command()

    def clear_content_area(self):
        """Dọn vùng nội dung trước khi mở view mới."""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_projects_view(self):
        """Mở màn quản lý dự án."""
        self.clear_content_area()
        ProjectsView(self.content_area, actor=self.current_actor(), actor_role=self.current_role()).pack(fill="both", expand=True)

    def show_tasks_view(self):
        """Mở màn quản lý công việc."""
        self.clear_content_area()
        self.tasks_page = TasksView(self.content_area, actor=self.current_actor(), actor_role=self.current_role())
        self.tasks_page.pack(fill="both", expand=True)

    def show_matrix_view(self):
        """Mở màn ma trận Eisenhower."""
        self.clear_content_area()
        all_tasks = TaskViewModel(actor=self.current_actor(), actor_role=self.current_role()).scoped_tasks()
        EisenhowerView(self.content_area, all_tasks).pack(fill="both", expand=True)

    def show_timeline_view(self):
        """Mở màn timeline dạng Gantt mini."""
        self.clear_content_area()
        TimelineView(self.content_area, actor=self.current_actor(), actor_role=self.current_role()).pack(fill="both", expand=True)

    def show_stats_view(self):
        """Mở màn thống kê tổng quan."""
        self.clear_content_area()
        StatsView(self.content_area, actor=self.current_actor(), actor_role=self.current_role()).pack(fill="both", expand=True)

    def show_logs_view(self):
        """Mở màn nhật ký hệ thống."""
        self.clear_content_area()
        AuditLogsView(self.content_area, actor=self.current_actor(), actor_role=self.current_role()).pack(fill="both", expand=True)

    def show_tools_view(self):
        """Mở màn công cụ hệ thống (export/backup)."""
        self.clear_content_area()
        SystemToolsView(self.content_area, actor=self.current_actor(), actor_role=self.current_role()).pack(fill="both", expand=True)

    def show_users_view(self):
        """Mở màn quản lý tài khoản (admin)."""
        self.clear_content_area()
        UsersView(self.content_area, self.auth_vm).pack(fill="both", expand=True)

    def start_logout_flow(self):
        """Hiển thị màn chờ đăng xuất."""
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
        """Chạy thanh tiến trình khi đăng xuất."""
        self.logout_progress.set(value / 100)
        self.logout_percent_label.configure(text=f"{value}%")
        if value >= 100:
            self._logout_after_id = None
            self.show_auth_screen()
            return
        next_value = min(100, value + 10)
        self._logout_after_id = self.after(55, lambda: self._animate_logout_progress(next_value))


class StatsView(ctk.CTkFrame):
    """Màn thống kê tổng quan."""

    def __init__(self, master, actor="system", actor_role="member"):
        super().__init__(master, fg_color="transparent")
        self.project_vm = ProjectViewModel(actor=actor, actor_role=actor_role)
        self.task_vm = TaskViewModel(actor=actor, actor_role=actor_role)
        self.setup_ui()

    def setup_ui(self):
        """Tạo giao diện thống kê."""
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="Thống kê tổng quan", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=24, pady=(24, 14))
        stats = self.task_vm.get_stats()
        cards = ctk.CTkFrame(container, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(0, 18))

        self.create_card(cards, "Dự án", len(self.project_vm.scoped_projects()), "#2563eb").pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.create_card(cards, "Công việc", stats["total"], "#7c3aed").pack(side="left", fill="x", expand=True, padx=8)
        self.create_card(cards, "Chưa xong", stats["total"] - stats["done"], "#f59e0b").pack(side="left", fill="x", expand=True, padx=8)
        self.create_card(cards, "Hoàn thành", stats["done"], "#16a34a").pack(side="left", fill="x", expand=True, padx=(8, 0))

        progress_frame = ctk.CTkFrame(container, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        progress_frame.pack(fill="x", padx=24, pady=(0, 18))
        ctk.CTkLabel(progress_frame, text=f"Tiến độ hoàn thành: {stats['progress']}%", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=18, pady=(16, 8)
        )
        progress = ctk.CTkProgressBar(progress_frame, height=14)
        progress.set(stats["progress"] / 100 if stats["total"] else 0)
        progress.pack(fill="x", padx=18, pady=(0, 18))

        labels, weekly_values = self.task_vm.get_weekly_completion()
        self.create_matplotlib_chart(container, "Tiến độ hoàn thành theo tuần", labels, weekly_values).pack(fill="x", padx=24, pady=(0, 18))

        lower = ctk.CTkFrame(container, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        lower.grid_columnconfigure((0, 1), weight=1, uniform="stats")
        lower.grid_rowconfigure(0, weight=1)

        status_data = {
            "Chưa làm": len([task for task in self.task_vm.scoped_tasks() if task.status == "Chưa làm"]),
            "Đang làm": len([task for task in self.task_vm.scoped_tasks() if task.status == "Đang làm"]),
            "Chờ duyệt": len([task for task in self.task_vm.scoped_tasks() if task.status == "Chờ duyệt"]),
            "Hoàn thành": stats["done"],
        }
        deadline_data = {
            "Quá hạn": stats["overdue"],
            "Sắp tới": stats["upcoming"],
            "Ổn định": max(0, stats["total"] - stats["overdue"] - stats["upcoming"]),
        }

        left = ctk.CTkFrame(lower, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = ctk.CTkFrame(lower, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.create_bar_chart(left, "Biểu đồ trạng thái", status_data, ["#60a5fa", "#f59e0b", "#a78bfa", "#22c55e"]).pack(
            fill="both", expand=True, pady=(0, 10)
        )
        self.create_bar_chart(left, "Phân bổ ưu tiên", stats["priorities"], ["#ef4444", "#f59e0b", "#22c55e", "#94a3b8"]).pack(
            fill="both", expand=True
        )
        self.create_donut_chart(right, "Theo dõi deadline", deadline_data, ["#ef4444", "#f59e0b", "#22c55e"]).pack(fill="x")

        urgent_tasks = self.task_vm.get_deadline_insights(limit=4)
        if urgent_tasks:
            list_frame = ctk.CTkFrame(right, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
            list_frame.pack(fill="x", pady=(10, 0))
            ctk.CTkLabel(list_frame, text="Việc cần chú ý", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
            for task, label, color in urgent_tasks:
                row = ctk.CTkFrame(list_frame, fg_color=("#ffffff", "#202020"), corner_radius=8)
                row.pack(fill="x", padx=8, pady=4)
                ctk.CTkLabel(row, text=task.name, anchor="w", font=("Segoe UI", 12, "bold"), wraplength=280).pack(
                    fill="x", padx=12, pady=(7, 0)
                )
                ctk.CTkLabel(row, text=f"{task.task_id} - {task.deadline or '-'} - {label}", anchor="w", text_color=color).pack(
                    fill="x", padx=12, pady=(0, 7)
                )

    def create_bar_chart(self, parent, title, data, colors):
        panel = ctk.CTkFrame(parent, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        ctk.CTkLabel(panel, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(14, 8))
        canvas = tk.Canvas(panel, height=160, bg="#171717", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        def draw():
            canvas.delete("all")
            width = max(canvas.winfo_width(), 320)
            max_value = max(data.values()) if data else 1
            max_value = max(max_value, 1)
            row_height = 34
            for index, (label, value) in enumerate(data.items()):
                y = 18 + index * row_height
                bar_width = int((width - 150) * (value / max_value))
                color = colors[index % len(colors)]
                canvas.create_text(4, y, anchor="w", text=label, fill="#e5e7eb", font=("Segoe UI", 10, "bold"))
                canvas.create_rectangle(110, y - 8, width - 38, y + 8, fill="#374151", outline="")
                canvas.create_rectangle(110, y - 8, 110 + bar_width, y + 8, fill=color, outline="")
                canvas.create_text(width - 18, y, anchor="e", text=str(value), fill="#e5e7eb", font=("Segoe UI", 10, "bold"))

        canvas.bind("<Configure>", lambda _event: draw())
        panel.after(80, draw)
        return panel

    def create_donut_chart(self, parent, title, data, colors):
        panel = ctk.CTkFrame(parent, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        ctk.CTkLabel(panel, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(14, 8))
        canvas = tk.Canvas(panel, height=190, bg="#171717", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        def draw():
            canvas.delete("all")
            width = max(canvas.winfo_width(), 320)
            total = sum(data.values())
            x0, y0, size = 28, 18, 120
            if total <= 0:
                canvas.create_oval(x0, y0, x0 + size, y0 + size, outline="#374151", width=24)
                canvas.create_text(x0 + size / 2, y0 + size / 2, text="0", fill="#e5e7eb", font=("Segoe UI", 24, "bold"))
            else:
                start = 90
                for index, (label, value) in enumerate(data.items()):
                    extent = 360 * value / total
                    canvas.create_arc(
                        x0,
                        y0,
                        x0 + size,
                        y0 + size,
                        start=start,
                        extent=-extent,
                        style="arc",
                        outline=colors[index % len(colors)],
                        width=24,
                    )
                    start -= extent
                canvas.create_text(x0 + size / 2, y0 + size / 2, text=str(total), fill="#e5e7eb", font=("Segoe UI", 24, "bold"))

            legend_x = min(width - 190, 210)
            for index, (label, value) in enumerate(data.items()):
                y = 42 + index * 34
                color = colors[index % len(colors)]
                canvas.create_rectangle(legend_x, y - 7, legend_x + 14, y + 7, fill=color, outline="")
                canvas.create_text(legend_x + 24, y, anchor="w", text=f"{label}: {value}", fill="#e5e7eb", font=("Segoe UI", 10, "bold"))

        canvas.bind("<Configure>", lambda _event: draw())
        panel.after(80, draw)
        return panel

    def create_line_chart(self, parent, title, labels, values):
        panel = ctk.CTkFrame(parent, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        ctk.CTkLabel(panel, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(14, 2))
        ctk.CTkLabel(
            panel,
            text="Mỗi điểm là số công việc được chuyển sang Hoàn thành trong tuần đó.",
            text_color="#94a3b8",
            font=("Segoe UI", 11),
        ).pack(anchor="w", padx=18, pady=(0, 6))
        canvas = tk.Canvas(panel, height=170, bg="#171717", highlightthickness=0)
        canvas.pack(fill="x", padx=18, pady=(0, 14))

        def draw():
            canvas.delete("all")
            width = max(canvas.winfo_width(), 420)
            height = max(canvas.winfo_height(), 160)
            left, right, top, bottom = 42, 18, 18, 36
            chart_w = width - left - right
            chart_h = height - top - bottom
            max_value = max(values) if values else 0
            max_value = max(max_value, 1)

            canvas.create_line(left, top, left, top + chart_h, fill="#475569")
            canvas.create_line(left, top + chart_h, left + chart_w, top + chart_h, fill="#475569")
            for step in range(max_value + 1):
                y = top + chart_h - (step / max_value) * chart_h
                canvas.create_line(left, y, left + chart_w, y, fill="#273244")
                canvas.create_text(left - 10, y, text=str(step), anchor="e", fill="#94a3b8", font=("Segoe UI", 8))

            if not labels:
                return
            points = []
            gap = chart_w / max(len(labels) - 1, 1)
            for index, value in enumerate(values):
                x = left + index * gap
                y = top + chart_h - (value / max_value) * chart_h
                points.append((x, y))
                canvas.create_text(x, top + chart_h + 16, text=labels[index], fill="#94a3b8", font=("Segoe UI", 8))
                canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#60a5fa", outline="")
                canvas.create_text(x, y - 12, text=str(value), fill="#e5e7eb", font=("Segoe UI", 8, "bold"))
            for first, second in zip(points, points[1:]):
                canvas.create_line(first[0], first[1], second[0], second[1], fill="#60a5fa", width=3)

        canvas.bind("<Configure>", lambda _event: draw())
        panel.after(80, draw)
        return panel

    def create_matplotlib_chart(self, parent, title, labels, values):
        """Vẽ biểu đồ đường (Line chart) bằng Matplotlib và nhúng trực tiếp vào giao diện.

        Số liệu lấy từ TaskViewModel.get_weekly_completion() do nhóm Backend (SV1) cung cấp.
        Biểu đồ có đủ Title, nhãn trục X/Y và Legend theo yêu cầu.
        """
        panel = ctk.CTkFrame(parent, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        ctk.CTkLabel(panel, text=f"{title} (Matplotlib)", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(14, 4))

        figure = Figure(figsize=(7, 2.7), dpi=100, facecolor="#171717")
        axes = figure.add_subplot(111)
        axes.set_facecolor("#171717")
        axes.plot(labels, values, marker="o", color="#60a5fa", linewidth=2, label="Công việc hoàn thành")
        axes.set_title(title, color="#e5e7eb")
        axes.set_xlabel("Tuần (ngày bắt đầu)", color="#cbd5e1")
        axes.set_ylabel("Số công việc", color="#cbd5e1")
        axes.tick_params(colors="#94a3b8")
        for spine in axes.spines.values():
            spine.set_color("#475569")
        axes.grid(True, color="#273244", linestyle="--", linewidth=0.6)
        axes.legend(facecolor="#202020", edgecolor="#475569", labelcolor="#e5e7eb")
        max_value = max(values) if values else 0
        axes.set_yticks(range(0, max_value + 1))
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0, 12))
        return panel

    def create_card(self, parent, label, value, color):
        """Tạo một ô số liệu nhỏ."""
        card = ctk.CTkFrame(parent, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        ctk.CTkLabel(card, text=label, text_color="#94a3b8", font=("Segoe UI", 13)).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkLabel(card, text=str(value), text_color=color, font=("Segoe UI", 30, "bold")).pack(anchor="w", padx=16, pady=(0, 14))
        return card


if __name__ == "__main__":
    app = ProjectManagerApp()
    app.mainloop()
