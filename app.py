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

if not API_KEY:
    print("⚠️ 環境変数が設定されていません。setup.sh を実行してください！")
    exit(1)

pb = pushbullet.Pushbullet(API_KEY)

# Flask設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')  # Render用にDB設定を変更
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

# 初期データとして、保存された講師情報を動的に処理
last_notify_counts = {}

def send_push_notification(teacher_id, name, user_pushbullet_token):
    """Push通知を送信"""
    url = f"https://eikaiwa.dmm.com/teacher/schedule/{teacher_id}/"
    pb.push_link(f"{name} レッスン開講通知", url, device_token=user_pushbullet_token)
    print(f"📢 Push通知送信: {name} - {url}")

def get_teacher_name(teacher_id):
    """講師名を取得"""
    url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    teacher_name = soup.find("h1")

    if teacher_name:
        return teacher_name.get_text(strip=True)
    else:
        return None

def check_teacher_availability():
    """データベースに登録された全ユーザーの予約状況を確認し、必要なら通知"""
    users = UserData.query.all()  # データベース内の全ユーザーを取得
    for user in users:
        teacher_id = user.teacher_id
        user_token = user.pushbullet_token

        # 講師名を取得
        teacher_name = get_teacher_name(teacher_id)
        if teacher_name:
            print(f"講師名: {teacher_name}")
        else:
            print(f"⚠️ {teacher_id} の講師名が見つかりません")

        load_url = f"https://eikaiwa.dmm.com/teacher/schedule/{teacher_id}/"
        html = requests.get(load_url)
        soup = BeautifulSoup(html.content, "html.parser")

        if html.status_code != 200:
            print(f"⚠️ {teacher_id} のページが見つかりません (ステータスコード: {html.status_code})")
            continue

        # 予約可能な時間を確認
        fileText = "\n".join([element.text for element in soup.find_all(class_="oneday")])
        current_count = fileText.count("予約可")

        # 通知が必要な場合のみ送信
        if current_count > last_notify_counts.get(teacher_id, 0):
            send_push_notification(teacher_id, teacher_name, user_token)
            last_notify_counts[teacher_id] = current_count

# APSchedulerを使って定期的にスクレイピングを実行
scheduler = BackgroundScheduler()
scheduler.add_job(check_teacher_availability, 'interval', minutes=1)  # 1分ごとに実行
scheduler.start()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        teacher_id = request.form.get("teacher_id")
        pushbullet_token = request.form.get("pushbullet_token")

        if not teacher_id or not pushbullet_token:
            flash("すべての項目を入力してください！", "danger")
        else:
            # ユーザーのデータをデータベースに保存
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
