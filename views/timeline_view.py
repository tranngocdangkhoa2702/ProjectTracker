import customtkinter as ctk
from datetime import datetime

from viewmodels.task_mananger_viewmodel import TaskViewModel


class TimelineView(ctk.CTkFrame):
    """Màn timeline dạng Gantt mini theo deadline task."""

    def __init__(self, master, actor="system"):
        """Khởi tạo dữ liệu timeline ở chế độ chỉ xem."""
        super().__init__(master, fg_color="transparent")
        self.vm = TaskViewModel(actor=actor, can_manage=False)
        self.setup_ui()

    def setup_ui(self):
        """Render danh sách task theo trục thời gian deadline."""
        ctk.CTkLabel(self, text="Timeline (Gantt mini)", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=24, pady=(24, 14))
        items = self.vm.get_timeline_items()
        if not items:
            ctk.CTkLabel(self, text="Chưa có dữ liệu deadline hợp lệ (dd/mm).", text_color="#94a3b8").pack(anchor="w", padx=24)
            return

        now = datetime.now().date()
        deltas = [abs((deadline - now).days) for _, deadline in items]
        max_span = max(deltas) if deltas else 1
        if max_span == 0:
            max_span = 1

        container = ctk.CTkScrollableFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        container.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        for task, deadline in items:
            delta = (deadline - now).days
            ratio = min(1.0, abs(delta) / max_span)
            bar_color = "#ef4444" if delta < 0 else ("#f59e0b" if delta <= 7 else "#22c55e")
            note = f"Quá hạn {abs(delta)} ngày" if delta < 0 else (f"Còn {delta} ngày" if delta > 0 else "Hạn hôm nay")

            card = ctk.CTkFrame(container, fg_color=("#ffffff", "#202020"), corner_radius=8)
            card.pack(fill="x", padx=8, pady=6)
            ctk.CTkLabel(card, text=f"{task.task_id} - {task.name}", font=("Segoe UI", 13, "bold"), anchor="w").pack(
                fill="x", padx=12, pady=(10, 2)
            )
            ctk.CTkLabel(card, text=f"Deadline: {task.deadline} | {note}", text_color="#94a3b8", anchor="w").pack(
                fill="x", padx=12, pady=(0, 8)
            )
            bar = ctk.CTkProgressBar(card, progress_color=bar_color, height=12)
            bar.set(ratio)
            bar.pack(fill="x", padx=12, pady=(0, 12))
