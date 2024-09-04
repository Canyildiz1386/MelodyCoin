from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from datetime import datetime, timedelta, timezone
import os
from werkzeug.utils import secure_filename
from flask_admin.form import ImageUploadField
from markupsafe import Markup
from PIL import Image
from flask_login import UserMixin


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "static/nfts"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"


def format_thousands(value):
    return "{:,}".format(value)


app.jinja_env.filters["format_thousands"] = format_thousands

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(150), nullable=False)
    tg_id = db.Column(db.String(100), nullable=True)
    tg_username = db.Column(db.String(150), nullable=True)
    level = db.Column(db.Integer, default=1)
    profit = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=0)
    join_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    last_reward_date = db.Column(db.Date, nullable=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    referred_users = db.relationship(
        "User", backref=db.backref("referrer", remote_side=[id]), lazy=True
    )

    def coins_for_next_level(self):
        return 100 * (2 ** (self.level - 1))

    def progress_to_next_level(self):
        coins_for_this_level = 100 * (2 ** (self.level - 2)) if self.level > 1 else 0
        total_required_for_level = self.coins_for_next_level() - coins_for_this_level
        return max(
            0,
            min(
                ((self.coins - coins_for_this_level) / total_required_for_level) * 100,
                100,
            ),
        )

    def check_level_up(self):
        while self.coins >= self.coins_for_next_level():
            self.level += 1

    def days_since_joined(self):
        return (datetime.now(timezone.utc).date() - self.join_date).days + 1

    def can_collect_reward(self):
        if not self.last_reward_date:
            return True
        return (datetime.now(timezone.utc).date() - self.last_reward_date).days >= 1

    def next_collect_time(self):
        if not self.last_reward_date:
            return None
        return datetime.combine(
            self.last_reward_date, datetime.min.time(), timezone.utc
        ) + timedelta(days=1)

    def collect_reward(self, day, reward_amount):
        if self.can_collect_reward():
            self.coins += reward_amount
            self.last_reward_date = datetime.now(timezone.utc).date()
            self.check_level_up()
            db.session.commit()
            return True
        return False

    def calculate_reward(self, day):
        base_reward = 10
        return base_reward * (2 ** (day - 1))


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)


class NFT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    profit = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    is_vip = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    owner = db.relationship("User", backref="owned_nfts", lazy=True)


class AdminUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    reward = db.Column(db.Integer, nullable=False)


class UserTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)


@app.before_request
def create_wallet():
    if Wallet.query.count() == 0:
        wallet = Wallet(address="your_predefined_wallet_address")
        db.session.add(wallet)
        db.session.commit()


@app.route("/loading")
def loading():
    return render_template("loading page/loading.html")


@app.route("/nickname", methods=["GET", "POST"])
def nickname():
    if "nickname" in session:
        return redirect(url_for("loading"))

    tg_id = request.args.get("tg_id")
    tg_username = request.args.get("username")
    referrer_id = request.args.get("referrer_id")  

    if request.method == "POST":
        nickname = request.form["nickname"]
        
        if not nickname:
            return render_template("input page/input.html", error="Nickname is required!")

        user = User.query.filter_by(nickname=nickname).first()

        if not user:
            user = User(
                nickname=nickname,
                tg_id=tg_id, 
                tg_username=tg_username,  
                level=1,
                profit=0,
                coins=100,  # Give 100 coins to the new user
                referrer_id=referrer_id  # Set the referrer ID if present
            )
            db.session.add(user)

            # If there's a referrer, reward both users
            if referrer_id:
                referrer = User.query.filter_by(id=referrer_id).first()
                if referrer:
                    referrer.coins += 100  # Give 100 coins to the referrer
                    db.session.commit()

            db.session.commit()

        # Save user data to session
        session["nickname"] = user.nickname
        session["level"] = user.level
        session["profit"] = user.profit
        session["coins"] = user.coins

        return redirect(url_for("loading"))

    return render_template("input page/input.html")


@app.route("/")
def home():
    if "nickname" not in session:
        return redirect(url_for("nickname"))
    nickname = session.get("nickname")
    user = User.query.filter_by(nickname=nickname).first()
    if user:
        user.check_level_up()
        db.session.commit()
        session["level"] = user.level
        session["coins"] = user.coins
    return render_template(
        "home page/home.html",
        nickname=nickname,
        level=session.get("level", 1),
        profit=session.get("profit", 0),
        coins=session.get("coins", 0),
        progress=user.progress_to_next_level(),
    )


@app.route("/daily-reward", methods=["GET", "POST"])
def daily_reward():
    if "nickname" not in session:
        return redirect(url_for("nickname"))

    nickname = session.get("nickname")
    user = User.query.filter_by(nickname=nickname).first()

    if user.last_reward_date:
        days_since_last_collect = (
            datetime.now(timezone.utc).date() - user.last_reward_date
        ).days
        next_active_day = user.days_since_joined() - days_since_last_collect + 1
    else:
        next_active_day = 1

    if request.method == "POST":
        day = user.days_since_joined()
        reward_amount = user.calculate_reward(next_active_day)
        if reward_amount and user.collect_reward(next_active_day, reward_amount):
            session["coins"] = user.coins
            return redirect(url_for("daily_reward"))
        error = (
            "You have already collected your reward today. Please come back tomorrow."
        )
        return render_template(
            "daily reward page/daily.html",
            days_since_joined=user.days_since_joined(),
            coins=session.get("coins", 0),
            error=error,
            next_active_day=next_active_day,
            can_collect_reward=user.can_collect_reward(),
            next_collect_time=user.next_collect_time(),
        )

    return render_template(
        "daily reward page/daily.html",
        days_since_joined=user.days_since_joined(),
        coins=session.get("coins", 0),
        next_active_day=next_active_day,
        can_collect_reward=user.can_collect_reward(),
        next_collect_time=user.next_collect_time(),
        calculate_reward=user.calculate_reward,
    )


@app.route("/wallet", methods=["GET", "POST"])
def wallet():
    wallet = Wallet.query.first()
    if "nickname" not in session:
        return redirect(url_for("nickname"))
    nickname = session.get("nickname")
    user = User.query.filter_by(nickname=nickname).first()
    if request.method == "POST":
        wallet_address = request.form.get("wallet_address")
        if wallet_address:
            user.wallet_address = wallet_address
            db.session.commit()
            session["wallet_address"] = wallet_address
    return render_template("wallet page/wallet.html", wallet_address=wallet.address)


@app.route("/nfts")
def nfts():
    sort_by = request.args.get("sort_by", "default")

    if sort_by == "price":
        nft_list = NFT.query.filter(NFT.user_id == None).order_by(NFT.price).all()
    elif sort_by == "vip":
        nft_list = NFT.query.filter(NFT.is_vip == True, NFT.user_id == None).all()
    else:
        nft_list = NFT.query.filter(NFT.user_id == None).all()

    return render_template("nfts page/nfts.html", nfts=nft_list)


if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admin = AdminUser.query.filter_by(username=username).first()
        if admin and admin.password == password:
            session["admin_logged_in"] = True
            session["admin_username"] = admin.username
            login_user(admin)
            return redirect(url_for("admin.index"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("Admin Page/admin_login.html")


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


@app.route("/admin-logout")
@login_required
def admin_logout():
    logout_user()
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return session.get("admin_logged_in")

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_login"))


class MyModelView(ModelView):
    def is_accessible(self):
        return session.get("admin_logged_in")

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_login"))


admin = Admin(
    app, name="Admin Panel", template_mode="bootstrap3", index_view=MyAdminIndexView()
)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(NFT, db.session))
admin.add_view(MyModelView(Wallet, db.session))
admin.add_view(MyModelView(Task, db.session))
admin.add_view(MyModelView(UserTask, db.session))


@app.route("/create_admin")
def create_admin():
    admin = AdminUser(username="admin", password="admin_password")
    db.session.add(admin)
    db.session.commit()
    return "Admin user created!"


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if "nickname" not in session:
        return redirect(url_for("nickname"))
    nickname = session.get("nickname")
    user = User.query.filter_by(nickname=nickname).first()
    if request.method == "POST":
        task_id = request.form.get("task_id")
        task = Task.query.get(task_id)
        user_task = UserTask.query.filter_by(user_id=user.id, task_id=task.id).first()
        if not user_task:
            user_task = UserTask(user_id=user.id, task_id=task.id, completed=True)
            user.coins += task.reward
            db.session.add(user_task)
            db.session.commit()
    active_tasks = (
        Task.query.join(UserTask, Task.id == UserTask.task_id, isouter=True)
        .filter((UserTask.completed == False) | (UserTask.completed.is_(None)))
        .all()
    )
    completed_tasks = (
        Task.query.join(UserTask)
        .filter(UserTask.user_id == user.id, UserTask.completed == True)
        .all()
    )
    return render_template(
        "tasks page/tasks.html",
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
    )


@app.route("/tapping")
def tapping():
    if "nickname" not in session:
        return redirect(url_for("nickname"))
    nickname = session.get("nickname")
    current_user = User.query.filter_by(nickname=nickname).first()
    if current_user:
        progress = current_user.progress_to_next_level()
    return render_template(
        "tapping page/tapping.html", current_user=current_user, progress=progress
    )


@app.route("/invite")
def invite():
    if "nickname" not in session:
        return redirect(url_for("nickname"))
    
    nickname = session.get("nickname")
    user = User.query.filter_by(nickname=nickname).first()
    referred_users = user.referred_users if user else []

    referral_link = f"https://t.me/Testmusicplayerx_bot?start={user.id}" if user else ""

    return render_template("invite page/invite.html", referred_users=referred_users, invite_link=referral_link)


@app.route("/level")
def level():
    if "nickname" not in session:
        return redirect(url_for("nickname"))
    nickname = session.get("nickname")
    current_user = User.query.filter_by(nickname=nickname).first()
    top_users = User.query.order_by(User.coins.desc()).limit(10).all()
    return render_template(
        "level page/level.html", top_users=top_users, current_user=current_user
    )


from flask import jsonify


@app.route("/tapping/add-coin", methods=["POST"])
def add_coin():
    nickname = session.get("nickname")
    user = User.query.filter_by(nickname=nickname).first()
    if user:
        user.coins += 1  
        user.check_level_up()  
        db.session.commit()  
        session["coins"] = user.coins  

        return jsonify(
            {
                "coins": user.coins,  
                "level": user.level,  
                "progress": user.progress_to_next_level(),  
                "profit": user.profit,  
            }
        )
    return jsonify({"error": "User not found"}), 404


class NFTModelView(ModelView):
    form_extra_fields = {
        "image": ImageUploadField(
            "Image",
            base_path=os.path.join(
                os.path.dirname(__file__), app.config["UPLOAD_FOLDER"]
            ),
            relative_path=app.config["UPLOAD_FOLDER"],
            thumbnail_size=(100, 100, True),
        )
    }

    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ""
        return Markup(
            f'<img src="{url_for("static", filename=f"uploads/nfts/{model.image}")}" width="50">'
        )

    column_list = ["name", "description", "profit", "price", "image", "is_vip"]
    form_columns = ["name", "description", "profit", "price", "image", "is_vip"]
    column_formatters = {"image": _list_thumbnail}


@app.route("/nfts/purchase", methods=["POST"])
def purchase_nft():
    if "nickname" not in session:
        return redirect(url_for("nickname"))

    nickname = session.get("nickname")
    user = User.query.filter_by(nickname=nickname).first()

    nft_id = request.form.get("nft_id")
    nft = NFT.query.get(nft_id)

    if nft and user.coins >= nft.price:
        user.coins -= nft.price
        nft.user_id = user.id
        db.session.commit()

        session["coins"] = user.coins
        flash("Purchase successful!", "success")
    else:
        flash("Not enough coins to purchase this NFT.", "danger")

    return redirect(url_for("nfts"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=9080,host="0.0.0.0")
