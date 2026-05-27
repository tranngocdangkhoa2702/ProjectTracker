import csv
import shutil
from datetime import datetime
from pathlib import Path

from models.audit_log_model import AuditLogModel
from viewmodels.project_manager_viewmodel import ProjectViewModel
from viewmodels.task_mananger_viewmodel import TaskViewModel


class SystemViewModel:
    """Nghiệp vụ hệ thống: export, backup/restore, audit logs."""

    def __init__(self, actor="system"):
        """Khởi tạo các VM con và context người thao tác."""
        self.root = Path(__file__).resolve().parents[1]
        self.audit = AuditLogModel()
        self.actor = actor
        self.project_vm = ProjectViewModel()
        self.task_vm = TaskViewModel()

    def export_reports(self):
        """Xuất báo cáo CSV cho dự án và công việc."""
        report_dir = self.root / "exports"
        report_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        projects_path = report_dir / f"projects_{stamp}.csv"
        tasks_path = report_dir / f"tasks_{stamp}.csv"

        with projects_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["project_id", "name", "description"])
            for p in self.project_vm.all_projects:
                writer.writerow([p.project_id, p.name, p.description])

        with tasks_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["task_id", "name", "deadline", "priority", "status"])
            for t in self.task_vm.all_tasks:
                writer.writerow([t.task_id, t.name, t.deadline, t.priority, t.status])

        self.audit.log(self.actor, "export_reports", "report", stamp, f"{projects_path.name}, {tasks_path.name}")
        return True, f"Đã xuất báo cáo:\n- {projects_path}\n- {tasks_path}"

    def create_backup(self):
        """Tạo bản sao lưu toàn bộ dữ liệu cốt lõi."""
        backup_dir = self.root / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_dir = backup_dir / f"backup_{stamp}"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        for filename in ["database.db", "projects.json", "tasks.json"]:
            src = self.root / filename
            if src.exists():
                shutil.copy2(src, bundle_dir / filename)

        self.audit.log(self.actor, "backup", "system", stamp, str(bundle_dir))
        return True, f"Đã backup dữ liệu tại:\n{bundle_dir}"

    def restore_latest_backup(self):
        """Khôi phục dữ liệu từ bản backup mới nhất."""
        backup_dir = self.root / "backups"
        if not backup_dir.exists():
            return False, "Chưa có thư mục backups."
        bundles = sorted([p for p in backup_dir.iterdir() if p.is_dir() and p.name.startswith("backup_")], reverse=True)
        if not bundles:
            return False, "Chưa có bản backup nào để khôi phục."
        latest = bundles[0]
        restored = []
        for filename in ["database.db", "projects.json", "tasks.json"]:
            src = latest / filename
            dst = self.root / filename
            if src.exists():
                shutil.copy2(src, dst)
                restored.append(filename)
        self.audit.log(self.actor, "restore_backup", "system", latest.name, ", ".join(restored))
        return True, f"Đã khôi phục từ {latest}\nFile: {', '.join(restored)}"

    def list_logs(self, limit=300):
        """Lấy danh sách audit log để hiển thị."""
        return self.audit.list_logs(limit=limit)
