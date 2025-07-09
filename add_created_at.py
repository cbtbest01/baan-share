import sqlite3

conn = sqlite3.connect("members.db")
conn.execute("ALTER TABLE entries ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;")
conn.commit()
conn.close()
print("✅ เพิ่มฟิลด์ created_at เรียบร้อยแล้ว")