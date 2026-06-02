import customtkinter as ctk
from tkinter import messagebox

from viewmodels.task_mananger_viewmodel import PRIORITIES, STATUSES, TaskViewModel
from views.projects_view import DateField


class TaskDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa công việc."""

    def __init__(
        self,
        parent,
        on_save_callback,
        task=None,
        project_options=None,
        assignee_options=None,
        generated_id="",
        status_options=None,
    ):
        super().__init__(parent)
        self.title("Công việc")
        self.geometry("500x610")
        self.minsize(500, 560)
        self.resizable(False, False)
        self.grab_set()
        self.task = task
        project_options = project_options or [""]
        assignee_options = assignee_options or [""]
        status_options = status_options or STATUSES

        ctk.CTkLabel(self, text="Thêm công việc mới" if task is None else "Cập nhật công việc", font=("Segoe UI", 20, "bold")).pack(
            pady=(22, 8)
        )

        form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=32, pady=(0, 8))

        self.e_id = self._entry(form, "Mã công việc", "Tự động tạo", task.task_id if task else generated_id)
        self.e_id.configure(state="disabled")
        self.e_name = self._entry(form, "Tên công việc", "VD: Viết báo cáo chương 2", task.name if task else "")

        self._field_label(form, "Dự án")
        self.e_project = ctk.CTkOptionMenu(form, values=project_options)
        self.e_project.set(task.project_id if task and task.project_id in project_options else project_options[0])
        self.e_project.pack(fill="x", pady=(4, 8))

        self._field_label(form, "Người được giao")
        self.e_assignee = ctk.CTkOptionMenu(form, values=assignee_options)
        self.e_assignee.set(task.assignee if task and task.assignee in assignee_options else assignee_options[0])
        self.e_assignee.pack(fill="x", pady=(4, 8))

        self._field_label(form, "Ngày bắt đầu")
        self.e_start_date = DateField(form, task.start_date if task else "")
        self.e_start_date.pack(fill="x", pady=(4, 8))

        self._field_label(form, "Hạn hoàn thành")
        self.e_deadline = DateField(form, task.deadline if task else "")
        self.e_deadline.pack(fill="x", pady=(4, 8))

        self._field_label(form, "Mức ưu tiên")
        self.e_priority = ctk.CTkOptionMenu(form, values=PRIORITIES)
        self.e_priority.set(task.priority if task else PRIORITIES[1])
        self.e_priority.pack(fill="x", pady=(4, 8))

        flags = ctk.CTkFrame(form, fg_color="transparent")
        flags.pack(fill="x", pady=(2, 8))
        self.urgent_var = ctk.BooleanVar(value=task.is_urgent if task else False)
        self.important_var = ctk.BooleanVar(value=task.is_important if task else True)
        ctk.CTkCheckBox(flags, text="Khẩn cấp", variable=self.urgent_var).pack(side="left", fill="x", expand=True)
        ctk.CTkCheckBox(flags, text="Quan trọng", variable=self.important_var).pack(side="left", fill="x", expand=True)

        self._field_label(form, "Trạng thái")
        self.e_status = ctk.CTkOptionMenu(form, values=status_options)
        current_status = task.status if task else "Chưa làm"
        self.e_status.set(current_status if current_status in status_options else status_options[0])
        self.e_status.pack(fill="x", pady=(4, 8))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=32, pady=(0, 18))
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
                self.e_start_date.get(),
                self.e_deadline.get(),
                self.e_priority.get(),
                self.e_status.get(),
                self.e_project.get(),
                self.e_assignee.get(),
                self.urgent_var.get(),
                self.important_var.get(),
                self,
                self.task,
            ),
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _field_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 12, "bold"), anchor="w", text_color=("#334155", "#e5e7eb")).pack(
            fill="x", pady=(4, 0)
        )

    def _entry(self, parent, label, placeholder, value):
        self._field_label(parent, label)
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=38)
        entry.insert(0, value)
        entry.pack(fill="x", pady=(4, 6))
        return entry


class StatusDialog(ctk.CTkToplevel):
    """Dialog cập nhật trạng thái công việc."""

    def __init__(self, parent, task, on_save_callback, status_options=None):
        super().__init__(parent)
        self.title("Cập nhật trạng thái")
        self.geometry("360x220")
        self.resizable(False, False)
        self.grab_set()
        self.task = task
        status_options = status_options or []

        ctk.CTkLabel(self, text="Cập nhật trạng thái", font=("Segoe UI", 20, "bold")).pack(pady=(24, 8))
        ctk.CTkLabel(self, text=f"{task.task_id} - {task.name}", text_color="#94a3b8", wraplength=310).pack(padx=24, pady=(0, 12))
        self.status_menu = ctk.CTkOptionMenu(self, values=status_options or [task.status])
        self.status_menu.set(task.status if task.status in status_options else (status_options[0] if status_options else task.status))
        self.status_menu.pack(fill="x", padx=28, pady=(0, 18))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=28)
        ctk.CTkButton(buttons, text="Hủy", fg_color="#3b3f45", command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(
            buttons,
            text="Lưu trạng thái",
            fg_color="#16a34a",
            command=lambda: on_save_callback(task.task_id, self.status_menu.get(), self),
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))


class ExtensionDialog(ctk.CTkToplevel):
    """Dialog thành viên gửi yêu cầu gia hạn."""

    def __init__(self, parent, task, on_save_callback):
        super().__init__(parent)
        self.title("Yêu cầu gia hạn")
        self.geometry("420x320")
        self.resizable(False, False)
        self.grab_set()
        self.task = task

        ctk.CTkLabel(self, text="Yêu cầu gia hạn", font=("Segoe UI", 20, "bold")).pack(pady=(22, 8))
        ctk.CTkLabel(self, text=f"{task.task_id} - {task.name}", text_color="#94a3b8", wraplength=350).pack(padx=24, pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=28, pady=4)
        ctk.CTkLabel(form, text=f"Hạn hiện tại: {task.deadline}", anchor="w", text_color="#94a3b8").pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(form, text="Hạn mới", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
        self.deadline_field = DateField(form, task.requested_deadline or task.deadline)
        self.deadline_field.pack(fill="x", pady=(4, 10))
        ctk.CTkLabel(form, text="Lý do", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
        self.reason_entry = ctk.CTkEntry(form, placeholder_text="VD: Cần thêm thời gian kiểm thử")
        self.reason_entry.insert(0, task.extension_reason or "")
        self.reason_entry.pack(fill="x", pady=(4, 12))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=28)
        ctk.CTkButton(buttons, text="Hủy", fg_color="#3b3f45", command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(
            buttons,
            text="Gửi yêu cầu",
            fg_color="#16a34a",
            command=lambda: on_save_callback(task.task_id, self.deadline_field.get(), self.reason_entry.get(), self),
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))


class TaskInfoDialog(ctk.CTkToplevel):
    """Dialog xem thông tin công việc đã hoàn thành."""

    def __init__(self, parent, task):
        super().__init__(parent)
        self.title("Thông tin công việc")
        self.geometry("420x400")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="Thông tin công việc", font=("Segoe UI", 20, "bold")).pack(pady=(24, 10))
        body = ctk.CTkFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        rows = [
            ("Mã", task.task_id),
            ("Tên", task.name),
            ("Dự án", task.project_id or "-"),
            ("Người được giao", task.assignee or "-"),
            ("Ngày bắt đầu", task.start_date or "-"),
            ("Hạn hoàn thành", task.deadline or "-"),
            ("Ưu tiên", task.priority),
            ("Trạng thái", task.status),
        ]
        for label, value in rows:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=5)
            ctk.CTkLabel(row, text=label, width=120, anchor="w", text_color="#94a3b8").pack(side="left")
            ctk.CTkLabel(row, text=value, anchor="w", font=("Segoe UI", 12, "bold"), wraplength=230).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(self, text="Đóng", command=self.destroy).pack(fill="x", padx=24, pady=(0, 20))


class TasksView(ctk.CTkFrame):
    """Màn hình quản lý công việc."""

    def __init__(self, master, actor="system", actor_role="member"):
        super().__init__(master, fg_color="transparent")
        self.actor = actor
        self.actor_role = actor_role
        self.view_model = TaskViewModel(actor=actor, actor_role=actor_role)
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))
        ctk.CTkLabel(header, text="Quản lý công việc", font=("Segoe UI", 26, "bold")).pack(side="left")
        self.add_btn = ctk.CTkButton(
            header, text="+ Thêm công việc", fg_color="#16a34a", hover_color="#15803d", width=150, command=self.open_add_dialog
        )
        self.add_btn.pack(side="right")

        alert_box = ctk.CTkFrame(self, fg_color=("#fef3c7", "#2c2411"), corner_radius=10)
        alert_box.pack(fill="x", padx=24, pady=(0, 10))
        urgent = self.view_model.get_deadline_insights(limit=1)
        msg = urgent[0][1] if urgent else "Không có cảnh báo hạn hoàn thành."
        ctk.CTkLabel(alert_box, text=f"Nhắc việc nhanh: {msg}", text_color=("#92400e", "#fbbf24")).pack(anchor="w", padx=12, pady=8)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(0, 12))
        toolbar.grid_columnconfigure(3, weight=1)
        self.status_filter = ctk.CTkOptionMenu(toolbar, values=["Tất cả"] + STATUSES, width=115, command=lambda _v: self.handle_filter())
        self.status_filter.set("Tất cả")
        self.status_filter.grid(row=0, column=0, sticky="w")
        self.priority_filter = ctk.CTkOptionMenu(toolbar, values=["Tất cả", "P1", "P2", "P3", "P4"], width=90, command=lambda _v: self.handle_filter())
        self.priority_filter.set("Tất cả")
        self.priority_filter.grid(row=0, column=1, sticky="w", padx=(8, 0))
        project_options = ["Tất cả"] + self.view_model.get_project_options()
        self.project_filter = ctk.CTkOptionMenu(toolbar, values=project_options, width=105, command=lambda _v: self.handle_filter())
        self.project_filter.set("Tất cả")
        self.project_filter.grid(row=0, column=2, sticky="w", padx=(8, 0))
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Tìm mã, tên, dự án, người được giao...", height=36)
        self.search_entry.grid(row=0, column=3, sticky="ew", padx=8)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.handle_filter())
        self.summary_label = ctk.CTkLabel(toolbar, text="", text_color="#94a3b8")
        self.summary_label.grid(row=0, column=4, sticky="e")

        self.table_container = ctk.CTkScrollableFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        self.table_container.pack(padx=24, pady=(0, 24), fill="both", expand=True)
        if not self.view_model.can_create_task():
            self.add_btn.configure(state="disabled", fg_color="#64748b")

    def refresh_table(self, data=None):
        for child in self.table_container.winfo_children():
            child.destroy()

        tasks = data if data is not None else self.view_model.display_tasks
        stats = self.view_model.get_stats()
        self.summary_label.configure(text=f"{stats['done']}/{stats['total']} hoàn thành")

        if not tasks:
            ctk.CTkLabel(self.table_container, text="Chưa có công việc phù hợp.", text_color="#94a3b8", font=("Segoe UI", 14)).pack(pady=40)
            return

        for index, task in enumerate(tasks):
            self._create_task_card(task, index)

    def _create_task_card(self, task, index):
        row_color = ("#ffffff", "#202020") if index % 2 == 0 else ("#f9fafb", "#1b1b1b")
        card = ctk.CTkFrame(self.table_container, fg_color=row_color, corner_radius=8)
        card.pack(fill="x", pady=5, padx=4)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top, text=f"{task.task_id} | {task.project_id or '-'}", width=110, anchor="w", text_color="#bfdbfe").grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(top, text=task.name, anchor="w", wraplength=520, font=("Segoe UI", 13, "bold")).grid(
            row=0, column=1, sticky="ew", padx=(8, 8)
        )
        status_color = "#22c55e" if task.status == "Hoàn thành" else ("#f59e0b" if task.status == "Chờ duyệt" else "#60a5fa")
        ctk.CTkLabel(top, text=self._status_text(task), text_color=status_color, font=("Segoe UI", 12, "bold"), wraplength=150).grid(
            row=0, column=2, sticky="e"
        )

        meta_parts = [
            f"Người được giao: {task.assignee or '-'}",
            f"Bắt đầu: {task.start_date or '-'}",
            f"Hạn: {task.deadline or '-'}",
            f"Ưu tiên: {task.priority}",
        ]
        ctk.CTkLabel(card, text="  |  ".join(meta_parts), anchor="w", text_color="#94a3b8", wraplength=860).grid(
            row=1, column=0, sticky="ew", padx=12, pady=(0, 6)
        )

        hint = self._workflow_hint(task)
        if hint:
            ctk.CTkLabel(card, text=hint, anchor="w", text_color="#fbbf24", wraplength=860).grid(
                row=2, column=0, sticky="ew", padx=12, pady=(0, 6)
            )

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        self._pack_task_actions(actions, task)

    def _status_text(self, task):
        if self.view_model.is_pending_member_task(task):
            return "Chờ leader duyệt"
        if task.extension_status:
            return f"{task.status} | {self._extension_label(task)}"
        return task.status

    def _workflow_hint(self, task):
        if self.view_model.is_pending_member_task(task):
            return "Công việc do thành viên tạo, cần trưởng nhóm duyệt trước khi thực hiện."
        if task.extension_status == "member_requested":
            return f"Thành viên xin gia hạn đến {task.requested_deadline or '-'}, trưởng nhóm cần gửi yêu cầu lên admin."
        if task.extension_status == "leader_requested_admin":
            return f"Trưởng nhóm đã gửi yêu cầu gia hạn đến {task.requested_deadline or '-'} cho admin."
        if task.extension_status == "admin_approved":
            return f"Admin đã duyệt gia hạn đến {task.requested_deadline or '-'}, trưởng nhóm cần xác nhận cho thành viên."
        return ""

    def _pack_task_actions(self, actions, task):
        if self.view_model.is_completed(task):
            ctk.CTkButton(actions, text="Xem", width=72, height=30, fg_color="#2563eb", command=lambda t=task: TaskInfoDialog(self, t)).pack(
                side="left", padx=3, pady=2
            )
            return

        if self.view_model.can_approve_member_task(task):
            ctk.CTkButton(
                actions, text="Duyệt", width=70, height=30, fg_color="#16a34a", command=lambda task_id=task.task_id: self.approve_member_task(task_id)
            ).pack(side="left", padx=3, pady=2)

        status_options = self.view_model.get_status_options(task)
        status_button_text = "Xác nhận" if task.status == "Chờ duyệt" and "Hoàn thành" in status_options else "Cập nhật"
        btn_status = ctk.CTkButton(
            actions,
            text=status_button_text,
            width=88,
            height=30,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=lambda t=task: self.open_status_dialog(t),
        )
        btn_status.pack(side="left", padx=3, pady=2)

        btn_edit = ctk.CTkButton(actions, text="Sửa", width=58, height=30, fg_color="#52525b", command=lambda t=task: self.open_edit_dialog(t))
        btn_edit.pack(side="left", padx=3, pady=2)
        btn_delete = ctk.CTkButton(
            actions, text="Xóa", width=58, height=30, fg_color="#dc2626", hover_color="#b91c1c", command=lambda task_id=task.task_id: self.delete_task(task_id)
        )
        btn_delete.pack(side="left", padx=3, pady=2)
        self._pack_extension_button(actions, task)

        if not self.view_model.can_update_task_status(task):
            btn_status.configure(state="disabled", fg_color="#64748b")
        if not self.view_model.can_manage_task(task):
            btn_edit.configure(state="disabled", fg_color="#64748b")
            btn_delete.configure(state="disabled", fg_color="#64748b")

    def _extension_label(self, task):
        labels = {
            "member_requested": "Xin GH",
            "leader_requested_admin": "Chờ admin",
            "admin_approved": "Admin OK",
        }
        return labels.get(task.extension_status, task.extension_status)

    def _pack_extension_button(self, actions, task):
        if self.view_model.can_request_extension(task):
            ctk.CTkButton(actions, text="Gia hạn", width=66, height=28, fg_color="#7c3aed", command=lambda t=task: self.open_extension_dialog(t)).pack(
                side="left", padx=2
            )
        elif self.view_model.can_forward_extension_to_admin(task):
            ctk.CTkButton(actions, text="Gửi admin", width=76, height=28, fg_color="#7c3aed", command=lambda task_id=task.task_id: self.forward_extension(task_id)).pack(
                side="left", padx=2
            )
        elif self.view_model.can_admin_approve_extension(task):
            ctk.CTkButton(
                actions, text="Admin duyệt", width=88, height=28, fg_color="#16a34a", command=lambda task_id=task.task_id: self.admin_approve_extension(task_id)
            ).pack(side="left", padx=2)
        elif self.view_model.can_leader_finalize_extension(task):
            ctk.CTkButton(
                actions, text="Duyệt GH", width=76, height=28, fg_color="#16a34a", command=lambda task_id=task.task_id: self.leader_finalize_extension(task_id)
            ).pack(side="left", padx=2)

    def handle_filter(self):
        filtered_data = self.view_model.filter_and_search(
            self.status_filter.get(),
            self.search_entry.get(),
            self.priority_filter.get(),
            self.project_filter.get(),
        )
        self.refresh_table(filtered_data)

    def _assignee_options(self):
        return self.view_model.get_assignee_options() or ["-"]

    def open_add_dialog(self):
        if not self.view_model.can_create_task():
            messagebox.showwarning("Thông báo", "Bạn không có quyền thêm công việc.")
            return
        TaskDialog(
            self,
            self.handle_save,
            project_options=self.view_model.get_project_options(manageable_only=True),
            assignee_options=self._assignee_options(),
            generated_id=self.view_model.generate_task_id(),
            status_options=self.view_model.get_edit_status_options(None),
        )

    def open_edit_dialog(self, task):
        if self.view_model.is_completed(task):
            TaskInfoDialog(self, task)
            return
        if not self.view_model.can_manage_task(task):
            messagebox.showwarning("Thông báo", "Bạn không có quyền sửa công việc này.")
            return
        TaskDialog(
            self,
            self.handle_save,
            task,
            project_options=self.view_model.get_project_options(manageable_only=True),
            assignee_options=self._assignee_options(),
            status_options=self.view_model.get_edit_status_options(task),
        )

    def open_status_dialog(self, task):
        if self.view_model.is_completed(task):
            TaskInfoDialog(self, task)
            return
        options = self.view_model.get_status_options(task)
        if not options:
            messagebox.showwarning("Thông báo", "Bạn không có quyền cập nhật trạng thái công việc này.")
            return
        StatusDialog(self, task, self.handle_status_save, options)

    def open_extension_dialog(self, task):
        if not self.view_model.can_request_extension(task):
            messagebox.showwarning("Thông báo", "Bạn không có quyền gửi yêu cầu gia hạn cho công việc này.")
            return
        ExtensionDialog(self, task, self.handle_extension_request)

    def handle_status_save(self, task_id, status, dialog):
        success, message = self.view_model.update_status(task_id, status)
        if success:
            dialog.destroy()
            self.handle_filter()
        else:
            messagebox.showwarning("Thông báo", message)

    def approve_member_task(self, task_id):
        success, message = self.view_model.approve_member_task(task_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_filter()

    def handle_extension_request(self, task_id, requested_deadline, reason, dialog):
        success, message = self.view_model.request_extension(task_id, requested_deadline, reason)
        if success:
            dialog.destroy()
            self.handle_filter()
        else:
            messagebox.showwarning("Thông báo", message)

    def forward_extension(self, task_id):
        success, message = self.view_model.forward_extension_to_admin(task_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_filter()

    def admin_approve_extension(self, task_id):
        success, message = self.view_model.admin_approve_extension(task_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_filter()

    def leader_finalize_extension(self, task_id):
        success, message = self.view_model.leader_finalize_extension(task_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_filter()

    def handle_save(
        self,
        task_id,
        name,
        start_date,
        deadline,
        priority,
        status,
        project_id,
        assignee,
        is_urgent,
        is_important,
        dialog,
        original_task,
    ):
        if assignee == "-":
            assignee = ""
        if original_task is None:
            success, message = self.view_model.validate_and_add(
                task_id, name, start_date, deadline, priority, status, project_id, assignee, is_urgent, is_important
            )
        else:
            success, message = self.view_model.update_task(
                original_task.task_id, task_id, name, start_date, deadline, priority, status, project_id, assignee, is_urgent, is_important
            )
        if success:
            dialog.destroy()
            self.handle_filter()
        else:
            messagebox.showwarning("Thông báo", message)

    def delete_task(self, task_id):
        if not messagebox.askyesno("Xác nhận", f"Xóa công việc '{task_id}'?"):
            return
        success, message = self.view_model.delete_task(task_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_filter()
