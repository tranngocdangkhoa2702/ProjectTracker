import calendar
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

from viewmodels.project_manager_viewmodel import PROJECT_STATUSES, ProjectViewModel
from viewmodels.task_mananger_viewmodel import TaskViewModel


class DatePickerPopup(ctk.CTkToplevel):
    """Lịch chọn ngày đơn giản, trả về định dạng dd/mm."""

    def __init__(self, parent, initial_value, on_select):
        super().__init__(parent)
        self.title("Chọn ngày")
        self.geometry("330x360")
        self.resizable(False, False)
        self.grab_set()
        self.on_select = on_select
        today = datetime.now()
        parsed = self._parse_date(initial_value)
        self.year = today.year
        self.month = parsed.month if parsed else today.month
        self.day = parsed.day if parsed else None
        self._build()

    def _parse_date(self, value):
        try:
            return datetime.strptime(value.strip(), "%d/%m")
        except (ValueError, AttributeError):
            return None

    def _build(self):
        for child in self.winfo_children():
            child.destroy()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkButton(header, text="<", width=42, command=self._prev_month).pack(side="left")
        ctk.CTkLabel(header, text=f"Tháng {self.month}/{self.year}", font=("Segoe UI", 16, "bold")).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(header, text=">", width=42, command=self._next_month).pack(side="right")

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=16, pady=8)
        for col in range(7):
            grid.grid_columnconfigure(col, weight=1, uniform="cal")

        for col, text in enumerate(["T2", "T3", "T4", "T5", "T6", "T7", "CN"]):
            ctk.CTkLabel(grid, text=text, font=("Segoe UI", 12, "bold"), text_color="#94a3b8").grid(row=0, column=col, padx=2, pady=2)

        for row_index, week in enumerate(calendar.monthcalendar(self.year, self.month), start=1):
            for col, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(grid, text="", width=36, height=30).grid(row=row_index, column=col, padx=2, pady=2)
                    continue
                is_selected = day == self.day
                ctk.CTkButton(
                    grid,
                    text=str(day),
                    width=36,
                    height=30,
                    fg_color="#2563eb" if is_selected else ("#e5e7eb", "#242424"),
                    text_color="#ffffff" if is_selected else ("#111827", "#e5e7eb"),
                    hover_color="#1d4ed8",
                    command=lambda d=day: self._choose(d),
                ).grid(row=row_index, column=col, padx=2, pady=2)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(4, 16))
        ctk.CTkButton(footer, text="Bỏ trống", fg_color="#52525b", command=self._clear).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(footer, text="Hôm nay", command=self._today).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self._build()

    def _next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self._build()

    def _choose(self, day):
        self.on_select(f"{day:02d}/{self.month:02d}")
        self.destroy()

    def _clear(self):
        self.on_select("")
        self.destroy()

    def _today(self):
        self.on_select(datetime.now().strftime("%d/%m"))
        self.destroy()


class DateField(ctk.CTkFrame):
    """Ô chọn ngày có nút lịch và nút xóa."""

    def __init__(self, parent, value="", enabled=True):
        super().__init__(parent, fg_color="transparent")
        self.value = ctk.StringVar(value=value or "")
        self.enabled = enabled
        self.button = ctk.CTkButton(self, text=self.value.get() or "Chọn ngày", height=38, anchor="w", command=self._open_picker)
        self.button.pack(side="left", fill="x", expand=True)
        self.clear_button = ctk.CTkButton(
            self, text="X", width=38, height=38, fg_color="#52525b", hover_color="#3f3f46", command=self.clear
        )
        self.clear_button.pack(side="left", padx=(6, 0))
        if not enabled:
            self.button.configure(state="disabled", fg_color="#64748b")
            self.clear_button.configure(state="disabled", fg_color="#64748b")

    def _set(self, value):
        self.value.set(value)
        self.button.configure(text=value or "Chọn ngày")

    def _open_picker(self):
        if not self.enabled:
            return
        DatePickerPopup(self, self.value.get(), self._set)

    def clear(self):
        if not self.enabled:
            return
        self._set("")

    def get(self):
        return self.value.get()


class MemberPicker(ctk.CTkScrollableFrame):
    """Danh sách chọn thành viên từ các tài khoản member đang hoạt động."""

    def __init__(self, parent, members, selected=None, enabled=True):
        super().__init__(parent, fg_color=("#f3f4f6", "#171717"), corner_radius=8, height=92)
        self.vars = {}
        selected = set(selected or [])
        if not members:
            ctk.CTkLabel(self, text="Chưa có tài khoản thành viên đang hoạt động.", text_color="#94a3b8").pack(anchor="w", padx=10, pady=10)
            return

        for member in members:
            var = ctk.BooleanVar(value=member in selected)
            self.vars[member] = var
            ctk.CTkCheckBox(self, text=member, variable=var, state="normal" if enabled else "disabled").pack(anchor="w", padx=10, pady=5)

    def get_selected(self):
        return [name for name, var in self.vars.items() if var.get()]


class ProjectDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa dự án."""

    def __init__(
        self,
        parent,
        on_save_callback,
        project=None,
        user_options=None,
        member_options=None,
        actor_role="member",
        actor="system",
        generated_id="",
    ):
        super().__init__(parent)
        self.title("Dự án")
        self.geometry("700x610")
        self.minsize(700, 560)
        self.resizable(False, False)
        self.grab_set()
        self.project = project
        self.user_options = user_options or [actor]
        self.member_options = member_options or []

        ctk.CTkLabel(self, text="Thêm dự án mới" if project is None else "Cập nhật dự án", font=("Segoe UI", 22, "bold")).pack(
            pady=(20, 10)
        )

        form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=34, pady=(0, 8))
        form.grid_columnconfigure((0, 1), weight=1, uniform="project_form")

        self.entry_id = self._entry(form, "Mã dự án", "Tự động tạo", project.project_id if project else generated_id, 0, 0)
        self.entry_id.configure(state="disabled")
        self.status_menu = self._option(form, "Trạng thái", PROJECT_STATUSES, project.status if project else "Lên kế hoạch", 0, 1)
        self.entry_name = self._entry(form, "Tên dự án", "VD: Ứng dụng quản lý đồ án", project.name if project else "", 1, 0, 2)

        self._field_label(form, "Mô tả dự án", 2, 0, 2)
        self.entry_desc = ctk.CTkTextbox(form, height=76, corner_radius=8)
        self.entry_desc.insert("1.0", project.description if project else "")
        self.entry_desc.grid(row=5, column=0, columnspan=2, sticky="ew", padx=6, pady=(4, 10))

        leader_value = project.leader if project and project.leader else (actor if actor_role == "leader" else self.user_options[0])
        self.leader_menu = self._option(form, "Người phụ trách", self.user_options, leader_value, 3, 0)
        if actor_role != "admin":
            self.leader_menu.configure(state="disabled")

        self._field_label(form, "Thành viên tham gia", 3, 1)
        self.members_picker = MemberPicker(form, self.member_options, project.members if project else [], enabled=actor_role == "admin")
        self.members_picker.grid(row=7, column=1, sticky="new", padx=6, pady=(4, 10))

        self._field_label(form, "Ngày bắt đầu", 4, 0)
        self.start_entry = DateField(form, project.start_date if project else "", enabled=actor_role == "admin")
        self.start_entry.grid(row=9, column=0, sticky="ew", padx=6, pady=(4, 10))
        self._field_label(form, "Ngày kết thúc", 4, 1)
        self.end_entry = DateField(form, project.end_date if project else "")
        self.end_entry.grid(row=9, column=1, sticky="ew", padx=6, pady=(4, 10))

        hint = "Thành viên chỉ lấy từ tài khoản có quyền Thành viên và đang hoạt động."
        ctk.CTkLabel(form, text=hint, anchor="w", text_color="#94a3b8", wraplength=580).grid(
            row=10, column=0, columnspan=2, sticky="ew", padx=6, pady=(2, 8)
        )

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=34, pady=(0, 18))
        ctk.CTkButton(buttons, text="Hủy", fg_color="#3b3f45", hover_color="#4b5563", height=38, command=self.destroy).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        ctk.CTkButton(
            buttons,
            text="Lưu",
            fg_color="#16a34a",
            hover_color="#15803d",
            height=38,
            command=lambda: on_save_callback(
                self.entry_id.get(),
                self.entry_name.get(),
                self.entry_desc.get("1.0", "end").strip(),
                self.status_menu.get(),
                self.leader_menu.get(),
                self.members_picker.get_selected(),
                self.start_entry.get(),
                self.end_entry.get(),
                self,
                self.project,
            ),
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _field_label(self, parent, text, row, column, columnspan=1):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 12, "bold"), anchor="w", text_color=("#334155", "#e5e7eb")).grid(
            row=row * 2, column=column, columnspan=columnspan, sticky="ew", padx=6, pady=(6, 0)
        )

    def _entry(self, parent, label, placeholder, value, row, column, columnspan=1):
        self._field_label(parent, label, row, column, columnspan)
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=38)
        entry.insert(0, value)
        entry.grid(row=row * 2 + 1, column=column, columnspan=columnspan, sticky="ew", padx=6, pady=(4, 10))
        return entry

    def _option(self, parent, label, values, value, row, column):
        self._field_label(parent, label, row, column)
        menu = ctk.CTkOptionMenu(parent, values=values or ["-"])
        menu.set(value if value in values else (values[0] if values else "-"))
        menu.grid(row=row * 2 + 1, column=column, sticky="new", padx=6, pady=(4, 10))
        return menu


class ProjectsView(ctk.CTkFrame):
    """Màn hình quản lý dự án."""

    def __init__(self, master, actor="system", actor_role="member"):
        super().__init__(master, fg_color="transparent")
        self.actor = actor
        self.actor_role = actor_role
        self.view_model = ProjectViewModel(actor=actor, actor_role=actor_role)
        self.task_view_model = TaskViewModel(actor=actor, actor_role=actor_role)
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))
        ctk.CTkLabel(header, text="Quản lý dự án", font=("Segoe UI", 26, "bold")).pack(side="left")
        self.add_btn = ctk.CTkButton(
            header, text="+ Thêm dự án", fg_color="#16a34a", hover_color="#15803d", width=130, command=self.open_add_dialog
        )
        self.add_btn.pack(side="right")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(0, 12))
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo mã, tên, người phụ trách hoặc trạng thái...", height=36)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.handle_search)
        self.count_label = ctk.CTkLabel(toolbar, text="", text_color="#94a3b8", width=120)
        self.count_label.pack(side="right", padx=(12, 0))

        self.table_container = ctk.CTkScrollableFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        self.table_container.pack(pady=(0, 24), padx=24, fill="both", expand=True)
        if not self.view_model.can_create_project():
            self.add_btn.configure(state="disabled", fg_color="#64748b")

    def refresh_table(self, data=None):
        for child in self.table_container.winfo_children():
            child.destroy()

        projects = data if data is not None else self.view_model.display_projects
        self.count_label.configure(text=f"{len(projects)} dự án")

        progress_map = self.task_view_model.get_project_progress()

        if not projects:
            ctk.CTkLabel(self.table_container, text="Chưa có dự án phù hợp.", text_color="#94a3b8", font=("Segoe UI", 14)).pack(pady=40)
            return

        for index, project in enumerate(projects):
            row_color = ("#ffffff", "#202020") if index % 2 == 0 else ("#f9fafb", "#1b1b1b")
            row = ctk.CTkFrame(self.table_container, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=5, padx=4)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=project.project_id, width=76, anchor="w", text_color="#bfdbfe").grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(row, text=project.name, anchor="w", wraplength=430, font=("Segoe UI", 13, "bold")).grid(
                row=0, column=1, sticky="ew", padx=(0, 8), pady=(10, 2)
            )
            ctk.CTkLabel(row, text=project.status, width=120, anchor="e", text_color="#60a5fa", font=("Segoe UI", 12, "bold")).grid(
                row=0, column=2, sticky="e", padx=12, pady=(10, 2)
            )

            meta = (
                f"Người phụ trách: {project.leader or '-'}  |  "
                f"Tiến độ: {progress_map.get(project.project_id, 0)}%  |  "
                f"Thành viên: {', '.join(project.members) or '-'}"
            )
            ctk.CTkLabel(row, text=meta, anchor="w", text_color="#94a3b8", wraplength=760).grid(
                row=1, column=0, columnspan=3, sticky="ew", padx=12, pady=(0, 6)
            )

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
            btn_edit = ctk.CTkButton(actions, text="Sửa", width=54, height=28, fg_color="#52525b", command=lambda p=project: self.open_edit_dialog(p))
            btn_edit.pack(side="left", padx=2)
            btn_delete = ctk.CTkButton(
                actions, text="Xóa", width=54, height=28, fg_color="#dc2626", hover_color="#b91c1c", command=lambda pid=project.project_id: self.delete_project(pid)
            )
            btn_delete.pack(side="left", padx=2)
            if not self.view_model.can_manage_project(project):
                btn_edit.configure(state="disabled", fg_color="#64748b")
            if self.actor_role != "admin":
                btn_delete.configure(state="disabled", fg_color="#64748b")

    def handle_search(self, _event=None):
        self.refresh_table(self.view_model.search(self.search_entry.get()))

    def _leader_options(self):
        try:
            from models.user_model import UserModel

            users = UserModel().list_active_users()
            names = [user["username"] for user in users if user["role"] in ("admin", "leader")]
            return names or [self.actor]
        except Exception:
            return [self.actor]

    def _member_options(self):
        return self.view_model.active_member_usernames()

    def open_add_dialog(self):
        if not self.view_model.can_create_project():
            messagebox.showwarning("Thông báo", "Bạn không có quyền thêm dự án.")
            return
        ProjectDialog(
            self,
            self.handle_save,
            user_options=self._leader_options(),
            member_options=self._member_options(),
            actor_role=self.actor_role,
            actor=self.actor,
            generated_id=self.view_model.generate_project_id(),
        )

    def open_edit_dialog(self, project):
        if not self.view_model.can_manage_project(project):
            messagebox.showwarning("Thông báo", "Bạn không có quyền sửa dự án này.")
            return
        ProjectDialog(
            self,
            self.handle_save,
            project,
            user_options=self._leader_options(),
            member_options=self._member_options(),
            actor_role=self.actor_role,
            actor=self.actor,
        )

    def handle_save(self, project_id, name, description, status, leader, members, start_date, end_date, dialog, original_project):
        if original_project is None:
            success, message = self.view_model.validate_and_add(project_id, name, description, status, leader, members, start_date, end_date)
        else:
            success, message = self.view_model.update_project(
                original_project.project_id, project_id, name, description, status, leader, members, start_date, end_date
            )

        if success:
            dialog.destroy()
            self.handle_search()
        else:
            messagebox.showwarning("Thông báo", message)

    def delete_project(self, project_id):
        if not messagebox.askyesno("Xác nhận", f"Xóa dự án '{project_id}'?"):
            return
        success, message = self.view_model.delete_project(project_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_search()
