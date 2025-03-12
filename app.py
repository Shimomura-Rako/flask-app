import os

import requests

from flask_sqlalchemy import SQLAlchemy

import pushbullet

from bs4 import BeautifulSoup

from dotenv import load_dotenv

from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, render_template, request, flash, redirect

 

# Flask設定

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

 

# データベースのモデル

class UserData(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    teacher_id = db.Column(db.String(100), nullable=False)

    teacher_name = db.Column(db.String(255), nullable=True)

    pushbullet_token = db.Column(db.String(255), nullable=False)

 

# 初回実行時にデータベースを作成

with app.app_context():

    db.create_all()

 

# 講師名を取得する関数

def get_teacher_name(teacher_id):

    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"

    headers = {"User-Agent": "Mozilla/5.0"}

    html = requests.get(load_url, headers=headers)

   

    if html.status_code != 200:

        return None

   

    soup = BeautifulSoup(html.content, "html.parser")

    teacher_name_tag = soup.find("h1")

    return teacher_name_tag.text.strip() if teacher_name_tag else "不明な講師"

 

# Pushbullet通知を送信する関数

def send_push_notification(user_token, teacher_id, name):

    try:

        pb_user = pushbullet.Pushbullet(user_token)

        url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"

        pb_user.push_link(f"{name} レッスン開講通知", url)

        print(f"📢 Push通知送信: {name} - {url}")

    except Exception as e:

        print(f"⚠️ Pushbullet通知の送信に失敗しました: {e}")

 

# 予約状況を確認する関数

def check_teacher_availability():

    users = UserData.query.all()

    for user in users:

        teacher_name = get_teacher_name(user.teacher_id)

        if teacher_name:

            send_push_notification(user.pushbullet_token, user.teacher_id, teacher_name)

 

# APSchedulerで定期実行

scheduler = BackgroundScheduler()

scheduler.add_job(check_teacher_availability, 'interval', minutes=1)

scheduler.start()

 

# ルートページ

@app.route("/", methods=["GET", "POST"])

def index():

    if request.method == "POST":

        teacher_id = request.form.get("teacher_id")

        pushbullet_token = request.form.get("pushbullet_token")

       

        if not teacher_id or not pushbullet_token:

            flash("すべての項目を入力してください！", "danger")

        else:

            teacher_name = get_teacher_name(teacher_id)

            if not teacher_name:

                flash("講師情報が取得できませんでした。番号を確認してください。", "danger")

            else:

                new_data = UserData(teacher_id=teacher_id, teacher_name=teacher_name, pushbullet_token=pushbullet_token)

                db.session.add(new_data)

                db.session.commit()

                flash(f"{teacher_name} (講師番号: {teacher_id}) を登録しました！", "success")

 

        return redirect("/")

 

    all_data = UserData.query.all()

    return render_template("index.html", all_data=all_data)

 

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
