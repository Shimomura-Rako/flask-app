import os
import requests
from flask_sqlalchemy import SQLAlchemy
from pushbullet import Pushbullet
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, flash, redirect, session

# Flask設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Renderではデータが消える可能性あり
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

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

# 共通のUser-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 講師名を取得する関数
def get_teacher_name(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    try:
        response = requests.get(load_url, headers=HEADERS, timeout=5, allow_redirects=True)

        # もしリダイレクトされてトップページに戻ったら、存在しないと判断
        if response.url == "https://eikaiwa.dmm.com/":
            print(f"⚠ 存在しない講師ID: {teacher_id}（リダイレクト検出）")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        teacher_name_tag = soup.find("h1")
        
        if teacher_name_tag:
            return teacher_name_tag.text.strip()

        print(f"⚠ 講師 {teacher_id} の情報が見つかりません (ページ構造が変わった可能性)")
    except requests.exceptions.RequestException as e:
        print(f"⚠ リクエストエラー: {e}")
    
    return None

# 予約状況を確認し、必要なら通知を送る
def check_teacher_availability():
    with app.app_context():
        users = UserData.query.all()
        for user in users:
            current_count = get_available_slots(user.teacher_id)
            if current_count is None:
                print(f"⚠ {user.teacher_name} ({user.teacher_id}) のデータが取得できません。削除済みかも。")
                continue  

            print(f"📊 {user.teacher_name} ({user.teacher_id}) - 予約可数: {current_count}, 前回: {user.last_available_count}")
            if current_count > user.last_available_count:
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
    if "teacher_list" not in session:
        session["teacher_list"] = []  # 初回アクセス時に空リストを作成

    # **全体の登録数チェック（全ブラウザ合計で10件まで）**
    total_teachers = UserData.query.count()
    if total_teachers >= 10:
        flash("全体の登録が最大10件に達しました！", "danger")
        return redirect("/")

    if request.method == "POST":
        # **ブラウザごとの登録数チェック（1つのブラウザで10件まで）**
        if len(session["teacher_list"]) >= 10:
            flash("このブラウザでは最大10件までしか登録できません！", "danger")
            return redirect("/")

        teacher_id = request.form.get("teacher_id")
        pushbullet_token = request.form.get("pushbullet_token")

        if not teacher_id or not pushbullet_token:
            flash("すべての項目を入力してください！", "danger")
        else:
            # **すでに登録されている講師をブロック**
            existing_teacher = UserData.query.filter_by(teacher_id=teacher_id).first()
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
                    pushbullet_token=pushbullet_token
                )
                db.session.add(new_data)
                db.session.commit()

                # **セッションに登録した講師IDを追加**
                session["teacher_list"].append(teacher_id)
                session.modified = True

                flash(f"{teacher_name} (講師番号: {teacher_id}) を登録しました！", "success")

        return redirect("/")
    
    all_data = UserData.query.all()
    return render_template("index.html", all_data=all_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
