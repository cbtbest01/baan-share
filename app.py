from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html", year=datetime.now().year)

# พร้อม route อื่น ๆ ในอนาคต
@app.route("/add")
def add():
    return "<h2>ฟอร์มบันทึกรายการ (กำลังพัฒนา)</h2>"

@app.route("/summary")
def summary():
    return "<h2>รายการย้อนหลัง (กำลังพัฒนา)</h2>"

@app.route("/members")
def members():
    return "<h2>รายชื่อสมาชิก (กำลังพัฒนา)</h2>"

@app.route("/notifications")
def notifications():
    return "<h2>แจ้งเตือน (กำลังพัฒนา)</h2>"

@app.route("/admin")
def admin():
    return "<h2>จัดการระบบ (สำหรับแม่โบว์)</h2>"