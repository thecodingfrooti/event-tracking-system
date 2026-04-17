from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- MODELS ---------------- #

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship("Registration", back_populates="student", cascade="all, delete-orphan")


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=True)
    location = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=True)

    registrations = db.relationship("Registration", back_populates="event", cascade="all, delete-orphan")


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="registrations")
    event = db.relationship("Event", back_populates="registrations")


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- INIT DB ---------------- #

def seed_sample_data():
    if Event.query.count() > 0:
        return

    sample_events = [
        Event(
            title="Tech Talk: AI in Education",
            description="A beginner-friendly session exploring how AI is transforming learning.",
            category="Technology",
            location="Auditorium A",
            date=datetime(2026, 4, 20).date(),
            start_time=datetime.strptime("15:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            capacity=80,
        ),
        Event(
            title="Intercollege Football Tournament",
            description="Join the annual football tournament.",
            category="Sports",
            location="Main Ground",
            date=datetime(2026, 4, 25).date(),
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            capacity=22,
        ),
    ]

    db.session.add_all(sample_events)
    db.session.commit()


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    events = Event.query.order_by(Event.date, Event.start_time).all()
    return render_template("index.html", events=events)


@app.route("/events/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("event_detail.html", event=event)


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    event_id = request.form.get("event_id")

    if not name or not email or not event_id:
        flash("Please fill all fields", "danger")
        return redirect(url_for("home"))

    event = Event.query.get_or_404(event_id)

    student = Student.query.filter_by(email=email).first()
    if not student:
        student = Student(name=name, email=email)
        db.session.add(student)
        db.session.flush()

    registration = Registration(student=student, event=event)
    db.session.add(registration)
    db.session.commit()

    flash("Registered successfully!", "success")
    return redirect(url_for("event_detail", event_id=event.id))
   


# ---------------- START APP ---------------- #

with app.app_context():
    db.create_all()
    seed_sample_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))