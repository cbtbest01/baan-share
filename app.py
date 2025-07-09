from flask import Flask, render_template, request, redirect, flash, session, url_for
from datetime import datetime
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'my-very-secret-key'  # ใช้สำหรับ flash และ session

# ================================
# เชื่อมต่อฐานข้อมูล
# ================================
def get_db_connection():
    conn = sqlite3.connect('members.db')
    conn.row_factory = sqlite3.Row
    return conn

# ================================
# ระบบล็อกอิน
# ================================
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            flash("กรุณาเข้าสู่ระบบก่อน 🔐")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "123456":
            session["logged_in"] = True
            flash("เข้าสู่ระบบสำเร็จ 🎉")
            return redirect("/")
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง ❌")
            return redirect("/login")
    return render_template("login.html", year=datetime.now().year)

@app.route("/logout")
def logout():
    session.clear()
    flash("ออกจากระบบเรียบร้อยแล้ว 👋")
    return redirect("/login")

# ================================
# Routes หลัก
# ================================
@app.route("/")
@login_required
def home():
    return render_template("home.html", year=datetime.now().year)

@app.route("/add", methods=['GET', 'POST'])
@login_required
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
@login_required
def summary():
    return render_template("summary.html", year=datetime.now().year)

@app.route("/members", methods=["GET", "POST"])
@login_required
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
@login_required
def edit_member(id):
    conn = get_db_connection()
    if request.method == "POST":
        new_name = request.form["name"]
        conn.execute("UPDATE members SET name = ? WHERE id = ?", (new_name, id))
        conn.commit()
        conn.close()
        flash("แก้ไขชื่อสมาชิกแล้ว 🎉")
        return redirect("/members")
    member = conn.execute("SELECT * FROM members WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template("edit_member.html", member=member, year=datetime.now().year)

@app.route("/members/delete/<int:id>")
@login_required
def delete_member(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM members WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("ลบสมาชิกแล้ว ❌")
    return redirect("/members")

@app.route("/notifications")
@login_required
def notifications():
    return render_template("notifications.html", year=datetime.now().year)

@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html", year=datetime.now().year)

# ================================
# รายงาน
# ================================
@app.route("/report/daily-total")
@login_required
def report_daily_total():
    return render_template("report_daily_total.html", year=datetime.now().year)

@app.route("/report/daily-by-group")
@login_required
def report_by_group():
    return render_template("report_by_group.html", year=datetime.now().year)

@app.route("/report/member-list")
@login_required
def report_member_list():
    return render_template("report_member_list.html", year=datetime.now().year)

@app.route("/report/daily-net")
@login_required
def report_net_daily():
    return render_template("report_net_daily.html", year=datetime.now().year)

@app.route("/report/balance")
@login_required
def report_balance():
    return render_template("report_balance.html", year=datetime.now().year)

@app.route("/report/outstanding")
@login_required
def report_outstanding():
    return render_template("report_outstanding.html", year=datetime.now().year)
@app.route("/groups")
@login_required
def groups():
    conn = get_db_connection()
    groups = conn.execute("SELECT * FROM groups").fetchall()
    conn.close()
    return render_template("groups.html", groups=groups, year=datetime.now().year)

@app.route("/groups/new", methods=["GET", "POST"])
@login_required
def add_group():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["name"]
        rounds = request.form["rounds"]
        amount = request.form["amount"]
        start_date = request.form["start_date"]
        note = request.form["note"]
        members = request.form.getlist("members")  # checkbox list

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO groups (name, rounds, amount_per_round, start_date, note)
            VALUES (?, ?, ?, ?, ?)
        """, (name, rounds, amount, start_date, note))
        group_id = cur.lastrowid

        for m_id in members:
            cur.execute("INSERT INTO member_groups (member_id, group_id) VALUES (?, ?)", (m_id, group_id))

        conn.commit()
        conn.close()
        flash("สร้างวงแชร์ใหม่แล้ว 🎉")
        return redirect("/groups")

    all_members = conn.execute("SELECT * FROM members").fetchall()
    conn.close()
    return render_template("add_group.html", members=all_members, year=datetime.now().year)

@app.route("/groups/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_group(id):
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["name"]
        rounds = request.form["rounds"]
        amount = request.form["amount"]
        start_date = request.form["start_date"]
        note = request.form["note"]
        selected_members = request.form.getlist("members")

        conn.execute("""
            UPDATE groups
            SET name=?, rounds=?, amount_per_round=?, start_date=?, note=?
            WHERE id=?
        """, (name, rounds, amount, start_date, note, id))

        conn.execute("DELETE FROM member_groups WHERE group_id = ?", (id,))
        for m_id in selected_members:
            conn.execute("INSERT INTO member_groups (member_id, group_id) VALUES (?, ?)", (m_id, id))

        conn.commit()
        conn.close()
        flash("อัปเดตวงแชร์เรียบร้อย 🛠️")
        return redirect("/groups")

    group = conn.execute("SELECT * FROM groups WHERE id=?", (id,)).fetchone()
    members = conn.execute("SELECT * FROM members").fetchall()
    current = conn.execute("SELECT member_id FROM member_groups WHERE group_id=?", (id,)).fetchall()
    current_ids = [row["member_id"] for row in current]
    conn.close()
    return render_template("edit_group.html", group=group, members=members, current_ids=current_ids, year=datetime.now().year)

@app.route("/groups/delete/<int:id>")
@login_required
def delete_group(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM member_groups WHERE group_id = ?", (id,))
    conn.execute("DELETE FROM groups WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("ลบวงแชร์เรียบร้อยแล้ว ❌")
    return redirect("/groups")