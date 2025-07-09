import sqlite3

conn = sqlite3.connect("members.db")
c = conn.cursor()

# ลบตารางเก่าหากมีอยู่ (เพื่อ reset ใหม่)
c.execute("DROP TABLE IF EXISTS members")
c.execute("DROP TABLE IF EXISTS groups")
c.execute("DROP TABLE IF EXISTS member_groups")
c.execute("DROP TABLE IF EXISTS entries")

# 👤 สมาชิก
c.execute("""
    CREATE TABLE members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
""")

# 🌀 วงแชร์
c.execute("""
    CREATE TABLE groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rounds INTEGER,
        amount_per_round REAL,
        start_date TEXT,
        note TEXT
    )
""")

# 🔗 ความสัมพันธ์สมาชิก-วง
c.execute("""
    CREATE TABLE member_groups (
        member_id INTEGER,
        group_id INTEGER,
        PRIMARY KEY (member_id, group_id),
        FOREIGN KEY (member_id) REFERENCES members(id),
        FOREIGN KEY (group_id) REFERENCES groups(id)
    )
""")

# 💸 รายการแชร์ พร้อมเวลาบันทึก
c.execute("""
    CREATE TABLE entries (
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
""")

conn.commit()
conn.close()
print("✅ สร้างฐานข้อมูล members.db เรียบร้อยแล้ว")