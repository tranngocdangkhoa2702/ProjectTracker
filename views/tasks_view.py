import customtkinter as ctk


class TasksView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="✅ QUẢN LÝ CÔNG VIỆC (TASKS)", font=("Arial", 22, "bold")).pack(pady=20, anchor="w",
                                                                                                padx=20)

        # Bộ lọc (giả lập)
        filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        filter_bar.pack(fill="x", padx=20, pady=10)
        ctk.CTkSegmentedButton(filter_bar, values=["Tất cả", "Đang làm", "Hoàn thành"]).pack(side="left")

        # Khu vực hiển thị bảng (giả lập)
        table_mock = ctk.CTkTextbox(self, width=600, height=400)
        table_mock.pack(pady=20, padx=20, fill="both", expand=True)
        table_mock.insert("0.0", "task_id | task_name | deadline | priority | status\n")
        table_mock.insert("end", "-------------------------------------------------\n")
        table_mock.insert("end", "101     | Code Login | 20/12   | 1 (P1)   | Todo\n")
        table_mock.insert("end", "102     | Vẽ CSDL   | 18/12   | 2 (P2)   | Done\n")
        table_mock.configure(state="disabled")