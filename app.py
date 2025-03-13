import os
import requests
from flask import Flask, request, jsonify, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from pushbullet import Pushbullet
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler

# Flask設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

# データベースのモデル
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(100), nullable=False, unique=True)
    teacher_name = db.Column(db.String(255), nullable=True)
    pushbullet_token = db.Column(db.String(255), nullable=False)
    last_available_count = db.Column(db.Integer, default=0)  # 前回の「予約可」の数

# 初回実行時にデータベースを作成
with app.app_context():
    db.create_all()

# 講師名を取得する関数
def get_teacher_name(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(load_url, headers=headers, timeout=5)
        if response.status_code == 404:
            print(f"⚠ 講師 {teacher_id} のページが存在しません")
            return "NOT_FOUND"
        if response.status_code != 200:
            print(f"⚠ 講師 {teacher_id} のページが取得できません (HTTP {response.status_code})")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        teacher_name_tag = soup.find("h1")  # `class="teacher-name"` は不要
        return teacher_name_tag.text.strip() if teacher_name_tag else None

    except requests.exceptions.RequestException as e:
        print(f"⚠ リクエストエラー: {e}")
        return None

# 予約可の枠数を取得
def get_available_slots(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(load_url, headers=headers, timeout=5)
        if response.status_code != 200:
            return 0
        soup = BeautifulSoup(response.content, "html.parser")
        return len(soup.find_all(class_="status-open"))  # 「予約可」のクラスをカウント

    except requests.exceptions.RequestException as e:
        print(f"⚠ リクエストエラー: {e}")
        return 0

# 予約状況をチェックし通知を送る
def check_and_notify():
    with app.app_context():
        users = UserData.query.all()
        for user in users:
            teacher_name = get_teacher_name(user.teacher_id)

            if teacher_name == "NOT_FOUND":
                try:
                    pb = Pushbullet(user.pushbullet_token)
                    pb.push_note("DMM英会話", f"⚠ 講師 {user.teacher_id} のページが削除されました")
                except Exception as e:
                    print(f"⚠ Pushbulletエラー: {e}")
                continue

            if teacher_name is None:
                continue

            available_slots = get_available_slots(user.teacher_id)
            if available_slots > user.last_available_count:
                try:
                    pb = Pushbullet(user.pushbullet_token)
                    pb.push_note("DMM英会話", f"{teacher_name} の予約枠が増えました！")
                except Exception as e:
                    print(f"⚠ Pushbulletエラー: {e}")

            user.last_available_count = available_slots
            db.session.commit()

# 定期実行のスケジューラー設定
scheduler = BackgroundScheduler()
scheduler.add_job(check_and_notify, "interval", seconds=60)  # 1分ごとに実行
scheduler.start()

# 講師データを削除するルート
@app.route("/delete_teacher", methods=["POST"])
def delete_teacher():
    teacher_id = request.form.get("teacher_id")
    if not teacher_id:
        flash("講師IDを入力してください。", "warning")
        return redirect("/")

    teacher_data = UserData.query.filter_by(teacher_id=teacher_id).first()
    if teacher_data:
        db.session.delete(teacher_data)
        db.session.commit()
        flash(f"講師番号 {teacher_id} を削除しました！", "success")
    else:
        flash(f"講師番号 {teacher_id} は存在しません。", "danger")

    return redirect("/")

# 講師を登録するAPI
@app.route("/register", methods=["POST"])
def register_teacher():
    teacher_id = request.json.get("teacher_id")
    pushbullet_token = request.json.get("pushbullet_token")

    if not teacher_id or not pushbullet_token:
        return jsonify({"error": "講師IDとPushbulletトークンが必要です"}), 400

    if UserData.query.count() >= 10:
        return jsonify({"error": "登録できる講師は最大10件までです"}), 400

    existing_user = UserData.query.filter_by(teacher_id=teacher_id).first()
    if existing_user:
        return jsonify({"error": "この講師はすでに登録されています"}), 400

    teacher_name = get_teacher_name(teacher_id)
    if teacher_name in [None, "NOT_FOUND"]:
        return jsonify({"error": "講師情報が取得できませんでした。番号を確認してください。"}), 400

    new_user = UserData(teacher_id=teacher_id, teacher_name=teacher_name, pushbullet_token=pushbullet_token)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"講師 {teacher_name} が登録されました"}), 200

# Flaskアプリ起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
