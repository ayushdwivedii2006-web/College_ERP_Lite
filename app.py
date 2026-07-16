from flask import Flask, render_template, request, redirect, url_for, session, Response
import sqlite3
import os
import glob
import traceback
from datetime import datetime
attendance_session = ""
attendance_course = ""
attendance_semester = ""
attendance_section = ""
attendance_subject = ""

from werkzeug.utils import secure_filename
import cv2
from deepface import DeepFace
app = Flask(__name__)


app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "college_erp_secret"


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("college.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )

        admin = cursor.fetchone()

        connection.close()

        if admin:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "❌ Invalid Username or Password"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Courses
    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]

    # Today's Attendance
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE attendance_date=?",
        (today,)
    )
    today_attendance = cursor.fetchone()[0]

    # Total Fees Collected
    cursor.execute("SELECT SUM(paid_fee) FROM fees")
    total_fees = cursor.fetchone()[0]

    if total_fees is None:
        total_fees = 0

    # Pending Fees
    cursor.execute("SELECT SUM(remaining_fee) FROM fees")
    pending_fees = cursor.fetchone()[0]

    if pending_fees is None:
        pending_fees = 0

    connection.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        today_attendance=today_attendance,
        total_fees=total_fees,
        pending_fees=pending_fees
    )


# ---------------- STUDENTS ----------------
# ---------------- STUDENTS ----------------
@app.route("/students", methods=["GET", "POST"])
def students():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # ---------------- ADD STUDENT ----------------
    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        course = request.form["course"]
        mobile = request.form["mobile"]
        email = request.form["email"]

        photo = request.files["photo"]

        filename = ""

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cursor.execute("""
            INSERT INTO students
            (name, roll, course, mobile, email, photo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            roll,
            course,
            mobile,
            email,
            filename
        ))

        connection.commit()

    # ---------------- SEARCH ----------------
    search = request.args.get("search")

    if search:

        cursor.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR roll LIKE ?
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("SELECT * FROM students")

    students_data = cursor.fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=students_data
    )

    # SEARCH
    search = request.args.get("search")

    if search:

        cursor.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR roll LIKE ?
        """, ('%' + search + '%', '%' + search + '%'))

    else:

        cursor.execute("SELECT * FROM students")

    students_data = cursor.fetchall()

    connection.close()

    return render_template("students.html", students=students_data)


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete_student(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))

    connection.commit()
    connection.close()

    return redirect("/students")


# ---------------- EDIT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        course = request.form["course"]
        mobile = request.form["mobile"]
        email = request.form["email"]

        # Photo Upload
        photo = request.files["photo"]

        if photo and photo.filename != "":

            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            cursor.execute("""
                UPDATE students
                SET name=?, roll=?, course=?, mobile=?, email=?, photo=?
                WHERE id=?
            """, (
                name,
                roll,
                course,
                mobile,
                email,
                filename,
                id
            ))

        else:

            cursor.execute("""
                UPDATE students
                SET name=?, roll=?, course=?, mobile=?, email=?
                WHERE id=?
            """, (
                name,
                roll,
                course,
                mobile,
                email,
                id
            ))

        connection.commit()
        connection.close()

        return redirect("/students")

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    connection.close()

    return render_template("edit_student.html", student=student)
# ---------------- VIEW STUDENT ----------------
@app.route("/student/<int:id>")
def view_student(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    connection.close()

    return render_template(
        "student_profile.html",
        student=student
    )


# ---------------- CHANGE ADMIN ----------------
@app.route("/change-admin", methods=["GET", "POST"])
def change_admin():

    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        new_username = request.form["username"]
        new_password = request.form["password"]

        connection = sqlite3.connect("college.db")
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE admin SET username=?, password=? WHERE id=1",
            (new_username, new_password)
        )

        connection.commit()
        connection.close()

        session.clear()

        return """
        <h2>✅ Username & Password Updated Successfully</h2>
        <a href="/">Login Again</a>
        """

    return render_template("change_admin.html")

# ---------------- COURSES ----------------
@app.route("/courses", methods=["GET", "POST"])
def courses():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # ADD COURSE
    if request.method == "POST":

        course_name = request.form["course_name"]
        course_code = request.form["course_code"]
        duration = request.form["duration"]
        fees = request.form["fees"]

        cursor.execute("""
            INSERT INTO courses(course_name, course_code, duration, fees)
            VALUES (?, ?, ?, ?)
        """, (course_name, course_code, duration, fees))

        connection.commit()

    # SEARCH
    search = request.args.get("search")

    if search:

        cursor.execute("""
            SELECT * FROM courses
            WHERE course_name LIKE ? OR course_code LIKE ?
        """, ('%' + search + '%', '%' + search + '%'))

    else:

        cursor.execute("SELECT * FROM courses")

    courses_data = cursor.fetchall()

    connection.close()

    return render_template("courses.html", courses=courses_data)

# ---------------- DELETE COURSE ----------------
@app.route("/delete-course/<int:id>")
def delete_course(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM courses WHERE id=?", (id,))

    connection.commit()
    connection.close()

    return redirect("/courses")

# ---------------- EDIT COURSE ----------------
@app.route("/edit-course/<int:id>", methods=["GET", "POST"])
def edit_course(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        course_name = request.form["course_name"]
        course_code = request.form["course_code"]
        duration = request.form["duration"]
        fees = request.form["fees"]

        cursor.execute("""
            UPDATE courses
            SET course_name=?, course_code=?, duration=?, fees=?
            WHERE id=?
        """, (course_name, course_code, duration, fees, id))

        connection.commit()
        connection.close()

        return redirect("/courses")

    cursor.execute("SELECT * FROM courses WHERE id=?", (id,))
    course = cursor.fetchone()

    connection.close()

    return render_template("edit_course.html", course=course)
# ---------------- FEES ----------------
@app.route("/fees", methods=["GET", "POST"])
def fees():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # ADD FEES
    if request.method == "POST":

        student_name = request.form["student_name"]
        roll = request.form["roll"]
        total_fee = int(request.form["total_fee"])
        paid_fee = int(request.form["paid_fee"])

        remaining_fee = total_fee - paid_fee

        cursor.execute("""
            INSERT INTO fees(student_name, roll, total_fee, paid_fee, remaining_fee)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_name,
            roll,
            total_fee,
            paid_fee,
            remaining_fee
        ))

        connection.commit()

    # SEARCH
    search = request.args.get("search")

    if search:

        cursor.execute("""
            SELECT * FROM fees
            WHERE student_name LIKE ? OR roll LIKE ?
        """, (
            '%' + search + '%',
            '%' + search + '%'
        ))

    else:

        cursor.execute("SELECT * FROM fees")

    fees_data = cursor.fetchall()

    connection.close()

    return render_template(
        "fees.html",
        fees=fees_data
    )
# ---------------- DELETE FEE ----------------
@app.route("/delete-fee/<int:id>")
def delete_fee(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM fees WHERE id=?", (id,))

    connection.commit()
    connection.close()

    return redirect("/fees")
# ---------------- EDIT FEE ----------------
@app.route("/edit-fee/<int:id>", methods=["GET", "POST"])
def edit_fee(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        student_name = request.form["student_name"]
        roll = request.form["roll"]
        total_fee = int(request.form["total_fee"])
        paid_fee = int(request.form["paid_fee"])

        remaining_fee = total_fee - paid_fee

        cursor.execute("""
            UPDATE fees
            SET student_name=?, roll=?, total_fee=?, paid_fee=?, remaining_fee=?
            WHERE id=?
        """, (
            student_name,
            roll,
            total_fee,
            paid_fee,
            remaining_fee,
            id
        ))

        connection.commit()
        connection.close()

        return redirect("/fees")

    cursor.execute("SELECT * FROM fees WHERE id=?", (id,))
    fee = cursor.fetchone()

    connection.close()

    return render_template("edit_fee.html", fee=fee)
# ---------------- ATTENDANCE ----------------
# ---------------- ATTENDANCE ----------------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # ADD ATTENDANCE
    if request.method == "POST":

        student_name = request.form["student_name"]
        roll = request.form["roll"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute("""
            INSERT INTO attendance
            (student_name, roll, attendance_date, status)
            VALUES (?, ?, ?, ?)
        """, (
            student_name,
            roll,
            attendance_date,
            status
        ))

        connection.commit()

    # SEARCH
    search = request.args.get("search")

    if search:

        cursor.execute("""
            SELECT * FROM attendance
            WHERE student_name LIKE ? OR roll LIKE ?
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("SELECT * FROM attendance")

    attendance_data = cursor.fetchall()

    connection.close()

    return render_template(
        "attendance.html",
        attendance=attendance_data
    )
@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        course = request.form["course"]
        semester = request.form["semester"]
        subject_name = request.form["subject_name"]
        subject_code = request.form["subject_code"]

        # Duplicate Check
        cursor.execute(
            """
            SELECT id
            FROM subjects
            WHERE
                course=?
                AND semester=?
                AND subject_name=?
            """,
            (
                course,
                semester,
                subject_name
            )
        )

        already = cursor.fetchone()

        if already is None:

            cursor.execute(
    """
    INSERT INTO subjects(

        subject_name,
        subject_code,
        course,
        semester

    )

    VALUES(?,?,?,?)

    """,
    (

        subject_name,
        subject_code,
        course,
        semester

    )
)

            connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM subjects
        ORDER BY course, semester, subject_name
        """
    )

    subjects = cursor.fetchall()

    connection.close()

    return render_template(
        "subjects.html",
        subjects=subjects
    )


# ---------------- DELETE ATTENDANCE ----------------
@app.route("/delete-attendance/<int:id>")
def delete_attendance(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM attendance WHERE id=?", (id,))

    connection.commit()
    connection.close()

    return redirect("/attendance")


# ---------------- EDIT ATTENDANCE ----------------
@app.route("/edit-attendance/<int:id>", methods=["GET", "POST"])
def edit_attendance(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        student_name = request.form["student_name"]
        roll = request.form["roll"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE attendance
            SET student_name=?, roll=?, attendance_date=?, status=?
            WHERE id=?
        """, (
            student_name,
            roll,
            attendance_date,
            status,
            id
        ))

        connection.commit()
        connection.close()

        return redirect("/attendance")

    cursor.execute("SELECT * FROM attendance WHERE id=?", (id,))
    attendance = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_attendance.html",
        attendance=attendance
    )
# ---------------- AI FACE RECOGNITION ----------------
# ---------------- AI FACE RECOGNITION ----------------
def recognize_student(image_path):

    photos = glob.glob("static/uploads/*")

    best_match = None
    best_distance = 1

    for photo in photos:

        try:

            result = DeepFace.verify(
                img1_path=image_path,
                img2_path=photo,
                model_name="Facenet",
                detector_backend="opencv",
                enforce_detection=False
            )

            print("--------------------------------")
            print("Photo :", photo)
            print("Verified :", result["verified"])
            print("Distance :", result["distance"])

            if result["verified"] and result["distance"] < best_distance:

               best_distance = result["distance"]
               best_match = photo

        except Exception as e:
            print("DeepFace Error:")
            traceback.print_exc()    
     
    if best_match is not None and best_distance < 0.55:

        filename = os.path.basename(best_match)

        connection = sqlite3.connect("college.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT name, roll FROM students WHERE photo=?",
            (filename,)
        )

        student = cursor.fetchone()

        connection.close()

        print("MATCH FOUND :", student)

        return student

    print("NO MATCH")

    return None
# Camera
def generate_frames():

    # Camera yahin open hoga
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    last_student = ""
    last_detected_student = None
    frame_count = 0

    while True:

        success, frame = camera.read()

        if not success:
            continue

        frame_count += 1

        # Har 15 frame ke baad AI chalega
        if frame_count % 15 == 0:

            cv2.imwrite("temp.jpg", frame)

            print("Scanning Face...")

            try:

                student = recognize_student("temp.jpg")

            except Exception as e:

                print("AI Error :", e)
                student = None

            if student:

                last_detected_student = student

            else:

                last_detected_student = None
        # ---------------- FACE DETECTED ----------------
        # ---------------- FACE DETECTED ----------------
        # ---------------- FACE DETECTED ----------------

        if last_detected_student:

            name = last_detected_student[0]
            roll = last_detected_student[1]

            cv2.rectangle(
                frame,
                (20, 20),
                (450, 90),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"{name} ({roll})",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            if last_student != roll:

                print("Saving Attendance...", name, roll)

                connection = sqlite3.connect("college.db")
                cursor = connection.cursor()

                today = datetime.now().strftime("%Y-%m-%d")
                current_time = datetime.now().strftime("%I:%M:%S %p")

                session_name = attendance_session
                course = attendance_course
                semester = attendance_semester
                section = attendance_section
                subject = attendance_subject

                cursor.execute(
                    """
                    SELECT id
                    FROM attendance
                    WHERE roll=? AND attendance_date=?
                    """,
                    (roll, today)
                )

                already = cursor.fetchone()

                if already is None:

                    cursor.execute(
                        """
                        INSERT INTO attendance(

                            student_name,
                            roll,
                            session,
                            course,
                            semester,
                            section,
                            subject,
                            attendance_date,
                            attendance_time,
                            status

                        )

                        VALUES(?,?,?,?,?,?,?,?,?,?)

                        """,
                        (

                            name,
                            roll,
                            session_name,
                            course,
                            semester,
                            section,
                            subject,
                            today,
                            current_time,
                            "Present"

                        )
                    )

                    connection.commit()

                    print("✅ Attendance Saved Successfully")

                else:

                    print("⚠ Attendance Already Marked")

                connection.close()

                last_student = roll


            else:

                cv2.rectangle(
                    frame,
                    (20, 20),
                    (320, 90),
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Unknown",
                    (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            ret, buffer = cv2.imencode(".jpg", frame)

            frame = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                frame +
                b'\r\n'
            )


@app.route("/video")
def video():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

    
        # ---------------- UNKNOWN ----------------

#                        camera
@app.route("/camera", methods=["GET", "POST"])
def camera_page():

    global attendance_session
    global attendance_course
    global attendance_semester
    global attendance_section
    global attendance_subject

    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        attendance_session = request.form["session"]

        attendance_course = request.form["course"]

        attendance_semester = request.form["semester"]

        attendance_section = request.form["section"]

        attendance_subject = request.form["subject"]

        print("========== AI ATTENDANCE ==========")
        print("Session :", attendance_session)
        print("Course :", attendance_course)
        print("Semester :", attendance_semester)
        print("Section :", attendance_section)
        print("Subject :", attendance_subject)
        print("===================================")

    return render_template(
        "camera.html",
        session_name=attendance_session,
        course=attendance_course,
        semester=attendance_semester,
        section=attendance_section,
        subject=attendance_subject
    )     


# ---------------- RESULTS ----------------
@app.route("/results", methods=["GET", "POST"])
def results():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # ---------------- POST ----------------

    if request.method == "POST":

        student_name = request.form["student_name"]
        roll = request.form["roll"]
        course = request.form["course"]

        subjects = request.form.getlist("subject[]")
        marks = request.form.getlist("marks[]")
        total_marks = request.form.getlist("total_marks[]")

        obtained_total = 0
        maximum_total = 0

        for i in range(len(subjects)):

            obtained_total += int(marks[i])
            maximum_total += int(total_marks[i])

        percentage = (obtained_total / maximum_total) * 100

        if percentage >= 90:
            grade = "A+"

        elif percentage >= 80:
            grade = "A"

        elif percentage >= 70:
            grade = "B"

        elif percentage >= 60:
            grade = "C"

        elif percentage >= 40:
            grade = "D"

        else:
            grade = "F"

        result = "PASS" if percentage >= 40 else "FAIL"

        cursor.execute(
            """
            INSERT INTO results
            (
                student_name,
                roll,
                course,
                obtained_marks,
                total_marks,
                percentage,
                grade,
                result
            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                student_name,
                roll,
                course,
                obtained_total,
                maximum_total,
                percentage,
                grade,
                result
            )
        )

        result_id = cursor.lastrowid

        for i in range(len(subjects)):

            cursor.execute(
                """
                INSERT INTO result_subjects
                (
                    result_id,
                    subject_name,
                    marks,
                    max_marks
                )
                VALUES(?,?,?,?)
                """,
                (
                    result_id,
                    subjects[i],
                    int(marks[i]),
                    int(total_marks[i])
                )
            )

        connection.commit()

    # ---------------- STUDENTS ----------------

    cursor.execute("""
        SELECT name, roll, course
        FROM students
        ORDER BY name
    """)

    students = cursor.fetchall()

    # ---------------- SUBJECTS ----------------

    cursor.execute("""
        SELECT *
        FROM subjects
        ORDER BY course, semester
    """)

    all_subjects = cursor.fetchall()

    # ---------------- SEARCH ----------------

    search = request.args.get("search")

    if search:

        cursor.execute(
            """
            SELECT *
            FROM results
            WHERE student_name LIKE ?
            OR roll LIKE ?
            """,
            (
                "%" + search + "%",
                "%" + search + "%"
            )
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM results
            ORDER BY id DESC
            """
        )

    results_data = cursor.fetchall()

    connection.close()

    return render_template(
        "results.html",
        results=results_data,
        students=students,
        subjects=all_subjects
    )
# ---------------- DELETE RESULT ----------------
@app.route("/delete-result/<int:id>")
def delete_result(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM results WHERE id=?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/results")

# ---------------- EDIT RESULT ----------------
@app.route("/edit-result/<int:id>", methods=["GET", "POST"])
def edit_result(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        student_name = request.form["student_name"]
        roll = request.form["roll"]
        subject = request.form["subject"]

        marks = int(request.form["marks"])
        total_marks = int(request.form["total_marks"])

        percentage = (marks / total_marks) * 100

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 40:
            grade = "D"
        else:
            grade = "F"

        cursor.execute("""
            UPDATE results
            SET student_name=?,
                roll=?,
                subject=?,
                marks=?,
                total_marks=?,
                percentage=?,
                grade=?
            WHERE id=?
        """, (
            student_name,
            roll,
            subject,
            marks,
            total_marks,
            percentage,
            grade,
            id
        ))

        connection.commit()
        connection.close()

        return redirect("/results")

    cursor.execute(
        "SELECT * FROM results WHERE id=?",
        (id,)
    )

    result = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_result.html",
        result=result
    )

@app.route("/student-profile/<roll>")
def student_profile(roll):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # Student Details
    cursor.execute(
        "SELECT * FROM students WHERE roll=?",
        (roll,)
    )
    student = cursor.fetchone()

    # Fees
    cursor.execute(
        "SELECT * FROM fees WHERE roll=?",
        (roll,)
    )
    fees = cursor.fetchone()

    # Attendance
    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE roll=?",
        (roll,)
    )
    attendance = cursor.fetchone()[0]

    # Latest Result
    cursor.execute(
        "SELECT * FROM results WHERE roll=? ORDER BY id DESC LIMIT 1",
        (roll,)
    )
    result = cursor.fetchone()

    connection.close()

    return render_template(
        "student_profile.html",
        student=student,
        fees=fees,
        attendance=attendance,
        result=result
    )

# ---------------- VIEW RESULT ----------------
@app.route("/view-result/<int:id>")
def view_result(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    # Result
    cursor.execute(
        "SELECT * FROM results WHERE id=?",
        (id,)
    )
    result = cursor.fetchone()

    # Subject Details
    cursor.execute(
        """
        SELECT subject_name, marks, max_marks
        FROM result_subjects
        WHERE result_id=?
        """,
        (id,)
    )
    subjects = cursor.fetchall()

    # Student Photo
    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE roll=?
        """,
        (result[2],)
    )
    student = cursor.fetchone()

    # College Details
    cursor.execute(
        """
        SELECT *
        FROM college_settings
        WHERE id=1
        """
    )
    college = cursor.fetchone()

    connection.close()

    return render_template(
        "view_result.html",
        result=result,
        subjects=subjects,
        student=student,
        college=college
    )

    # ---------------- MAIN RESULT ----------------
    cursor.execute(
        "SELECT * FROM results WHERE id=?",
        (id,)
    )

    result = cursor.fetchone()

    # ---------------- SUBJECTS ----------------
    cursor.execute(
        """
        SELECT subject_name, marks, max_marks
        FROM result_subjects
        WHERE result_id=?
        """,
        (id,)
    )
    # ---------------- EDIT SUBJECT ----------------

@app.route("/edit-subject/<int:id>", methods=["GET", "POST"])
def edit_subject(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        subject_name = request.form["subject_name"]
        subject_code = request.form["subject_code"]
        course = request.form["course"]
        semester = request.form["semester"]

        cursor.execute(
            """
            UPDATE subjects

            SET

                subject_name=?,
                subject_code=?,
                course=?,
                semester=?

            WHERE id=?
            """,
            (
                subject_name,
                subject_code,
                course,
                semester,
                id
            )
        )

        connection.commit()

        connection.close()

        return redirect("/subjects")

    cursor.execute(
        "SELECT * FROM subjects WHERE id=?",
        (id,)
    )

    subject = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_subject.html",
        subject=subject
    )


# ---------------- DELETE SUBJECT ----------------

@app.route("/delete-subject/<int:id>")
def delete_subject(id):

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM subjects WHERE id=?",
        (id,)
    )

    connection.commit()

    connection.close()

    return redirect("/subjects")

    subjects = cursor.fetchall()

    # ---------------- STUDENT ----------------
    cursor.execute(
        "SELECT * FROM students WHERE roll=?",
        (result[2],)
    )

    student = cursor.fetchone()

    # ---------------- COLLEGE SETTINGS ----------------
    cursor.execute(
        "SELECT * FROM college_settings"
    )

    college = cursor.fetchone()

    connection.close()

    return render_template(
        "view_result.html",
        result=result,
        subjects=subjects,
        student=student,
        college=college
    )
# ---------------- COLLEGE SETTINGS ----------------
@app.route("/college-settings", methods=["GET", "POST"])
def college_settings():

    if "user" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("college.db")
    cursor = connection.cursor()

    if request.method == "POST":

        college_name = request.form["college_name"]
        address = request.form["address"]
        phone = request.form["phone"]
        email = request.form["email"]
        website = request.form["website"]
        principal_name = request.form["principal_name"]

        logo = ""

        if "logo" in request.files:

            file = request.files["logo"]

            if file.filename != "":

                filename = secure_filename(file.filename)

                file.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

                logo = filename

        cursor.execute("""
        UPDATE college_settings
        SET
            college_name=?,
            address=?,
            phone=?,
            email=?,
            website=?,
            principal_name=?,
            logo=CASE
                    WHEN ?='' THEN logo
                    ELSE ?
                 END
        WHERE id=1
        """, (

            college_name,
            address,
            phone,
            email,
            website,
            principal_name,
            logo,
            logo

        ))

        connection.commit()

    cursor.execute("SELECT * FROM college_settings")

    college = cursor.fetchone()

    connection.close()

    return render_template(
        "college_settings.html",
        college=college
    )
        


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

print(app.url_map)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=False)