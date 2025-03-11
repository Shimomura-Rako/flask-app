from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet

app = Flask(__name__)

# スクレイピング関数
def get_teacher_name(teacher_id):
    url = f"https://eikaiwa.dmm.com/teacher/index/{teacher_id}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    teacher_name = soup.find("h1")

    if teacher_name:
        return teacher_name.get_text(strip=True)
    else:
        return None

# Pushbullet通知関数
def send_push_notification(api_key, message):
    pb = Pushbullet(api_key)
    push = pb.push_note("DMM英会話 - 予約空き通知", message)

    if push.get("active"):
        print("通知を送信しました！")
    else:
        print("通知の送信に失敗しました。")

# ホームページ
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        teacher_id = request.form["teacher_id"]
        api_key = request.form["api_key"]
        teacher_name = get_teacher_name(teacher_id)

        if teacher_name:
            send_push_notification(api_key, f"{teacher_name} の空き枠があります！")
            return render_template("index.html", teacher_name=teacher_name, success=True)
        else:
            return render_template("index.html", error="講師名が取得できませんでした。", success=False)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

