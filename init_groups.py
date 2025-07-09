import sqlite3

conn = sqlite3.connect('members.db')
c = conn.cursor()

# ตารางวงแชร์
c.execute('''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rounds INTEGER,
    amount_per_round INTEGER,
    start_date TEXT,
    note TEXT
)
''')

# ตารางเชื่อม สมาชิก <-> วงแชร์
c.execute('''
CREATE TABLE IF NOT EXISTS member_groups (
    member_id INTEGER,
    group_id INTEGER,
    PRIMARY KEY (member_id, group_id),
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
''')

conn.commit()
conn.close()
print("✅ สร้างตาราง groups และ member_groups แล้วเรียบร้อย")