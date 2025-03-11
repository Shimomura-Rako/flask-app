from pushbullet import Pushbullet

def send_push_notification(api_key, message):
    pb = Pushbullet(api_key)
    push = pb.push_note("DMM英会話 - 予約空き通知", message)

    if push.get("active"):
        print("通知を送信しました！")
    else:
        print("通知の送信に失敗しました。")

# APIキーを入力（環境変数で指定しても良い）
api_key = input("Pushbullet APIキーを入力: ")
send_push_notification(api_key, "予約可能な空き枠があります！")
