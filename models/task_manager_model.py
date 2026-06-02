class Task:
    def __init__(
        self,
        task_id,
        name,
        deadline,
        priority,
        status,
        project_id="",
        assignee="",
        created_by="",
        start_date="",
        completed_at="",
        is_urgent=False,
        is_important=False,
        approval_state="approved",
        extension_status="",
        requested_deadline="",
        extension_reason="",
    ):
        self.task_id = str(task_id)
        self.name = str(name)
        self.start_date = str(start_date or "")
        self.deadline = str(deadline)
        self.priority = str(priority)
        self.status = str(status)
        self.project_id = str(project_id or "")
        self.assignee = str(assignee or "")
        self.created_by = str(created_by or "")
        self.completed_at = str(completed_at or "")
        self.is_urgent = bool(is_urgent)
        self.is_important = bool(is_important)
        self.approval_state = str(approval_state or "approved")
        self.extension_status = str(extension_status or "")
        self.requested_deadline = str(requested_deadline or "")
        self.extension_reason = str(extension_reason or "")
