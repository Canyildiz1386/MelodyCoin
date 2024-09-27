import hmac
import hashlib
from flask import Flask, request, abort, render_template, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/melodyCoinDB"
mongo = PyMongo(app)

SECRET_KEY = "your_secret_key"

def generate_hash(user_id, username):
    data = f"user_id={user_id}&username={username}"
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

def validate_hash(user_id, username, received_hash):
    expected_hash = generate_hash(user_id, username)
    return hmac.compare_digest(expected_hash, received_hash)

@app.route('/input_page', methods=['GET', 'POST'])
def input_page():
    user_id = request.args.get('user_id')
    username = request.args.get('username')
    received_hash = request.args.get('hash')

    if not validate_hash(user_id, username, received_hash):
        abort(403)

    if request.method == 'POST':
        nickname = request.form['nickname']

        existing_user = mongo.db.users.find_one({"user_id": user_id})

        if not existing_user:
            user = {
                "user_id": user_id,
                "username": username,
                "nickname": nickname,
                "hash": received_hash,
                "level": 1,  
                "profit": 0 
            }
            mongo.db.users.insert_one(user)
        else:
            mongo.db.users.update_one({"user_id": user_id}, {"$set": {"nickname": nickname}})

        return redirect(url_for('home_page', user_id=user_id, username=username, hash=received_hash, nickname=nickname))

    return render_template('input page/input.html', user_id=user_id, username=username, hash=received_hash)

@app.route('/')
def home_page():
    user_id = request.args.get('user_id')
    username = request.args.get('username')
    received_hash = request.args.get('hash')
    nickname = request.args.get('nickname')

    if not user_id or not username or not received_hash:
        abort(403)

    if not validate_hash(user_id, username, received_hash):
        abort(403)

    if not nickname:
        return redirect(url_for('input_page', user_id=user_id, username=username, hash=received_hash))

    user = mongo.db.users.find_one({"user_id": user_id})

    if not user:
        return redirect(url_for('input_page', user_id=user_id, username=username, hash=received_hash))

    return render_template('home page/home.html', username=user["username"], user_id=user["user_id"], nickname=user["nickname"], level=user["level"], profit=user["profit"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
