from flask import Flask, request, jsonify
import os

app = Flask(__name__)

API_KEY = "pamoka_dmm2025"  # ← ここにAPIキーを設定！

@app.route('/register', methods=['POST'])
def register():
    key = request.headers.get("X-API-Key")  # APIキーを取得
    if key != API_KEY:  # APIキーが違う場合、アクセス拒否！
        return jsonify({"error": "Unauthorized"}), 403  

    email = request.json.get('email')
    return jsonify({"message": f"{email} registered!"}), 201

if __name__ == '__main__':
    app.run()
