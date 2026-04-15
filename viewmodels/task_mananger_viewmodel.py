import json
import os
from ProjectTracker.models.task_manager_model import Task


class TaskViewModel:
    def __init__(self):
        # Đường dẫn file lưu trữ công việc
        self.file_path = "tasks.json"
        self.all_tasks = []

        # Nạp dữ liệu từ file khi khởi động
        self.load_data()

        self.display_tasks = list(self.all_tasks)
        self.current_filter = "Tất cả"

    def load_data(self):
        """Đọc danh sách công việc từ file JSON"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.all_tasks = [
                        Task(t["task_id"], t["name"], t["deadline"], t["priority"], t["status"])
                        for t in data
                    ]
            except Exception as e:
                print(f"Lỗi đọc file tasks.json: {e}")
                self.all_tasks = []
        else:
            # Dữ liệu mẫu nếu file chưa tồn tại
            self.all_tasks = [
                Task("101", "Code Login", "20/12", "1 (P1)", "Todo"),
                Task("102", "Vẽ CSDL", "18/12", "2 (P2)", "Done")
            ]
            self.save_data()

    def save_data(self):
        """Lưu danh sách công việc hiện tại vào file JSON"""
        try:
            data_to_save = [
                {
                    "task_id": t.task_id,
                    "name": t.name,
                    "deadline": t.deadline,
                    "priority": t.priority,
                    "status": t.status
                } for t in self.all_tasks
            ]
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi ghi file tasks.json: {e}")

    def validate_and_add(self, t_id, t_name, t_deadline, t_priority):
        if not t_id.strip() or not t_name.strip():
            return False, "ID và Tên công việc không được để trống!"

        if any(t.task_id == t_id for t in self.all_tasks):
            return False, f"ID '{t_id}' đã tồn tại!"

        # Tạo công việc mới (mặc định trạng thái là Todo)
        new_task = Task(t_id, t_name, t_deadline, t_priority, "Todo")
        self.all_tasks.append(new_task)

        # LƯU VÀO FILE NGAY LẬP TỨC
        self.save_data()

        # Cập nhật lại danh sách hiển thị
        self.filter_and_search()
        return True, "Thêm công việc thành công"

    def filter_and_search(self, status_filter=None, search_query=""):
        if status_filter:
            self.current_filter = status_filter

        query = search_query.lower().strip()

        # Bước 1: Lọc theo trạng thái
        if self.current_filter == "Tất cả":
            temp_list = self.all_tasks
        elif self.current_filter == "Đang làm":
            temp_list = [t for t in self.all_tasks if t.status == "Todo"]
        else:  # Hoàn thành
            temp_list = [t for t in self.all_tasks if t.status == "Done"]

        # Bước 2: Lọc theo tìm kiếm (Tên hoặc ID)
        self.display_tasks = [
            t for t in temp_list
            if query in t.name.lower() or query in t.task_id.lower()
        ]
        return self.display_tasks