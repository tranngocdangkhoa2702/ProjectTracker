class Task:
    def __init__(self, task_id, name, deadline, priority, status):
        self.task_id = str(task_id)
        self.name = str(name)
        self.deadline = str(deadline)
        self.priority = str(priority)
        self.status = str(status) # "Todo" hoặc "Done"