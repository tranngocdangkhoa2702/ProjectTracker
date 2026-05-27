import sqlite3
from datetime import datetime
from pathlib import Path


class AuditLogModel:
    def __init__(self, db_name="database.db"):
        self.db_name = Path(__file__).resolve().parents[1] / db_name
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id TEXT,
                    details TEXT,
                    created_at TEXT NOT NULL
                )"""
            )
            conn.commit()

    def log(self, actor, action, target_type, target_id="", details=""):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO audit_logs (actor, action, target_type, target_id, details, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    actor or "system",
                    action,
                    target_type,
                    str(target_id) if target_id is not None else "",
                    details,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()

    def list_logs(self, limit=300):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, actor, action, target_type, target_id, details, created_at
                   FROM audit_logs
                   ORDER BY id DESC
                   LIMIT ?""",
                (limit,),
            )
            rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "actor": row[1],
                "action": row[2],
                "target_type": row[3],
                "target_id": row[4],
                "details": row[5],
                "created_at": row[6],
            }
            for row in rows
        ]
