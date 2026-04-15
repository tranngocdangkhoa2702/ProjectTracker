import customtkinter as ctk
from tkinter import messagebox
from ProjectTracker.viewmodels.task_mananger_viewmodel import TaskViewModel

class AddTaskDialog(ctk.CTkToplevel):
    # (Phần này code của bạn đã ổn, mình giữ nguyên)
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("Thêm Công Việc Mới")
        self.geometry("350x450")
        self.grab_set()

        ctk.CTkLabel(self, text="THÔNG TIN CÔNG VIỆC", font=("Arial", 16, "bold")).pack(pady=20)
        self.e_id = ctk.CTkEntry(self, placeholder_text="ID (ví dụ: 103)", width=250)
        self.e_id.pack(pady=10)
        self.e_name = ctk.CTkEntry(self, placeholder_text="Tên công việc...", width=250)
        self.e_name.pack(pady=10)
        self.e_deadline = ctk.CTkEntry(self, placeholder_text="Deadline (dd/mm)...", width=250)
        self.e_deadline.pack(pady=10)
        self.e_priority = ctk.CTkOptionMenu(self, values=["1 (P1)", "2 (P2)", "3 (P3)"], width=250)
        self.e_priority.pack(pady=10)

        ctk.CTkButton(self, text="Lưu", fg_color="green",
                     command=lambda: on_save_callback(
                         self.e_id.get(), self.e_name.get(),
                         self.e_deadline.get(), self.e_priority.get(), self)).pack(pady=20)

class TasksView(ctk.CTkFrame):
    def __init__(self, master):
        # 1. Gọi init của lớp cha ngay lập tức
        super().__init__(master)
        self.view_model = TaskViewModel()
        # 2. Các hàm setup phải nằm cùng cấp độ thụt lề với __init__
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        # Header
        ctk.CTkLabel(self, text="☑️ QUẢN LÝ CÔNG VIỆC (TASKS)", font=("Arial", 22, "bold")).pack(pady=20, anchor="w", padx=20)

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=10)

        # Segmented Button
        self.seg_button = ctk.CTkSegmentedButton(toolbar, values=["Tất cả", "Đang làm", "Hoàn thành"],
                                                 command=self.handle_filter)
        self.seg_button.set("Tất cả")
        self.seg_button.pack(side="left", padx=5)

        # Ô tìm kiếm
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Tìm task...", width=150)
        self.search_entry.pack(side="left", padx=20)
        self.search_entry.bind("<KeyRelease>", lambda e: self.handle_filter())

        # Nút thêm
        ctk.CTkButton(toolbar, text="+ Thêm Task", fg_color="#28a745", width=100,
                      command=self.open_add_dialog).pack(side="right", padx=5)

        # Table Container
        self.table_container = ctk.CTkScrollableFrame(self, fg_color="#2b2b2b")
        self.table_container.pack(pady=10, padx=20, fill="both", expand=True)

    def refresh_table(self, data=None):
        for child in self.table_container.winfo_children():
            child.destroy()

        tasks = data if data is not None else self.view_model.display_tasks

        h_frame = ctk.CTkFrame(self.table_container, fg_color="#3d3d3d")
        h_frame.pack(fill="x", pady=2)
        cols = [("ID", 60), ("Tên công việc", 180), ("Deadline", 100), ("Priority", 100), ("Status", 100)]
        for text, width in cols:
            ctk.CTkLabel(h_frame, text=text, width=width, font=("Arial", 12, "bold")).pack(side="left", padx=10)

        for t in tasks:
            row = ctk.CTkFrame(self.table_container, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=t.task_id, width=60).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=t.name, width=180, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=t.deadline, width=100).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=t.priority, width=100).pack(side="left", padx=10)

            status_color = "#ffcc00" if t.status == "Todo" else "#28a745"
            ctk.CTkLabel(row, text=t.status, width=100, text_color=status_color).pack(side="left", padx=10)

    def handle_filter(self, status=None):
        status = status if status else self.seg_button.get()
        query = self.search_entry.get()
        filtered_data = self.view_model.filter_and_search(status, query)
        self.refresh_table(filtered_data)

    def open_add_dialog(self):
        AddTaskDialog(self, self.handle_add_save)

    def handle_add_save(self, t_id, t_name, t_deadline, t_priority, dialog):
        success, message = self.view_model.validate_and_add(t_id, t_name, t_deadline, t_priority)
        if success:
            dialog.destroy()
            self.handle_filter()
        else:
            messagebox.showwarning("Lỗi", message)