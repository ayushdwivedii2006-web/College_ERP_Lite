import sqlite3

connection = sqlite3.connect("college.db")
cursor = connection.cursor()

# ---------------- STUDENTS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll TEXT UNIQUE,
    course TEXT,
    mobile TEXT,
    email TEXT,
    photo TEXT,
    face_encoding BLOB
)
""")

# ---------------- COURSES TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS courses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT,
    course_code TEXT,
    duration TEXT,
    fees TEXT
)
""")
# ---------------- SUBJECTS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    subject_name TEXT,

    subject_code TEXT,

    course TEXT,

    semester TEXT

)
""")

# ---------------- FEES TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS fees(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    roll TEXT,
    total_fee INTEGER,
    paid_fee INTEGER,
    remaining_fee INTEGER
)
""")

# ---------------- ATTENDANCE TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_name TEXT,

    roll TEXT,

    session TEXT,

    course TEXT,

    semester TEXT,

    section TEXT,

    subject TEXT,

    attendance_date TEXT,

    attendance_time TEXT,

    status TEXT

)
""")

# ---------------- RESULTS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    roll TEXT,
    course TEXT,
    obtained_marks INTEGER,
    total_marks INTEGER,
    percentage REAL,
    grade TEXT,
    result TEXT
)
""")

# ---------------- RESULT SUBJECTS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS result_subjects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER,
    subject_name TEXT,
    marks INTEGER,
    max_marks INTEGER,
    FOREIGN KEY(result_id) REFERENCES results(id)
)
""")

# ---------------- COLLEGE SETTINGS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS college_settings(

    id INTEGER PRIMARY KEY,

    college_name TEXT,

    address TEXT,

    phone TEXT,

    email TEXT,

    website TEXT,

    principal_name TEXT,

    logo TEXT

)
""")

# ---------------- ADMIN TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
""")

# ---------------- DEFAULT COLLEGE ----------------
cursor.execute("SELECT * FROM college_settings")

if cursor.fetchone() is None:

    cursor.execute("""
    INSERT INTO college_settings
    VALUES(
        1,
        'ABC College',
        'Your Address',
        '9999999999',
        'college@gmail.com',
        'www.college.com',
        'Principal',
        ''
    )
    """)

# ---------------- DEFAULT ADMIN ----------------
cursor.execute("SELECT * FROM admin")

if cursor.fetchone() is None:

    cursor.execute(
        "INSERT INTO admin VALUES(1,'admin','1234')"
    )

connection.commit()
connection.close()

print("✅ Database Ready Successfully")