import customtkinter as ctk
from tkinter import messagebox

from viewmodels.project_manager_viewmodel import ProjectViewModel


class ProjectDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa dự án."""

    def __init__(self, parent, on_save_callback, project=None):
        """Khởi tạo dialog theo mode tạo mới hoặc cập nhật."""
        super().__init__(parent)
        self.title("Dự án")
        self.geometry("430x430")
        self.resizable(False, False)
        self.grab_set()
        self.project = project

        ctk.CTkLabel(self, text="Thêm dự án mới" if project is None else "Cập nhật dự án", font=("Segoe UI", 20, "bold")).pack(
            pady=(24, 8)
        )

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=32, pady=8)

        self.entry_id = self._entry(form, "ID dự án", project.project_id if project else "")
        self.entry_name = self._entry(form, "Tên dự án", project.name if project else "")
        self.entry_desc = ctk.CTkTextbox(form, height=110, corner_radius=8)
        self.entry_desc.insert("1.0", project.description if project else "")
        self.entry_desc.pack(fill="x", pady=10)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=32, pady=(16, 0))
        ctk.CTkButton(buttons, text="Hủy", fg_color="#3b3f45", hover_color="#4b5563", command=self.destroy).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        ctk.CTkButton(
            buttons,
            text="Lưu",
            fg_color="#16a34a",
            hover_color="#15803d",
            command=lambda: on_save_callback(
                self.entry_id.get(),
                self.entry_name.get(),
                self.entry_desc.get("1.0", "end").strip(),
                self,
                self.project,
            ),
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _entry(self, parent, placeholder, value):
        """Tạo ô nhập liệu dùng chung."""
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=40)
        entry.insert(0, value)
        entry.pack(fill="x", pady=10)
        return entry


class ProjectsView(ctk.CTkFrame):
    """Màn hình quản lý dự án."""

    def __init__(self, master, actor="system", can_manage=True):
        """Khởi tạo view và nạp dữ liệu dự án."""
        super().__init__(master, fg_color="transparent")
        self.can_manage = can_manage
        self.view_model = ProjectViewModel(actor=actor, can_manage=can_manage)
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        """Dựng toàn bộ thành phần UI của màn dự án."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))

        ctk.CTkLabel(header, text="Quản lý dự án", font=("Segoe UI", 26, "bold")).pack(side="left")
        self.add_btn = ctk.CTkButton(
            header, text="+ Thêm dự án", fg_color="#16a34a", hover_color="#15803d", width=130, command=self.open_add_dialog
        )
        self.add_btn.pack(side="right")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(0, 12))
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo ID, tên hoặc mô tả...", height=36)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.handle_search)
        self.count_label = ctk.CTkLabel(toolbar, text="", text_color="#94a3b8", width=120)
        self.count_label.pack(side="right", padx=(12, 0))

        self.table_container = ctk.CTkScrollableFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        self.table_container.pack(pady=(0, 24), padx=24, fill="both", expand=True)

        if not self.can_manage:
            self.add_btn.configure(state="disabled", fg_color="#64748b")

    def refresh_table(self, data=None):
        """Render lại bảng dự án theo dữ liệu hiện tại."""
        for child in self.table_container.winfo_children():
            child.destroy()

        projects = data if data is not None else self.view_model.display_projects
        self.count_label.configure(text=f"{len(projects)} dự án")

        header = ctk.CTkFrame(self.table_container, fg_color=("#e5e7eb", "#242424"), corner_radius=8)
        header.pack(fill="x", pady=(0, 8), padx=4)
        columns = [("ID", 95), ("Tên dự án", 230), ("Mô tả", 330), ("Thao tác", 150)]
        for text, width in columns:
            ctk.CTkLabel(header, text=text, width=width, font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left", padx=8, pady=10)

        if not projects:
            ctk.CTkLabel(self.table_container, text="Chưa có dự án phù hợp.", text_color="#94a3b8", font=("Segoe UI", 14)).pack(pady=40)
            return

        for index, project in enumerate(projects):
            row_color = ("#ffffff", "#202020") if index % 2 == 0 else ("#f9fafb", "#1b1b1b")
            row = ctk.CTkFrame(self.table_container, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            ctk.CTkLabel(row, text=project.project_id, width=95, anchor="w").pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=project.name, width=230, anchor="w", wraplength=220).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=project.description or "-", width=330, anchor="w", wraplength=320).pack(side="left", padx=8, pady=8)

            actions = ctk.CTkFrame(row, fg_color="transparent", width=150)
            actions.pack(side="left", padx=8, pady=6)
            btn_edit = ctk.CTkButton(
                actions, text="Sửa", width=58, height=28, fg_color="#52525b", hover_color="#3f3f46", command=lambda p=project: self.open_edit_dialog(p)
            )
            btn_edit.pack(side="left", padx=2)
            btn_delete = ctk.CTkButton(
                actions,
                text="Xóa",
                width=58,
                height=28,
                fg_color="#dc2626",
                hover_color="#b91c1c",
                command=lambda project_id=project.project_id: self.delete_project(project_id),
            )
            btn_delete.pack(side="left", padx=2)
            if not self.can_manage:
                btn_edit.configure(state="disabled", fg_color="#64748b")
                btn_delete.configure(state="disabled", fg_color="#64748b")

    def handle_search(self, _event=None):
        """Xử lý tìm kiếm realtime theo ô search."""
        self.refresh_table(self.view_model.search(self.search_entry.get()))

    def open_add_dialog(self):
        """Mở dialog tạo dự án mới."""
        if not self.can_manage:
            messagebox.showwarning("Thông báo", "Bạn không có quyền thêm dự án.")
            return
        ProjectDialog(self, self.handle_save)

    def open_edit_dialog(self, project):
        """Mở dialog chỉnh sửa dự án hiện có."""
        if not self.can_manage:
            messagebox.showwarning("Thông báo", "Bạn không có quyền sửa dự án.")
            return
        ProjectDialog(self, self.handle_save, project)

    def handle_save(self, project_id, name, description, dialog, original_project):
        """Lưu dữ liệu dự án từ dialog về viewmodel."""
        if original_project is None:
            success, message = self.view_model.validate_and_add(project_id, name, description)
        else:
            success, message = self.view_model.update_project(original_project.project_id, project_id, name, description)

        if success:
            dialog.destroy()
            self.handle_search()
        else:
            messagebox.showwarning("Thông báo", message)

    def delete_project(self, project_id):
        """Xóa dự án sau khi xác nhận."""
        if not messagebox.askyesno("Xác nhận", f"Xóa dự án '{project_id}'?"):
            return
        success, message = self.view_model.delete_project(project_id)
        if not success:
            messagebox.showwarning("Thông báo", message)
        self.handle_search()
