import os
import requests
from flask_sqlalchemy import SQLAlchemy
import pushbullet
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, flash, redirect
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    last_available_count = db.Column(db.Integer, default=0)  # 前回の「予約可」の数

# 初回実行時にデータベースを作成
with app.app_context():
    db.create_all()

# 講師名を取得する関数
def get_teacher_name(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        html = requests.get(load_url, headers=headers)
        html.raise_for_status()  # HTTPエラーを例外として処理
        soup = BeautifulSoup(html.content, "html.parser")
        teacher_name_tag = soup.find("h1", class_="teacher-main__name")  # クラス名を修正

        if teacher_name_tag:
            return teacher_name_tag.text.strip()
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"講師名取得中にエラーが発生しました: {e}")
        return None

# 講師ページから「予約可」の数を取得
def get_available_slots(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        html = requests.get(load_url, headers=headers)
        html.raise_for_status()  # HTTPエラーを例外として処理
        soup = BeautifulSoup(html.content, "html.parser")
        available_slots = len(soup.find_all("span", class_="reservation-status--available"))  # クラス名とタグを指定してカウント
        return available_slots
    except requests.exceptions.RequestException as e:
        logging.error(f"予約状況取得中にエラーが発生しました: {e}")
        return 0

# Pushbullet通知を送信する関数
def send_push_notification(user_token, teacher_id, name):
    try:
        pb_user = pushbullet.Pushbullet(user_token)
        url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
        pb_user.push_link(f"{name} レッスン開講通知", url)
        logging.info(f" Push通知送信: {name} - {url}")
    except Exception as e:
        logging.error(f"⚠ Pushbullet通知の送信に失敗しました: {e}")

# 予約状況を確認し、必要なら通知を送る
def check_teacher_availability():
    with app.app_context():
        users = UserData.query.all()
        for user in users:
            current_count = get_available_slots(user.teacher_id)
            logging.info(f"講師 {user.teacher_name} の予約可数: {current_count}")

            if current_count > user.last_available_count:
                if current_count > 0:
                    send_push_notification(user.pushbullet_token, user.teacher_id, user.teacher_name)

            user.last_available_count = current_count
            db.session.commit()

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
                new_data = UserData(teacher_id=teacher_id, teacher_name=teacher_name, pushbullet_token=pushbullet_token, last_available_count=0)
                db.session.add(new_data)
                db.session.commit()
                flash(f"{teacher_name} (講師番号: {teacher_id}) を登録しました！", "success")

        return redirect("/")

    all_data = UserData.query.all()
    return render_template("index.html", all_data=all_data)

# 講師データを削除するルート
@app.route("/delete_teacher", methods=["POST"])
def delete_teacher():
    teacher_id = request.form.get("teacher_id")
    teacher_data = UserData.query.filter_by(teacher_id=teacher_id).first()

    if teacher_data:
        db.session.delete(teacher_data)
        db.session.commit()
        flash(f"講師番号 {teacher_id} を削除しました！", "success")
    else:
        flash(f"講師番号 {teacher_id} は存在しません。", "danger")

    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
