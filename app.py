from flask import Flask, render_template, request, redirect, flash, session
import os
import requests
import random
import string
from flask_sqlalchemy import SQLAlchemy
from pushbullet import Pushbullet
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(100), nullable=False)
    teacher_name = db.Column(db.String(255), nullable=True)
    pushbullet_token = db.Column(db.String(255), nullable=False)
    last_available_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.String(255), nullable=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def generate_user_id(length=10):
    return 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@app.before_request
def assign_user_id():
    if "user_id" not in session:
        session["user_id"] = None

@app.route("/set_user", methods=["GET", "POST"])
def set_user():
    if request.method == "POST":
        user_id = request.form.get("user_id").strip()
        if not user_id:
            flash("ユーザーIDを入力してください！", "danger")
        else:
            session["user_id"] = user_id
            flash(f"ユーザーIDを設定しました: {user_id}", "success")
            return redirect("/")
    else:
        user_id = generate_user_id()
        session["user_id"] = user_id
        return render_template("set_user.html", user_id=user_id)

@app.route("/", methods=["GET", "POST"])
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/set_user")

    UserData.query.filter_by(user_id=user_id).update({"last_accessed": datetime.utcnow()})
    db.session.commit()

    total_teachers = UserData.query.filter_by(user_id=user_id).count()

    if request.method == "POST":
        if total_teachers >= 10:
            flash("このアカウントでは最大10件までしか登録できません！", "danger")
            return redirect("/")

        teacher_id = request.form.get("teacher_id")
        pushbullet_token = request.form.get("pushbullet_token")

        if not teacher_id or not pushbullet_token:
            flash("すべての項目を入力してください！", "danger")
        else:
            existing_teacher = UserData.query.filter_by(teacher_id=teacher_id, user_id=user_id).first()
            if existing_teacher:
                flash("この講師はすでに登録されています！", "warning")
                return redirect("/")

            teacher_name = get_teacher_name(teacher_id)
            if not teacher_name:
                flash("講師情報が取得できませんでした。番号を確認してください。", "danger")
            else:
                new_data = UserData(
                    teacher_id=teacher_id,
                    teacher_name=teacher_name,
                    pushbullet_token=pushbullet_token,
                    user_id=user_id
                )
                db.session.add(new_data)
                db.session.commit()
                flash(f"{teacher_name} (講師番号: {teacher_id}) を登録しました！", "success")

        return redirect("/")

    all_data = UserData.query.filter_by(user_id=user_id).all()
    return render_template("index.html", all_data=all_data, total_teachers=total_teachers, user_id=user_id)

@app.route("/delete_teacher", methods=["POST", "GET"])
def delete_teacher():
    if request.method == "GET":
        return redirect("/")

    teacher_id = request.form.get("teacher_id")
    user_id = session.get("user_id")
    teacher_data = UserData.query.filter_by(teacher_id=teacher_id, user_id=user_id).first()
    if teacher_data:
        db.session.delete(teacher_data)
        db.session.commit()
        flash(f"講師番号 {teacher_id} を削除しました！", "success")
    else:
        flash(f"講師番号 {teacher_id} は存在しません。", "danger")
    return redirect("/")

def get_teacher_name(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    try:
        response = requests.get(load_url, headers=HEADERS, timeout=5, allow_redirects=True)
        if response.url == "https://eikaiwa.dmm.com/":
            return None
        soup = BeautifulSoup(response.content, "html.parser")
        teacher_name_tag = soup.find("h1")
        return teacher_name_tag.text.strip() if teacher_name_tag else None
    except requests.exceptions.RequestException:
        return None

def get_available_slots(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    try:
        response = requests.get(load_url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            return 0
        soup = BeautifulSoup(response.content, "html.parser")
        return len(soup.find_all(string="予約可"))
    except requests.exceptions.RequestException:
        return 0

def send_push_notification(user_token, teacher_id, name):
    try:
        pb_user = Pushbullet(user_token)
        url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
        pb_user.push_link(f"{name} レッスン開講通知", url)
    except Exception as e:
        print(f"⚠ Pushbullet通知の送信に失敗しました: {e}")

def check_teacher_availability():
    with app.app_context():
        try:
            users = UserData.query.all()
            for user in users:
                current_count = get_available_slots(user.teacher_id)
                if current_count is None:
                    continue
                if current_count > user.last_available_count:
                    send_push_notification(user.pushbullet_token, user.teacher_id, user.teacher_name)
                user.last_available_count = current_count
                db.session.commit()
        except Exception as e:
            print(f"⚠ 通知チェックでエラー発生: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(check_teacher_availability, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
