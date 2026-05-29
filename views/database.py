import json
import os
import pandas as pd


# ==========================================
# 1. THIẾT KẾ CLASS (OOP)
# ==========================================
class Task:

    def __init__(self, task_id, name, status="Chưa xong"):
        self.task_id = task_id
        self.name = name
        self.status = status  # "Chưa xong" hoặc "Đã xong"

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
        }


class Project:

    def __init__(self, project_id, project_name):
        self.project_id = project_id
        self.project_name = project_name
        self.tasks = []

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "tasks": [task.to_dict() for task in self.tasks],
        }


# ==========================================
# 2. XỬ LÝ FILE (JSON STORAGE) & CHỨC NĂNG CRUD + THỐNG KÊ
# ==========================================
class ProjectManager:

    def __init__(self, file_path="data.json"):
        self.file_path = file_path
        self.projects = {}
        self.load_data()

    # Xử lý File: Đọc dữ liệu từ file JSON
    def load_data(self):
        if not os.path.exists(self.file_path):
            self.projects = {}
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for p_id, p_info in data.items():
                    proj = Project(p_id, p_info["project_name"])
                    for t_data in p_info["tasks"]:
                        task = Task(
                            t_data["task_id"], t_data["name"], t_data["status"]
                        )
                        proj.tasks.append(task)
                    self.projects[p_id] = proj
        except Exception:
            self.projects = {}

    # Xử lý File: Ghi dữ liệu vào file JSON
    def save_data(self):
        data_to_save = {
            p_id: proj.to_dict() for p_id, proj in self.projects.items()
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    # CRUD: Thêm công việc mới vào dự án
    def add_task(self, project_id, project_name, task_id, task_name):
        if project_id not in self.projects:
            self.projects[project_id] = Project(project_id, project_name)

        # Kiểm tra trùng ID task
        if any(
            t.task_id == task_id for t in self.projects[project_id].tasks
        ):
            print(f" Mã công việc {task_id} đã tồn tại!")
            return False

        new_task = Task(task_id, task_name)
        self.projects[project_id].tasks.append(new_task)
        self.save_data()
        print(f" Đã thêm công việc '{task_name}' thành công.")
        return True

    # CRUD: Cập nhật trạng thái hoặc tên công việc
    def update_task(self, project_id, task_id, new_name=None, status=None):
        if project_id not in self.projects:
            print(" Không tìm thấy dự án!")
            return False

        for task in self.projects[project_id].tasks:
            if task.task_id == task_id:
                if new_name:
                    task.name = new_name
                if status:
                    task.status = status
                self.save_data()
                print(f" Đã cập nhật công việc {task_id}.")
                return True

        print(" Không tìm thấy công việc cần sửa!")
        return False

    # CRUD: Xóa công việc khỏi dự án
    def delete_task(self, project_id, task_id):
        if project_id not in self.projects:
            print(" Không tìm thấy dự án!")
            return False

        project = self.projects[project_id]
        for task in project.tasks:
            if task.task_id == task_id:
                project.tasks.remove(task)
                self.save_data()
                print(f" Đã xóa công việc {task_id}.")
                return True

        print("Không tìm thấy công việc cần xóa!")
        return False

    # Tính toán thống kê: Tính tỷ lệ % hoàn thành
    def calculate_completion_rate(self, project_id):
        if project_id not in self.projects:
            return 0.0

        tasks = self.projects[project_id].tasks
        if not tasks:
            return 0.0

        completed_tasks = sum(1 for t in tasks if t.status == "Đã xong")
        rate = (completed_tasks / len(tasks)) * 100
        return round(rate, 2)

    # Xuất báo cáo: Sử dụng Pandas để xuất danh sách ra file .xlsx
    def export_to_excel(self, filename="BaoCao_CongViec.xlsx"):
        all_tasks_list = []
        for p_id, proj in self.projects.items():
            rate = self.calculate_completion_rate(p_id)
            for t in proj.tasks:
                all_tasks_list.append(
                    {
                        "Mã Dự Án": p_id,
                        "Tên Dự Án": proj.project_name,
                        "Mã Công Việc": t.task_id,
                        "Tên Công Việc": t.name,
                        "Trạng Thái": t.status,
                        "Tiến Độ Dự Án (%)": f"{rate}%",
                    }
                )

        if not all_tasks_list:
            print("⚠️ Không có dữ liệu để xuất Excel.")
            return

        df = pd.DataFrame(all_tasks_list)
        df.to_excel(filename, index=False)
        print(f" Đã xuất file báo cáo thành công: {filename}")


# ==========================================
# CHẠY THỬ MÔ PHỎNG (TEST CODE)
# ==========================================
if __name__ == "__main__":
    # Khởi tạo bộ quản lý
    manager = ProjectManager()

    print("--- 1. Thêm công việc ---")
    manager.add_task("DA01", "Quản Lý Đồ Án", "T01", "Thiết kế Class OOP")
    manager.add_task("DA01", "Quản Lý Đồ Án", "T02", "Viết hàm JSON Storage")
    manager.add_task("DA01", "Quản Lý Đồ Án", "T03", "Xử lý Pandas Excel")

    print("\n--- 2. Cập nhật trạng thái (Đã xong) ---")
    manager.update_task("DA01", "T01", status="Đã xong")
    manager.update_task("DA01", "T02", status="Đã xong")

    print("\n--- 3. Xem tỷ lệ hoàn thành dự án ---")
    tile = manager.calculate_completion_rate("DA01")
    print(f"Tiến độ dự án DA01: {tile}%")

    print("\n--- 4. Xuất báo cáo ra Excel ---")
    manager.export_to_excel()