import customtkinter as ctk

from ProjectTracker.viewmodels.matrix_viewmodel import EisenhowerViewModel
from ProjectTracker.viewmodels.task_mananger_viewmodel import TaskViewModel


class EisenhowerView(ctk.CTkFrame):
    def __init__(self, master, all_tasks):
        super().__init__(master)
        self.all_tasks = TaskViewModel().all_tasks
        self.view_model = EisenhowerViewModel(all_tasks)
        self.setup_ui()

    def setup_ui(self):
        # Tiêu đề
        ctk.CTkLabel(self, text="🗄️ MA TRẬN EISENHOWER (Phân loại)",
                     font=("Arial", 22, "bold")).pack(pady=20, anchor="w", padx=20)

        # Container chứa 4 ô (Grid 2x2)
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=20, pady=10)
        self.grid_container.grid_columnconfigure((0, 1), weight=1)
        self.grid_container.grid_rowconfigure((0, 1), weight=1)

        # Định nghĩa cấu hình cho 4 ô
        quadrants = [
            {"pos": (0, 0), "title": "DO FIRST (P1)", "sub": "Khẩn & Quan trọng", "color": "#441a1a", "border": "#ff4d4d", "p": "P1"},
            {"pos": (0, 1), "title": "SCHEDULE (P2)", "sub": "Không khẩn & Quan trọng", "color": "#1a2e1a", "border": "#4dff4d", "p": "P2"},
            {"pos": (1, 0), "title": "DELEGATE (P3)", "sub": "Khẩn & Không quan trọng", "color": "#2e2b1a", "border": "#ffcc00", "p": "P3"},
            {"pos": (1, 1), "title": "DELETE (P4)", "sub": "Không khẩn & Không quan trọng", "color": "#252526", "border": "#808080", "p": "P4"}
        ]

        for q in quadrants:
            # Tạo khung cho từng ô
            frame = ctk.CTkFrame(self.grid_container, fg_color=q["color"],
                                 border_color=q["border"], border_width=2)
            frame.grid(row=q["pos"][0], column=q["pos"][1], padx=10, pady=10, sticky="nsew")

            # Tiêu đề ô
            ctk.CTkLabel(frame, text=q["title"], font=("Arial", 14, "bold"), text_color=q["border"]).pack(pady=(10, 0))
            ctk.CTkLabel(frame, text=q["sub"], font=("Arial", 11), text_color=q["border"]).pack(pady=(0, 10))

            # Danh sách công việc bên trong mỗi ô
            tasks_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            tasks_scroll.pack(fill="both", expand=True, padx=5, pady=5)

            tasks = self.view_model.get_tasks_by_priority(q["p"])
            if not tasks:
                ctk.CTkLabel(tasks_scroll, text="(Trống)", text_color="gray").pack()
            else:
                for t in tasks:
                    task_label = ctk.CTkLabel(tasks_scroll, text=f"• {t.name}", anchor="w", font=("Arial", 12))
                    task_label.pack(fill="x", padx=10)