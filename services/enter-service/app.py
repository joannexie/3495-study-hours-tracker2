import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from db import get_conn

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret")

AUTH_URL = os.environ.get("AUTH_URL", "http://auth-service:3000")

def require_login():
    token = session.get("token")
    if not token:
        return False, None
    r = requests.post(f"{AUTH_URL}/verify", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    if r.status_code != 200:
        return False, None
    return True, r.json().get("username")

@app.get("/")
def home():
    ok, username = require_login()
    if not ok:
        return redirect(url_for("login"))
    return redirect(url_for("enter"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username","").strip()
    password = request.form.get("password","").strip()

    try:
        r = requests.post(f"{AUTH_URL}/login", json={"username": username, "password": password}, timeout=5)
    except Exception:
        flash("Auth service not reachable. Is docker compose running?", "error")
        return redirect(url_for("login"))

    if r.status_code != 200:
        flash("Invalid login. Try again.", "error")
        return redirect(url_for("login"))

    data = r.json()
    session["token"] = data["token"]
    session["username"] = data["username"]
    return redirect(url_for("enter"))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/enter", methods=["GET","POST"])
def enter():
    ok, username = require_login()
    if not ok:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("enter.html", username=username)

    subject = request.form.get("subject","").strip()
    hours_raw = request.form.get("hours","").strip()
    date_raw = request.form.get("study_date","").strip()

    # basic validation
    if not subject or not hours_raw or not date_raw:
        flash("Please fill in subject, hours, and date.", "error")
        return redirect(url_for("enter"))

    try:
        hours = float(hours_raw)
        if hours <= 0:
            raise ValueError()
    except ValueError:
        flash("Hours must be a number greater than 0.", "error")
        return redirect(url_for("enter"))

    try:
        study_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
    except ValueError:
        flash("Date must be in YYYY-MM-DD format.", "error")
        return redirect(url_for("enter"))

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO study_logs (username, subject, hours, study_date) VALUES (%s, %s, %s, %s)",
            (username, subject, hours, study_date),
        )
    conn.close()

    flash("Saved! Add another log or open Show Results to see analytics.", "success")
    return redirect(url_for("enter"))

@app.get("/recent")
def recent():
    ok, username = require_login()
    if not ok:
        return redirect(url_for("login"))

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT subject, hours, study_date, created_at FROM study_logs WHERE username=%s ORDER BY id DESC LIMIT 10",
            (username,),
        )
        rows = cur.fetchall()
    conn.close()
    return render_template("recent.html", username=username, rows=rows)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
