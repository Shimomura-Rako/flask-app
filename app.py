import os
import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, jsonify, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import pushbullet
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()
API_KEY = os.getenv("API_KEY")
TEACHERS_RAW = os.getenv("TEACHERS")

if not API_KEY or not TEACHERS_RAW:
    print("⚠️ 環境変数が設定されていません。setup.sh を実行してください！")
    exit(1)

pb = pushbullet.Pushbullet(API_KEY)

# Flask設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Renderで使う場合、SQLiteでも問題ない
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

# 講師情報を辞書に変換
teachers = {t.split(":")[0]: t.split(":")[1] for t in TEACHERS_RAW.split(",")}
last_notify_counts = {id: 0 for id in teachers}

def send_push_notification(teacher_id, name):
    """Push通知を送信"""
    url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    pb.push_link(f"{name} レッスン開講通知", url)
    print(f"📢 Push通知送信: {name} - {url}")

def check_teacher_availability(teacher_id, name):
    """予約状況を確認して、通知が必要なら送信"""
    global last_notify_counts
    print(f"⏳ {name} の状況を確認中...")

    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    html = requests.get(load_url)
    soup = BeautifulSoup(html.content, "html.parser")

    if html.status_code != 200:
        print(f"⚠️ {name} のページが見つかりません: {load_url} (ステータスコード: {html.status_code})")
        return

    # 予約可能な時間を確認
    fileText = "\n".join([element.text for element in soup.find_all(class_="oneday")])
    current_count = fileText.count("予約可")

    if current_count > last_notify_counts[teacher_id]:
        send_push_notification(teacher_id, name)
        last_notify_counts[teacher_id] = current_count

def job():
    """定期的に全ての講師の予約状況を確認"""
    for teacher_id, name in teachers.items():
        check_teacher_availability(teacher_id, name)

# APSchedulerを使って定期的にスクレイピングを実行
scheduler = BackgroundScheduler()
scheduler.add_job(job, 'interval', minutes=1)  # 1分ごとに実行
scheduler.start()

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
    return render_template("index.html", all_data=all_data)  # ここを変更！

if __name__ == "__main__":
    # Render用にポートとホスト設定を変更
    port = int(os.environ.get("PORT", 5000))  # Renderが指定したポートを使用
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)  # 全てのIPアドレスからアクセス可能にする

