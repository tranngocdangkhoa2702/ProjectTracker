class ProjectModel:
    def __init__(self, project_id, name, description, status="Lên kế hoạch", leader="", members=None, start_date="", end_date=""):
        self.project_id = str(project_id)
        self.name = str(name)
        self.description = str(description)
        self.status = str(status or "Lên kế hoạch")
        self.leader = str(leader or "")
        self.members = list(members or [])
        self.start_date = str(start_date or "")
        self.end_date = str(end_date or "")
