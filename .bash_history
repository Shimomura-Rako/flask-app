ls
less app.py
bash setup.sh
ls
python3 --version
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install requests pushbullet.py beautifulsoup4 schedule python-dotenv flask
pip3 install --break-system-packages requests pushbullet.py beautifulsoup4 schedule python-dotenv flask
python3 -c "import flask; print('Flask is installed')"
echo 'from flask import Flask
app = Flask(__name__)
@app.route("/")
def home():
    return "Hello, Flask on WSL!"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)' > app.py
ls
nano app.pu
nano app.py
ls
python3 app.py
nano scraping.py
python3 scraping.py
nano scraping.py
python3 scraping.py
nano push_notification.py
python3 push_notification.py
scraping.py
nano scraping.py
python3 scraping.py
nano scraping.py
python3 scraping.py
nano scraping.py
python3 scraping.py
nano scraping.py
python3 scraping.py
nano app.py
mkdir templates
nano templates/index.html
pwd
ls
python3 app.py
git init
git branch -m main
git remote add origin https://github.com/yourusername/your-repository-name.git
git add .
git commit -m "First commit"
git push -u origin main
git branch
git checkout -b main
git push -u origin main
git add .
git commit -m "Initial commit"
git push -u origin main
git config --global user.name "miwanakayo"
git config --global user.email "mi_wa82co65626@yahoo.co.jp"
git config --global user.name
git config --global user.email
git add .
git commit -m "Initial commit"
git push -u origin main
git remote -v
git remote set-url origin https://github.com/Shimomura-Rako/flask-app.git
git push -u origin main
pip freeze > requirements.txt
ls
git add requirements.txt
git commit -m "Add requirements.txt"
git push origin main
git pull origin main
git pull --no-rebase origin main
git pull origin main --allow-unrelated-histories
git pull --no-rebase origin main
git pull origin main --allow-unrelated-histories
git config pull.rebase false
git pull origin main
git pull origin main --allow-unrelated-histories
git push origin main
git status
cloud-init
ls
nano requirements.txt
pip freeze
pip freeze > requirements.txt
pip freeze
pip uninstall cloud-init
python3 -m venv myenv
sudo apt install python3.12-venv
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
pip uninstall cloud-init
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Remove cloud-init from requirements.txt"
git push origin main
pip freeze
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
pip freeze
pip install -r requirements.txt
pip freeze
cat requirements.txt
ls -l
source myenv/bin/activate  # 仮想環境をアクティベート
pip freeze > requirements.txt  # 現在の依存関係をrequirements.txtに出力
cat requirements.txt
pip list
pip install -r requirements.txt
ls
ls l
ls -l
pip install flask requests beautifulsoup4 # 必要なパッケージを追加
ls -l
pip freeze
pip freeze > requirements.txt
ls -l
nano requirements.txt
git add requirements.txt
git commit -m "Update requirements.txt with installed dependencies"
git push origin main
pip install pushbullet.py
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add pushbullet.py to requirements.txt"
git push origin main
ls -l
nano requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add schedule and python-dotenv to requirements.txt"
git push origin main
myenv/
.cache/
git add .gitignore  # .gitignoreを追加
git commit -m "Add myenv and pip cache to .gitignore"  # コミット
git push origin main  # GitHubにプッシュ
nano app.py
git add app.py
git commit -m "Updated app.py to use 0.0.0.0 and correct port"
git push origin main
ls -l
nano app.py
cp import os
import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, jsonify, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import pushbullet
from bs4 import BeautifulSoup
from dotenv import load_dotenv
# 環境変数をロード
load_dotenv() API_KEY = os.getenv("API_KEY")
TEACHERS_RAW =                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                ls
rm app.py
nano app.py
cd templates
ls
rm index.html
nano index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
cd ..
ls
nano app_bk.py
nano app.py
cd templates
ll
rm index.html
nano index.html
cd ..
ls
cp app.py app_bk4.py
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls -l
cd templates
ll
rm index_bk.html
cp index.html index_bk.html
rm index.html
nano index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
pwd
ls
cp index.html index_bk2.html
rm  index.html
nano  index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
cd ..
ls
view app.py
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
pwd
app.py
nano app.py
ls
cd templates
ll
nano index.html
cp index.html index_bk3.html
rm index.html
nano index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
cd ..
ls
cp app.py app_bk5.py
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git commit -m "Update app.py and index.html"
git push origin main
nano app.py
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git commit -m "Update app.py and index.html"
git push origin main
rm app.py
nano app.py
ls
cd templates
ls
rm index.html
nano index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
cd ..
ls
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
rm app.py
nano import os
import requests
from flask_sqlalchemy import SQLAlchemy
import pushbullet
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, flash, redirect
import logging
# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Flask設定
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
# データベースのモデル
class UserData(db.Model):
# 初回実行時にデータベースを作成
with app.app_context():
# 講師ページから「予約可」の数を取得
def get_available_slots(teacher_id):
# Pushbullet通知を送信する関数
def send_push_notification(user_token, teacher_id, name):
# 予約状況を確認し、必要なら通知を送る
def check_teacher_availability():
scheduler.add_job(check_teacher_availability, 'interval', minutes=1)
scheduler.start()
@app.route("/", methods=["GET", "POST"])
def index():
# 講師データを削除するルート
@app.route("/delete_teacher", methods=["POST"])
def delete_teacher():
if __name__ == "__main__":;     port = int(os.environ.get("PORT", 5000))
ls
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git commit -m "Update app.py and index.html"
git push origin main
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git commit -m "Update app.py and index.html"
git push origin main
nano app.py
ls
cd templates
]ls
ls -l
nano index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls -l
cat index.html
cd ..
ls
nano app.py
cd templates
ll
nano index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
git add app.py index.html
git commit -m "Updated app.py and index.html"
git push origin main  # または使用しているブランチ名
git add app.py templates/index.html
ls -l
cd ..
git add app.py templates/index.html
git commit -m "Updated app.py and index.html"
git push origin main
git branch
git log
git push origin main
git add app.py templates/index.html
git commit -m "Updated app.py and index.html"
git push origin main
ls -l
view app.py
nano app.py
cp app.py app2.py
rm app_bk.py
rm app_bk2.py
rm app_bk3.py
ls
nano app.py
ps aux | grep vim
kill 1221
nano app.py
ls -a
rm app.py.swp
rm .app.py.swp
nano app.py
git add app.py templates/index.html
git commit -m "Updated app.py and index.html"
git push origin main
pwd
ls
rm app_bk5.py
rm  app_bk4.py
ls
rm  app2.py
cp app.py app_bk.py
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Updated app.py and index.html"
git push origin main
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Updated app.py and index.html"
git push origin main
pwd
ls
cd templates
ls
nano index.html
cd ..
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
cd templates
nano index.html
cd ..
ls
cd templates
nano index.html
cd ..
ls
nano app.py
git commit -m "Update app.py and index.html"
git push origin main
nano app.py
git commit -m "Update app.py and index.html"
git push origin main
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
rm app.py
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
rm app.py
nano app.py
ls
cd templates
ks
ls
nano index.html
rm index.html
nano index.html
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
cd ..
ls
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
nano app.py
git commit -m "Update app.py and index.html"
git push origin main
rm app.py
nano app.py
git commit -m "Update app.py and index.html"
git push origin main
nano app.py
cd templates
nano index.html
rm index.html
nano index.html
cd ..
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
nano test_api.py
curl -X POST http://127.0.0.1:5000/register      -H "Content-Type: application/json"      -d '{"email": "test@example.com"}'
python3 test_api.py
pwd
cd ../..
ls
cd python
pwd
curl -X POST http://127.0.0.1:5000/register      -H "Content-Type: application/json"      -d '{"email": "test@example.com"}'
]curl -X POST http://127.0.0.1:5000/register      -H "Content-Type: application/json"      -d '{"email": "hacker@example.com"}'
sudo apt update
sudo apt install curl
curl -X POST http://127.0.0.1:5000/register      -H "Content-Type: application/json"      -d '{"email": "hacker@example.com"}'
curl -X POST http://127.0.0.1:5000/register      -H "Content-Type: application/json"      -d '{"email": "hacker@example.com"}'
curl -X POST http://127.0.0.1:5000/register      -H "X-API-Key: pamoka_dmm2025" \  # ここにAPIキーをつける！
curl -X POST http://127.0.0.1:5000/register -H "X-API-Key: pamoka_dmm2025" -H "Content-Type: application/json" -d '{"email": "friend@example.com"}'
curl -X POST http://127.0.0.1:5000/register_teacher      -H "Content-Type: application/json"      -d '{"email": "a@example.com", "teacher_name": "John Smith"}'
curl -X POST http://127.0.0.1:5000/register_teacher      -H "Content-Type: application/json"      -d '{"email": "a@example.com", "teacher_name": "John Smith"}'
curl -X POST http://127.0.0.1:5000/register_teacher      -H "Content-Type: application/json"      -d '{"email": "a@example.com", "teacher_name": "John Smith"}'
nano test_api.py
curl -X POST https://your-app.onrender.com/register      -H "Content-Type: application/json"      -d '{"email": "hacker@example.com"}'
pwd
python3 test_api.py
nano test_api.py
python3 test_api.py
pwd
ls -l
rm test_api.py
nano test_api.py
rm test_api.py
nano test_api.py
cd  templates
ll
rm index_bk*
ls
ll
cd ..
ls
ll
cd templates
nano register.html
cd ..
ls
python3 test_api.py
ls
cd templates
ls
cd ..
ls
nano app.py
nano app.@y
nano app.py
nano test.py
python test.py
python3 test.py
git --version
ls
mkdir my_project
cd my_project
git init
nano test.txt
echo "Hello, Git!" > test.txt
git add test.txt
echo "新しい行を追加！"
cat test.txt
ls
cat test.txt
echo "Hello, Git!" > test.txt  # ファイル作成
git add test.txt  # Gitに登録
git commit -m "最初のファイル追加"
echo "新しい行を追加！" >> test.txt
cat test.txt
git checkout test.txt
cat test.txt
git log --onelin
git log --oneline
git log
ls
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
pwd
ls
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
pwd
ls
cd templates
ls
nano index.html
cd ..
ls
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
nano app.py
git add app.py templates/index.html
git commit -m "Update app.py and index.html"
git push origin main
ls
rm app.py
nano app.py
cd templates
ls
nano set_user.html
git status
ls
pwd
cd ..
ls
git add .
git add app.py templates/set_user.html
git commit -m "Add /set_user page and user ID input support"
git push origin main
pwd
cd templates
ls
pwd
rm set_user.html
nano set_user.html
cd ,,
cd ..
git add .
git commit -m "Add /set_user page and user ID input support"
git push origin main
cd templates
ls
rm set_user.html
nano set_user.html
cd ..
ls
pwd
cd templates
ls
rm set_user.html
nano set_user.html
cd ..
ls
nano app.py
rm app.py
nano app.py
git add .
git commit -m "Add /set_user page and user ID input support"
git push origin main
nano app.py
rm app.py
nano app.py
git add .
git commit -m "Add /set_user page and user ID input support"
git push origin main
ls
nano app.py
git add .
git commit -m "Add /set_user page and user ID input support"
git push origin main
ls
rm app_bk.py
cp app.py app_bk.py
rm app.py
nano app.py
cd templates
ls
cp set_user.html set_user_bk.html
rm set_user.html
nano set_user.html
git add .
git commit -m "Add /set_user page and user ID input support"
git push origin main
cd templates
ls
nano set_user.html
cd ..
ls
git add .
git commit -m "Add /set_user page and user ID input support"
git push origin main
cd templates
ls
nano set_user.html
cd ..
ls
nano app.py
git add 