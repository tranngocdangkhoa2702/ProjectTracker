class EisenhowerViewModel:
    def __init__(self, all_tasks):
        self.all_tasks = all_tasks

    def get_tasks_by_priority(self, priority_level):
        """Lọc danh sách công việc theo cấp độ P1, P2, P3 hoặc P4."""
        return [task for task in self.all_tasks if priority_level in task.priority]
