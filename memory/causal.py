from typing import Dict, List, Set
import sqlite3

class CausalGraph:
    def __init__(self, db_path: str = "acr_causal.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS causal_links (
                parent_id TEXT,
                child_id TEXT,
                link_type TEXT,
                strength REAL,
                PRIMARY KEY (parent_id, child_id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_link(self, parent_id: str, child_id: str, link_type: str = "leads_to", strength: float = 1.0):
        if not parent_id or not child_id:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO causal_links (parent_id, child_id, link_type, strength)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(parent_id, child_id) DO UPDATE SET strength = strength + 0.1
        ''', (parent_id, child_id, link_type, strength))
        conn.commit()
        conn.close()

    def get_descendants(self, event_id: str) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT child_id FROM causal_links WHERE parent_id = ?', (event_id,))
        results = [r[0] for r in cursor.fetchall()]
        conn.close()
        return results
