import os
import requests
from flask_sqlalchemy import SQLAlchemy
from pushbullet import Pushbullet  # 修正
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, flash, redirect

# Flask設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Renderではデータが消える可能性あり
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
            return None  # 存在しないと判断

        soup = BeautifulSoup(response.content, "html.parser")
        teacher_name_tag = soup.find("h1")
        
        if teacher_name_tag:
            return teacher_name_tag.text.strip()

        print(f"⚠ 講師 {teacher_id} の情報が見つかりません (ページ構造が変わった可能性)")
    except requests.exceptions.RequestException as e:
        print(f"⚠ リクエストエラー: {e}")
    
    return None  # エラー時は None を返す


# 「予約可」の数を取得
def get_available_slots(teacher_id):
    load_url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    try:
        response = requests.get(load_url, headers=HEADERS, timeout=5)
        if response.status_code == 404:
            print(f"⚠ 講師 {teacher_id} のページが存在しません (HTTP 404)")
            return None

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

# Pushbullet通知を送信
def send_push_notification(user_token, teacher_id, name):
    try:
        pb_user = Pushbullet(user_token)  # 修正
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
            if current_count is None:
                print(f"⚠ {user.teacher_name} ({user.teacher_id}) のデータが取得できません。削除済みかも。")
                continue  # 予約可が取得できない場合はスキップ

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


# 今ある `index()` 関数を削除して、このコードを追加する
@app.route("/", methods=["GET", "POST"])
def index():
    if "teacher_list" not in session:
        session["teacher_list"] = []  # 初回アクセス時に空リストを作成

    # **データベースから正しい登録データを取得し、session を更新**
    db_teacher_ids = [user.teacher_id for user in UserData.query.all()]
    session["teacher_list"] = db_teacher_ids  # データベースと同期
    session.modified = True  # セッションを更新

    total_teachers = UserData.query.count()
    if total_teachers >= 10:
        flash("全体の登録が最大10件に達しました！", "danger")
        return redirect("/")

    if request.method == "POST":
        if len(session["teacher_list"]) >= 10:
            flash("このブラウザでは最大10件までしか登録できません！", "danger")
            return redirect("/")

        teacher_id = request.form.get("teacher_id")
        pushbullet_token = request.form.get("pushbullet_token")

        if not teacher_id or not pushbullet_token:
            flash("すべての項目を入力してください！", "danger")
        else:
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

                session["teacher_list"].append(teacher_id)
                session.modified = True

                flash(f"{teacher_name} (講師番号: {teacher_id}) を登録しました！", "success")

        return redirect("/")
    
    # **データベースから取得した全講師を表示（セッションが消えても大丈夫）**
    all_data = UserData.query.all()
    return render_template("index.html", all_data=all_data)




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)  # 本番では debug=False

