from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "dev-secret"  # needed for flash messages

# ---- MySQL connection configuration (adjust if your server differs) ----
db_config = {
    'host': '172.31.160.1',
    'port': '3306',
    'user': 'root',
    'password': 'F-15Eagle@WC',
    'database': 'database'      # change this to your HW2 db name if needed
}

# ---- DB helpers ----------------------------------------------------------
def get_conn():
    return mysql.connector.connect(**db_config)

def init_db():
    """Create tables if they do not exist."""
    sqls = [
        """
        CREATE TABLE IF NOT EXISTS Students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name  VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS Courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code  VARCHAR(32) NOT NULL UNIQUE,
            title VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS Enrollments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id  INT NOT NULL,
            term       VARCHAR(64) NOT NULL,
            UNIQUE KEY uq_enroll (student_id, course_id, term),
            CONSTRAINT fk_enr_student FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE,
            CONSTRAINT fk_enr_course  FOREIGN KEY (course_id)  REFERENCES Courses(id)  ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """
    ]
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        for s in sqls:
            cur.execute(s)
        conn.commit()
    finally:
        if cur: cur.close()
        if conn and conn.is_connected(): conn.close()

# ---- Routes: Home --------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ---- Students CRUD -------------------------------------------------------
@app.route("/students")
def students_list():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, email FROM Students ORDER BY id;")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("students.html", students=rows)

@app.route("/students/add", methods=["POST"])
def students_add():
    name = request.form.get("name","").strip()
    email = request.form.get("email","").strip() or None
    if not name:
        flash("Name is required", "error")
        return redirect(url_for("students_list"))
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Students (name, email) VALUES (%s, %s);", (name, email))
        conn.commit()
        flash("Student created", "ok")
    except Error as e:
        conn.rollback()
        flash(f"DB error: {e}", "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("students_list"))

@app.route("/students/delete/<int:sid>", methods=["POST"])
def students_delete(sid):
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Students WHERE id=%s;", (sid,))
        conn.commit()
        flash("Student deleted", "ok")
    except Error as e:
        conn.rollback()
        flash(f"DB error: {e}", "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("students_list"))

@app.route("/students/edit/<int:sid>", methods=["GET", "POST"])
def students_edit(sid):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    if request.method == "GET":
        cur.execute("SELECT id, name, email FROM Students WHERE id=%s;", (sid,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if not row:
            flash("Student not found", "error")
            return redirect(url_for("students_list"))
        return render_template("student_edit.html", student=row)
    else:
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip() or None
        cur2 = conn.cursor()
        try:
            cur2.execute("UPDATE Students SET name=%s, email=%s WHERE id=%s;", (name, email, sid))
            conn.commit()
            flash("Student updated", "ok")
        except Error as e:
            conn.rollback()
            flash(f"DB error: {e}", "error")
        finally:
            cur.close(); cur2.close(); conn.close()
        return redirect(url_for("students_list"))

# ---- Courses CRUD --------------------------------------------------------
@app.route("/courses")
def courses_list():
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, code, title FROM Courses ORDER BY id;")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("courses.html", courses=rows)

@app.route("/courses/add", methods=["POST"])
def courses_add():
    code = request.form.get("code","").strip()
    title = request.form.get("title","").strip()
    if not code or not title:
        flash("Code and title are required", "error")
        return redirect(url_for("courses_list"))
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Courses (code, title) VALUES (%s, %s);", (code, title))
        conn.commit()
        flash("Course created", "ok")
    except Error as e:
        conn.rollback()
        flash(f"DB error: {e}", "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("courses_list"))

@app.route("/courses/delete/<int:cid>", methods=["POST"])
def courses_delete(cid):
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Courses WHERE id=%s;", (cid,))
        conn.commit()
        flash("Course deleted", "ok")
    except Error as e:
        conn.rollback()
        flash(f"DB error: {e}", "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("courses_list"))

@app.route("/courses/edit/<int:cid>", methods=["GET", "POST"])
def courses_edit(cid):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    if request.method == "GET":
        cur.execute("SELECT id, code, title FROM Courses WHERE id=%s;", (cid,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if not row:
            flash("Course not found", "error")
            return redirect(url_for("courses_list"))
        return render_template("course_edit.html", course=row)
    else:
        code = request.form.get("code","").strip()
        title = request.form.get("title","").strip()
        cur2 = conn.cursor()
        try:
            cur2.execute("UPDATE Courses SET code=%s, title=%s WHERE id=%s;", (code, title, cid))
            conn.commit()
            flash("Course updated", "ok")
        except Error as e:
            conn.rollback()
            flash(f"DB error: {e}", "error")
        finally:
            cur.close(); cur2.close(); conn.close()
        return redirect(url_for("courses_list"))

# ---- Enrollments CRUD ----------------------------------------------------
@app.route("/enrollments")
def enrollments_list():
    # show enrollments with JOINed names/codes
    sql = """
    SELECT e.id, s.name AS student_name, c.code AS course_code, c.title AS course_title, e.term
    FROM Enrollments e
    JOIN Students s ON s.id = e.student_id
    JOIN Courses  c ON c.id = e.course_id
    ORDER BY s.name, c.code, e.term;
    """
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute(sql); rows = cur.fetchall()

    # for the add form dropdowns
    cur.execute("SELECT id, name FROM Students ORDER BY name;")
    students = cur.fetchall()
    cur.execute("SELECT id, code FROM Courses ORDER BY code;")
    courses = cur.fetchall()

    cur.close(); conn.close()
    return render_template("enrollments.html", enrollments=rows, students=students, courses=courses)

@app.route("/enrollments/add", methods=["POST"])
def enrollments_add():
    student_id = request.form.get("student_id")
    course_id  = request.form.get("course_id")
    term       = request.form.get("term","").strip()
    if not student_id or not course_id or not term:
        flash("Student, Course, and Term are required", "error")
        return redirect(url_for("enrollments_list"))

    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Enrollments (student_id, course_id, term) VALUES (%s, %s, %s);",
            (student_id, course_id, term)
        )
        conn.commit()
        flash("Enrollment created", "ok")
    except Error as e:
        conn.rollback()
        flash(f"DB error: {e}", "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("enrollments_list"))

@app.route("/enrollments/delete/<int:eid>", methods=["POST"])
def enrollments_delete(eid):
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Enrollments WHERE id=%s;", (eid,))
        conn.commit()
        flash("Enrollment deleted", "ok")
    except Error as e:
        conn.rollback()
        flash(f"DB error: {e}", "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("enrollments_list"))

# ---- JOIN report (explicit) ----------------------------------------------
@app.route("/report")
def report():
    sql = """
    SELECT s.name AS student_name, c.code AS course_code, c.title AS course_title, e.term
    FROM Enrollments e
    JOIN Students s ON s.id = e.student_id
    JOIN Courses  c ON c.id = e.course_id
    ORDER BY student_name, course_code, term;
    """
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute(sql); rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("report.html", rows=rows)

def bootstrap():
    # Flask 3.x: call our DB initializer explicitly at startup
    with app.app_context():
        init_db()

if __name__ == "__main__":
    bootstrap()
    app.run(debug=True)