import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet
import schedule
import time

# 最初に講師IDとAPIキーを入力
teacher_id = input("講師IDを入力: ")
api_key = input("Pushbullet APIキーを入力: ")

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

# スクレイピングと通知送信を定期実行する関数
def job():
    teacher_name = get_teacher_name(teacher_id)

    if teacher_name:
        print(f"講師名: {teacher_name}")
        
        # 空き枠チェック（今回は仮に通知送信）
        send_push_notification(api_key, f"{teacher_name} の空き枠があります！")
    else:
        print("講師名が取得できませんでした。")

# スケジュール設定（1時間ごとに実行）
schedule.every(50).seconds.do(job)

# 定期的に実行
while True:
    schedule.run_pending()
    time.sleep(1)  # 1秒ごとに待機

