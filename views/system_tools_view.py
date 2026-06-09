import customtkinter as ctk
from tkinter import messagebox

from viewmodels.system_viewmodel import SystemViewModel


class SystemToolsView(ctk.CTkFrame):
    """Man cong cu he thong: export, backup, restore."""

    def __init__(self, master, actor="system", actor_role="member"):
        super().__init__(master, fg_color="transparent")
        self.actor_role = actor_role
        self.vm = SystemViewModel(actor=actor, actor_role=actor_role)
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Công cụ quản trị", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=24, pady=(24, 10))

        box = ctk.CTkFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        box.pack(fill="x", padx=24, pady=(0, 12))
        ctk.CTkLabel(box, text="Xuất báo cáo CSV", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(box, text="Xuất danh sách dự án và công việc theo phạm vi quyền hiện tại.", text_color="#94a3b8").pack(
            anchor="w", padx=16, pady=(0, 10)
        )
        export_buttons = ctk.CTkFrame(box, fg_color="transparent")
        export_buttons.pack(anchor="w", padx=16, pady=(0, 14))
        ctk.CTkButton(export_buttons, text="Xuất CSV", command=self.export_reports).pack(side="left")
        ctk.CTkButton(
            export_buttons, text="Xuất Excel (.xlsx)", fg_color="#16a34a", hover_color="#15803d", command=self.export_excel
        ).pack(side="left", padx=(10, 0))

        box2 = ctk.CTkFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        box2.pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkLabel(box2, text="Sao lưu dữ liệu", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(box2, text="Sao lưu/khôi phục là nghiệp vụ của quản trị vì có thể ghi đè toàn bộ dữ liệu.", text_color="#94a3b8").pack(
            anchor="w", padx=16, pady=(0, 10)
        )
        self.backup_btn = ctk.CTkButton(box2, text="Tạo bản sao lưu", fg_color="#0ea5e9", hover_color="#0284c7", command=self.create_backup)
        self.backup_btn.pack(anchor="w", padx=16, pady=(0, 8))
        self.restore_btn = ctk.CTkButton(
            box2, text="Khôi phục bản sao lưu mới nhất", fg_color="#f59e0b", hover_color="#d97706", command=self.restore_backup
        )
        self.restore_btn.pack(anchor="w", padx=16, pady=(0, 14))
        if self.actor_role != "admin":
            self.backup_btn.configure(state="disabled", fg_color="#64748b")
            self.restore_btn.configure(state="disabled", fg_color="#64748b")

        self.status = ctk.CTkTextbox(self, height=260, corner_radius=10)
        self.status.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.status.insert("1.0", "Sẵn sàng xuất báo cáo hoặc sao lưu dữ liệu.\n")
        self.status.configure(state="disabled")

    def append_status(self, text):
        self.status.configure(state="normal")
        self.status.insert("end", text + "\n\n")
        self.status.see("end")
        self.status.configure(state="disabled")

    def export_reports(self):
        success, message = self.vm.export_reports()
        self.append_status(message)
        if success:
            messagebox.showinfo("Thành công", "Đã xuất báo cáo CSV.")
        else:
            messagebox.showwarning("Thông báo", message)

    def export_excel(self):
        success, message = self.vm.export_to_excel()
        self.append_status(message)
        if success:
            messagebox.showinfo("Thành công", "Đã xuất báo cáo Excel (.xlsx) bằng Pandas.")
        else:
            messagebox.showwarning("Thông báo", message)

    def create_backup(self):
        success, message = self.vm.create_backup()
        self.append_status(message)
        if success:
            messagebox.showinfo("Thành công", "Đã tạo bản sao lưu.")
        else:
            messagebox.showwarning("Thông báo", message)

    def restore_backup(self):
        if not messagebox.askyesno("Xác nhận", "Khôi phục sẽ ghi đè dữ liệu hiện tại. Tiếp tục?"):
            return
        success, message = self.vm.restore_latest_backup()
        self.append_status(message)
        if success:
            messagebox.showinfo("Thành công", "Đã khôi phục bản sao lưu mới nhất.")
        else:
            messagebox.showwarning("Thông báo", message)
