import customtkinter as ctk

from viewmodels.system_viewmodel import SystemViewModel


class AuditLogsView(ctk.CTkFrame):
    """Màn hình xem nhật ký thao tác hệ thống."""

    def __init__(self, master, actor="system", actor_role="member"):
        super().__init__(master, fg_color="transparent")
        self.vm = SystemViewModel(actor=actor, actor_role=actor_role)
        self.logs = []
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 10))
        ctk.CTkLabel(header, text="Nhật ký hệ thống", font=("Segoe UI", 26, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Làm mới", width=90, command=self.refresh).pack(side="right")

        self.search = ctk.CTkEntry(self, placeholder_text="Lọc theo người thao tác, hành động hoặc đối tượng...", height=36)
        self.search.pack(fill="x", padx=24, pady=(0, 12))
        self.search.bind("<KeyRelease>", lambda _e: self.render())

        self.container = ctk.CTkScrollableFrame(self, fg_color=("#f3f4f6", "#171717"), corner_radius=10)
        self.container.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    def refresh(self):
        self.logs = self.vm.list_logs(limit=500)
        self.render()

    def render(self):
        for child in self.container.winfo_children():
            child.destroy()

        query = self.search.get().lower().strip()
        logs = [
            log
            for log in self.logs
            if not query
            or query in log["actor"].lower()
            or query in log["action"].lower()
            or query in log["target_type"].lower()
            or query in str(log["target_id"]).lower()
        ]
        if not logs:
            ctk.CTkLabel(self.container, text="Không có nhật ký phù hợp.", text_color="#94a3b8").pack(pady=30)
            return

        for log in logs:
            card = ctk.CTkFrame(self.container, fg_color=("#ffffff", "#202020"), corner_radius=8)
            card.pack(fill="x", padx=8, pady=5)
            ctk.CTkLabel(
                card,
                text=f"[{log['created_at']}] {log['actor']} - {log['action']}",
                font=("Segoe UI", 12, "bold"),
                anchor="w",
            ).pack(fill="x", padx=12, pady=(8, 2))
            ctk.CTkLabel(
                card,
                text=f"{log['target_type']}:{log['target_id']} | {log['details']}",
                text_color="#94a3b8",
                anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 8))
