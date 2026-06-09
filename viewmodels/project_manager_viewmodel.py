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
        """Khởi tạo ViewModel: xác định người dùng/vai trò, nạp dữ liệu dự án và lọc danh sách hiển thị."""
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
        """Trả về kết quả từ chối thao tác do không đủ quyền."""
        return False, "Bạn không có quyền thực hiện thao tác này với dự án."

    def _normalize_status(self, status):
        """Chuẩn hóa trạng thái dự án về tiếng Việt hợp lệ (mặc định 'Lên kế hoạch')."""
        status = str(status or "").strip()
        status = PROJECT_STATUS_ALIASES.get(status, status or "Lên kế hoạch")
        return status if status in PROJECT_STATUSES else "Lên kế hoạch"

    def _parse_members(self, members):
        """Chuyển danh sách thành viên (list hoặc chuỗi ngăn cách dấu phẩy) thành list đã làm sạch."""
        if isinstance(members, list):
            return [str(member).strip() for member in members if str(member).strip()]
        return [member.strip() for member in str(members or "").split(",") if member.strip()]

    def _project_to_dict(self, project):
        """Chuyển đối tượng ProjectModel thành dict để ghi ra file JSON."""
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
        """Kiểm tra chuỗi ngày có đúng định dạng dd/mm hay không (rỗng được coi là hợp lệ)."""
        if not value:
            return True
        try:
            datetime.strptime(value, "%d/%m")
            return True
        except ValueError:
            return False

    def _parse_date(self, value):
        """Phân tích chuỗi dd/mm thành đối tượng date (gán năm hiện tại); trả về None nếu lỗi."""
        try:
            return datetime.strptime(value.strip(), "%d/%m").replace(year=datetime.now().year).date()
        except (ValueError, AttributeError):
            return None

    def _validate_common(self, project_id, name, description, status, start_date, end_date):
        """Kiểm tra ràng buộc chung của dự án: bắt buộc nhập, trạng thái hợp lệ, ngày đúng định dạng và thứ tự."""
        if not project_id or not name:
            return False, "ID và tên dự án không được để trống."
        if not description:
            return False, "Mô tả dự án không được để trống."
        if status not in PROJECT_STATUSES:
            return False, "Trạng thái dự án không hợp lệ."
        if not start_date:
            return False, "Ngày bắt đầu dự án không được để trống."
        if not end_date:
            return False, "Ngày kết thúc dự án không được để trống."
        if not self._is_valid_date(start_date) or not self._is_valid_date(end_date):
            return False, "Ngày bắt đầu/kết thúc phải đúng định dạng dd/mm."
        if self._parse_date(start_date) > self._parse_date(end_date):
            return False, "Ngày bắt đầu dự án không được trễ hơn ngày kết thúc."
        return True, ""

    def _leader_role_is_valid(self, username):
        """Kiểm tra người phụ trách có phải tài khoản admin/leader đang hoạt động (rỗng được chấp nhận)."""
        if not username:
            return True
        for user in self.user_model.list_active_users():
            if user["username"] == username:
                return user["role"] in ("admin", "leader")
        return False

    def active_member_usernames(self):
        """Trả về danh sách username của các tài khoản có vai trò 'member' đang hoạt động."""
        return [user["username"] for user in self.user_model.list_active_users() if user["role"] == "member"]

    def _validate_members(self, members):
        """Kiểm tra mọi thành viên đều là tài khoản member đang hoạt động."""
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
        """Trả về True nếu người dùng hiện tại là quản trị viên."""
        return self.actor_role == "admin"

    def _is_leader(self):
        """Trả về True nếu người dùng hiện tại là trưởng nhóm."""
        return self.actor_role == "leader"

    def can_create_project(self):
        """Cho biết người dùng có quyền thêm dự án mới hay không (chỉ admin)."""
        return self._is_admin()

    def can_manage_project(self, project):
        """Cho biết có quyền thao tác (thêm/sửa/xóa) dự án không. Chỉ admin; trưởng nhóm và thành viên chỉ được xem."""
        return self._is_admin()

    def can_view_project(self, project):
        """Cho biết người dùng có quyền xem dự án: admin xem tất cả, leader/member xem dự án mình phụ trách hoặc tham gia."""
        if self._is_admin():
            return True
        if self._is_leader():
            return not project.leader or project.leader == self.actor or self.actor in project.members
        return self.actor in project.members or project.leader == self.actor

    def scoped_projects(self):
        """Trả về các dự án mà người dùng hiện tại được phép xem."""
        return [project for project in self.all_projects if self.can_view_project(project)]

    def manageable_project_ids(self):
        """Trả về ID các dự án mà người dùng hiện tại được phép thao tác."""
        return [project.project_id for project in self.all_projects if self.can_manage_project(project)]

    def load_data(self):
        """Nạp dự án từ projects.json (tạo dữ liệu mẫu nếu chưa có), chuẩn hóa và lọc thành viên không hợp lệ."""
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
        """Ghi toàn bộ danh sách dự án ra file projects.json."""
        try:
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump([self._project_to_dict(project) for project in self.all_projects], f, ensure_ascii=False, indent=4)
        except OSError as exc:
            print(f"Không thể lưu dữ liệu: {exc}")

    def validate_and_add(self, project_id, name, description, status="Lên kế hoạch", leader="", members=None, start_date="", end_date=""):
        """Kiểm tra hợp lệ và thêm dự án mới (kiểm tra quyền, trùng ID, người phụ trách, thành viên) rồi lưu và ghi log."""
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

        valid, message = self._validate_common(project_id, name, description, status, start_date, end_date)
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
        """Kiểm tra hợp lệ và cập nhật một dự án đã có (kiểm tra quyền, trùng ID, người phụ trách, thành viên) rồi lưu và ghi log."""
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

        valid, message = self._validate_common(project_id, name, description, status, start_date, end_date)
        if not valid:
            return False, message
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
        """Đếm số công việc trong tasks.json đang gắn với dự án chỉ định."""
        if not self.tasks_path.exists():
            return 0
        try:
            with self.tasks_path.open("r", encoding="utf-8") as f:
                tasks = json.load(f)
        except (json.JSONDecodeError, OSError):
            return 0
        return len([task for task in tasks if task.get("project_id") == project_id])

    def delete_project(self, project_id):
        """Xóa dự án nếu là admin và không còn công việc nào gắn với dự án, rồi lưu và ghi log."""
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
        """Tìm và trả về dự án theo ID; trả về None nếu không có."""
        return next((p for p in self.all_projects if p.project_id == project_id), None)

    def search(self, query):
        """Lọc các dự án được phép xem theo từ khóa (mã, tên, mô tả, trạng thái, người phụ trách) và cập nhật danh sách hiển thị."""
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
