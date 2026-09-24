import secrets
import sqlite3
from functools import wraps
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import validate_appointment, validate_login, validate_registration
from app.models import APPOINTMENT_FEE
from database.db_config import get_db

bp = Blueprint("main", __name__)


def db():
    return get_db(current_app.config["DATABASE"])


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Administrator access is required.", "error")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.route("/")
def index():
    return render_template("base.html", home=True)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        errors = validate_registration(name, email, password)
        conn = db()
        if not errors and conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            errors.append("An account with this email already exists.")
        if errors:
            conn.close()
            for error in errors:
                flash(error, "error")
            return render_template("registration.html")
        conn.execute(
            "INSERT INTO users(full_name,email,password_hash) VALUES(?,?,?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        conn.close()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("registration.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        errors = validate_login(email, password)
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if not errors and (not user or not check_password_hash(user["password_hash"], password)):
            errors.append("Invalid email or password.")
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("login.html")
        session.clear()
        session.update(user_id=user["id"], name=user["full_name"], role=user["role"], email=user["email"])
        flash("Login successful.", "success")
        return redirect(url_for("main.admin_dashboard" if user["role"] == "admin" else "main.appointment"))
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.login"))


@bp.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    conn = db()
    doctors = conn.execute("SELECT * FROM doctors ORDER BY name").fetchall()
    if request.method == "POST":
        doctor_id = request.form.get("doctor_id", type=int)
        date = request.form.get("appointment_date", "")
        time = request.form.get("appointment_time", "")
        errors = validate_appointment(doctor_id, date, time)
        doctor = conn.execute("SELECT * FROM doctors WHERE id=?", (doctor_id,)).fetchone() if doctor_id else None
        if not doctor:
            errors.append("Selected doctor does not exist.")
        elif doctor["availability"] != "Available":
            errors.append("Selected doctor is currently unavailable.")
        existing = None
        if doctor_id and date and time:
            existing = conn.execute(
                "SELECT id FROM appointments WHERE doctor_id=? AND appointment_date=? AND appointment_time=? AND status != 'Cancelled'",
                (doctor_id, date, time),
            ).fetchone()
        if existing:
            errors.append("This appointment slot is already booked.")
        if errors:
            conn.close()
            for error in errors:
                flash(error, "error")
            return render_template("appointment.html", doctors=doctors, fee=APPOINTMENT_FEE)
        cursor = conn.execute(
            "INSERT INTO appointments(patient_id,doctor_id,appointment_date,appointment_time) VALUES(?,?,?,?)",
            (session["user_id"], doctor_id, date, time),
        )
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for("main.payment", appointment_id=appointment_id))
    conn.close()
    return render_template("appointment.html", doctors=doctors, fee=APPOINTMENT_FEE)


@bp.route("/payment/<int:appointment_id>", methods=["GET", "POST"])
@login_required
def payment(appointment_id):
    conn = db()
    appointment_row = conn.execute(
        "SELECT a.*, d.name doctor_name FROM appointments a JOIN doctors d ON d.id=a.doctor_id WHERE a.id=? AND a.patient_id=?",
        (appointment_id, session["user_id"]),
    ).fetchone()
    if not appointment_row:
        conn.close()
        flash("Appointment not found.", "error")
        return redirect(url_for("main.appointment"))
    if request.method == "POST":
        method = request.form.get("method", "Card")
        if method not in {"Card", "UPI"}:
            flash("Select a supported payment method.", "error")
            conn.close()
            return render_template("payment.html", appointment=appointment_row, fee=APPOINTMENT_FEE)
        ref = "ABC-" + secrets.token_hex(5).upper()
        conn.execute(
            "INSERT INTO payments(appointment_id,amount,method,status,transaction_ref) VALUES(?,?,?,?,?)",
            (appointment_id, APPOINTMENT_FEE, method, "Paid", ref),
        )
        conn.execute(
            "UPDATE appointments SET status='Confirmed', payment_status='Paid' WHERE id=?",
            (appointment_id,),
        )
        conn.commit()
        conn.close()
        flash("Payment successful and appointment confirmed.", "success")
        return redirect(url_for("main.history"))
    conn.close()
    return render_template("payment.html", appointment=appointment_row, fee=APPOINTMENT_FEE)


@bp.route("/history")
@login_required
def history():
    conn = db()
    rows = conn.execute(
        "SELECT a.*, d.name doctor_name, d.specialty FROM appointments a JOIN doctors d ON d.id=a.doctor_id WHERE a.patient_id=? ORDER BY a.appointment_date DESC, a.appointment_time DESC",
        (session["user_id"],),
    ).fetchall()
    conn.close()
    return render_template("history.html", appointments=rows)


@bp.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if len(name) < 2 or "@" not in email or len(message) < 5:
            flash("Please provide a valid name, email and message.", "error")
            return render_template("support.html")
        conn = db()
        conn.execute(
            "INSERT INTO support_messages(user_id,name,email,message) VALUES(?,?,?,?)",
            (session.get("user_id"), name, email, message),
        )
        conn.commit()
        conn.close()
        flash("Your support request has been submitted.", "success")
        return redirect(url_for("main.support"))
    return render_template("support.html")


@bp.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    conn = db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_doctor":
            name = request.form.get("name", "").strip()
            specialty = request.form.get("specialty", "").strip()
            availability = request.form.get("availability", "Available")
            if name and specialty and availability in {"Available", "Unavailable"}:
                conn.execute("INSERT INTO doctors(name,specialty,availability) VALUES(?,?,?)", (name, specialty, availability))
                conn.commit()
                flash("Doctor added successfully.", "success")
            else:
                flash("Enter valid doctor details.", "error")
        elif action == "toggle_doctor":
            doctor_id = request.form.get("doctor_id", type=int)
            doctor = conn.execute("SELECT availability FROM doctors WHERE id=?", (doctor_id,)).fetchone()
            if doctor:
                new_value = "Unavailable" if doctor["availability"] == "Available" else "Available"
                conn.execute("UPDATE doctors SET availability=? WHERE id=?", (new_value, doctor_id))
                conn.commit()
                flash("Doctor availability updated.", "success")
        elif action == "close_support":
            msg_id = request.form.get("message_id", type=int)
            conn.execute("UPDATE support_messages SET status='Closed' WHERE id=?", (msg_id,))
            conn.commit()
            flash("Support request closed.", "success")
    doctors = conn.execute("SELECT * FROM doctors ORDER BY name").fetchall()
    appointments = conn.execute(
        "SELECT a.*, u.full_name patient_name, d.name doctor_name FROM appointments a JOIN users u ON u.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id ORDER BY a.appointment_date DESC, a.appointment_time DESC"
    ).fetchall()
    messages = conn.execute("SELECT * FROM support_messages ORDER BY created_at DESC").fetchall()
    stats = {
        "patients": conn.execute("SELECT COUNT(*) FROM users WHERE role='patient'").fetchone()[0],
        "doctors": conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
        "appointments": conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
        "open_support": conn.execute("SELECT COUNT(*) FROM support_messages WHERE status='Open'").fetchone()[0],
    }
    conn.close()
    return render_template("admin_dashboard.html", doctors=doctors, appointments=appointments, messages=messages, stats=stats)


@bp.app_errorhandler(sqlite3.IntegrityError)
def handle_integrity_error(error):
    return render_template("error.html", message="The requested operation could not be completed because the data conflicts with an existing record."), 409
