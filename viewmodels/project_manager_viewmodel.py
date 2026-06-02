import json
from datetime import datetime
from pathlib import Path

from models.audit_log_model import AuditLogModel
from models.project_manager_model import ProjectModel
from models.user_model import UserModel


PROJECT_STATUSES = ["Lên kế hoạch", "Đang thực hiện", "Tạm dừng", "Hoàn thành", "Đã hủy"]
PROJECT_STATUS_ALIASES = {
    "Planning": "Lên kế hoạch",
    "Active": "Đang thực hiện",
    "Paused": "Tạm dừng",
    "Done": "Hoàn thành",
    "Cancelled": "Đã hủy",
}


class ProjectViewModel:
    """Nghiep vu quan ly du an: CRUD, phan quyen va rang buoc du lieu."""

    def __init__(self, actor="system", actor_role=None, can_manage=None):
        self.root = Path(__file__).resolve().parents[1]
        self.file_path = self.root / "projects.json"
        self.tasks_path = self.root / "tasks.json"
        self.all_projects = []
        self.display_projects = []
        self.actor = actor or "system"
        self.actor_role = actor_role or ("admin" if can_manage else "member")
        self.audit = AuditLogModel()
        self.user_model = UserModel()
        self.load_data()
        self.search("")

    def _deny(self):
        return False, "Bạn không có quyền thực hiện thao tác này với dự án."

    def _normalize_status(self, status):
        status = str(status or "").strip()
        status = PROJECT_STATUS_ALIASES.get(status, status or "Lên kế hoạch")
        return status if status in PROJECT_STATUSES else "Lên kế hoạch"

    def _parse_members(self, members):
        if isinstance(members, list):
            return [str(member).strip() for member in members if str(member).strip()]
        return [member.strip() for member in str(members or "").split(",") if member.strip()]

    def _project_to_dict(self, project):
        return {
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "leader": project.leader,
            "members": project.members,
            "start_date": project.start_date,
            "end_date": project.end_date,
        }

    def _is_valid_date(self, value):
        if not value:
            return True
        try:
            datetime.strptime(value, "%d/%m")
            return True
        except ValueError:
            return False

    def _validate_common(self, project_id, name, status, start_date, end_date):
        if not project_id or not name:
            return False, "ID và tên dự án không được để trống."
        if status not in PROJECT_STATUSES:
            return False, "Trạng thái dự án không hợp lệ."
        if not self._is_valid_date(start_date) or not self._is_valid_date(end_date):
            return False, "Ngày bắt đầu/kết thúc phải đúng định dạng dd/mm."
        return True, ""

    def _leader_role_is_valid(self, username):
        if not username:
            return True
        for user in self.user_model.list_active_users():
            if user["username"] == username:
                return user["role"] in ("admin", "leader")
        return False

    def active_member_usernames(self):
        return [user["username"] for user in self.user_model.list_active_users() if user["role"] == "member"]

    def _validate_members(self, members):
        valid_members = set(self.active_member_usernames())
        invalid = [member for member in members if member not in valid_members]
        if invalid:
            return False, "Thành viên dự án phải là tài khoản thành viên đang hoạt động: " + ", ".join(invalid)
        return True, ""

    def generate_project_id(self):
        """Sinh ID du an tiep theo theo mau HUIT01, HUIT02..."""
        max_number = 0
        for project in self.all_projects:
            project_id = project.project_id.upper()
            if project_id.startswith("HUIT") and project_id[4:].isdigit():
                max_number = max(max_number, int(project_id[4:]))
        return f"HUIT{max_number + 1:02d}"

    def _is_admin(self):
        return self.actor_role == "admin"

    def _is_leader(self):
        return self.actor_role == "leader"

    def can_create_project(self):
        return self._is_admin()

    def can_manage_project(self, project):
        if self._is_admin():
            return True
        if self._is_leader():
            return not project.leader or project.leader == self.actor
        return False

    def can_view_project(self, project):
        if self._is_admin():
            return True
        if self._is_leader():
            return not project.leader or project.leader == self.actor or self.actor in project.members
        return self.actor in project.members or project.leader == self.actor

    def scoped_projects(self):
        return [project for project in self.all_projects if self.can_view_project(project)]

    def manageable_project_ids(self):
        return [project.project_id for project in self.all_projects if self.can_manage_project(project)]

    def load_data(self):
        if not self.file_path.exists():
            self.all_projects = [
                ProjectModel("HUIT01", "Đồ án Python", "Quản lý công việc và tiến độ.", "Đang thực hiện", self.actor, []),
                ProjectModel("HUIT02", "Website HUIT", "Cổng thông tin dành cho sinh viên.", "Lên kế hoạch", self.actor, []),
            ]
            self.save_data()
            return

        migrated = False
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.all_projects = []
            valid_member_set = set(self.active_member_usernames())
            for p in data:
                normalized_status = self._normalize_status(p.get("status", "Lên kế hoạch"))
                members = self._parse_members(p.get("members", []))
                filtered_members = [member for member in members if member in valid_member_set]
                if (
                    "status" not in p
                    or "leader" not in p
                    or "members" not in p
                    or normalized_status != p.get("status")
                    or filtered_members != members
                ):
                    migrated = True
                self.all_projects.append(
                    ProjectModel(
                        p.get("project_id", ""),
                        p.get("name", ""),
                        p.get("description", ""),
                        normalized_status,
                        p.get("leader", ""),
                        filtered_members,
                        p.get("start_date", ""),
                        p.get("end_date", ""),
                    )
                )
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Lỗi định dạng file projects.json: {exc}")
            self.all_projects = []

        if migrated:
            self.save_data()

    def save_data(self):
        try:
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump([self._project_to_dict(project) for project in self.all_projects], f, ensure_ascii=False, indent=4)
        except OSError as exc:
            print(f"Không thể lưu dữ liệu: {exc}")

    def validate_and_add(self, project_id, name, description, status="Lên kế hoạch", leader="", members=None, start_date="", end_date=""):
        if not self.can_create_project():
            return self._deny()
        project_id = project_id.strip() or self.generate_project_id()
        name = name.strip()
        description = description.strip()
        status = self._normalize_status(status)
        leader = leader.strip() or (self.actor if self._is_leader() else "")
        members = self._parse_members(members)
        start_date = start_date.strip()
        end_date = end_date.strip()

        valid, message = self._validate_common(project_id, name, status, start_date, end_date)
        if not valid:
            return False, message
        if not self._leader_role_is_valid(leader):
            return False, "Người phụ trách dự án phải là tài khoản quản trị hoặc trưởng nhóm đang hoạt động."
        valid_members, member_message = self._validate_members(members)
        if not valid_members:
            return False, member_message
        if any(p.project_id.lower() == project_id.lower() for p in self.all_projects):
            return False, f"ID '{project_id}' da ton tai."

        project = ProjectModel(project_id, name, description, status, leader, members, start_date, end_date)
        self.all_projects.append(project)
        self.save_data()
        self.search("")
        self.audit.log(self.actor, "create_project", "project", project_id, f"{name} | leader={leader} | status={status}")
        return True, "Thêm dự án thành công."

    def update_project(self, old_project_id, project_id, name, description, status="Lên kế hoạch", leader="", members=None, start_date="", end_date=""):
        project = self.get_project(old_project_id)
        if project is None:
            return False, "Không tìm thấy dự án cần cập nhật."
        if not self.can_manage_project(project):
            return self._deny()

        project_id = project_id.strip()
        name = name.strip()
        description = description.strip()
        status = self._normalize_status(status)
        leader = leader.strip()
        members = self._parse_members(members)
        start_date = start_date.strip()
        end_date = end_date.strip()

        valid, message = self._validate_common(project_id, name, status, start_date, end_date)
        if not valid:
            return False, message
        if self._is_leader():
            leader = project.leader
            members = project.members
            start_date = project.start_date
        else:
            if not self._leader_role_is_valid(leader):
                return False, "Người phụ trách dự án phải là tài khoản quản trị hoặc trưởng nhóm đang hoạt động."
            valid_members, member_message = self._validate_members(members)
            if not valid_members:
                return False, member_message
        if any(p.project_id.lower() == project_id.lower() and p.project_id != old_project_id for p in self.all_projects):
            return False, f"ID '{project_id}' da ton tai."

        project.project_id = project_id
        project.name = name
        project.description = description
        project.status = status
        project.leader = leader or project.leader or (self.actor if self._is_leader() else "")
        project.members = members
        project.start_date = start_date
        project.end_date = end_date
        self.save_data()
        self.search("")
        self.audit.log(self.actor, "update_project", "project", project_id, f"{name} | leader={project.leader} | status={status}")
        return True, "Cập nhật dự án thành công."

    def _task_count_for_project(self, project_id):
        if not self.tasks_path.exists():
            return 0
        try:
            with self.tasks_path.open("r", encoding="utf-8") as f:
                tasks = json.load(f)
        except (json.JSONDecodeError, OSError):
            return 0
        return len([task for task in tasks if task.get("project_id") == project_id])

    def delete_project(self, project_id):
        project = self.get_project(project_id)
        if project is None:
            return False, "Không tìm thấy dự án cần xóa."
        if not self._is_admin():
            return False, "Chỉ quản trị viên mới được xóa dự án."
        if not self.can_manage_project(project):
            return self._deny()
        task_count = self._task_count_for_project(project_id)
        if task_count:
            return False, f"Không thể xóa dự án vì còn {task_count} công việc đang gắn với dự án."

        self.all_projects = [p for p in self.all_projects if p.project_id != project_id]
        self.save_data()
        self.search("")
        self.audit.log(self.actor, "delete_project", "project", project_id, "delete")
        return True, "Đã xóa dự án."

    def get_project(self, project_id):
        return next((p for p in self.all_projects if p.project_id == project_id), None)

    def search(self, query):
        query = query.lower().strip()
        projects = self.scoped_projects()
        if query:
            projects = [
                p
                for p in projects
                if query in p.name.lower()
                or query in p.project_id.lower()
                or query in p.description.lower()
                or query in p.status.lower()
                or query in p.leader.lower()
            ]
        self.display_projects = projects
        return self.display_projects
