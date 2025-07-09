from flask import Flask, render_template, request, redirect, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'my-very-secret-key'

# 🌐 เชื่อมต่อฐานข้อมูล
def get_db_connection():
    conn = sqlite3.connect('members.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("home.html", year=datetime.now().year)

@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        member = request.form['member']
        entry_type = request.form['type']
        amount = request.form['amount']
        note = request.form['note']
        flash(f'บันทึกสำเร็จ: {member} - {entry_type} {amount} บาท')
        return redirect("/add")
    return render_template("add.html", year=datetime.now().year)

@app.route("/summary")
def summary():
    return render_template("summary.html", year=datetime.now().year)

# ✅ สมาชิก
@app.route("/members", methods=["GET", "POST"])
def members():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["name"]
        if name.strip():
            conn.execute("INSERT INTO members (name) VALUES (?)", (name,))
            conn.commit()
            flash("เพิ่มสมาชิกแล้วเรียบร้อย ✅")
        return redirect("/members")
    members = conn.execute("SELECT * FROM members").fetchall()
    conn.close()
    return render_template("members.html", members=members, year=datetime.now().year)

@app.route("/members/edit/<int:id>", methods=["GET", "POST"])
def edit_member(id):
    conn = get_db_connection()
    if request.method == "POST":
        new_name = request.form["name"]
        conn.execute("UPDATE members SET name = ? WHERE id = ?", (new_name, id))
        conn.commit()
        flash("แก้ไขชื่อสมาชิกแล้ว 🎉")
        return redirect("/members")
    member = conn.execute("SELECT * FROM members WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template("edit_member.html", member=member, year=datetime.now().year)

@app.route("/members/delete/<int:id>")
def delete_member(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM members WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("ลบสมาชิกแล้ว ❌")
    return redirect("/members")

@app.route("/notifications")
def notifications():
    return render_template("notifications.html", year=datetime.now().year)

@app.route("/admin")
def admin():
    return render_template("admin.html", year=datetime.now().year)

# 📊 รายงาน
@app.route("/report/daily-total")
def report_daily_total():
    return render_template("report_daily_total.html", year=datetime.now().year)

@app.route("/report/daily-by-group")
def report_by_group():
    return render_template("report_by_group.html", year=datetime.now().year)

@app.route("/report/member-list")
def report_member_list():
    return render_template("report_member_list.html", year=datetime.now().year)

@app.route("/report/daily-net")
def report_net_daily():
    return render_template("report_net_daily.html", year=datetime.now().year)

@app.route("/report/balance")
def report_balance():
    return render_template("report_balance.html", year=datetime.now().year)

@app.route("/report/outstanding")
def report_outstanding():
    return render_template("report_outstanding.html", year=datetime.now().year)