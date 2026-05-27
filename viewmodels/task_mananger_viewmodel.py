import json
from datetime import datetime
from pathlib import Path

from models.audit_log_model import AuditLogModel
from models.task_manager_model import Task


class TaskViewModel:
    """Nghiệp vụ quản lý công việc: CRUD, lọc, thống kê, timeline."""

    def __init__(self, actor="system", can_manage=True):
        """Khởi tạo dữ liệu task cùng quyền thao tác."""
        self.file_path = Path(__file__).resolve().parents[1] / "tasks.json"
        self.all_tasks = []
        self.display_tasks = []
        self.current_filter = "Tất cả"
        self.actor = actor
        self.can_manage = can_manage
        self.audit = AuditLogModel()
        self.load_data()
        self.filter_and_search()

    def _deny(self):
        """Thông báo dùng chung khi user không có quyền sửa dữ liệu."""
        return False, "Bạn không có quyền chỉnh sửa công việc."

    def load_data(self):
        """Đọc dữ liệu task từ JSON, tạo mẫu nếu file chưa tồn tại."""
        if not self.file_path.exists():
            self.all_tasks = [
                Task("T01", "Thiết kế giao diện Login", "15/04", "1 (P1)", "Todo"),
                Task("T02", "Cài đặt thư viện CustomTkinter", "12/04", "1 (P1)", "Done"),
            ]
            self.save_data()
            return

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.all_tasks = [
                Task(
                    t.get("task_id", ""),
                    t.get("name", ""),
                    t.get("deadline", ""),
                    t.get("priority", "2 (P2)"),
                    t.get("status", "Todo"),
                )
                for t in data
            ]
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Lỗi đọc file tasks.json: {exc}")
            self.all_tasks = []

    def save_data(self):
        """Lưu danh sách task hiện tại ra JSON."""
        data_to_save = [
            {
                "task_id": t.task_id,
                "name": t.name,
                "deadline": t.deadline,
                "priority": t.priority,
                "status": t.status,
            }
            for t in self.all_tasks
        ]
        try:
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            print(f"Lỗi ghi file tasks.json: {exc}")

    def validate_and_add(self, task_id, name, deadline, priority, status="Todo"):
        """Validate và thêm công việc mới."""
        if not self.can_manage:
            return self._deny()
        task_id = task_id.strip()
        name = name.strip()
        deadline = deadline.strip()

        if not task_id or not name:
            return False, "ID và tên công việc không được để trống!"
        if any(t.task_id.lower() == task_id.lower() for t in self.all_tasks):
            return False, f"ID '{task_id}' đã tồn tại!"

        self.all_tasks.append(Task(task_id, name, deadline, priority, status))
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "create_task", "task", task_id, f"{name} | {priority} | {status}")
        return True, "Thêm công việc thành công."

    def update_task(self, old_task_id, task_id, name, deadline, priority, status):
        """Cập nhật thông tin công việc theo ID cũ."""
        if not self.can_manage:
            return self._deny()
        task_id = task_id.strip()
        name = name.strip()
        deadline = deadline.strip()

        if not task_id or not name:
            return False, "ID và tên công việc không được để trống!"
        if any(t.task_id.lower() == task_id.lower() and t.task_id != old_task_id for t in self.all_tasks):
            return False, f"ID '{task_id}' đã tồn tại!"

        task = self.get_task(old_task_id)
        if task is None:
            return False, "Không tìm thấy công việc cần cập nhật."

        task.task_id = task_id
        task.name = name
        task.deadline = deadline
        task.priority = priority
        task.status = status
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "update_task", "task", task_id, f"{name} | {priority} | {status}")
        return True, "Cập nhật công việc thành công."

    def delete_task(self, task_id):
        """Xóa công việc theo ID."""
        if not self.can_manage:
            return self._deny()
        before = len(self.all_tasks)
        self.all_tasks = [t for t in self.all_tasks if t.task_id != task_id]
        if len(self.all_tasks) == before:
            return False, "Không tìm thấy công việc cần xóa."
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "delete_task", "task", task_id, "delete")
        return True, "Đã xóa công việc."

    def toggle_status(self, task_id):
        """Đổi trạng thái Todo <-> Done."""
        if not self.can_manage:
            return self._deny()
        task = self.get_task(task_id)
        if task is None:
            return False, "Không tìm thấy công việc."
        task.status = "Done" if task.status == "Todo" else "Todo"
        self.save_data()
        self.filter_and_search()
        self.audit.log(self.actor, "toggle_task_status", "task", task_id, task.status)
        return True, "Đã cập nhật trạng thái."

    def get_task(self, task_id):
        """Tìm công việc theo ID."""
        return next((t for t in self.all_tasks if t.task_id == task_id), None)

    def filter_and_search(self, status_filter=None, search_query="", priority_filter="Tất cả"):
        """Lọc theo trạng thái/ưu tiên và tìm kiếm text."""
        if status_filter:
            self.current_filter = status_filter

        query = search_query.lower().strip()
        if self.current_filter == "Tất cả":
            temp_list = self.all_tasks
        elif self.current_filter == "Đang làm":
            temp_list = [t for t in self.all_tasks if t.status == "Todo"]
        else:
            temp_list = [t for t in self.all_tasks if t.status == "Done"]

        if priority_filter != "Tất cả":
            temp_list = [t for t in temp_list if priority_filter in t.priority]

        self.display_tasks = [
            t for t in temp_list if query in t.name.lower() or query in t.task_id.lower() or query in t.priority.lower()
        ]
        return self.display_tasks

    def get_stats(self):
        """Trả về số liệu tổng quan để render dashboard."""
        total = len(self.all_tasks)
        done = len([t for t in self.all_tasks if t.status == "Done"])
        todo = total - done
        priorities = {p: len([t for t in self.all_tasks if p in t.priority]) for p in ["P1", "P2", "P3", "P4"]}
        deadline_items = self._deadline_items()
        overdue = len([item for item in deadline_items if item[1] < 0])
        upcoming = len([item for item in deadline_items if 0 <= item[1] <= 7])
        return {
            "total": total,
            "done": done,
            "todo": todo,
            "progress": round((done / total) * 100) if total else 0,
            "priorities": priorities,
            "overdue": overdue,
            "upcoming": upcoming,
        }

    def _parse_deadline(self, deadline):
        """Parse deadline định dạng dd/mm thành date năm hiện tại."""
        try:
            deadline_date = datetime.strptime(deadline.strip(), "%d/%m").date()
            return deadline_date.replace(year=datetime.now().year)
        except (ValueError, AttributeError):
            return None

    def _deadline_items(self):
        """Lấy danh sách task chưa done kèm số ngày còn lại tới hạn."""
        today = datetime.now().date()
        items = []
        for task in self.all_tasks:
            if task.status == "Done":
                continue
            deadline = self._parse_deadline(task.deadline)
            if deadline is None:
                continue
            items.append((task, (deadline - today).days))
        return items

    def get_deadline_insights(self, limit=6):
        """Trả về top task cần chú ý deadline (quá hạn/sắp hạn)."""
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
        """Dữ liệu timeline sắp xếp theo ngày deadline tăng dần."""
        items = []
        for t in self.all_tasks:
            deadline = self._parse_deadline(t.deadline)
            if deadline is None:
                continue
            items.append((t, deadline))
        return sorted(items, key=lambda item: item[1])
