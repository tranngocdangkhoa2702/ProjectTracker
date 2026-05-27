import customtkinter as ctk
from tkinter import messagebox

from viewmodels.task_mananger_viewmodel import TaskViewModel


PRIORITIES = ["1 (P1)", "2 (P2)", "3 (P3)", "4 (P4)"]
STATUSES = ["Todo", "Done"]


class TaskDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa công việc."""

    def __init__(self, parent, on_save_callback, task=None):
        """Khởi tạo dialog theo mode tạo mới hoặc cập nhật."""
        super().__init__(parent)
        self.title("Công việc")
        self.geometry("420x500")
        self.resizable(False, False)
        self.grab_set()
        self.task = task

        ctk.CTkLabel(self, text="Thêm công việc mới" if task is None else "Cập nhật công việc", font=("Segoe UI", 20, "bold")).pack(
            pady=(24, 8)
        )

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=32, pady=8)

        self.e_id = self._entry(form, "ID công việc", task.task_id if task else "")
        self.e_name = self._entry(form, "Tên công việc", task.name if task else "")
        self.e_deadline = self._entry(form, "Deadline (dd/mm)", task.deadline if task else "")

        self.e_priority = ctk.CTkOptionMenu(form, values=PRIORITIES)
        self.e_priority.set(task.priority if task else PRIORITIES[1])
        self.e_priority.pack(fill="x", pady=10)

        self.e_status = ctk.CTkOptionMenu(form, values=STATUSES)
        self.e_status.set(task.status if task else "Todo")
        self.e_status.pack(fill="x", pady=10)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=32, pady=(20, 0))
        ctk.CTkButton(buttons, text="Hủy", fg_color="#3b3f45", hover_color="#4b5563", command=self.destroy).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        ctk.CTkButton(
            buttons,
            text="Lưu",
            fg_color="#16a34a",
            hover_color="#15803d",
            command=lambda: on_save_callback(
                self.e_id.get(),
                self.e_name.get(),
                self.e_deadline.get(),
                self.e_priority.get(),
                self.e_status.get(),
                self,
                self.task,
            ),
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _entry(self, parent, placeholder, value):
        """Tạo ô nhập liệu dùng chung."""
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=40)
        entry.insert(0, value)
        entry.pack(fill="x", pady=10)
        return entry


class TasksView(ctk.CTkFrame):
    """Màn hình quản lý công việc."""

    def __init__(self, master, actor="system", can_manage=True):
        """Khởi tạo view task theo quyền của user."""
        super().__init__(master, fg_color="transparent")
        self.can_manage = can_manage
        self.view_model = TaskViewModel(actor=actor, can_manage=can_manage)
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        """Dựng toàn bộ thành phần UI của màn công việc."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))

        ctk.CTkLabel(header, text="Quản lý công việc", font=("Segoe UI", 26, "bold")).pack(side="left")
        self.add_btn = ctk.CTkButton(
            header, text="+ Thêm task", fg_color="#16a34a", hover_color="#15803d", width=120, command=self.open_add_dialog
        )
        self.add_btn.pack(side="right")

        alert_box = ctk.CTkFrame(self, fg_color=("#fef3c7", "#2c2411"), corner_radius=10)
        alert_box.pack(fill="x", padx=24, pady=(0, 10))
        urgent = self.view_model.get_deadline_insights(limit=1)
        msg = urgent[0][1] if urgent else "Không có cảnh báo deadline."
        ctk.CTkLabel(alert_box, text=f"Nhắc việc nhanh: {msg}", text_color=("#92400e", "#fbbf24")).pack(anchor="w", padx=12, pady=8)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(0, 12))

        self.seg_button = ctk.CTkSegmentedButton(toolbar, values=["Tất cả", "Đang làm", "Hoàn thành"], command=self.handle_filter)
        self.seg_button.set("Tất cả")
        self.seg_button.pack(side="left")

        self.priority_filter = ctk.CTkOptionMenu(toolbar, values=["Tất cả", "P1", "P2", "P3", "P4"], width=90, command=lambda _v: self.handle_filter())
        self.priority_filter.set("Tất cả")
        self.priority_filter.pack(side="left", padx=10)

        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo ID, tên hoặc ưu tiên...", width=260, height=36)
        self.search_entry.pack(side="left", padx=4)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.handle_filter())

        self.summary_label = ctk.CTkLabel(toolbar, text="", text_color="#94a3b8")
        self.summary_label.pack(side="right")

        self.table_container = ctk.CTkScrollableFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        self.table_container.pack(padx=24, pady=(0, 24), fill="both", expand=True)

        if not self.can_manage:
            self.add_btn.configure(state="disabled", fg_color="#64748b")

    def refresh_table(self, data=None):
        """Render lại bảng công việc."""
        for child in self.table_container.winfo_children():
            child.destroy()

        tasks = data if data is not None else self.view_model.display_tasks
        stats = self.view_model.get_stats()
        self.summary_label.configure(text=f"{stats['done']}/{stats['total']} hoàn thành")

        header = ctk.CTkFrame(self.table_container, fg_color=("#e5e7eb", "#242424"), corner_radius=8)
        header.pack(fill="x", pady=(0, 8), padx=4)
        columns = [("ID", 70), ("Tên công việc", 260), ("Deadline", 95), ("Ưu tiên", 95), ("Trạng thái", 95), ("Thao tác", 220)]
        for text, width in columns:
            ctk.CTkLabel(header, text=text, width=width, font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left", padx=8, pady=10)

        if not tasks:
            ctk.CTkLabel(self.table_container, text="Chưa có công việc phù hợp.", text_color="#94a3b8", font=("Segoe UI", 14)).pack(pady=40)
            return

        for index, task in enumerate(tasks):
            row_color = ("#ffffff", "#202020") if index % 2 == 0 else ("#f9fafb", "#1b1b1b")
            row = ctk.CTkFrame(self.table_container, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            ctk.CTkLabel(row, text=task.task_id, width=70, anchor="w").pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=task.name, width=260, anchor="w", wraplength=250).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=task.deadline or "-", width=95, anchor="w").pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=task.priority, width=95, anchor="w").pack(side="left", padx=8, pady=8)

            status_color = "#22c55e" if task.status == "Done" else "#f59e0b"
            ctk.CTkLabel(row, text="Hoàn thành" if task.status == "Done" else "Đang làm", width=95, text_color=status_color, anchor="w").pack(
                side="left", padx=8, pady=8
            )

            actions = ctk.CTkFrame(row, fg_color="transparent", width=220)
            actions.pack(side="left", padx=8, pady=6)
            btn_toggle = ctk.CTkButton(
                actions, text="Đổi", width=52, height=28, fg_color="#2563eb", hover_color="#1d4ed8", command=lambda task_id=task.task_id: self.toggle_status(task_id)
            )
            btn_toggle.pack(side="left", padx=2)
            btn_edit = ctk.CTkButton(
                actions, text="Sửa", width=52, height=28, fg_color="#52525b", hover_color="#3f3f46", command=lambda t=task: self.open_edit_dialog(t)
            )
            btn_edit.pack(side="left", padx=2)
            btn_delete = ctk.CTkButton(
                actions, text="Xóa", width=52, height=28, fg_color="#dc2626", hover_color="#b91c1c", command=lambda task_id=task.task_id: self.delete_task(task_id)
            )
            btn_delete.pack(side="left", padx=2)

            if not self.can_manage:
                btn_toggle.configure(state="disabled", fg_color="#64748b")
                btn_edit.configure(state="disabled", fg_color="#64748b")
                btn_delete.configure(state="disabled", fg_color="#64748b")

    def handle_filter(self, status=None):
        """Lọc công việc theo trạng thái/ưu tiên và text."""
        status = status or self.seg_button.get()
        filtered_data = self.view_model.filter_and_search(status, self.search_entry.get(), self.priority_filter.get())
        self.refresh_table(filtered_data)

    def open_add_dialog(self):
        """Mở dialog thêm task nếu có quyền."""
        if not self.can_manage:
            messagebox.showwarning("Thông báo", "Bạn không có quyền thêm công việc.")
            return
        TaskDialog(self, self.handle_save)

    def open_edit_dialog(self, task):
        """Mở dialog sửa task nếu có quyền."""
        if not self.can_manage:
            messagebox.showwarning("Thông báo", "Bạn không có quyền sửa công việc.")
            return
        TaskDialog(self, self.handle_save, task)

    def handle_save(self, task_id, name, deadline, priority, status, dialog, original_task):
        """Lưu dữ liệu task từ dialog về viewmodel."""
        if original_task is None:
            success, message = self.view_model.validate_and_add(task_id, name, deadline, priority, status)
        else:
            success, message = self.view_model.update_task(original_task.task_id, task_id, name, deadline, priority, status)
        if success:
            dialog.destroy()
            self.handle_filter()
        else:
            messagebox.showwarning("Thông báo", message)

    def toggle_status(self, task_id):
        """Đổi nhanh trạng thái task."""
        success, message = self.view_model.toggle_status(task_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_filter()

    def delete_task(self, task_id):
        """Xóa task sau khi xác nhận."""
        if not messagebox.askyesno("Xác nhận", f"Xóa công việc '{task_id}'?"):
            return
        success, message = self.view_model.delete_task(task_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_filter()
