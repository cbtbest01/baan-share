from flask import Flask, render_template, request, redirect, flash, session, url_for
from datetime import datetime
from functools import wraps
import sqlite3
import pytz

app = Flask(__name__)
app.secret_key = 'my-secret-key'

def get_db_connection():
    conn = sqlite3.connect('members.db')
    conn.row_factory = sqlite3.Row
    return conn

def format_thai_datetime(dt_str):
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
    dt = pytz.utc.localize(dt).astimezone(pytz.timezone("Asia/Bangkok"))
    return dt.strftime("%d/%m/%Y %H:%M")

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            flash("กรุณาเข้าสู่ระบบก่อน")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user == "maebow" and pwd == "123456":
            session["logged_in"] = True
            flash("เข้าสู่ระบบสำเร็จ 🎉")
            return redirect("/")
        flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง ❌")
        return redirect("/login")
    return render_template("login.html", year=datetime.now().year)

@app.route("/logout")
def logout():
    session.clear()
    flash("ออกจากระบบเรียบร้อยแล้ว 👋")
    return redirect("/login")

@app.route("/")
@login_required
def home():
    return render_template("home.html", year=datetime.now().year)

@app.route("/members", methods=["GET", "POST"])
@login_required
def members():
    conn = get_db_connection()
    if request.method == "POST":
        name = request.form["name"]
        if name.strip():
            conn.execute("INSERT INTO members (name) VALUES (?)", (name,))
            conn.commit()
            flash("เพิ่มสมาชิกเรียบร้อยแล้ว ✅")
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
        conn.execute("UPDATE members SET name=? WHERE id=?", (new_name, id))
        conn.commit()
        conn.close()
        flash("แก้ไขชื่อสมาชิกแล้ว 🎉")
        return redirect("/members")
    member = conn.execute("SELECT * FROM members WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_member.html", member=member, year=datetime.now().year)

@app.route("/members/delete/<int:id>")
@login_required
def delete_member(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM members WHERE id=?", (id,))
    conn.execute("DELETE FROM member_groups WHERE member_id=?", (id,))
    conn.commit()
    conn.close()
    flash("ลบสมาชิกแล้ว ❌")
    return redirect("/members")

@app.route("/members/<int:id>/groups")
@login_required
def member_groups(id):
    conn = get_db_connection()
    member = conn.execute("SELECT * FROM members WHERE id=?", (id,)).fetchone()
    groups = conn.execute("""
        SELECT g.*, (
            SELECT IFNULL(SUM(e.amount), 0)
            FROM entries e
            WHERE e.group_id = g.id AND e.member_id = ?
        ) AS paid_amount
        FROM groups g
        JOIN member_groups mg ON g.id = mg.group_id
        WHERE mg.member_id = ?
    """, (id, id)).fetchall()
    conn.close()
    return render_template("member_groups.html", member=member, groups=groups, year=datetime.now().year)

@app.route("/members/<int:member_id>/groups/<int:group_id>/entries")
@login_required
def member_entries_in_group(member_id, group_id):
    conn = get_db_connection()
    member = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    group = conn.execute("SELECT * FROM groups WHERE id=?", (group_id,)).fetchone()
    entries = conn.execute("""
        SELECT e.*, m.name AS member_name
        FROM entries e
        JOIN members m ON e.member_id = m.id
        WHERE e.member_id = ? AND e.group_id = ?
        ORDER BY e.created_at ASC
    """, (member_id, group_id)).fetchall()
    conn.close()
    return render_template("member_entries_in_group.html",
                           member=member,
                           group=group,
                           entries=entries,
                           format_thai_datetime=format_thai_datetime,
                           year=datetime.now().year)

@app.route("/groups")
@login_required
def groups():
    conn = get_db_connection()
    groups = conn.execute("SELECT * FROM groups").fetchall()
    conn.close()
    return render_template("groups.html",
                           groups=groups,
                           format_thai_datetime=format_thai_datetime,
                           year=datetime.now().year)

@app.route("/groups/<int:id>")
@login_required
def view_group(id):
    conn = get_db_connection()
    group = conn.execute("SELECT * FROM groups WHERE id=?", (id,)).fetchone()
    members = conn.execute("""
        SELECT m.id, m.name, IFNULL(SUM(e.amount), 0) AS total_paid
        FROM members m
        JOIN member_groups mg ON m.id = mg.member_id
        LEFT JOIN entries e ON e.member_id = m.id AND e.group_id = ?
        WHERE mg.group_id = ?
        GROUP BY m.id
        ORDER BY m.name
    """, (id, id)).fetchall()
    entries = conn.execute("""
        SELECT e.*, m.name AS member_name
        FROM entries e
        JOIN members m ON e.member_id = m.id
        WHERE e.group_id = ?
        ORDER BY e.created_at DESC
    """, (id,)).fetchall()
    conn.close()
    return render_template("group_detail.html", group=group, members=members, entries=entries, year=datetime.now().year)

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
        members = request.form.getlist("members")

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO groups (name, rounds, amount_per_round, start_date, note)
            VALUES (?, ?, ?, ?, ?)""",
            (name, rounds, amount, start_date, note)
        )
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
        members = request.form.getlist("members")

        conn.execute("""
            UPDATE groups SET name=?, rounds=?, amount_per_round=?, start_date=?, note=? WHERE id=?""",
            (name, rounds, amount, start_date, note, id)
        )
        conn.execute("DELETE FROM member_groups WHERE group_id=?", (id,))
        for m_id in members:
            conn.execute("INSERT INTO member_groups (member_id, group_id) VALUES (?, ?)", (m_id, id))
        conn.commit()
        conn.close()
        flash("อัปเดตวงแชร์เรียบร้อย 🛠️")
        return redirect("/groups")

    group = conn.execute("SELECT * FROM groups WHERE id=?", (id,)).fetchone()
    members = conn.execute("SELECT * FROM members").fetchall()
    current = conn.execute("SELECT member_id FROM member_groups WHERE group_id=?", (id,)).fetchall()
    current_ids = [r["member_id"] for r in current]
    conn.close()
    return render_template("edit_group.html",
                           group=group,
                           members=members,
                           current_ids=current_ids,
                           year=datetime.now().year)
@app.route("/groups/delete/<int:id>")
@login_required
def delete_group(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM member_groups WHERE group_id=?", (id,))
    conn.execute("DELETE FROM groups WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("ลบวงแชร์เรียบร้อยแล้ว ❌")
    return redirect("/groups")
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    conn = get_db_connection()
    if request.method == "POST":
        group_id = request.form["group"]
        member_id = request.form["member"]
        entry_type = request.form["type"]
        amount = request.form["amount"]
        note = request.form["note"]

        conn.execute("""
            INSERT INTO entries (group_id, member_id, type, amount, note)
            VALUES (?, ?, ?, ?, ?)""",
            (group_id, member_id, entry_type, amount, note)
        )
        conn.commit()
        flash("✅ บันทึกรายการเรียบร้อยแล้ว")
        return redirect("/add")

    groups = conn.execute("SELECT * FROM groups").fetchall()
    conn.close()
    return render_template("add.html", groups=groups, year=datetime.now().year)
@app.route("/members/by-group/<int:group_id>")
@login_required
def members_by_group(group_id):
    conn = get_db_connection()
    members = conn.execute("""
        SELECT m.id, m.name
        FROM members m
        JOIN member_groups mg ON m.id = mg.member_id
        WHERE mg.group_id = ?
    """, (group_id,)).fetchall()
    conn.close()
    return {"members": [dict(m) for m in members]}

@app.route("/report/balance", methods=["GET"])
@login_required
def report_balance():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = get_db_connection()
    params = []
    query = """
        SELECT g.name AS group_name, m.name AS member_name,
               COUNT(e.id) AS entry_count,
               SUM(e.amount) AS total_amount
        FROM entries e
        JOIN members m ON e.member_id = m.id
        JOIN groups g ON e.group_id = g.id
    """

    where = []
    if start:
        where.append("DATE(e.created_at) >= DATE(?)")
        params.append(start)
    if end:
        where.append("DATE(e.created_at) <= DATE(?)")
        params.append(end)
    if where:
        query += " WHERE " + " AND ".join(where)

    query += " GROUP BY g.id, m.id ORDER BY g.name, m.name"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("report_balance.html", rows=rows, start_date=start or "", end_date=end or "", year=datetime.now().year)
    