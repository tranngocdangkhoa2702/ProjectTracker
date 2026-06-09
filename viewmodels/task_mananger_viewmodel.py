import json
from datetime import datetime, timedelta
from pathlib import Path

from models.audit_log_model import AuditLogModel
from models.task_manager_model import Task
from models.user_model import UserModel


PRIORITIES = ["1 (P1)", "2 (P2)", "3 (P3)", "4 (P4)"]
STATUSES = ["Chưa làm", "Đang làm", "Chờ duyệt", "Hoàn thành"]
STATUS_ALIASES = {
    "Todo": "Chưa làm",
    "Doing": "Đang làm",
    "Review": "Chờ duyệt",
    "Done": "Hoàn thành",
}


class TaskViewModel:
    """Nghiep vu quan ly cong viec: phan quyen, CRUD, loc, thong ke va timeline."""

    def __init__(self, actor="system", actor_role=None, can_manage=None):
        self.root = Path(__file__).resolve().parents[1]
        self.file_path = self.root / "tasks.json"
        self.projects_path = self.root / "projects.json"
        self.all_tasks = []
        self.display_tasks = []
        self.current_filter = "Tất cả"
        self.actor = actor or "system"
        self.actor_role = actor_role or ("admin" if can_manage else "member")
        self.audit = AuditLogModel()
        self.user_model = UserModel()
        self.load_data()
        self.filter_and_search()

    def _deny(self):
        return False, "Bạn không có quyền thực hiện thao tác này với công việc."

    def _normalize_status(self, status):
        status = str(status or "").strip()
        return STATUS_ALIASES.get(status, status or "Chưa làm")

    def _is_admin(self):
        return self.actor_role == "admin"

    def _is_leader(self):
        return self.actor_role == "leader"

    def _role_of_user(self, username):
        username = str(username or "").strip()
        if not username:
            return ""
        for user in self.user_model.list_active_users():
            if user["username"] == username:
                return user["role"]
        return ""

    def _created_by_leader(self, task):
        return self._role_of_user(task.created_by) == "leader"

    def active_member_usernames(self):
        return [user["username"] for user in self.user_model.list_active_users() if user["role"] == "member"]

    def _assignee_is_valid(self, assignee):
        return not assignee or assignee in self.active_member_usernames()

    def _load_projects(self):
        if not self.projects_path.exists():
            return []
        try:
            with self.projects_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _project_ids(self):
        return [project.get("project_id", "") for project in self._load_projects() if project.get("project_id")]

    def _project_dates(self, project_id):
        """Tra ve (ngay bat dau, ngay ket thuc) cua du an theo project_id."""
        for project in self._load_projects():
            if project.get("project_id") == project_id:
                return str(project.get("start_date", "") or ""), str(project.get("end_date", "") or "")
        return "", ""

    def _managed_project_ids(self):
        projects = self._load_projects()
        if self._is_admin():
            return [project.get("project_id", "") for project in projects if project.get("project_id")]
        if self._is_leader():
            return [
                project.get("project_id", "")
                for project in projects
                if project.get("project_id") and (not project.get("leader") or project.get("leader") == self.actor)
            ]
        return []

    def _visible_project_ids(self):
        projects = self._load_projects()
        if self._is_admin():
            return [project.get("project_id", "") for project in projects if project.get("project_id")]
        if self._is_leader():
            return [
                project.get("project_id", "")
                for project in projects
                if project.get("project_id")
                and (
                    not project.get("leader")
                    or project.get("leader") == self.actor
                    or self.actor in project.get("members", [])
                )
            ]
        return [
            project.get("project_id", "")
            for project in projects
            if project.get("project_id") and (project.get("leader") == self.actor or self.actor in project.get("members", []))
        ]

    def _task_to_dict(self, task):
        return {
            "task_id": task.task_id,
            "name": task.name,
            "start_date": task.start_date,
            "deadline": task.deadline,
            "priority": task.priority,
            "is_urgent": task.is_urgent,
            "is_important": task.is_important,
            "status": task.status,
            "project_id": task.project_id,
            "assignee": task.assignee,
            "created_by": task.created_by,
            "completed_at": task.completed_at,
            "approval_state": task.approval_state,
            "extension_status": task.extension_status,
            "requested_deadline": task.requested_deadline,
            "extension_reason": task.extension_reason,
        }

    def _priority_flags(self, priority):
        if "P1" in str(priority):
            return True, True
        if "P2" in str(priority):
            return False, True
        if "P3" in str(priority):
            return True, False
        return False, False

    def _parse_deadline(self, deadline):
        try:
            deadline_date = datetime.strptime(deadline.strip(), "%d/%m").date()
            return deadline_date.replace(year=datetime.now().year)
        except (ValueError, AttributeError):
            return None

    def _validate_deadline(self, deadline):
        return self._parse_deadline(deadline) is not None

    def _validate_common(self, task_id, name, start_date, deadline, priority, status, project_id):
        if not task_id or not name:
            return False, "ID và tên công việc không được để trống."
        if not start_date:
            return False, "Ngày bắt đầu công việc không được để trống."
        if not self._validate_deadline(start_date):
            return False, "Ngày bắt đầu phải đúng định dạng dd/mm và là ngày hợp lệ."
        if not deadline:
            return False, "Hạn hoàn thành không được để trống."
        if not self._validate_deadline(deadline):
            return False, "Hạn hoàn thành phải đúng định dạng dd/mm và là ngày hợp lệ."
        if self._parse_deadline(start_date) > self._parse_deadline(deadline):
            return False, "Ngày bắt đầu công việc không được sau hạn hoàn thành."
        if priority not in PRIORITIES:
            return False, "Mức ưu tiên không hợp lệ."
        if status not in STATUSES:
            return False, "Trạng thái công việc không hợp lệ."
        if not project_id:
            return False, "Công việc phải được gắn với một dự án."
        if project_id not in self._project_ids():
            return False, "Dự án được chọn không tồn tại."

        # Cong viec phai nam trong khoang thoi gian cua du an.
        project_start, project_end = self._project_dates(project_id)
        if project_start and self._validate_deadline(project_start):
            if self._parse_deadline(start_date) < self._parse_deadline(project_start):
                return False, f"Ngày bắt đầu công việc không được sớm hơn ngày bắt đầu dự án ({project_start})."
        if project_end and self._validate_deadline(project_end):
            if self._parse_deadline(deadline) > self._parse_deadline(project_end):
                return False, f"Hạn hoàn thành công việc không được trễ hơn ngày kết thúc dự án ({project_end})."
        return True, ""

    def can_create_task(self):
        if self.actor_role == "member":
            return bool(self._visible_project_ids())
        return bool(self._managed_project_ids())

    def is_completed(self, task):
        return task.status == "Hoàn thành"

    def can_manage_task(self, task):
        if self.is_completed(task):
            return False
        if self._is_admin():
            return True
        if self._is_leader():
            return task.project_id in self._managed_project_ids()
        return False

    def is_pending_member_task(self, task):
        return task.approval_state == "member_pending"

    def can_approve_member_task(self, task):
        return self._is_leader() and task.project_id in self._managed_project_ids() and self.is_pending_member_task(task)

    def can_update_task_status(self, task):
        if self.is_completed(task):
            return False
        return bool(self.get_status_options(task))

    def get_status_options(self, task):
        if self.is_completed(task):
            return []
        if self.is_pending_member_task(task):
            return []
        if self._is_admin():
            return STATUSES[:]
        if self.actor_role == "member":
            if task.assignee != self.actor:
                return []
            if self.is_pending_member_task(task):
                return []
            return ["Đang làm", "Chờ duyệt"]
        if self._is_leader() and task.project_id in self._managed_project_ids():
            if task.status == "Chờ duyệt":
                if self._created_by_leader(task):
                    return ["Đang làm", "Chờ duyệt"]
                return ["Đang làm", "Chờ duyệt", "Hoàn thành"]
            return ["Chưa làm", "Đang làm", "Chờ duyệt"]
        return []

    def get_edit_status_options(self, task=None):
        if task is None:
            if self.actor_role == "member":
                return ["Chờ duyệt"]
            return ["Chưa làm", "Đang làm"]
        if self._is_admin():
            return STATUSES[:]
        if self._is_leader():
            return [status for status in ["Chưa làm", "Đang làm", "Chờ duyệt"] if status == task.status or status in self.get_status_options(task)]
        return [task.status]

    def can_view_task(self, task):
        if self._is_admin():
            return True
        if self._is_leader():
            return task.project_id in self._visible_project_ids() or task.assignee == self.actor
        return task.project_id in self._visible_project_ids() or task.assignee == self.actor

    def can_request_extension(self, task):
        return (
            self.actor_role == "member"
            and task.assignee == self.actor
            and not self.is_completed(task)
            and not self.is_pending_member_task(task)
            and task.status != "Chờ duyệt"
            and not task.extension_status
        )

    def can_forward_extension_to_admin(self, task):
        return self._is_leader() and task.project_id in self._managed_project_ids() and task.extension_status == "member_requested"

    def can_admin_approve_extension(self, task):
        return self._is_admin() and task.extension_status == "leader_requested_admin"

    def can_leader_finalize_extension(self, task):
        return self._is_leader() and task.project_id in self._managed_project_ids() and task.extension_status == "admin_approved"

    def generate_task_id(self):
        """Sinh ID cong viec tiep theo theo mau T01, T02..."""
        max_number = 0
        for task in self.all_tasks:
            task_id = task.task_id.upper()
            if task_id.startswith("T") and task_id[1:].isdigit():
                max_number = max(max_number, int(task_id[1:]))
        return f"T{max_number + 1:02d}"

    def scoped_tasks(self):
        return [task for task in self.all_tasks if self.can_view_task(task)]

    def load_data(self):
        default_project_id = next(iter(self._project_ids()), "")
        if not self.file_path.exists():
            self.all_tasks = [
                Task("T01", "Thiết kế giao diện Login", "15/04", "1 (P1)", "Chưa làm", default_project_id, "", self.actor),
                Task("T02", "Cài đặt thư viện CustomTkinter", "12/04", "1 (P1)", "Hoàn thành", default_project_id, "", self.actor),
            ]
            self.save_data()
            return

        migrated = False
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.all_tasks = []
            for t in data:
                if (
                    "project_id" not in t
                    or "assignee" not in t
                    or "created_by" not in t
                    or "start_date" not in t
                    or "completed_at" not in t
                    or "is_urgent" not in t
                    or "is_important" not in t
                    or "approval_state" not in t
                    or "extension_status" not in t
                    or "requested_deadline" not in t
                    or "extension_reason" not in t
                ):
                    migrated = True
                status = self._normalize_status(t.get("status", "Chưa làm"))
                if status not in STATUSES:
                    status = "Chưa làm"
                if status != t.get("status"):
                    migrated = True
                priority = t.get("priority", "2 (P2)") if t.get("priority", "2 (P2)") in PRIORITIES else "2 (P2)"
                default_urgent, default_important = self._priority_flags(priority)
                completed_at = t.get("completed_at", "")
                if status == "Hoàn thành" and not completed_at:
                    completed_at = t.get("deadline", "")
                    migrated = True
                self.all_tasks.append(
                    Task(
                        t.get("task_id", ""),
                        t.get("name", ""),
                        t.get("deadline", ""),
                        priority,
                        status,
                        t.get("project_id", default_project_id),
                        t.get("assignee", ""),
                        t.get("created_by", "system"),
                        t.get("start_date", ""),
                        completed_at,
                        t.get("is_urgent", default_urgent),
                        t.get("is_important", default_important),
                        t.get("approval_state", "approved"),
                        t.get("extension_status", ""),
                        t.get("requested_deadline", ""),
                        t.get("extension_reason", ""),
                    )
                )
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Lỗi đọc file tasks.json: {exc}")
            self.all_tasks = []

        if migrated:
            self.save_data()

    def save_data(self):
        try:
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump([self._task_to_dict(task) for task in self.all_tasks], f, ensure_ascii=False, indent=4)
        except OSError as exc:
            print(f"Lỗi ghi file tasks.json: {exc}")

    def validate_and_add(
        self,
        task_id,
        name,
        start_date,
        deadline,
        priority,
        status="Chưa làm",
        project_id="",
        assignee="",
        is_urgent=None,
        is_important=None,
    ):
        if not self.can_create_task():
            return self._deny()
        task_id = task_id.strip() or self.generate_task_id()
        name = name.strip()
        start_date = start_date.strip()
        deadline = deadline.strip()
        status = self._normalize_status(status)
        project_id = project_id.strip()
        assignee = assignee.strip()
        if self.actor_role == "member":
            status = "Chờ duyệt"
            assignee = self.actor

        valid, message = self._validate_common(task_id, name, start_date, deadline, priority, status, project_id)
        if not valid:
            return False, message
        if not self._is_admin() and status not in self.get_edit_status_options(None):
            return False, "Trạng thái khởi tạo công việc không hợp lệ với vai trò hiện tại."
        if not assignee:
            return False, "Vui lòng chọn người được giao cho công việc."
        if not self._assignee_is_valid(assignee):
            return False, "Người được giao phải là tài khoản thành viên đang hoạt động."
        allowed_project_ids = self._visible_project_ids() if self.actor_role == "member" else self._managed_project_ids()
        if project_id not in allowed_project_ids:
            return False, "Bạn không có quyền tạo công việc trong dự án này."
        if any(t.task_id.lower() == task_id.lower() for t in self.all_tasks):
            return False, f"ID '{task_id}' da ton tai."

        default_urgent, default_important = self._priority_flags(priority)
        is_urgent = default_urgent if is_urgent is None else bool(is_urgent)
        is_important = default_important if is_important is None else bool(is_important)
        completed_at = datetime.now().strftime("%d/%m") if status == "Hoàn thành" else ""
        approval_state = "member_pending" if self.actor_role == "member" else "approved"
        self.all_tasks.append(
            Task(
                task_id,
                name,
                deadline,
                priority,
                status,
                project_id,
                assignee,
                self.actor,
                start_date,
                completed_at,
                is_urgent,
                is_important,
                approval_state,
            )
        )
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "create_task", "task", task_id, f"{name} | {project_id} | {assignee} | {start_date}->{deadline} | {priority} | {status}")
        return True, "Thêm công việc thành công."

    def update_task(
        self,
        old_task_id,
        task_id,
        name,
        start_date,
        deadline,
        priority,
        status,
        project_id="",
        assignee="",
        is_urgent=None,
        is_important=None,
    ):
        task = self.get_task(old_task_id)
        if task is None:
            return False, "Không tìm thấy công việc cần cập nhật."
        if self.is_completed(task):
            return False, "Công việc đã hoàn thành nên chỉ được xem thông tin."
        if not self.can_manage_task(task):
            return self._deny()

        task_id = task_id.strip()
        name = name.strip()
        start_date = start_date.strip()
        deadline = deadline.strip()
        status = self._normalize_status(status)
        project_id = project_id.strip()
        assignee = assignee.strip()

        valid, message = self._validate_common(task_id, name, start_date, deadline, priority, status, project_id)
        if not valid:
            return False, message
        if status not in self.get_edit_status_options(task):
            return False, "Bạn không có quyền đặt công việc sang trạng thái này khi chỉnh sửa."
        if self._is_leader() and deadline != task.deadline:
            old_deadline = self._parse_deadline(task.deadline)
            new_deadline = self._parse_deadline(deadline)
            if old_deadline and new_deadline and new_deadline > old_deadline:
                return False, "Muốn tăng hạn hoàn thành cho thành viên, trưởng nhóm phải gửi yêu cầu gia hạn lên quản trị viên."
        if not assignee:
            return False, "Vui lòng chọn người được giao cho công việc."
        if not self._assignee_is_valid(assignee):
            return False, "Người được giao phải là tài khoản thành viên đang hoạt động."
        if project_id not in self._managed_project_ids():
            return False, "Bạn không có quyền gắn công việc vào dự án này."
        if any(t.task_id.lower() == task_id.lower() and t.task_id != old_task_id for t in self.all_tasks):
            return False, f"ID '{task_id}' da ton tai."

        task.task_id = task_id
        task.name = name
        task.start_date = start_date
        task.deadline = deadline
        task.priority = priority
        if is_urgent is not None:
            task.is_urgent = bool(is_urgent)
        if is_important is not None:
            task.is_important = bool(is_important)
        if status == "Hoàn thành" and task.status != "Hoàn thành":
            task.completed_at = datetime.now().strftime("%d/%m")
        if status != "Hoàn thành":
            task.completed_at = ""
        task.status = status
        task.project_id = project_id
        task.assignee = assignee
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "update_task", "task", task_id, f"{name} | {project_id} | {assignee} | {start_date}->{deadline} | {priority} | {status}")
        return True, "Cập nhật công việc thành công."

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc cần xóa."
        if self.is_completed(task):
            return False, "Công việc đã hoàn thành nên chỉ được xem thông tin."
        if not self.can_manage_task(task):
            return self._deny()

        self.all_tasks = [t for t in self.all_tasks if t.task_id != task_id]
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "delete_task", "task", task_id, "delete")
        return True, "Đã xóa công việc."

    def approve_member_task(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        if not self.can_approve_member_task(task):
            return self._deny()
        task.approval_state = "approved"
        task.status = "Chưa làm"
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "approve_member_task", "task", task_id, "leader approved member-created task")
        return True, "Đã duyệt công việc. Thành viên có thể cập nhật sang Đang làm."

    def request_extension(self, task_id, requested_deadline, reason=""):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        requested_deadline = str(requested_deadline or "").strip()
        reason = str(reason or "").strip()
        if not self.can_request_extension(task):
            return self._deny()
        if not self._validate_deadline(requested_deadline):
            return False, "Ngày gia hạn phải đúng định dạng dd/mm và là ngày hợp lệ."
        if self._parse_deadline(requested_deadline) <= self._parse_deadline(task.deadline):
            return False, "Ngày gia hạn phải sau hạn hoàn thành hiện tại."
        task.extension_status = "member_requested"
        task.requested_deadline = requested_deadline
        task.extension_reason = reason
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "request_extension", "task", task_id, f"{task.deadline}->{requested_deadline} | {reason}")
        return True, "Đã gửi yêu cầu gia hạn cho trưởng nhóm."

    def forward_extension_to_admin(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        if not self.can_forward_extension_to_admin(task):
            return self._deny()
        task.extension_status = "leader_requested_admin"
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "forward_extension_to_admin", "task", task_id, task.requested_deadline)
        return True, "Đã gửi yêu cầu gia hạn lên quản trị viên."

    def admin_approve_extension(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        if not self.can_admin_approve_extension(task):
            return self._deny()
        task.extension_status = "admin_approved"
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "admin_approve_extension", "task", task_id, task.requested_deadline)
        return True, "Quản trị viên đã phê duyệt. Trưởng nhóm cần xác nhận lại cho thành viên."

    def leader_finalize_extension(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        if not self.can_leader_finalize_extension(task):
            return self._deny()
        old_deadline = task.deadline
        task.deadline = task.requested_deadline
        task.extension_status = ""
        task.requested_deadline = ""
        task.extension_reason = ""
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "leader_finalize_extension", "task", task_id, f"{old_deadline}->{task.deadline}")
        return True, "Đã duyệt gia hạn cho thành viên."

    def update_status(self, task_id, status):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        if self.is_completed(task):
            return False, "Công việc đã hoàn thành nên không thể cập nhật trạng thái."
        if not self.can_update_task_status(task):
            return self._deny()
        if status not in STATUSES:
            return False, "Trạng thái công việc không hợp lệ."
        if status not in self.get_status_options(task):
            if self.actor_role == "member":
                return False, "Thành viên chỉ được chuyển công việc sang Đang làm hoặc Chờ duyệt."
            if self._is_leader() and status == "Hoàn thành" and self._created_by_leader(task):
                return False, "Công việc do trưởng nhóm giao cần quản trị viên xác nhận hoàn thành."
            return False, "Bạn không có quyền chuyển sang trạng thái này."

        task.status = status
        if status == "Hoàn thành":
            task.completed_at = datetime.now().strftime("%d/%m")
        else:
            task.completed_at = ""
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "update_task_status", "task", task_id, status)
        return True, "Đã cập nhật trạng thái."

    def toggle_status(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        next_status = "Hoàn thành" if task.status != "Hoàn thành" else "Chưa làm"
        return self.update_status(task_id, next_status)

    def get_task(self, task_id):
        return next((t for t in self.all_tasks if t.task_id == task_id), None)

    def filter_and_search(self, status_filter=None, search_query="", priority_filter="Tất cả", project_filter="Tất cả", assignee_filter="Tất cả"):
        if status_filter:
            self.current_filter = status_filter

        query = search_query.lower().strip()
        temp_list = self.scoped_tasks()
        if self.current_filter != "Tất cả":
            temp_list = [t for t in temp_list if t.status == self.current_filter]
        if priority_filter != "Tất cả":
            temp_list = [t for t in temp_list if priority_filter in t.priority]
        if project_filter != "Tất cả":
            temp_list = [t for t in temp_list if t.project_id == project_filter]
        if assignee_filter != "Tất cả":
            temp_list = [t for t in temp_list if t.assignee == assignee_filter]

        self.display_tasks = [
            t
            for t in temp_list
            if query in t.name.lower()
            or query in t.task_id.lower()
            or query in t.priority.lower()
            or query in t.status.lower()
            or query in t.project_id.lower()
            or query in t.assignee.lower()
        ]
        return self.display_tasks

    def get_stats(self):
        tasks = self.scoped_tasks()
        total = len(tasks)
        done = len([t for t in tasks if t.status == "Hoàn thành"])
        todo = len([t for t in tasks if t.status == "Chưa làm"])
        doing = len([t for t in tasks if t.status == "Đang làm"])
        review = len([t for t in tasks if t.status == "Chờ duyệt"])
        priorities = {p: len([t for t in tasks if p in t.priority]) for p in ["P1", "P2", "P3", "P4"]}
        deadline_items = self._deadline_items(tasks)
        overdue = len([item for item in deadline_items if item[1] < 0])
        upcoming = len([item for item in deadline_items if 0 <= item[1] <= 7])
        return {
            "total": total,
            "done": done,
            "todo": todo,
            "doing": doing,
            "review": review,
            "progress": round((done / total) * 100) if total else 0,
            "priorities": priorities,
            "overdue": overdue,
            "upcoming": upcoming,
        }

    def get_project_progress(self):
        progress = {}
        for project_id in self._project_ids():
            tasks = [task for task in self.all_tasks if task.project_id == project_id]
            done = len([task for task in tasks if task.status == "Hoàn thành"])
            progress[project_id] = round(done / len(tasks) * 100) if tasks else 0
        return progress

    def get_weekly_completion(self, weeks=6):
        today = datetime.now().date()
        start = today - timedelta(days=today.weekday() + 7 * (weeks - 1))
        labels = []
        values = []
        for index in range(weeks):
            week_start = start + timedelta(days=index * 7)
            week_end = week_start + timedelta(days=6)
            labels.append(f"{week_start.strftime('%d/%m')}")
            count = 0
            for task in self.scoped_tasks():
                completed = self._parse_deadline(task.completed_at)
                if completed and week_start <= completed <= week_end:
                    count += 1
            values.append(count)
        return labels, values

    def _deadline_items(self, tasks=None):
        today = datetime.now().date()
        items = []
        for task in tasks if tasks is not None else self.scoped_tasks():
            if task.status == "Hoàn thành":
                continue
            deadline = self._parse_deadline(task.deadline)
            if deadline is None:
                continue
            items.append((task, (deadline - today).days))
        return items

    def get_deadline_insights(self, limit=6):
        insights = []
        for task, days_left in sorted(self._deadline_items(), key=lambda item: item[1]):
            if days_left < 0:
                label = f"Quá hạn {abs(days_left)} ngày"
                color = "#ef4444"
            elif days_left == 0:
                label = "Hạn hôm nay"
                color = "#f59e0b"
            else:
                label = f"Còn {days_left} ngày"
                color = "#22c55e" if days_left > 7 else "#f59e0b"
            insights.append((task, label, color))
        return insights[:limit]

    def get_timeline_items(self):
        items = []
        for task in self.scoped_tasks():
            deadline = self._parse_deadline(task.deadline)
            if deadline is None:
                continue
            items.append((task, deadline))
        return sorted(items, key=lambda item: item[1])

    def get_project_options(self, manageable_only=False):
        if manageable_only and self.actor_role == "member":
            project_ids = self._visible_project_ids()
        else:
            project_ids = self._managed_project_ids() if manageable_only else self._visible_project_ids()
        return project_ids or self._project_ids()

    def get_assignee_options(self):
        if self.actor_role == "member":
            return [self.actor]
        return self.active_member_usernames()
