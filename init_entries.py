import sqlite3
from datetime import datetime

conn = sqlite3.connect("members.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    member_id INTEGER,
    type TEXT,
    amount REAL,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (member_id) REFERENCES members(id)
)
''')

conn.commit()
conn.close()
print("✅ สร้างตาราง entries เรียบร้อยแล้ว")