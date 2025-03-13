import os
import requests
from flask_sqlalchemy import SQLAlchemy
import pushbullet
from bs4 import BeautifulSoup
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
        if response.status_code != 200:
            print(f"⚠ 講師 {teacher_id} のページが見つかりません (HTTP {response.status_code})")
            return None
        soup = BeautifulSoup(response.content, "html.parser")
        # 修正箇所: クラス指定を除去してh1タグを取得する
        teacher_name_tag = soup.find("h1")  # #修正箇所#
        if teacher_name_tag:
            return teacher_name_tag.text.strip()
        print(f"⚠ 講師 {teacher_id} の情報が見つかりません (ページ構造が変わった可能性)")
    except requests.exceptions.RequestException as e:
        print(f"⚠ リクエストエラー: {e}")
    return None  # エラー時は None を返す

# 講師ページから「予約可」の数を取得
def get_available_slots(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(load_url, headers=headers, timeout=5)
        if response.status_code == 404:
            print(f"⚠ 講師 {teacher_id} のページが存在しません (HTTP 404)")
            return None  # ページが存在しない場合 None を返す #修正箇所#

        if response.status_code != 200:
            print(f"⚠ 講師 {teacher_id} のページ取得失敗 (HTTP {response.status_code})")
            return 0

        soup = BeautifulSoup(response.content, "html.parser")
        available_slots = len(soup.find_all(string="予約可"))

        print(f"🔍 講師 {teacher_id} の予約可数: {available_slots}")

        return available_slots

    except requests.exceptions.RequestException as e:
        print(f"⚠ リクエストエラー: {e}")

    return 0

# Pushbullet通知を送信する関数
def send_push_notification(user_token, teacher_id, name):
    try:
        pb_user = pushbullet.Pushbullet(user_token)
        url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
        pb_user.push_link(f"{name} レッスン開講通知", url)
        print(f"📢 Push通知送信: {name} - {url}")
    except Exception as e:
        print(f"⚠ Pushbullet通知の送信に失敗しました: {e}")

# 予約状況を確認し、必要なら通知を送る
def check_teacher_availability():
    with app.app_context():
        users = UserData.query.all()
        for user in users:
            current_count = get_available_slots(user.teacher_id)
            # None になっている場合（講師削除の可能性）
            if current_count is None:  # #修正箇所#
                print(f"⚠ {user.teacher_name} ({user.teacher_id}) のデータが取得できません。削除済みかも。")
                continue  # 予約可が取得できない場合はスキップ

            print(f"📊 {user.teacher_name} ({user.teacher_id}) - 予約可数: {current_count}, 前回: {user.last_available_count}")
            if current_count > user.last_available_count:
                if current_count > 0:
                    send_push_notification(user.pushbullet_token, user.teacher_id, user.teacher_name)
                    print(f"📢 通知送信: {user.teacher_name}")
            user.last_available_count = current_count
            db.session.commit()
            print(f"✅ {user.teacher_name} の last_available_count を {user.last_available_count} に更新")

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
                new_data = UserData(
                    teacher_id=teacher_id, 
                    teacher_name=teacher_name, 
                    pushbullet_token=pushbullet_token, 
                    last_available_count=0
                )
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


