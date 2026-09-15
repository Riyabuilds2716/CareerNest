
from flask import Flask, render_template, request, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "jobportal_admin_secret"


# =========================
# Database Setup
# =========================

def create_database():

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    # Applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            cover_message TEXT
        )
    """)

    # Contact Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    # Job Seekers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_seekers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            qualification TEXT NOT NULL,
            skills TEXT
        )
    """)

    # Jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            skills TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# Add Default Jobs
# =========================

def seed_jobs():

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    default_jobs = [

        (
            "Python Developer",
            "Tech Solutions",
            "Mumbai",
            "Python, Flask, SQL",
            "Develop and maintain Python-based web applications."
        ),

        (
            "Web Developer",
            "Web Works",
            "Mumbai",
            "HTML, CSS, JavaScript",
            "Create and maintain responsive websites."
        ),

        (
            "Data Entry Operator",
            "Data Services",
            "Pune",
            "Excel, Typing, MS Office",
            "Manage and maintain digital data records."
        ),

        (
            "Software Tester",
            "Quality Tech",
            "Mumbai",
            "Testing, SQL, Manual Testing",
            "Test software applications and identify bugs."
        ),

        (
            "Graphic Designer",
            "Creative Studio",
            "Pune",
            "Photoshop, Canva, Illustrator",
            "Design graphics and visual content."
        ),

        (
            "Digital Marketing Intern",
            "Digital World",
            "Mumbai",
            "SEO, Social Media, Marketing",
            "Assist with digital marketing campaigns."
        ),

        (
            "Frontend Developer",
            "Tech World",
            "Mumbai",
            "HTML, CSS, JavaScript",
            "Build attractive and responsive frontend interfaces."
        ),

        (
            "Database Assistant",
            "Database Solutions",
            "Pune",
            "SQL, MySQL, DBMS",
            "Assist with database management and records."
        ),

        (
            "Java Developer",
            "Software Hub",
            "Mumbai",
            "Java, OOP, SQL",
            "Develop and maintain Java applications."
        ),

        (
            "C++ Developer",
            "Code Masters",
            "Mumbai",
            "C++, OOP, DSA",
            "Develop software using C++ programming."
        ),

        (
            "SQL Developer",
            "DataTech",
            "Pune",
            "SQL, MySQL, Database",
            "Create and manage database queries."
        ),

        (
            "Python Intern",
            "Innovate Labs",
            "Mumbai",
            "Python, Django, SQL",
            "Assist developers in Python-based projects."
        ),

        (
            "UI/UX Designer",
            "Design Studio",
            "Mumbai",
            "Figma, UI Design, UX",
            "Design user-friendly website interfaces."
        ),

        (
            "Content Writer",
            "Media Works",
            "Pune",
            "Writing, SEO, Research",
            "Create website and marketing content."
        ),

        (
            "SEO Executive",
            "Digital Growth",
            "Mumbai",
            "SEO, Google Analytics, Marketing",
            "Improve website visibility through SEO."
        ),

        (
            "HR Intern",
            "Corporate Solutions",
            "Mumbai",
            "Communication, MS Office, HR",
            "Assist the HR team with recruitment activities."
        ),

        (
            "Business Analyst Intern",
            "Business Tech",
            "Pune",
            "Excel, SQL, Analysis",
            "Assist with business data and reporting."
        ),

        (
            "Backend Developer",
            "Server Solutions",
            "Mumbai",
            "Python, Flask, SQL",
            "Develop backend services and APIs."
        ),

        (
            "Full Stack Developer",
            "Digital Technologies",
            "Mumbai",
            "HTML, CSS, JavaScript, Python, SQL",
            "Work on both frontend and backend development."
        ),

        (
            "Technical Support Executive",
            "IT Support Services",
            "Pune",
            "Networking, Communication, Troubleshooting",
            "Provide technical assistance to users."
        )
    ]

    # Add only jobs that are not already present
    for job in default_jobs:

        cursor.execute(
            "SELECT id FROM jobs WHERE name = ?",
            (job[0],)
        )

        existing_job = cursor.fetchone()

        if existing_job is None:

            cursor.execute("""
                INSERT INTO jobs
                (name, company, location, skills, description)
                VALUES (?, ?, ?, ?, ?)
            """, job)

    conn.commit()
    conn.close()


create_database()
seed_jobs()


# =========================
# Home Page
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# Jobs + Search
# =========================

@app.route("/jobs")
def jobs():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip().lower()

    location = request.args.get(
        "location",
        ""
    ).strip().lower()

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM jobs
        ORDER BY id DESC
    """)

    all_jobs = cursor.fetchall()

    conn.close()

    filtered_jobs = []

    for job in all_jobs:

        keyword_match = (
            keyword == ""
            or keyword in job["name"].lower()
            or keyword in job["company"].lower()
            or keyword in job["skills"].lower()
        )

        location_match = (
            location == ""
            or location in job["location"].lower()
        )

        if keyword_match and location_match:

            filtered_jobs.append(job)

    return render_template(
        "jobs.html",
        jobs=filtered_jobs,
        keyword=keyword,
        location=location
    )


# =========================
# Job Details
# =========================

@app.route("/job-details/<job_name>")
def job_details(job_name):

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM jobs
        WHERE name = ?
    """, (job_name,))

    job = cursor.fetchone()

    conn.close()

    if job is None:

        return """
        <h2>Job Not Found</h2>
        <a href="/jobs">Back to Jobs</a>
        """

    return render_template(
        "job_details.html",
        job_name=job["name"],
        company=job["company"],
        location=job["location"],
        skills=job["skills"],
        description=job["description"]
    )


# =========================
# Apply for Job
# =========================

@app.route("/apply/<job_name>", methods=["GET", "POST"])
def apply(job_name):

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        cover_message = request.form["cover_message"]

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO applications
            (job_name, full_name, email, phone, cover_message)
            VALUES (?, ?, ?, ?, ?)
        """, (
            job_name,
            full_name,
            email,
            phone,
            cover_message
        ))

        conn.commit()
        conn.close()

        return render_template(
            "apply_success.html"
        )

    return render_template(
        "apply.html",
        job_name=job_name
    )
# =========================
# Manage Applications
# =========================

@app.route("/manage-applications")
def manage_applications():

    if not session.get("admin_logged_in"):
        return """
        <h2>Access Denied</h2>
        <p>Please login as admin first.</p>
        <a href="/admin-login">Admin Login</a>
        """

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM applications
        ORDER BY id DESC
    """)

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_applications.html",
        applications=applications
    )


# =========================
# Job Seeker Registration
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"].strip()
        phone = request.form["phone"]
        password = request.form["password"]
        qualification = request.form["qualification"]
        skills = request.form.get("skills", "")

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO job_seekers
                (full_name, email, phone, password, qualification, skills)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                full_name,
                email,
                phone,
                hashed_password,
                qualification,
                skills
            ))

            conn.commit()
            conn.close()

            return render_template(
                "registration_success.html"
            )

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <h2>Email Already Registered</h2>
            <p>This email is already registered. Please use another email.</p>
            <a href="/register">Back to Registration</a>
            """

    return render_template("register.html")


# =========================
# Job Seeker Login
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, full_name, password
            FROM job_seekers
            WHERE email = ?
        """, (email,))

        user = cursor.fetchone()

        conn.close()

        if user is None:

            return """
            <h2>Login Failed</h2>
            <p>No account found with this email.</p>
            <a href="/login">Try Again</a>
            """

        if check_password_hash(
            user[2],
            password
        ):

            session["job_seeker_id"] = user[0]
            session["job_seeker_name"] = user[1]

            return render_template(
                "login_success.html",
                name=user[1]
            )

        return """
        <h2>Login Failed</h2>
        <p>Incorrect password.</p>
        <a href="/login">Try Again</a>
        """

    return render_template("login.html")


# =========================
# About Page
# =========================

@app.route("/about")
def about():

    return render_template("about.html")


# =========================
# Help & Contact
# =========================

@app.route("/help", methods=["GET", "POST"])
def help():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages
            (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            subject,
            message
        ))

        conn.commit()
        conn.close()

        return render_template(
            "contact_success.html"
        )

    return render_template("help.html")


# =========================
# Admin Login
# =========================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            return render_template(
                "admin_login_success.html"
            )

        return """
        <h2>Invalid Admin Login</h2>
        <p>Username or password is incorrect.</p>
        <a href="/admin-login">Try Again</a>
        """

    return render_template(
        "admin_login.html" 
    )


# =========================
# Admin Dashboard
# =========================

@app.route("/admin")
def admin():

    if not session.get(
        "admin_logged_in"
    ):

        return """
        <h2>Access Denied</h2>
        <p>Please login as admin first.</p>
        <a href="/admin-login">Admin Login</a>
        """

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM jobs"
    )

    job_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications"
    )

    application_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM job_seekers"
    )

    seeker_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM messages"
    )

    message_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        job_count=job_count,
        application_count=application_count,
        seeker_count=seeker_count,
        message_count=message_count
    )


# =========================
# Manage Jobs
# =========================

@app.route("/manage-jobs")
def manage_jobs():

    if not session.get(
        "admin_logged_in"
    ):

        return """
        <h2>Access Denied</h2>
        <p>Please login as admin first.</p>
        <a href="/admin-login">Admin Login</a>
        """

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM jobs
        ORDER BY id DESC
    """)

    jobs_list = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_jobs.html",
        jobs=jobs_list
    )


# =========================
# Admin Logout
# =========================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return """
    <h2>Admin Logged Out</h2>
    <a href="/admin-login">Admin Login</a>
    """

# =========================
# Manage Applications
# =========================

@app.route("/manage-applications")
def manage_applications():

    if not session.get("admin_logged_in"):
        return """
        <h2>Access Denied</h2>
        <p>Please login as admin first.</p>
        <a href="/admin-login">Admin Login</a>
        """

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM applications
        ORDER BY id DESC
    """)

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_applications.html",
        applications=applications
    )
# =========================
# Start Flask
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )
