"""Health Prediction App - Flask + SQLite CRUD with AI-generated remarks."""
import os
import sqlite3

from flask import Flask, flash, g, jsonify, redirect, render_template, request, url_for

from ai_service import get_remarks
from validators import validate_patient

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "patients.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-env")

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    dob TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    glucose REAL NOT NULL,
    haemoglobin REAL NOT NULL,
    cholesterol REAL NOT NULL,
    remarks TEXT
)
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(SCHEMA)


def email_taken(email, exclude_id=None):
    row = get_db().execute(
        "SELECT id FROM patients WHERE email = ? AND id IS NOT ?", (email, exclude_id)
    ).fetchone()
    return row is not None


# ---------- READ ----------
@app.route("/")
def index():
    patients = get_db().execute("SELECT * FROM patients ORDER BY id").fetchall()
    return render_template("index.html", patients=patients, form={})


@app.route("/api/patients")
def api_patients():
    rows = get_db().execute("SELECT * FROM patients ORDER BY id").fetchall()
    return jsonify([dict(r) for r in rows])


# ---------- CREATE ----------
@app.route("/add", methods=["POST"])
def add():
    clean, errors = validate_patient(request.form)
    if not errors and email_taken(clean["email"]):
        errors.append("A patient with this email already exists (duplicate record).")
    if errors:
        for e in errors:
            flash(e, "error")
        patients = get_db().execute("SELECT * FROM patients ORDER BY id").fetchall()
        return render_template("index.html", patients=patients, form=request.form), 400

    clean["remarks"] = get_remarks(clean)
    db = get_db()
    db.execute(
        "INSERT INTO patients (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks) "
        "VALUES (:full_name, :dob, :email, :glucose, :haemoglobin, :cholesterol, :remarks)",
        clean,
    )
    db.commit()
    flash(f"Record for {clean['full_name']} created.", "success")
    return redirect(url_for("index"))


# ---------- UPDATE ----------
@app.route("/edit/<int:pid>", methods=["GET", "POST"])
def edit(pid):
    db = get_db()
    row = db.execute("SELECT * FROM patients WHERE id = ?", (pid,)).fetchone()
    if row is None:
        flash("Record not found.", "error")
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("edit.html", p=row, form=dict(row))

    clean, errors = validate_patient(request.form)
    if not errors and email_taken(clean["email"], exclude_id=pid):
        errors.append("Another patient already uses this email.")
    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("edit.html", p=row, form=request.form), 400

    values_changed = any(clean[k] != row[k] for k in ("dob", "glucose", "haemoglobin", "cholesterol"))
    clean["remarks"] = get_remarks(clean) if values_changed else row["remarks"]
    clean["id"] = pid
    db.execute(
        "UPDATE patients SET full_name=:full_name, dob=:dob, email=:email, glucose=:glucose, "
        "haemoglobin=:haemoglobin, cholesterol=:cholesterol, remarks=:remarks WHERE id=:id",
        clean,
    )
    db.commit()
    flash("Record updated.", "success")
    return redirect(url_for("index"))


# ---------- DELETE ----------
@app.route("/delete/<int:pid>", methods=["POST"])
def delete(pid):
    db = get_db()
    db.execute("DELETE FROM patients WHERE id = ?", (pid,))
    db.commit()
    flash("Record deleted.", "success")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=False, port=5000)
