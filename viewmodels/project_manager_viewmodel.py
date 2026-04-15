import json
import os
from ProjectTracker.models.project_manager_model import ProjectModel


class ProjectViewModel:
    def __init__(self):
        # Tên file lưu trữ dữ liệu
        self.file_path = "projects.json"
        self.all_projects = []

        # Tải dữ liệu từ file lên khi khởi tạo
        self.load_data()

        # Danh sách dùng để hiển thị trên UI
        self.display_projects = list(self.all_projects)

    def load_data(self):
        """Đọc danh sách đồ án từ file JSON"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Chuyển đổi từ dictionary trong JSON sang đối tượng ProjectModel
                    self.all_projects = [
                        ProjectModel(p["project_id"], p["name"], p["description"])
                        for p in data
                    ]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Lỗi định dạng file JSON: {e}")
                self.all_projects = []
        else:
            # Nếu file chưa tồn tại, tạo danh sách mặc định hoặc để trống
            self.all_projects = [
                ProjectModel("1", "Đồ án Python", "Quản lý công việc"),
                ProjectModel("2", "Website HUIT", "Trang tin tức")
            ]
            self.save_data()  # Tạo luôn file lần đầu

    def save_data(self):
        """Lưu danh sách đồ án hiện tại vào file JSON"""
        try:
            # Chuyển đổi danh sách đối tượng thành danh sách dictionary để JSON hiểu được
            data_to_save = [
                {
                    "project_id": p.project_id,
                    "name": p.name,
                    "description": p.description
                } for p in self.all_projects
            ]
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Không thể lưu dữ liệu: {e}")

    def validate_and_add(self, p_id, p_name, p_desc):
        # Ràng buộc: Không được để trống
        if not p_id.strip() or not p_name.strip():
            return False, "ID và Tên không được để trống!"

        # Ràng buộc: ID không được trùng
        if any(p.project_id == p_id for p in self.all_projects):
            return False, f"ID '{p_id}' đã tồn tại!"

        # Thêm vào danh sách tạm trong bộ nhớ
        new_project = ProjectModel(p_id, p_name, p_desc)
        self.all_projects.append(new_project)

        # Cập nhật file JSON ngay lập tức
        self.save_data()

        self.display_projects = list(self.all_projects)
        return True, "Thêm thành công"

    def search(self, query):
        query = query.lower().strip()
        if not query:
            self.display_projects = list(self.all_projects)
        else:
            self.display_projects = [
                p for p in self.all_projects
                if query in p.name.lower() or query in p.project_id.lower()
            ]
        return self.display_projects