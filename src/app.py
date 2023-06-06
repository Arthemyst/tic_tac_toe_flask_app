from datetime import datetime

from config import CustomEnvironment
from flask import (Flask, make_response, redirect, render_template, request,
                   session, url_for)
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from tic_tac_toe_game.ai.negamax import Negamax
from tic_tac_toe_game.player import AIPlayer, HumanPlayer
from tic_tac_toe_game.tic_tac_toe import TicTacToe

database_ip = CustomEnvironment.get_database_ip()
database_name = CustomEnvironment.get_database_name()
database_password = CustomEnvironment.get_database_password()
database_user = CustomEnvironment.get_database_user()

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{database_user}:{database_password}@{database_ip}:5432/{database_name}"
app.secret_key = CustomEnvironment.get_secret_key()
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
ai_algo = Negamax(2)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    player_stats = db.relationship("PlayerStats", backref="user", lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class PlayerStats(db.Model):
    __tablename__ = "playerstats"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    login_datetime = db.Column(db.DateTime)
    logout_datetime = db.Column(db.DateTime, nullable=True)
    credits = db.Column(db.Integer, default=10)
    wins = db.Column(db.Integer, default=0)
    loses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)

    def __init__(self, user_id, login_datetime):
        self.user_id = user_id
        self.login_datetime = login_datetime
        self.credits = 10
        self.wins = 0
        self.loses = 0
        self.ties = 0


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User.query.filter_by(username=username).first()
        if user:
            return """
            <script>
                alert("Username already exists");
                window.location.href = "{}";
            </script>
            """.format(
                url_for("login")
            )
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return """
        <script>
            alert("User created");
            window.location.href = "{}";
        </script>
        """.format(
            url_for("login")
        )
    return render_template("register.html")


@app.route("/check_session")
def check_session():
    return f"{session.items()}"


@app.route("/check_cookies")
def check_cookiesn():
    cookies = request.cookies

    return render_template("cookies.html", cookies=cookies)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session["username"] = request.form["username"]
            session["check_if_game_is_on"] = False
            session["login_datetime"] = login_datetime
            session["wins"] = 0
            session["loses"] = 0
            session["ties"] = 0
            session["credits"] = 10
            session["game_board"] = ",".join(map(str, [0 for i in range(9)]))
            login_datetime_for_user = PlayerStats.query.filter_by(
                user_id=user.id, login_datetime=login_datetime
            ).first()
            if not login_datetime_for_user:
                new_login_datetime = PlayerStats(
                    user_id=user.id, login_datetime=login_datetime
                )
                db.session.add(new_login_datetime)
                db.session.commit()

            return redirect(url_for("play_game"))

        else:
            return """
            <script>
                alert('Invalid username or password');
                window.location.href = "{}";
            </script>
            """.format(
                url_for("login")
            )

    return render_template("login.html")


@app.route("/logout")
def logout():
    response = make_response("Logged out")
    response.set_cookie("game_board", "", expires=0)
    login_datetime = session.get("login_datetime")
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    login_date_for_user = PlayerStats.query.filter_by(
        user_id=user.id, login_datetime=login_datetime
    ).first()
    login_date_for_user.logout_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    login_date_for_user.wins = session.get("wins")
    login_date_for_user.loses = session.get("loses")
    login_date_for_user.ties = session.get("ties")
    login_date_for_user.credits = session.get("credits")
    db.session.commit()
    session.clear()

    return """
    <script>
        alert('You have been logged out. Please log in if you want to play again.');
        window.location.href = "{}";
    </script>
    """.format(
        url_for("login")
    )


@app.route("/player_stats", methods=["GET", "POST"])
def player_stats():
    pass


@app.route("/game", methods=["GET", "POST"])
def play_game():
    game = TicTacToe([HumanPlayer(), AIPlayer(ai_algo)])
    game_cookie = session.get("game_board")
    if game_cookie:
        game.board = [int(x) for x in game_cookie.split(",")]
    if "choice" in request.form:
        game.play_move(request.form["choice"])
        if not game.is_over():
            ai_move = game.get_move()
            game.play_move(ai_move)
    if "reset" in request.form:
        if session["credits"] > 2:
            session["credits"] -= 3
            session["check_if_game_is_on"] = True
        else:
            return redirect(url_for("logout"))

        game.board = [0 for i in range(9)]
    if "credits" in request.form:
        session["credits"] = 10

    if game.is_over():
        msg = game.winner()
        game_msg = msg[0]
        result = msg[2]
        if result == 0:
            session["ties"] += 1
        elif result == 1:
            session["loses"] += 1
        elif result == 2:
            session["wins"] += 1
            session["credits"] += 4
        game.board = [0 for i in range(9)]
        session["check_if_game_is_on"] = False
    else:
        game_msg = "play move"
    game_is_on = session.get("check_if_game_is_on")
    response = make_response(
        render_template(
            "game.html",
            game=game,
            msg=game_msg,
            user_credits=session.get("credits"),
            user_wins=session.get("wins"),
            user_loses=session.get("loses"),
            user_ties=session.get("ties"),
            check_if_game_is_on=game_is_on,
        )
    )
    session["game_board"] = ",".join(map(str, game.board))
    return response


def run_web_app():
    app.run(debug=True, host="0.0.0.0")
