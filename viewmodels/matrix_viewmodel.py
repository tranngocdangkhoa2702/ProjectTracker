class EisenhowerViewModel:
    def __init__(self, all_tasks):
        self.all_tasks = all_tasks # Danh sách lấy từ TaskManager

    def get_tasks_by_priority(self, priority_level):
        """Lọc danh sách công việc theo cấp độ P1, P2, P3, hoặc P4"""
        return [t for t in self.all_tasks if priority_level in t.priority]