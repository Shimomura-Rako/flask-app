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

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLiteを使用

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

 

# データベースのモデル

class UserData(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    teacher_id = db.Column(db.String(100), nullable=False)

    pushbullet_token = db.Column(db.String(255), nullable=False)

 

# 初回実行時にデータベースを作成

with app.app_context():

    db.create_all()

 

# Pushbullet通知を送信する関数

def send_push_notification(user_token, teacher_id, name):

    """Push通知を送信"""

    try:

        pb_user = pushbullet.Pushbullet(user_token)

        url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"

        pb_user.push_link(f"{name} レッスン開講通知", url)

        print(f"📢 Push通知送信: {name} - {url}")

    except Exception as e:

        print(f"⚠️ Pushbullet通知の送信に失敗しました: {e}")

 

# 予約状況を確認し、通知を送る関数

def check_teacher_availability():

    """データベースに登録された全ユーザーの予約状況を確認し、必要なら通知"""

    users = UserData.query.all()  # データベース内の全ユーザーを取得

    for user in users:

        teacher_id = user.teacher_id

        user_token = user.pushbullet_token

 

        # 教師ページURLを生成

        load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"

        headers = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

        }

        html = requests.get(load_url, headers=headers)

       

        if html.status_code != 200:

            print(f"⚠️ {teacher_id} のページが見つかりません (ステータスコード: {html.status_code})")

            continue

 

        soup = BeautifulSoup(html.content, "html.parser")

 

        # 講師名を取得

        teacher_name_tag = soup.find("h1")

        if teacher_name_tag and teacher_name_tag.text:

            teacher_name = teacher_name_tag.text.strip()

        else:

            teacher_name = "不明な講師"

 

        print(f"🎤 取得した講師名: {teacher_name}")  # デバッグ用

 

        # 予約状況を確認（仮のコード）

        # ここで予約情報をチェックし、必要に応じて通知を送信します

 

        # 例: 予約可の場合にPush通知を送る

        send_push_notification(user_token, teacher_id, teacher_name)

 

# APSchedulerを使って定期的にスクレイピングを実行

scheduler = BackgroundScheduler()

scheduler.add_job(check_teacher_availability, 'interval', minutes=1)  # 1分ごとに実行

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

            new_data = UserData(teacher_id=teacher_id, pushbullet_token=pushbullet_token)

            db.session.add(new_data)

            db.session.commit()

            flash("データを保存しました！", "success")

 

        return redirect("/")

 

    all_data = UserData.query.all()

    return render_template("index.html", all_data=all_data)

 

if __name__ == "__main__":

    # Render用にポートとホスト設定を変更

    port = int(os.environ.get("PORT", 5000))  # Renderが指定したポートを使用

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)  # 全てのIPアドレスからアクセス可能にする

 
