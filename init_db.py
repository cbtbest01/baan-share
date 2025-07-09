import sqlite3

conn = sqlite3.connect('members.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

print("✅ สร้างตาราง members ในฐานข้อมูลเรียบร้อยแล้ว")