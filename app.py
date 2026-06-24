# from flask import Flask, request, render_template, redirect, url_for
# from ultralytics import YOLO
# from PIL import Image
# import os
# from database import insert_scan, get_all_scans

from flask import Flask, request, render_template, redirect, url_for, flash, session
from ultralytics import YOLO
from PIL import Image
import os
import sqlite3
import database  # updated database.py with user functions
from database import insert_scan, get_all_scans
from werkzeug.security import generate_password_hash, check_password_hash


UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "Tanuja@123"  # Change this to something strong

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = YOLO('weights/best.pt')
class_names = ["Grade A", "Grade B"]

@app.route('/')
def index():
    return render_template('index.html')

# ------------------- SIGNUP -------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = database.get_user_by_email(email)
        if existing_user:
            flash("Email already registered!", "error")
            return redirect(url_for("signup"))

        database.create_user(username, email, password)
        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# ------------------- LOGIN -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = database.verify_user(email, password)
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "error")

    return render_template("login.html")


# ------------------- FORGOT PASSWORD -------------------
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        new_password = request.form["new_password"]

        user = database.get_user_by_email(email)
        if user:
            database.update_password(email, new_password)
            flash("Password updated successfully!", "success")
            return redirect(url_for("login"))
        else:
            flash("Email not found!", "error")

    return render_template("forgot_password.html")


# ------------------- LOGOUT -------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))
    return render_template('dashboard.html')

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')



@app.route('/result', methods=['POST'])
def result():
    if 'file' not in request.files:
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('dashboard'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    results = model(filepath)

    counts = {0: 0, 1: 0}
    for box in results[0].boxes:
        cls = int(box.cls[0].item())
        counts[cls] += 1

    grade_a = counts[0]
    grade_b = counts[1]

    if grade_a > grade_b:
        final_grade = "Grade A"
    elif grade_b > grade_a:
        final_grade = "Grade B"
    else:
        final_grade = "Equal — Need Recheck"

    img_with_boxes = results[0].plot()
    base, _ = os.path.splitext(filepath)
    result_image_path = base + ".jpg"
    Image.fromarray(img_with_boxes).save(result_image_path, format="JPEG")
    image_path = result_image_path.replace("\\", "/")

    insert_scan(file.filename, grade_a, grade_b, final_grade)

    return render_template(
        'result.html',
        grade_a=grade_a,
        grade_b=grade_b,
        final_grade=final_grade,
        image=image_path
    )

@app.route('/history')
def history():
    scans = get_all_scans()
    return render_template('history.html', scans=scans)

@app.route('/delete/<int:scan_id>', methods=['POST'])
def delete_scan(scan_id):
    import sqlite3
    conn = sqlite3.connect("scan_history.db")
    c = conn.cursor()
    c.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('history'))

if __name__ == '__main__':
    app.run(debug=True)
