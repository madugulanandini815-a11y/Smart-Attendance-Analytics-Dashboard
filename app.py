from flask import Flask, render_template, request, redirect, session, send_file
import pymysql
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from openpyxl import Workbook
import os

app = Flask(__name__)
app.secret_key = "attendance123"

# ---------------- DATABASE CONNECTION ----------------

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Nandini@19",
    database="attendance_system"
)

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor = connection.cursor()
        sql = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()

        if user:
            session["username"] = username
            return redirect("/dashboard")

        return render_template(
            "login.html",
            message="Invalid Username or Password"
        )

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Faculty
    cursor.execute("SELECT COUNT(*) FROM faculty")
    total_faculty = cursor.fetchone()[0]

    # Total Subjects
    cursor.execute("SELECT COUNT(*) FROM subjects")
    total_subjects = cursor.fetchone()[0]

    # Attendance Percentage
    cursor.execute("""
        SELECT ROUND(
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            2
        )
        FROM attendance
    """)
    attendance_percentage = cursor.fetchone()[0]

    if attendance_percentage is None:
        attendance_percentage = 0

    # Present Students
    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE status='Present'
    """)
    present_students = cursor.fetchone()[0]

    # Absent Students
    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE status='Absent'
    """)
    absent_students = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_faculty=total_faculty,
        total_subjects=total_subjects,
        attendance_percentage=attendance_percentage,
        present_students=present_students,
        absent_students=absent_students
    )


# ---------------- STUDENTS ----------------

@app.route("/students")
def students():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            student_id,
            roll_no,
            name,
            department,
            semester,
            section,
            email,
            phone
        FROM students
        ORDER BY student_id
    """)
    students = cursor.fetchall()

    return render_template(
        "students.html",
        students=students
    )


# ---------------- ADD STUDENT ----------------

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        name = request.form["name"]
        department = request.form["department"]
        semester = request.form["semester"]
        section = request.form["section"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO students
        (roll_no,name,department,semester,section,email,phone)
        VALUES(%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            roll_no,
            name,
            department,
            semester,
            section,
            email,
            phone
        ))
        connection.commit()

        return redirect("/students")

    return render_template("add_student.html")


# ---------------- EDIT STUDENT ----------------

@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        name = request.form["name"]
        department = request.form["department"]
        semester = request.form["semester"]
        section = request.form["section"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
            UPDATE students
            SET
                roll_no=%s,
                name=%s,
                department=%s,
                semester=%s,
                section=%s,
                email=%s,
                phone=%s
            WHERE student_id=%s
        """,
        (
            roll_no,
            name,
            department,
            semester,
            section,
            email,
            phone,
            id
        ))
        connection.commit()

        return redirect("/students")

    cursor.execute(
        "SELECT * FROM students WHERE student_id=%s",
        (id,)
    )
    student = cursor.fetchone()

    return render_template(
        "edit_student.html",
        student=student
    )


# ---------------- DELETE STUDENT ----------------

@app.route("/delete_student/<int:id>")
def delete_student(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM students WHERE student_id=%s",
        (id,)
    )
    connection.commit()

    return redirect("/students")


# ---------------- FACULTY ----------------

@app.route("/faculty")
def faculty():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            faculty_id,
            faculty_name,
            subject,
            email,
            phone
        FROM faculty
        ORDER BY faculty_id
    """)
    faculty = cursor.fetchall()

    return render_template(
        "faculty.html",
        faculty=faculty
    )


# ---------------- ADD FACULTY ----------------

@app.route("/add_faculty", methods=["GET", "POST"])
def add_faculty():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        faculty_name = request.form["faculty_name"]
        subject = request.form["subject"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO faculty
            (faculty_name, subject, email, phone)
            VALUES (%s,%s,%s,%s)
        """,
        (
            faculty_name,
            subject,
            email,
            phone
        ))
        connection.commit()

        return redirect("/faculty")

    return render_template("add_faculty.html")


# ---------------- EDIT FACULTY ----------------

@app.route("/edit_faculty/<int:id>", methods=["GET", "POST"])
def edit_faculty(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":
        faculty_name = request.form["faculty_name"]
        subject = request.form["subject"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
            UPDATE faculty
            SET
                faculty_name=%s,
                subject=%s,
                email=%s,
                phone=%s
            WHERE faculty_id=%s
        """,
        (
            faculty_name,
            subject,
            email,
            phone,
            id
        ))
        connection.commit()

        return redirect("/faculty")

    cursor.execute(
        "SELECT * FROM faculty WHERE faculty_id=%s",
        (id,)
    )
    faculty = cursor.fetchone()

    return render_template(
        "edit_faculty.html",
        faculty=faculty
    )


# ---------------- DELETE FACULTY ----------------

@app.route("/delete_faculty/<int:id>")
def delete_faculty(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM faculty WHERE faculty_id=%s",
        (id,)
    )
    connection.commit()

    return redirect("/faculty")


# ---------------- DEPARTMENTS ----------------

@app.route("/departments")
def departments():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            department_id,
            department_name,
            hod_name,
            department_block
        FROM departments
        ORDER BY department_id
    """)
    departments = cursor.fetchall()

    return render_template(
        "departments.html",
        departments=departments
    )


# ---------------- ADD DEPARTMENT ----------------

@app.route("/add_department", methods=["GET", "POST"])
def add_department():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":
        department_name = request.form["department_name"]
        hod_name = request.form["hod_name"]
        department_block = request.form["department_block"]

        cursor.execute("""
            INSERT INTO departments
            (department_name, hod_name, department_block)
            VALUES(%s,%s,%s)
        """, (department_name, hod_name, department_block))
        connection.commit()

        return redirect("/departments")

    return render_template("add_department.html")


# ---------------- EDIT DEPARTMENT ----------------

@app.route("/edit_department/<int:id>", methods=["GET", "POST"])
def edit_department(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":
        department_name = request.form["department_name"]
        hod_name = request.form["hod_name"]
        department_block = request.form["department_block"]

        cursor.execute("""
        UPDATE departments
        SET
            department_name=%s,
            hod_name=%s,
            department_block=%s
        WHERE department_id=%s
        """,
        (
            department_name,
            hod_name,
            department_block,
            id
        ))
        connection.commit()

        return redirect("/departments")

    cursor.execute(
        "SELECT * FROM departments WHERE department_id=%s",
        (id,)
    )
    department = cursor.fetchone()

    return render_template(
        "edit_department.html",
        department=department
    )


# ---------------- DELETE DEPARTMENT ----------------

@app.route("/delete_department/<int:id>")
def delete_department(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM departments WHERE department_id=%s",
        (id,)
    )
    connection.commit()

    return redirect("/departments")


# ---------------- DEPARTMENT STUDENTS ----------------

@app.route("/department_students/<department>")
def department_students(department):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM students
        WHERE department=%s
    """, (department,))
    students = cursor.fetchall()

    return render_template(
        "department_students.html",
        students=students,
        department=department
    )


# ---------------- DEPARTMENT FACULTY ----------------

@app.route("/department_faculty/<department>")
def department_faculty(department):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM faculty
        WHERE department=%s
    """, (department,))
    faculty = cursor.fetchall()

    return render_template(
        "department_faculty.html",
        faculty=faculty,
        department=department
    )


# ---------------- STUDENT PROFILE ----------------

@app.route("/student_profile/<int:id>")
def student_profile(id):
    if "username" not in session:
        return redirect("/login")

    student_id = id
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            student_id,
            roll_no,
            name,
            department,
            semester,
            section,
            email,
            phone
        FROM students
        WHERE student_id=%s
    """,(student_id,))
    student = cursor.fetchone()

    cursor.execute("""
        SELECT
            s.subject_name,
            COUNT(a.attendance_id),
            SUM(
                CASE
                    WHEN a.status='Present'
                    THEN 1
                    ELSE 0
                END
            )
        FROM attendance a
        INNER JOIN subjects s
        ON a.subject_id=s.subject_id
        WHERE a.student_id=%s
        GROUP BY s.subject_name
    """,(student_id,))
    data = cursor.fetchall()

    attendance = []
    overall_present = 0
    overall_total = 0

    for row in data:
        subject = row[0]
        total = row[1]
        present = row[2] if row[2] else 0
        percentage = round((present / total) * 100, 2) if total else 0

        attendance.append((subject, present, total, percentage))
        overall_present += present
        overall_total += total

    overall_percentage = round((overall_present / overall_total) * 100, 2) if overall_total else 0

    if overall_percentage >= 85:
        prediction = "Excellent"
    elif overall_percentage >= 75:
        prediction = "Good"
    elif overall_percentage >= 65:
        prediction = "Average"
    else:
        prediction = "Low Attendance"

    return render_template(
        "student_profile.html",
        student=student,
        attendance=attendance,
        overall_percentage=overall_percentage,
        prediction=prediction
    )


# ---------------- SUBJECTS ----------------

@app.route("/subjects")
def subjects():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM subjects
        ORDER BY department, semester
    """)
    subjects = cursor.fetchall()

    return render_template(
        "subjects.html",
        subjects=subjects
    )


# ---------------- ADD SUBJECT ----------------

@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        department = request.form["department"]
        subject_name = request.form["subject_name"]
        semester = request.form["semester"]

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO subjects
            (subject_name, semester, department)
            VALUES(%s,%s,%s)
        """, (subject_name, semester, department))
        connection.commit()

        return redirect("/subjects")

    return render_template("add_subject.html")


# ---------------- EDIT SUBJECT ----------------

@app.route("/edit_subject/<int:id>", methods=["GET", "POST"])
def edit_subject(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":
        department = request.form["department"]
        subject_name = request.form["subject_name"]
        semester = request.form["semester"]

        cursor.execute("""
            UPDATE subjects
            SET
                department=%s,
                subject_name=%s,
                semester=%s
            WHERE subject_id=%s
        """, (department, subject_name, semester, id))
        connection.commit()

        return redirect("/subjects")

    cursor.execute(
        "SELECT * FROM subjects WHERE subject_id=%s",
        (id,)
    )
    subject = cursor.fetchone()

    return render_template(
        "edit_subject.html",
        subject=subject
    )


# ---------------- DELETE SUBJECT ----------------

@app.route("/delete_subject/<int:id>")
def delete_subject(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM subjects WHERE subject_id=%s",
        (id,)
    )
    connection.commit()

    return redirect("/subjects")


# ---------------- ATTENDANCE ----------------

@app.route("/attendance")
def attendance():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            attendance.attendance_id,
            students.name,
            subjects.subject_name,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        INNER JOIN students
            ON attendance.student_id = students.student_id
        INNER JOIN subjects
            ON attendance.subject_id = subjects.subject_id
        ORDER BY attendance.attendance_id
    """)
    attendance_records = cursor.fetchall()

    return render_template(
        "attendance.html",
        attendance=attendance_records
    )


# ---------------- ADD ATTENDANCE ----------------

@app.route("/add_attendance", methods=["GET", "POST"])
def add_attendance():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":
        department = request.form["department"]
        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute("""
            INSERT INTO attendance
            (student_id, subject_id, department, attendance_date, status)
            VALUES (%s,%s,%s,%s,%s)
        """,
        (
            student_id,
            subject_id,
            department,
            attendance_date,
            status
        ))
        connection.commit()

        return redirect("/attendance")

    # Students with Department
    cursor.execute("""
        SELECT
            student_id,
            name,
            department
        FROM students
        ORDER BY department, name
    """)
    students = cursor.fetchall()

    # Subjects with Department
    cursor.execute("""
        SELECT
            subject_id,
            subject_name,
            department
        FROM subjects
        ORDER BY department, subject_name
    """)
    subjects = cursor.fetchall()

    return render_template(
        "add_attendance.html",
        students=students,
        subjects=subjects
    )


# ---------------- EDIT ATTENDANCE ----------------

@app.route("/edit_attendance/<int:id>", methods=["GET", "POST"])
def edit_attendance(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":
        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute("""
        UPDATE attendance
        SET
            student_id=%s,
            subject_id=%s,
            attendance_date=%s,
            status=%s
        WHERE attendance_id=%s
        """,
        (
            student_id,
            subject_id,
            attendance_date,
            status,
            id
        ))
        connection.commit()

        return redirect("/attendance")

    cursor.execute("SELECT * FROM attendance WHERE attendance_id=%s", (id,))
    attendance_record = cursor.fetchone()

    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT subject_id, subject_name FROM subjects")
    subjects = cursor.fetchall()

    return render_template(
        "edit_attendance.html",
        attendance=attendance_record,
        students=students,
        subjects=subjects
    )


# ---------------- DELETE ATTENDANCE ----------------

@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM attendance WHERE attendance_id=%s",
        (id,)
    )
    connection.commit()

    return redirect("/attendance")


# ---------------- REPORTS ----------------

@app.route("/reports")
def reports():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    total_faculty = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    return render_template(
        "reports.html",
        total_students=total_students,
        total_faculty=total_faculty,
        total_attendance=total_attendance
    )


# ---------------- PREDICTION ----------------

@app.route("/prediction")
def prediction():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            students.name,
            COUNT(attendance.attendance_id) AS total_classes,
            SUM(
                CASE
                    WHEN attendance.status='Present'
                    THEN 1
                    ELSE 0
                END
            ) AS present
        FROM students
        LEFT JOIN attendance
        ON students.student_id = attendance.student_id
        GROUP BY students.student_id
    """)
    data = cursor.fetchall()

    predictions = []

    for row in data:
        name = row[0]
        total = row[1]
        present = row[2] if row[2] else 0

        if total == 0:
            percentage = 0
        else:
            percentage = round((present / total) * 100, 2)

        if percentage >= 85:
            result = "Excellent"
        elif percentage >= 75:
            result = "Good"
        elif percentage >= 65:
            result = "Average"
        else:
            result = "Low Attendance"

        predictions.append((name, percentage, result))

    return render_template(
        "prediction.html",
        prediction=predictions
    )


# ---------------- PDF EXPORT ----------------

@app.route("/export_students_pdf")
def export_students_pdf():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
        roll_no,
        name,
        department,
        semester,
        section
        FROM students
    """)
    data = cursor.fetchall()

    filename = "Student_Report.pdf"
    pdf = SimpleDocTemplate(filename)

    table_data = [["Roll No", "Name", "Department", "Semester", "Section"]]

    for row in data:
        table_data.append(list(row))

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.blue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("ALIGN", (0,0), (-1,-1), "CENTER")
    ]))

    pdf.build([table])

    return send_file(filename, as_attachment=True)


# ---------------- EXCEL EXPORT ----------------

@app.route("/export_students_excel")
def export_students_excel():
    if "username" not in session:
        return redirect("/login")

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
        roll_no,
        name,
        department,
        semester,
        section
        FROM students
    """)
    data = cursor.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    ws.append([
        "Roll No",
        "Name",
        "Department",
        "Semester",
        "Section"
    ])

    for row in data:
        ws.append(row)

    filename = "Student_Report.xlsx"
    wb.save(filename)

    return send_file(filename, as_attachment=True)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True)