import customtkinter as ctk


class ProjectsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Tiêu đề
        ctk.CTkLabel(self, text="📁 QUẢN LÝ DỰ ÁN (PROJECTS)", font=("Arial", 22, "bold")).pack(pady=20, anchor="w",
                                                                                               padx=20)

        # Thanh công cụ (giả lập)
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=10)

        ctk.CTkEntry(toolbar, placeholder_text="Tìm tên dự án...", width=200).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="+ Thêm Dự Án", fg_color="green", width=120).pack(side="right", padx=5)

        # Khu vực hiển thị bảng (giả lập bằng TextBox)
        table_mock = ctk.CTkTextbox(self, width=600, height=400)
        table_mock.pack(pady=20, padx=20, fill="both", expand=True)
        table_mock.insert("0.0", "project_id | project_name | description\n")
        table_mock.insert("end", "--------------------------------------\n")
        table_mock.insert("end", "1          | Đồ án Python | Quản lý công việc\n")
        table_mock.insert("end", "2          | Website HUIT | Trang tin tức\n")
        table_mock.configure(state="disabled")  # Không cho sửa