import customtkinter as ctk
from tkinter import messagebox

from ProjectTracker.viewmodels.project_manager_viewmodel import ProjectViewModel


class AddProjectDialog(ctk.CTkToplevel):
    """Cửa sổ Popup thêm dự án"""

    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("Thêm Dự Án Mới")
        self.geometry("350x400")
        self.grab_set()  # Giữ focus vào dialog

        ctk.CTkLabel(self, text="NHẬP THÔNG TIN DỰ ÁN", font=("Arial", 16, "bold")).pack(pady=20)

        self.entry_id = ctk.CTkEntry(self, placeholder_text="ID Dự án...", width=250)
        self.entry_id.pack(pady=10)

        self.entry_name = ctk.CTkEntry(self, placeholder_text="Tên dự án...", width=250)
        self.entry_name.pack(pady=10)

        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Mô tả...", width=250)
        self.entry_desc.pack(pady=10)

        self.btn_save = ctk.CTkButton(self, text="Lưu Dự Án", fg_color="green",
                                      command=lambda: on_save_callback(
                                          self.entry_id.get(),
                                          self.entry_name.get(),
                                          self.entry_desc.get(),
                                          self))
        self.btn_save.pack(pady=20)

class ProjectsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.view_model = ProjectViewModel()
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        # Tiêu đề
        ctk.CTkLabel(self, text="📁 QUẢN LÝ DỰ ÁN (PROJECTS)", font=("Arial", 22, "bold")).pack(pady=20, anchor="w",
                                                                                               padx=20)

        # Thanh công cụ
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Tìm tên dự án hoặc ID...", width=250)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.handle_search)  # Tìm kiếm ngay khi gõ

        self.btn_add = ctk.CTkButton(toolbar, text="+ Thêm Dự Án", fg_color="#28a745", hover_color="#218838",
                                     command=self.open_add_dialog)
        self.btn_add.pack(side="right", padx=5)

        # Khu vực bảng hiển thị (Sạch sẽ hơn TextBox)
        self.table_container = ctk.CTkScrollableFrame(self, fg_color="#2b2b2b")
        self.table_container.pack(pady=10, padx=20, fill="both", expand=True)

    def refresh_table(self, data=None):
        # Xóa các dòng cũ
        for child in self.table_container.winfo_children():
            child.destroy()

        projects = data if data is not None else self.view_model.display_projects

        # Tiêu đề cột
        header_frame = ctk.CTkFrame(self.table_container, fg_color="#3d3d3d")
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="ID", width=100, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Tên Dự Án", width=200, font=("Arial", 12, "bold"), anchor="w").pack(
            side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Mô Tả", font=("Arial", 12, "bold"), anchor="w").pack(side="left", padx=10,
                                                                                              fill="x", expand=True)

        # Đổ dữ liệu
        for p in projects:
            row = ctk.CTkFrame(self.table_container, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=p.project_id, width=100).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=p.name, width=200, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=p.description, anchor="w").pack(side="left", padx=10, fill="x", expand=True)

    def handle_search(self, event):
        query = self.search_entry.get()
        filtered_data = self.view_model.search(query)
        self.refresh_table(filtered_data)

    def open_add_dialog(self):
        AddProjectDialog(self, self.handle_add_save)

    def handle_add_save(self, p_id, p_name, p_desc, dialog_window):
        success, message = self.view_model.validate_and_add(p_id, p_name, p_desc)
        if success:
            dialog_window.destroy()
            self.refresh_table()
        else:
            messagebox.showwarning("Thông báo", message)