import customtkinter as ctk

from viewmodels.matrix_viewmodel import EisenhowerViewModel
from viewmodels.task_mananger_viewmodel import TaskViewModel


class EisenhowerView(ctk.CTkFrame):
    def __init__(self, master, all_tasks=None):
        super().__init__(master, fg_color="transparent")
        tasks = all_tasks if all_tasks else TaskViewModel().all_tasks
        self.view_model = EisenhowerViewModel(tasks)
        self.all_tasks = tasks
        self.setup_ui()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 8))
        ctk.CTkLabel(header, text="Ma trận Eisenhower", font=("Segoe UI", 26, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Phân loại theo Khẩn cấp / Quan trọng", text_color="#94a3b8").pack(side="right")

        summary = ctk.CTkFrame(self, fg_color="transparent")
        summary.pack(fill="x", padx=24, pady=(0, 10))
        total = len(self.all_tasks)
        done = len([task for task in self.all_tasks if task.status == "Hoàn thành"])
        pending = total - done
        for label, value, color in [
            ("Tổng công việc", total, "#60a5fa"),
            ("Chưa hoàn thành", pending, "#f59e0b"),
            ("Đã hoàn thành", done, "#22c55e"),
            ("Khẩn cấp & quan trọng", len(self.view_model.get_tasks_by_flags(True, True)), "#ef4444"),
        ]:
            card = ctk.CTkFrame(summary, fg_color=("#f3f4f6", "#171717"), corner_radius=8)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkLabel(card, text=label, text_color="#94a3b8", anchor="w").pack(fill="x", padx=14, pady=(10, 0))
            ctk.CTkLabel(card, text=str(value), text_color=color, font=("Segoe UI", 24, "bold"), anchor="w").pack(fill="x", padx=14, pady=(0, 10))

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.grid_container.grid_columnconfigure((0, 1), weight=1, uniform="matrix")
        self.grid_container.grid_rowconfigure((0, 1), weight=1, uniform="matrix")

        quadrants = [
            {
                "pos": (0, 0),
                "title": "Làm ngay",
                "sub": "Khẩn cấp và quan trọng",
                "hint": "Ưu tiên xử lý trước trong hôm nay.",
                "color": ("#fee2e2", "#2b1717"),
                "accent": "#ef4444",
                "urgent": True,
                "important": True,
            },
            {
                "pos": (0, 1),
                "title": "Lên lịch",
                "sub": "Quan trọng nhưng chưa khẩn",
                "hint": "Đưa vào kế hoạch làm việc tuần này.",
                "color": ("#dcfce7", "#142719"),
                "accent": "#22c55e",
                "urgent": False,
                "important": True,
            },
            {
                "pos": (1, 0),
                "title": "Ủy quyền",
                "sub": "Khẩn nhưng ít quan trọng",
                "hint": "Giao cho thành viên phù hợp theo dõi.",
                "color": ("#fef3c7", "#2c2411"),
                "accent": "#f59e0b",
                "urgent": True,
                "important": False,
            },
            {
                "pos": (1, 1),
                "title": "Theo dõi sau",
                "sub": "Ít khẩn và ít quan trọng",
                "hint": "Chỉ xử lý khi các việc chính đã ổn.",
                "color": ("#e5e7eb", "#202020"),
                "accent": "#94a3b8",
                "urgent": False,
                "important": False,
            },
        ]

        for quadrant in quadrants:
            self._create_quadrant(quadrant)

    def _create_quadrant(self, quadrant):
        tasks = self.view_model.get_tasks_by_flags(quadrant["urgent"], quadrant["important"])
        frame = ctk.CTkFrame(
            self.grid_container,
            fg_color=quadrant["color"],
            border_color=quadrant["accent"],
            border_width=2,
            corner_radius=10,
        )
        frame.grid(row=quadrant["pos"][0], column=quadrant["pos"][1], padx=8, pady=8, sticky="nsew")

        title_bar = ctk.CTkFrame(frame, fg_color="transparent")
        title_bar.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(title_bar, text=quadrant["title"], font=("Segoe UI", 17, "bold"), text_color=quadrant["accent"]).pack(side="left")
        ctk.CTkLabel(title_bar, text=str(len(tasks)), text_color=quadrant["accent"], font=("Segoe UI", 18, "bold")).pack(side="right")
        ctk.CTkLabel(frame, text=quadrant["sub"], text_color="#cbd5e1", anchor="w").pack(fill="x", padx=14)
        ctk.CTkLabel(frame, text=quadrant["hint"], text_color="#94a3b8", anchor="w", font=("Segoe UI", 11)).pack(fill="x", padx=14, pady=(2, 6))

        tasks_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        tasks_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        if not tasks:
            ctk.CTkLabel(tasks_scroll, text="Chưa có công việc", text_color="#94a3b8").pack(pady=20)
            return

        for task in tasks:
            item = ctk.CTkFrame(tasks_scroll, fg_color=("#ffffff", "#111111"), corner_radius=8)
            item.pack(fill="x", pady=5)
            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(8, 0))
            ctk.CTkLabel(top, text=task.name, anchor="w", font=("Segoe UI", 12, "bold"), wraplength=310).pack(side="left", fill="x", expand=True)
            badge_color = "#22c55e" if task.status == "Hoàn thành" else "#2563eb"
            ctk.CTkLabel(top, text=task.status, text_color=badge_color, font=("Segoe UI", 11, "bold")).pack(side="right")

            meta = f"{task.task_id} | {task.project_id or '-'} | Hạn: {task.deadline or '-'}"
            assignee = f" | Giao: {task.assignee}" if task.assignee else ""
            ctk.CTkLabel(item, text=meta + assignee, anchor="w", text_color="#94a3b8", wraplength=390).pack(
                fill="x", padx=10, pady=(2, 8)
            )
