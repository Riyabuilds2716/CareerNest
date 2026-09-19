
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = "jobportal_secret_key_2026"


# =========================================================
# APPEARANCE CONTEXT
# =========================================================

@app.context_processor
def inject_appearance():
    return {
        "appearance": session.get("appearance", "Light")
    }


# =========================================================
# GLOBAL THEME + STYLE.CSS
# =========================================================

@app.after_request
def apply_global_theme(response):

    if response.content_type and response.content_type.startswith("text/html"):

        html = response.get_data(as_text=True)

        if session.get("appearance") == "Dark":
            theme_class = "dark-mode"
        else:
            theme_class = "light-mode"

        import re

        body_match = re.search(
            r"<body\b([^>]*)>",
            html,
            re.IGNORECASE
        )

        if body_match:

            body_attributes = body_match.group(1)

            class_match = re.search(
                r'\bclass\s*=\s*(["\'])(.*?)\1',
                body_attributes,
                re.IGNORECASE
            )

            if class_match:

                classes = class_match.group(2).split()

                classes = [
                    c for c in classes
                    if c not in ["dark-mode", "light-mode"]
                ]

                classes.append(theme_class)

                new_attributes = (
                    body_attributes[:class_match.start(2)]
                    + " ".join(classes)
                    + body_attributes[class_match.end(2):]
                )

            else:

                new_attributes = (
                    body_attributes
                    + f' class="{theme_class}"'
                )

            new_body = "<body" + new_attributes + ">"

            html = (
                html[:body_match.start()]
                + new_body
                + html[body_match.end():]
            )

        if "/static/style.css" not in html:

            style_link = (
                '<link rel="stylesheet" '
                'href="/static/style.css">'
            )

            if re.search(
                r"</head>",
                html,
                re.IGNORECASE
            ):

                html = re.sub(
                    r"</head>",
                    style_link + "\n</head>",
                    html,
                    count=1,
                    flags=re.IGNORECASE
                )

        response.set_data(html)

    return response


# =========================================================
# DATABASE SETUP
# =========================================================

def init_db():

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

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
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [column[1] for column in cursor.fetchall()]


    if "approval_status" not in columns:
        cursor.execute(
            "ALTER TABLE jobs ADD COLUMN approval_status TEXT DEFAULT 'Approved'"
        )
    if "is_flagged" not in columns:
         cursor.execute(
        "ALTER TABLE jobs ADD COLUMN is_flagged INTEGER DEFAULT 0"
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            created_at TEXT
        )
    """)
    


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            cover_message TEXT,
            status TEXT DEFAULT 'Pending',
            applied_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_seekers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            qualification TEXT NOT NULL,
            skills TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    # =========================================================
# ACTIVITY LOGGER
# =========================================================

def log_activity(activity):

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    from datetime import datetime

    cursor.execute("""
        INSERT INTO activities (
            activity,
            created_at
        )
        VALUES (?, ?)
    """, (
        activity,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

 # =========================================================
# SEED ORIGINAL JOBS
# =========================================================

def seed_jobs():

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]

    if count == 0:

        jobs = [

            (
                "Technical Support Executive",
                "Tech Solutions",
                "Mumbai",
                "Technical Support, Communication",
                "Provide technical support and troubleshoot customer issues."
            ),

            (
                "Full Stack Developer",
                "WebTech Solutions",
                "Mumbai",
                "HTML, CSS, JavaScript, Python, Flask, SQL",
                "Develop complete web applications using frontend and backend technologies."
            ),

            (
                "Backend Developer",
                "CodeWorks",
                "Pune",
                "Python, Flask, SQL",
                "Develop and maintain backend services and APIs."
            ),

            (
                "Business Analyst Intern",
                "Business Solutions",
                "Mumbai",
                "Excel, SQL, Communication",
                "Assist in business analysis and prepare reports."
            ),

            (
                "HR Intern",
                "PeopleFirst",
                "Mumbai",
                "Communication, Excel, Recruitment",
                "Assist HR team with recruitment activities."
            ),

            (
                "SEO Executive",
                "Digital Growth",
                "Mumbai",
                "SEO, Google Analytics, Content",
                "Improve website visibility and search engine rankings."
            ),

            (
                "Content Writer",
                "Creative Media",
                "Mumbai",
                "Writing, Research, Communication",
                "Create engaging content for websites and digital platforms."
            ),

            (
                "UI/UX Designer",
                "Design Studio",
                "Pune",
                "Figma, UI Design, UX Research",
                "Design attractive and user-friendly digital interfaces."
            ),

            (
                "Python Intern",
                "Python Technologies",
                "Mumbai",
                "Python, Flask, SQL",
                "Assist developers in Python-based projects."
            ),

            (
                "SQL Developer",
                "Data Systems",
                "Pune",
                "SQL, Database, MySQL",
                "Create queries and manage database systems."
            ),

            (
                "C++ Developer",
                "Software Labs",
                "Mumbai",
                "C++, OOP, Data Structures",
                "Develop software applications using C++."
            ),

            (
                "Java Developer",
                "Java Technologies",
                "Mumbai",
                "Java, OOP, SQL",
                "Develop and maintain Java applications."
            ),

            (
                "Database Assistant",
                "Data Management",
                "Mumbai",
                "SQL, Database, Excel",
                "Assist with database management and data maintenance."
            ),

            (
                "Frontend Developer",
                "Frontend Solutions",
                "Mumbai",
                "HTML, CSS, JavaScript",
                "Build responsive and attractive web interfaces."
            ),

            (
                "Digital Marketing Intern",
                "Marketing Hub",
                "Mumbai",
                "Digital Marketing, SEO, Social Media",
                "Assist with digital marketing campaigns."
            ),

            (
                "Graphic Designer",
                "Creative Designs",
                "Pune",
                "Photoshop, Canva, Graphic Design",
                "Create graphics and visual content."
            ),

            (
                "Software Tester",
                "QualityTech",
                "Mumbai",
                "Manual Testing, Software Testing",
                "Test software applications and identify defects."
            ),

            (
                "Data Entry Operator",
                "Data Services",
                "Mumbai",
                "Typing, Excel, Data Entry",
                "Enter and maintain accurate data records."
            ),

            (
                "Web Developer",
                "Web Solutions",
                "Mumbai",
                "HTML, CSS, JavaScript, Python",
                "Develop and maintain modern websites."
            ),

            (
                "Python Developer",
                "Python Solutions",
                "Mumbai",
                "Python, Flask, SQL, APIs",
                "Develop Python applications and backend services."
            )

        ]

        cursor.executemany("""
            INSERT INTO jobs
            (
                name,
                company,
                location,
                skills,
                description
            )
            VALUES (?, ?, ?, ?, ?)
        """, jobs)

        conn.commit()

    conn.close()


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

init_db()
seed_jobs()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# JOBS PAGE + SEARCH
# =========================================================

@app.route("/jobs")
def jobs():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    if keyword and location:

        cursor.execute("""
            SELECT *
            FROM jobs
            WHERE
                (
                    name LIKE ?
                    OR skills LIKE ?
                    OR company LIKE ?
                )
                AND location LIKE ?
        """, (
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + location + "%"
        ))

    elif keyword:

        cursor.execute("""
            SELECT *
            FROM jobs
            WHERE
                name LIKE ?
                OR skills LIKE ?
                OR company LIKE ?
        """, (
            "%" + keyword + "%",
            "%" + keyword + "%",
            "%" + keyword + "%"
        ))

    elif location:

        cursor.execute("""
            SELECT *
            FROM jobs
            WHERE location LIKE ?
        """, (
            "%" + location + "%",
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM jobs
        """)

    jobs_list = cursor.fetchall()

    conn.close()

    return render_template(
        "jobs.html",
        jobs=jobs_list,
        keyword=keyword,
        location=location
    )
# =========================================================
# JOB DETAILS
# =========================================================

@app.route("/job/<job_name>")
def job_details(job_name):

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM jobs
        WHERE name = ?
    """, (job_name,))

    job = cursor.fetchone()

    conn.close()

    if not job:
        return "Job not found.", 404

    return render_template(
        "job_details.html",
        job=job
    )


# =========================================================
# VIEW JOB
# =========================================================

@app.route("/view-job/<int:job_id>")
def view_job(job_id):

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM jobs
        WHERE id = ?
    """, (job_id,))

    job = cursor.fetchone()

    conn.close()

    if not job:
        return "Job not found.", 404

    return render_template(
        "view_job.html",
        job=job
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():
    return render_template("about.html")


# =========================================================
# HELP & CONTACT
# =========================================================

@app.route("/help", methods=["GET", "POST"])
def help_contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages
            (
                name,
                email,
                subject,
                message
            )
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


# =========================================================
# JOB SEEKER REGISTRATION
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        qualification = request.form["qualification"]
        skills = request.form.get(
            "skills",
            ""
        )

        hashed_password = generate_password_hash(
            password
        )

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO job_seekers
                (
                    full_name,
                    email,
                    phone,
                    password,
                    qualification,
                    skills
                )
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
                "registration_success.html",
                name=full_name
            )

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Registration Error - Job Portal</title>
                <meta name="viewport"
                      content="width=device-width, initial-scale=1.0">
            </head>
            <body>

                <div style="
                    width:90%;
                    max-width:450px;
                    margin:50px auto;
                    padding:25px;
                    background:white;
                    border-radius:10px;
                    box-shadow:0 3px 12px rgba(0,0,0,0.15);
                    text-align:center;
                ">

                    <h2>⚠️ Registration Failed</h2>

                    <p>
                        This email address is already registered.
                    </p>

                    <br>

                    <a href="/register">
                        ← Back to Registration
                    </a>

                </div>

            </body>
            </html>
            """

    return render_template("register.html")


# =========================================================
# JOB SEEKER LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("jobportal.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM job_seekers
            WHERE email = ?
        """, (email,))

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["job_seeker_logged_in"] = True
            session["job_seeker_email"] = user["email"]
            session["job_seeker_name"] = user["full_name"]

            return render_template(
                "login_success.html",
                login_success=True,
                name=user["full_name"]
            )

        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Failed - Job Portal</title>
            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">
        </head>
        <body>

            <div style="
                width:90%;
                max-width:450px;
                margin:50px auto;
                padding:25px;
                background:white;
                border-radius:10px;
                box-shadow:0 3px 12px rgba(0,0,0,0.15);
                text-align:center;
            ">

                <h2>❌ Login Failed</h2>

                <p>
                    Invalid email or password.
                </p>

                <br>

                <a href="/login">
                    ← Try Again
                </a>

            </div>

        </body>
        </html>
        """

    return render_template("login.html")


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if not session.get("job_seeker_logged_in"):
        return redirect(url_for("login"))

    email = session.get("job_seeker_email")

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            full_name,
            email,
            phone,
            qualification,
            skills
        FROM job_seekers
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    conn.close()

    if not user:

        session.clear()

        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        profile=user
    )
# =========================================================
# EDIT PROFILE
# =========================================================

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if not session.get("job_seeker_logged_in"):
        return redirect(url_for("login"))

    email = session.get("job_seeker_email")

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        qualification = request.form.get(
            "qualification",
            ""
        ).strip()

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        cursor.execute("""
            UPDATE job_seekers
            SET
                full_name = ?,
                phone = ?,
                qualification = ?,
                skills = ?
            WHERE email = ?
        """, (
            full_name,
            phone,
            qualification,
            skills,
            email
        ))

        conn.commit()
        conn.close()

        session["job_seeker_name"] = full_name

        return redirect(
            url_for("profile")
        )

    cursor.execute("""
        SELECT
            full_name,
            email,
            phone,
            qualification,
            skills
        FROM job_seekers
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    conn.close()

    if not user:
        return redirect(url_for("login"))

    return render_template(
        "edit_profile.html",
        profile=user
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop(
        "job_seeker_logged_in",
        None
    )

    session.pop(
        "job_seeker_email",
        None
    )

    session.pop(
        "job_seeker_name",
        None
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# APPLY FOR JOB
# =========================================================

@app.route(
    "/apply/<job_name>",
    methods=["GET", "POST"]
)

def apply(job_name):

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cover_message = request.form.get(
            "cover_message",
            ""
        )

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO applications
            (
                job_name,
                full_name,
                email,
                phone,
                cover_message,
                status,
                applied_at
            )
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            job_name,
            full_name,
            email,
            phone,
            cover_message,
            "Pending"
        ))

        conn.commit()
        conn.close()

        return render_template(
            "apply_success.html",
            job_name=job_name
        )

    return render_template(
        "apply.html",
        job_name=job_name
    )


# =========================================================
# MY APPLICATIONS
# =========================================================

@app.route("/my-applications")
def my_applications():

    if not session.get("job_seeker_logged_in"):
        return redirect(url_for("login"))

    email = session.get(
        "job_seeker_email"
    )

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            job_name,
            full_name,
            email,
            phone,
            cover_message,
            status,
            applied_at
        FROM applications
        WHERE email = ?
        ORDER BY id DESC
    """, (email,))

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "my_applications.html",
        applications=applications
    )
# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        if username == "admin" and password == "admin2701":
            session["admin_logged_in"] = True

            return render_template(
                "admin_login_success.html"
            )

        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Login Failed</title>
        </head>
        <body>

            <div style="
                width:90%;
                max-width:450px;
                margin:50px auto;
                padding:25px;
                text-align:center;
            ">

                <h2>❌ Admin Login Failed</h2>

                <p>
                    Invalid admin username or password.
                </p>

                <a href="/admin-login">
                    ← Try Again
                </a>

            </div>

        </body>
        </html>
        """

    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM jobs"
    )
    total_jobs = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications"
    )
    total_applications = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM job_seekers"
    )
    total_job_seekers = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM employers"
    )
    total_employers = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM messages"
    )
    total_messages = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM activities"
    )
    total_activities = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        total_jobs=total_jobs,
        total_applications=total_applications,
        total_job_seekers=total_job_seekers,
        total_messages=total_messages,
        total_employers=total_employers,
        total_activities=total_activities
    )
# =========================================================
# ACTIVITY DASHBOARD
# =========================================================

@app.route("/activity-dashboard")
def activity_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            activity,
            created_at
        FROM activities
        ORDER BY id DESC
        LIMIT 20
    """)

    activities = cursor.fetchall()

    conn.close()

    return render_template(
        "activity_dashboard.html",
        activities=activities
    )





# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# MANAGE JOBS
# =========================================================

@app.route("/manage-jobs")
def manage_jobs():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            company,
            location,
            skills,
            description,
            approval_status,
            is_flagged
        FROM jobs
        ORDER BY id DESC
    """)

    jobs_list = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_jobs.html",
        jobs=jobs_list
    )


# =========================================================
# ADD JOB
# =========================================================

@app.route(
    "/add-job",
    methods=["GET", "POST"]
)
def add_job():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    if request.method == "POST":

        name = request.form["name"]
        company = request.form["company"]
        location = request.form["location"]
        skills = request.form["skills"]
        description = request.form["description"]

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO jobs
            (
                name,
                company,
                location,
                skills,
                description,
                approval_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            company,
            location,
            skills,
            description,
            "Pending"
        ))

        conn.commit()
        conn.close()

        log_activity("Admin added a new job")

        return redirect(
            url_for("manage_jobs")
        )

    return render_template(
        "add_job.html"
    )
# =========================================================
# EDIT JOB
# =========================================================

@app.route(
    "/edit-job/<int:job_id>",
    methods=["GET", "POST"]
)
def edit_job(job_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        company = request.form["company"]
        location = request.form["location"]
        skills = request.form["skills"]
        description = request.form["description"]

        cursor.execute("""
            UPDATE jobs
            SET
                name = ?,
                company = ?,
                location = ?,
                skills = ?,
                description = ?
            WHERE id = ?
        """, (
            name,
            company,
            location,
            skills,
            description,
            job_id
        ))

        conn.commit()
        conn.close()

        return render_template(
            "edit_job_success.html",
            job_name=name
        )

    cursor.execute("""
        SELECT
            id,
            name,
            company,
            location,
            skills,
            description
        FROM jobs
        WHERE id = ?
    """, (job_id,))

    job = cursor.fetchone()

    conn.close()

    if not job:
        return "Job not found.", 404

    return render_template(
        "edit_job.html",
        job=job
    )


# =========================================================
# DELETE JOB
# =========================================================

@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM jobs WHERE id = ?",
        (job_id,)
    )

    job = cursor.fetchone()

    if not job:

        conn.close()

        return "Job not found.", 404

    job_name = job[0]

    cursor.execute(
        "DELETE FROM jobs WHERE id = ?",
        (job_id,)
    )

    conn.commit()
    conn.close()

    return render_template(
        "delete_job_success.html",
        job_name=job_name
    )


# =========================================================
# MANAGE APPLICATIONS
# =========================================================

@app.route("/manage-applications")
def manage_applications():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            job_name,
            full_name,
            email,
            phone,
            cover_message,
            status,
            applied_at
        FROM applications
        ORDER BY id DESC
    """)

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_applications.html",
        applications=applications
    )
# =========================================================
# FLAG / UNFLAG JOB
# =========================================================

@app.route("/flag-job/<int:job_id>", methods=["POST"])
def flag_job(job_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )
    

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT is_flagged
        FROM jobs
        WHERE id = ?
    """, (job_id,))

    job = cursor.fetchone()

    if job is None:
        conn.close()
        return "Job not found.", 404

    current_status = job[0]

    if current_status == 1:
        new_status = 0
    else:
        new_status = 1

    cursor.execute("""
        UPDATE jobs
        SET is_flagged = ?
        WHERE id = ?
    """, (new_status, job_id))

    conn.commit()
    conn.close()

    return redirect(
        url_for("manage_jobs")
    )



# =========================================================
# UPDATE APPLICATION STATUS
# =========================================================

@app.route(
    "/update-application-status/<int:application_id>",
    methods=["POST"]
)
def update_application_status(application_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    status = request.form.get(
        "status",
        "Pending"
    )

    allowed_statuses = [
        "Pending",
        "Shortlisted",
        "Rejected"
    ]

    if status not in allowed_statuses:
        status = "Pending"

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE applications
        SET status = ?
        WHERE id = ?
    """, (
        status,
        application_id
    ))

    conn.commit()
    conn.close()

    return render_template(
        "application_status_success.html",
        status=status
    )
# =========================================================
# UPDATE JOB APPROVAL STATUS
# =========================================================

@app.route(
    "/update-job-approval/<int:job_id>",
    methods=["POST"]
)
def update_job_approval(job_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    approval_status = request.form.get(
        "approval_status"
    )

    allowed_statuses = [
        "Approved",
        "Rejected"
    ]

    if approval_status not in allowed_statuses:
        return "Invalid approval status.", 400

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs
        SET approval_status = ?
        WHERE id = ?
    """, (
        approval_status,
        job_id
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("manage_jobs")
    )
    if "is_flagged" not in columns:
      cursor.execute(
        "ALTER TABLE jobs ADD COLUMN is_flagged INTEGER DEFAULT 0"
    )

@app.route("/manage-employers")
def manage_employers():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            company_name,
            email,
            phone,
            address,
            created_at
        FROM employers
        ORDER BY id DESC
    """)

    employers = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_employers.html",
        employers=employers
    )
# =========================================================
# ADMIN - MANAGE JOB SEEKERS
# =========================================================

@app.route("/manage-job-seekers")
def manage_job_seekers():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            full_name,
            email,
            phone,
            qualification,
            skills
        FROM job_seekers
        ORDER BY id DESC
    """)

    seekers = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_job_seekers.html",
        seekers=seekers
    )
# =========================================================
# EDIT JOB SEEKER
# =========================================================

@app.route("/edit-job-seeker/<int:seeker_id>", methods=["GET", "POST"])
def edit_job_seeker(seeker_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        qualification = request.form["qualification"]
        skills = request.form["skills"]

        cursor.execute("""
            UPDATE job_seekers
            SET
                full_name = ?,
                email = ?,
                phone = ?,
                qualification = ?,
                skills = ?
            WHERE id = ?
        """, (
            full_name,
            email,
            phone,
            qualification,
            skills,
            seeker_id
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for("manage_job_seekers")
        )

    cursor.execute("""
        SELECT
            id,
            full_name,
            email,
            phone,
            qualification,
            skills
        FROM job_seekers
        WHERE id = ?
    """, (seeker_id,))

    seeker = cursor.fetchone()

    conn.close()

    if not seeker:
        return "Job seeker not found.", 404

    return render_template(
        "edit_job_seeker.html",
        seeker=seeker
    )


# =========================================================
# DELETE JOB SEEKER
# =========================================================

@app.route("/delete-job-seeker/<int:seeker_id>", methods=["POST"])
def delete_job_seeker(seeker_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM job_seekers
        WHERE id = ?
    """, (seeker_id,))

    conn.commit()
    conn.close()

    return redirect(
        url_for("manage_job_seekers")
    )
# =========================================================
# VIEW EMPLOYER
# =========================================================

@app.route("/view-employer/<int:employer_id>")
def view_employer(employer_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            company_name,
            email,
            phone,
            address,
            created_at
        FROM employers
        WHERE id = ?
    """, (employer_id,))

    employer = cursor.fetchone()

    conn.close()

    return render_template(
        "view_employer.html",
        employer=employer
    )
@app.route("/add-employer", methods=["GET", "POST"])
def add_employer():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    if request.method == "POST":

        company_name = request.form["company_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO employers
            (
                company_name,
                email,
                phone,
                address,
                created_at
            )
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (
            company_name,
            email,
            phone,
            address
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for("manage_employers")
        )

    return render_template(
        "add_employer.html"
    )
# =========================================================
# EDIT EMPLOYER
# =========================================================

@app.route("/edit-employer/<int:employer_id>", methods=["GET", "POST"])
def edit_employer(employer_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    if request.method == "POST":

        company_name = request.form["company_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        cursor.execute("""
            UPDATE employers
            SET
                company_name = ?,
                email = ?,
                phone = ?,
                address = ?
            WHERE id = ?
        """, (
            company_name,
            email,
            phone,
            address,
            employer_id
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for("manage_employers")
        )

    cursor.execute("""
        SELECT
            id,
            company_name,
            email,
            phone,
            address,
            created_at
        FROM employers
        WHERE id = ?
    """, (employer_id,))

    employer = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_employer.html",
        employer=employer
    )
    # =========================================================
# DELETE EMPLOYER
# =========================================================

@app.route("/delete-employer/<int:employer_id>")
def delete_employer(employer_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM employers
        WHERE id = ?
    """, (employer_id,))

    conn.commit()
    conn.close()

    return redirect(
        url_for("manage_employers")
    )





# =========================================================
# MANAGE CONTACT MESSAGES
# =========================================================

@app.route("/manage-messages")
def manage_messages():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )

    conn = sqlite3.connect("jobportal.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            subject,
            message
        FROM messages
        ORDER BY id DESC
    """)

    messages = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_messages.html",
        messages=messages
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
def settings():

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    return render_template(
        "settings.html"
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route(
    "/change-password",
    methods=["GET", "POST"]
)
def change_password():

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        current_password = request.form[
            "current_password"
        ]

        new_password = request.form[
            "new_password"
        ]

        confirm_password = request.form[
            "confirm_password"
        ]

        conn = sqlite3.connect("jobportal.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password
            FROM job_seekers
            WHERE email = ?
        """, (
            session["job_seeker_email"],
        ))

        user = cursor.fetchone()

        if not user:

            conn.close()

            return "User not found."

        if not check_password_hash(
            user[0],
            current_password
        ):

            conn.close()

            return "Current password is incorrect."

        if new_password != confirm_password:

            conn.close()

            return "New passwords do not match."

        if len(new_password) < 6:

            conn.close()

            return "New password must be at least 6 characters."

        hashed_password = generate_password_hash(
            new_password
        )

        cursor.execute("""
            UPDATE job_seekers
            SET password = ?
            WHERE email = ?
        """, (
            hashed_password,
            session["job_seeker_email"]
        ))

        conn.commit()
        conn.close()

        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Password Changed</title>
        </head>
        <body>

            <div style="
                width:90%;
                max-width:450px;
                margin:50px auto;
                padding:25px;
                text-align:center;
            ">

                <h2>✅ Password Changed Successfully</h2>

                <p>
                    Your password has been updated successfully.
                </p>

                <br>

                <a href="/settings">
                    ← Back to Settings
                </a>

            </div>

        </body>
        </html>
        """

    return """
    <!DOCTYPE html>
    <html>

    <head>

        <title>Change Password - Job Portal</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

    </head>

    <body>

        <div style="
            width:90%;
            max-width:450px;
            margin:50px auto;
            padding:25px;
            background:white;
            border-radius:10px;
            box-shadow:0 3px 12px rgba(0,0,0,0.15);
        ">

            <h2>🔐 Change Password</h2>

            <form method="POST">

                <label>Current Password</label>

                <input
                    type="password"
                    name="current_password"
                    required
                    style="
                        width:100%;
                        padding:10px;
                        margin:8px 0 15px 0;
                        box-sizing:border-box;
                    "
                >

                <label>New Password</label>

                <input
                    type="password"
                    name="new_password"
                    required
                    style="
                        width:100%;
                        padding:10px;
                        margin:8px 0 15px 0;
                        box-sizing:border-box;
                    "
                >

                <label>Confirm New Password</label>

                <input
                    type="password"
                    name="confirm_password"
                    required
                    style="
                        width:100%;
                        padding:10px;
                        margin:8px 0 15px 0;
                        box-sizing:border-box;
                    "
                >

                <button
                    type="submit"
                    style="
                        width:100%;
                        padding:11px;
                        background:#2f5f85;
                        color:white;
                        border:none;
                        border-radius:6px;
                        cursor:pointer;
                    "
                >
                    Change Password
                </button>

            </form>

            <br>

            <a href="/settings">
                ← Back to Settings
            </a>

        </div>

    </body>
    </html>
    """
# =========================================================
# LANGUAGE SETTINGS
# =========================================================

@app.route(
    "/language",
    methods=["POST"]
)
def language():

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    selected_language = request.form.get(
        "language",
        "English"
    )

    session["language"] = selected_language

    return redirect(
        url_for("settings")
    )


# =========================================================
# NOTIFICATION SETTINGS
# =========================================================

@app.route(
    "/notification-settings",
    methods=["GET", "POST"]
)
def notification_settings():

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        job_alerts = (
            request.form.get("job_alerts") == "on"
        )

        application_updates = (
            request.form.get("application_updates") == "on"
        )

        session["job_alerts"] = job_alerts
        session["application_updates"] = application_updates

        return redirect(
            url_for("settings")
        )

    job_alerts = session.get(
        "job_alerts",
        True
    )

    application_updates = session.get(
        "application_updates",
        True
    )

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>
            Notification Settings - Job Portal
        </title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

    </head>

    <body>

        <div style="
            width:90%;
            max-width:500px;
            margin:50px auto;
            padding:25px;
            background:white;
            border-radius:10px;
            box-shadow:0 3px 12px rgba(0,0,0,0.15);
        ">

            <h2>🔔 Notification Settings</h2>

            <form method="POST">

                <label style="
                    display:block;
                    margin:20px 0;
                ">

                    <input
                        type="checkbox"
                        name="job_alerts"
                        {"checked" if job_alerts else ""}
                    >

                    Job Alerts

                </label>

                <label style="
                    display:block;
                    margin:20px 0;
                ">

                    <input
                        type="checkbox"
                        name="application_updates"
                        {"checked" if application_updates else ""}
                    >

                    Application Updates

                </label>

                <button
                    type="submit"
                    style="
                        width:100%;
                        padding:11px;
                        background:#2f5f85;
                        color:white;
                        border:none;
                        border-radius:6px;
                        cursor:pointer;
                    "
                >
                    Save Notification Settings
                </button>

            </form>

            <br>

            <a href="/settings">
                ← Back to Settings
            </a>

        </div>

    </body>
    </html>
    """


# =========================================================
# APPEARANCE SETTINGS
# =========================================================

@app.route(
    "/appearance",
    methods=["POST"]
)
def appearance():

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    selected_appearance = request.form.get(
        "appearance",
        "Light"
    )

    session["appearance"] = selected_appearance

    return redirect(
        url_for("settings")
    )


# =========================================================
# PRIVACY & SECURITY
# =========================================================

@app.route("/privacy-security")
def privacy_security():

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    return """
    <!DOCTYPE html>
    <html>

    <head>

        <title>
            Privacy & Security - Job Portal
        </title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

    </head>

    <body>

        <div style="
            width:90%;
            max-width:550px;
            margin:50px auto;
            padding:25px;
            background:white;
            border-radius:10px;
            box-shadow:0 3px 12px rgba(0,0,0,0.15);
        ">

            <h2>🔒 Privacy & Security</h2>

            <p>
                Your account is protected by login
                authentication and password hashing.
            </p>

            <hr>

            <h3>Account Security</h3>

            <p>
                • Password is securely stored.<br>
                • Your account requires login access.<br>
                • Personal information is not displayed publicly.
            </p>

            <hr>

            <h3>Privacy</h3>

            <p>
                Your profile and application information
                is accessible only through your account.
            </p>

            <br>

            <a href="/settings">
                ← Back to Settings
            </a>

        </div>

    </body>
    </html>
    """
# =========================================================
# EMAIL PREFERENCES
# =========================================================

@app.route(
    "/email-preferences",
    methods=["GET", "POST"]
)
def email_preferences():

    if not session.get("job_seeker_logged_in"):
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        email_alerts = (
            request.form.get("email_alerts") == "on"
        )

        session["email_alerts"] = email_alerts

        return redirect(
            url_for("settings")
        )

    email_alerts = session.get(
        "email_alerts",
        True
    )

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>
            Email Preferences - Job Portal
        </title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

    </head>

    <body>

        <div style="
            width:90%;
            max-width:500px;
            margin:50px auto;
            padding:25px;
            background:white;
            border-radius:10px;
            box-shadow:0 3px 12px rgba(0,0,0,0.15);
        ">

            <h2>📧 Email Preferences</h2>

            <p>
                Manage your email notification preferences.
            </p>

            <form method="POST">

                <label style="
                    display:block;
                    margin:20px 0;
                ">

                    <input
                        type="checkbox"
                        name="email_alerts"
                        {"checked" if email_alerts else ""}
                    >

                    Receive Job & Application Email Alerts

                </label>

                <button
                    type="submit"
                    style="
                        width:100%;
                        padding:11px;
                        background:#2f5f85;
                        color:white;
                        border:none;
                        border-radius:6px;
                        cursor:pointer;
                    "
                >
                    Save Email Preferences
                </button>

            </form>

            <br>

            <a href="/settings">
                ← Back to Settings
            </a>

        </div>

    </body>
    </html>
    """


# =========================================================
# API - ALL JOBS
# =========================================================

@app.route("/api/jobs")
def api_jobs():

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            company,
            location,
            skills,
            description
        FROM jobs
        ORDER BY id
    """)

    jobs_list = cursor.fetchall()

    conn.close()

    jobs_data = []

    for job in jobs_list:

        jobs_data.append({
            "id": job["id"],
            "name": job["name"],
            "company": job["company"],
            "location": job["location"],
            "skills": job["skills"],
            "description": job["description"]
        })

    return jsonify(jobs_data)

# =========================================================
# API - SEARCH JOBS
# =========================================================

@app.route("/api/jobs/search")
def api_search_jobs():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            company,
            location,
            skills,
            description
        FROM jobs
        WHERE
            name LIKE ?
            OR company LIKE ?
            OR location LIKE ?
            OR skills LIKE ?
        ORDER BY id
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    jobs_list = cursor.fetchall()

    conn.close()

    jobs_data = []

    for job in jobs_list:

        jobs_data.append({
            "id": job["id"],
            "name": job["name"],
            "company": job["company"],
            "location": job["location"],
            "skills": job["skills"],
            "description": job["description"]
        })

    return jsonify(jobs_data)


# =========================================================
# API - SINGLE JOB
# =========================================================

@app.route("/api/jobs/<int:job_id>")
def api_single_job(job_id):

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            company,
            location,
            skills,
            description
        FROM jobs
        WHERE id = ?
    """, (job_id,))

    job = cursor.fetchone()

    conn.close()

    if not job:

        return jsonify({
            "error": "Job not found"
        }), 404

    return jsonify({
        "id": job["id"],
        "name": job["name"],
        "company": job["company"],
        "location": job["location"],
        "skills": job["skills"],
        "description": job["description"]
    })

# =========================================================
# API - ALL APPLICATIONS
# =========================================================

@app.route("/api/applications")
def api_applications():

    if not session.get("admin_logged_in"):
        return jsonify({
            "error": "Unauthorized access"
        }), 401

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            job_name,
            full_name,
            email,
            phone,
            cover_message,
            status,
            applied_at
        FROM applications
        ORDER BY id
    """)

    applications = cursor.fetchall()

    conn.close()

    applications_data = []

    for application in applications:

        applications_data.append({
            "id": application["id"],
            "job_name": application["job_name"],
            "full_name": application["full_name"],
            "email": application["email"],
            "phone": application["phone"],
            "cover_message": application["cover_message"],
            "status": application["status"],
            "applied_at": application["applied_at"]
        })

    return jsonify(applications_data)

# =========================================================
# API - ALL JOB SEEKERS
# =========================================================

@app.route("/api/job-seekers")
def api_job_seekers():

    if not session.get("admin_logged_in"):
        return jsonify({
            "error": "Unauthorized access"
        }), 401

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            full_name,
            email,
            phone,
            qualification,
            skills
        FROM job_seekers
        ORDER BY id
    """)

    seekers = cursor.fetchall()

    conn.close()

    seekers_data = []

    for seeker in seekers:

        seekers_data.append({
            "id": seeker["id"],
            "full_name": seeker["full_name"],
            "email": seeker["email"],
            "phone": seeker["phone"],
            "qualification": seeker["qualification"],
            "skills": seeker["skills"]
        })

    return jsonify(seekers_data)
# =========================================================
# API - ALL MESSAGES
# =========================================================

@app.route("/api/messages")
def api_messages():

    if not session.get("admin_logged_in"):
        return jsonify({
            "error": "Unauthorized access"
        }), 401

    conn = sqlite3.connect("jobportal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            subject,
            message
        FROM messages
        ORDER BY id DESC
    """)

    messages = cursor.fetchall()

    conn.close()

    messages_data = []

    for message in messages:

        messages_data.append({
            "id": message["id"],
            "name": message["name"],
            "email": message["email"],
            "subject": message["subject"],
            "message": message["message"]
        })

    return jsonify({
        "success": True,
        "count": len(messages_data),
        "messages": messages_data
    })

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
