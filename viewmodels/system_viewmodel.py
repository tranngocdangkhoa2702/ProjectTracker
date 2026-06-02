import csv
import shutil
from datetime import datetime
from pathlib import Path

from models.audit_log_model import AuditLogModel
from viewmodels.project_manager_viewmodel import ProjectViewModel
from viewmodels.task_mananger_viewmodel import TaskViewModel


class SystemViewModel:
    """Nghiep vu he thong: export, backup/restore va audit logs."""

    def __init__(self, actor="system", actor_role="member"):
        self.root = Path(__file__).resolve().parents[1]
        self.audit = AuditLogModel()
        self.actor = actor
        self.actor_role = actor_role
        self.project_vm = ProjectViewModel(actor=actor, actor_role=actor_role)
        self.task_vm = TaskViewModel(actor=actor, actor_role=actor_role)

    def _is_admin(self):
        return self.actor_role == "admin"

    def export_reports(self):
        if not self._is_admin():
            return False, "Bạn không có quyền xuất báo cáo."

        report_dir = self.root / "exports"
        report_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        projects_path = report_dir / f"projects_{stamp}.csv"
        tasks_path = report_dir / f"tasks_{stamp}.csv"

        with projects_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["project_id", "name", "description", "status", "leader", "members", "start_date", "end_date"])
            for p in self.project_vm.all_projects:
                if self.project_vm.can_view_project(p):
                    writer.writerow([p.project_id, p.name, p.description, p.status, p.leader, ", ".join(p.members), p.start_date, p.end_date])

        with tasks_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "task_id",
                    "project_id",
                    "name",
                    "assignee",
                    "start_date",
                    "deadline",
                    "requested_deadline",
                    "priority",
                    "status",
                    "approval_state",
                    "extension_status",
                    "created_by",
                ]
            )
            for t in self.task_vm.scoped_tasks():
                writer.writerow(
                    [
                        t.task_id,
                        t.project_id,
                        t.name,
                        t.assignee,
                        t.start_date,
                        t.deadline,
                        t.requested_deadline,
                        t.priority,
                        t.status,
                        t.approval_state,
                        t.extension_status,
                        t.created_by,
                    ]
                )

        self.audit.log(self.actor, "export_reports", "report", stamp, f"{projects_path.name}, {tasks_path.name}")
        return True, f"Đã xuất báo cáo:\n- {projects_path}\n- {tasks_path}"

    def create_backup(self):
        if not self._is_admin():
            return False, "Chỉ quản trị viên mới được tạo bản sao lưu toàn hệ thống."

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
        return True, f"Đã sao lưu dữ liệu tại:\n{bundle_dir}"

    def restore_latest_backup(self):
        if not self._is_admin():
            return False, "Chỉ quản trị viên mới được khôi phục bản sao lưu."

        backup_dir = self.root / "backups"
        if not backup_dir.exists():
            return False, "Chưa có thư mục sao lưu."
        bundles = sorted([p for p in backup_dir.iterdir() if p.is_dir() and p.name.startswith("backup_")], reverse=True)
        if not bundles:
            return False, "Chưa có bản sao lưu nào để khôi phục."
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
        if not self._is_admin():
            return []
        return self.audit.list_logs(limit=limit)
