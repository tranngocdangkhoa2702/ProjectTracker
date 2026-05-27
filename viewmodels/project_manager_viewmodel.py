import json
from pathlib import Path

from models.audit_log_model import AuditLogModel
from models.project_manager_model import ProjectModel


class ProjectViewModel:
    """Nghiệp vụ quản lý dự án: CRUD và tìm kiếm."""

    def __init__(self, actor="system", can_manage=True):
        """Khởi tạo dữ liệu dự án cùng quyền chỉnh sửa."""
        self.file_path = Path(__file__).resolve().parents[1] / "projects.json"
        self.all_projects = []
        self.display_projects = []
        self.actor = actor
        self.can_manage = can_manage
        self.audit = AuditLogModel()
        self.load_data()
        self.search("")

    def _deny(self):
        """Thông báo dùng chung khi không có quyền thao tác."""
        return False, "Bạn không có quyền chỉnh sửa dự án."

    def load_data(self):
        """Đọc dữ liệu dự án từ JSON, tạo dữ liệu mẫu nếu chưa có."""
        if not self.file_path.exists():
            self.all_projects = [
                ProjectModel("HUIT01", "Đồ án Python", "Quản lý công việc và tiến độ."),
                ProjectModel("HUIT02", "Website HUIT", "Cổng thông tin dành cho sinh viên."),
            ]
            self.save_data()
            return

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.all_projects = [ProjectModel(p.get("project_id", ""), p.get("name", ""), p.get("description", "")) for p in data]
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Lỗi định dạng file projects.json: {exc}")
            self.all_projects = []

    def save_data(self):
        """Ghi dữ liệu dự án hiện tại ra file JSON."""
        data_to_save = [{"project_id": p.project_id, "name": p.name, "description": p.description} for p in self.all_projects]
        try:
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            print(f"Không thể lưu dữ liệu: {exc}")

    def validate_and_add(self, project_id, name, description):
        """Validate và thêm dự án mới."""
        if not self.can_manage:
            return self._deny()
        project_id = project_id.strip()
        name = name.strip()
        description = description.strip()

        if not project_id or not name:
            return False, "ID và tên dự án không được để trống!"
        if any(p.project_id.lower() == project_id.lower() for p in self.all_projects):
            return False, f"ID '{project_id}' đã tồn tại!"

        self.all_projects.append(ProjectModel(project_id, name, description))
        self.save_data()
        self.search("")
        self.audit.log(self.actor, "create_project", "project", project_id, name)
        return True, "Thêm dự án thành công."

    def update_project(self, old_project_id, project_id, name, description):
        """Cập nhật dự án theo project_id cũ."""
        if not self.can_manage:
            return self._deny()
        project_id = project_id.strip()
        name = name.strip()
        description = description.strip()

        if not project_id or not name:
            return False, "ID và tên dự án không được để trống!"
        if any(p.project_id.lower() == project_id.lower() and p.project_id != old_project_id for p in self.all_projects):
            return False, f"ID '{project_id}' đã tồn tại!"

        project = self.get_project(old_project_id)
        if project is None:
            return False, "Không tìm thấy dự án cần cập nhật."

        project.project_id = project_id
        project.name = name
        project.description = description
        self.save_data()
        self.search("")
        self.audit.log(self.actor, "update_project", "project", project_id, name)
        return True, "Cập nhật dự án thành công."

    def delete_project(self, project_id):
        """Xóa dự án theo project_id."""
        if not self.can_manage:
            return self._deny()
        before = len(self.all_projects)
        self.all_projects = [p for p in self.all_projects if p.project_id != project_id]
        if len(self.all_projects) == before:
            return False, "Không tìm thấy dự án cần xóa."
        self.save_data()
        self.search("")
        self.audit.log(self.actor, "delete_project", "project", project_id, "delete")
        return True, "Đã xóa dự án."

    def get_project(self, project_id):
        """Tìm dự án theo ID."""
        return next((p for p in self.all_projects if p.project_id == project_id), None)

    def search(self, query):
        """Tìm dự án theo id/tên/mô tả."""
        query = query.lower().strip()
        if not query:
            self.display_projects = list(self.all_projects)
        else:
            self.display_projects = [
                p for p in self.all_projects if query in p.name.lower() or query in p.project_id.lower() or query in p.description.lower()
            ]
        return self.display_projects
