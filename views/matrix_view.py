import customtkinter as ctk

from viewmodels.matrix_viewmodel import EisenhowerViewModel
from viewmodels.task_mananger_viewmodel import TaskViewModel


class EisenhowerView(ctk.CTkFrame):
    def __init__(self, master, all_tasks=None):
        super().__init__(master, fg_color="transparent")
        tasks = all_tasks if all_tasks else TaskViewModel().all_tasks
        self.view_model = EisenhowerViewModel(tasks)
        self.setup_ui()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))
        ctk.CTkLabel(header, text="Ma trận Eisenhower", font=("Segoe UI", 26, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Phân loại theo mức ưu tiên P1-P4", text_color="#94a3b8").pack(side="right")

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.grid_container.grid_columnconfigure((0, 1), weight=1, uniform="matrix")
        self.grid_container.grid_rowconfigure((0, 1), weight=1, uniform="matrix")

        quadrants = [
            {
                "pos": (0, 0),
                "title": "Làm ngay",
                "sub": "Khẩn cấp và quan trọng",
                "color": ("#fee2e2", "#2b1717"),
                "accent": "#ef4444",
                "priority": "P1",
            },
            {
                "pos": (0, 1),
                "title": "Lên lịch",
                "sub": "Quan trọng nhưng chưa khẩn",
                "color": ("#dcfce7", "#142719"),
                "accent": "#22c55e",
                "priority": "P2",
            },
            {
                "pos": (1, 0),
                "title": "Ủy quyền",
                "sub": "Khẩn nhưng ít quan trọng",
                "color": ("#fef3c7", "#2c2411"),
                "accent": "#f59e0b",
                "priority": "P3",
            },
            {
                "pos": (1, 1),
                "title": "Loại bỏ",
                "sub": "Ít khẩn và ít quan trọng",
                "color": ("#e5e7eb", "#202020"),
                "accent": "#94a3b8",
                "priority": "P4",
            },
        ]

        for quadrant in quadrants:
            frame = ctk.CTkFrame(
                self.grid_container,
                fg_color=quadrant["color"],
                border_color=quadrant["accent"],
                border_width=2,
                corner_radius=10,
            )
            frame.grid(row=quadrant["pos"][0], column=quadrant["pos"][1], padx=8, pady=8, sticky="nsew")

            title_bar = ctk.CTkFrame(frame, fg_color="transparent")
            title_bar.pack(fill="x", padx=14, pady=(12, 6))
            ctk.CTkLabel(title_bar, text=quadrant["title"], font=("Segoe UI", 16, "bold"), text_color=quadrant["accent"]).pack(
                side="left"
            )
            tasks = self.view_model.get_tasks_by_priority(quadrant["priority"])
            ctk.CTkLabel(title_bar, text=str(len(tasks)), text_color=quadrant["accent"], font=("Segoe UI", 15, "bold")).pack(
                side="right"
            )
            ctk.CTkLabel(frame, text=quadrant["sub"], text_color="#94a3b8", anchor="w").pack(fill="x", padx=14)

            tasks_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            tasks_scroll.pack(fill="both", expand=True, padx=10, pady=10)

            if not tasks:
                ctk.CTkLabel(tasks_scroll, text="Chưa có công việc", text_color="#94a3b8").pack(pady=20)
            else:
                for task in tasks:
                    status = "Hoàn thành" if task.status == "Done" else "Đang làm"
                    item = ctk.CTkFrame(tasks_scroll, fg_color=("#ffffff", "#171717"), corner_radius=8)
                    item.pack(fill="x", pady=4)
                    ctk.CTkLabel(item, text=task.name, anchor="w", font=("Segoe UI", 12, "bold"), wraplength=280).pack(
                        fill="x", padx=10, pady=(8, 0)
                    )
                    ctk.CTkLabel(item, text=f"{task.task_id} • {task.deadline or '-'} • {status}", anchor="w", text_color="#94a3b8").pack(
                        fill="x", padx=10, pady=(0, 8)
                    )
