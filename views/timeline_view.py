import json
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path

import customtkinter as ctk

from viewmodels.task_mananger_viewmodel import TaskViewModel


STATUS_COLORS = {
    "Chưa làm": "#60a5fa",
    "Đang làm": "#f59e0b",
    "Chờ duyệt": "#a78bfa",
    "Hoàn thành": "#22c55e",
}


class TimelineView(ctk.CTkFrame):
    """Bieu do Gantt cho cac cong viec trong pham vi nguoi dung hien tai."""

    def __init__(self, master, actor="system", actor_role="member"):
        super().__init__(master, fg_color="transparent")
        self.vm = TaskViewModel(actor=actor, actor_role=actor_role)
        self.projects = self._load_projects()
        self.items = self._build_items()
        self.setup_ui()

    def _load_projects(self):
        path = Path(__file__).resolve().parents[1] / "projects.json"
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as f:
                projects = json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
        return {project.get("project_id", ""): project for project in projects}

    def _parse_date(self, value):
        try:
            return datetime.strptime(str(value).strip(), "%d/%m").date().replace(year=datetime.now().year)
        except (ValueError, AttributeError):
            return None

    def _build_items(self):
        parsed = []
        fallback_start = datetime.now().date().replace(day=1)
        for task in self.vm.scoped_tasks():
            deadline = self._parse_date(task.deadline)
            if deadline is None:
                continue
            project = self.projects.get(task.project_id, {})
            start = self._parse_date(task.start_date) or self._parse_date(project.get("start_date", "")) or fallback_start
            end = self._parse_date(project.get("end_date", "")) or deadline
            if start > deadline:
                start = deadline - timedelta(days=3)
            parsed.append(
                {
                    "task": task,
                    "project": project,
                    "start": start,
                    "deadline": deadline,
                    "project_end": max(end, deadline),
                }
            )
        return sorted(parsed, key=lambda item: (item["start"], item["deadline"], item["task"].task_id))

    def setup_ui(self):
        ctk.CTkLabel(self, text="Biểu đồ Gantt", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=24, pady=(24, 6))
        ctk.CTkLabel(
            self,
            text="Theo dõi tiến độ công việc theo mốc bắt đầu dự án và hạn hoàn thành.",
            text_color="#94a3b8",
            font=("Segoe UI", 13),
        ).pack(anchor="w", padx=24, pady=(0, 14))

        if not self.items:
            ctk.CTkLabel(self, text="Chưa có công việc có hạn hoàn thành hợp lệ để vẽ Gantt.", text_color="#94a3b8").pack(anchor="w", padx=24)
            return

        self._summary_cards()
        panel = ctk.CTkFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        panel.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        legend = ctk.CTkFrame(panel, fg_color="transparent")
        legend.pack(fill="x", padx=18, pady=(14, 4))
        for status, color in STATUS_COLORS.items():
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=(0, 18))
            ctk.CTkLabel(item, text="  ", width=18, height=18, fg_color=color, corner_radius=4).pack(side="left")
            ctk.CTkLabel(item, text=status, text_color="#94a3b8").pack(side="left", padx=(6, 0))

        canvas_shell = tk.Frame(panel, bg="#171717")
        canvas_shell.pack(fill="both", expand=True, padx=18, pady=(6, 18))
        self.canvas = tk.Canvas(canvas_shell, bg="#171717", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_shell, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Configure>", lambda _event: self._draw_gantt())
        self.after(80, self._draw_gantt)

    def _summary_cards(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(0, 14))
        today = datetime.now().date()
        total = len(self.items)
        overdue = len([item for item in self.items if item["deadline"] < today and item["task"].status != "Hoàn thành"])
        doing = len([item for item in self.items if item["task"].status == "Đang làm"])
        done = len([item for item in self.items if item["task"].status == "Hoàn thành"])
        data = [("Tổng việc", total, "#60a5fa"), ("Quá hạn", overdue, "#ef4444"), ("Đang làm", doing, "#f59e0b"), ("Hoàn thành", done, "#22c55e")]
        for label, value, color in data:
            card = ctk.CTkFrame(frame, fg_color=("#f8fafc", "#171717"), corner_radius=10)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkLabel(card, text=label, text_color="#94a3b8", anchor="w").pack(fill="x", padx=14, pady=(10, 0))
            ctk.CTkLabel(card, text=str(value), text_color=color, font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=14, pady=(0, 10))

    def _date_range(self):
        start = min(item["start"] for item in self.items)
        end = max(item["project_end"] for item in self.items)
        today = datetime.now().date()
        start = min(start, today) - timedelta(days=2)
        end = max(end, today) + timedelta(days=2)
        if (end - start).days < 7:
            end = start + timedelta(days=7)
        return start, end

    def _x_for_date(self, date_value, start, total_days, left, width):
        return left + ((date_value - start).days / total_days) * width

    def _draw_gantt(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 900)
        height = max(self.canvas.winfo_height(), 360)
        left = 250
        top = 54
        row_height = 42
        chart_width = width - left - 28
        start, end = self._date_range()
        total_days = max((end - start).days, 1)

        self.canvas.create_text(12, 22, anchor="w", text="Công việc", fill="#e5e7eb", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(left, 22, anchor="w", text=f"Từ {start.strftime('%d/%m')} đến {end.strftime('%d/%m')}", fill="#94a3b8", font=("Segoe UI", 10))

        tick_count = min(8, total_days + 1)
        for index in range(tick_count):
            day = start + timedelta(days=round(total_days * index / max(tick_count - 1, 1)))
            x = self._x_for_date(day, start, total_days, left, chart_width)
            self.canvas.create_line(x, 42, x, height - 12, fill="#2f3745")
            self.canvas.create_text(x, 34, text=day.strftime("%d/%m"), fill="#94a3b8", font=("Segoe UI", 9))

        today = datetime.now().date()
        if start <= today <= end:
            x_today = self._x_for_date(today, start, total_days, left, chart_width)
            self.canvas.create_line(x_today, 42, x_today, height - 12, fill="#ef4444", width=2)
            self.canvas.create_text(x_today + 6, 48, anchor="w", text="Hôm nay", fill="#ef4444", font=("Segoe UI", 9, "bold"))

        required_height = top + len(self.items) * row_height + 30
        self.canvas.configure(scrollregion=(0, 0, width, required_height))

        for index, item in enumerate(self.items):
            task = item["task"]
            y = top + index * row_height
            if index % 2 == 0:
                self.canvas.create_rectangle(0, y - 15, width, y + 22, fill="#202020", outline="")
            self.canvas.create_text(12, y, anchor="w", text=f"{task.task_id} - {task.name[:28]}", fill="#e5e7eb", font=("Segoe UI", 10, "bold"))
            meta = f"{task.project_id or '-'} | {task.assignee or '-'} | Bắt đầu: {task.start_date or '-'}"
            self.canvas.create_text(12, y + 15, anchor="w", text=meta, fill="#94a3b8", font=("Segoe UI", 9))

            x1 = self._x_for_date(item["start"], start, total_days, left, chart_width)
            x2 = self._x_for_date(item["deadline"], start, total_days, left, chart_width)
            if x2 < x1:
                x1, x2 = x2, x1
            x2 = max(x2, x1 + 12)
            color = STATUS_COLORS.get(task.status, "#60a5fa")
            self.canvas.create_rectangle(x1, y - 10, x2, y + 10, fill=color, outline="", width=0)
            self.canvas.create_text(x2 + 6, y, anchor="w", text=f"{task.deadline} - {task.status}", fill="#e5e7eb", font=("Segoe UI", 9, "bold"))
