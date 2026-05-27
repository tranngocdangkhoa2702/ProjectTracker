import customtkinter as ctk
from tkinter import messagebox

from viewmodels.system_viewmodel import SystemViewModel


class SystemToolsView(ctk.CTkFrame):
    """Màn công cụ hệ thống: export, backup, restore."""

    def __init__(self, master, actor="system"):
        """Khởi tạo view công cụ cho người quản trị."""
        super().__init__(master, fg_color="transparent")
        self.vm = SystemViewModel(actor=actor)
        self.setup_ui()

    def setup_ui(self):
        """Dựng giao diện các khối thao tác hệ thống."""
        ctk.CTkLabel(self, text="Công cụ quản trị", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=24, pady=(24, 10))

        box = ctk.CTkFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        box.pack(fill="x", padx=24, pady=(0, 12))
        ctk.CTkLabel(box, text="Xuất báo cáo CSV", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(box, text="Xuất danh sách dự án và công việc để nộp báo cáo.", text_color="#94a3b8").pack(anchor="w", padx=16, pady=(0, 10))
        ctk.CTkButton(box, text="Xuất báo cáo", command=self.export_reports).pack(anchor="w", padx=16, pady=(0, 14))

        box2 = ctk.CTkFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        box2.pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkLabel(box2, text="Backup dữ liệu", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(box2, text="Sao lưu database và file JSON vào thư mục backups.", text_color="#94a3b8").pack(anchor="w", padx=16, pady=(0, 10))
        ctk.CTkButton(box2, text="Tạo backup", fg_color="#0ea5e9", hover_color="#0284c7", command=self.create_backup).pack(
            anchor="w", padx=16, pady=(0, 8)
        )
        ctk.CTkButton(box2, text="Khôi phục backup mới nhất", fg_color="#f59e0b", hover_color="#d97706", command=self.restore_backup).pack(
            anchor="w", padx=16, pady=(0, 14)
        )

        self.status = ctk.CTkTextbox(self, height=260, corner_radius=10)
        self.status.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.status.insert("1.0", "Sẵn sàng thực hiện export/backup.\n")
        self.status.configure(state="disabled")

    def append_status(self, text):
        """Ghi log trạng thái thao tác lên ô kết quả."""
        self.status.configure(state="normal")
        self.status.insert("end", text + "\n\n")
        self.status.see("end")
        self.status.configure(state="disabled")

    def export_reports(self):
        """Thực thi xuất báo cáo CSV."""
        success, message = self.vm.export_reports()
        self.append_status(message)
        if success:
            messagebox.showinfo("Thành công", "Đã xuất báo cáo CSV.")

    def create_backup(self):
        """Thực thi tạo backup dữ liệu."""
        success, message = self.vm.create_backup()
        self.append_status(message)
        if success:
            messagebox.showinfo("Thành công", "Đã tạo backup.")

    def restore_backup(self):
        """Khôi phục dữ liệu từ bản backup mới nhất."""
        if not messagebox.askyesno("Xác nhận", "Khôi phục sẽ ghi đè dữ liệu hiện tại. Tiếp tục?"):
            return
        success, message = self.vm.restore_latest_backup()
        self.append_status(message)
        if success:
            messagebox.showinfo("Thành công", "Đã khôi phục backup mới nhất.")
        else:
            messagebox.showwarning("Thông báo", message)
