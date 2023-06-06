from datetime import datetime, date
from sqlalchemy import func
from config import CustomEnvironment
from flask import (Flask, make_response, redirect, render_template, request,
                   session, url_for)
from functools import wraps
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from tic_tac_toe_game.ai.negamax import Negamax
from tic_tac_toe_game.player import AIPlayer, HumanPlayer
from tic_tac_toe_game.tic_tac_toe import TicTacToe
from flask_login import login_required, current_user, LoginManager, login_user, logout_user, UserMixin
database_ip = CustomEnvironment.get_database_ip()
database_name = CustomEnvironment.get_database_name()
database_password = CustomEnvironment.get_database_password()
database_user = CustomEnvironment.get_database_user()

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{database_user}:{database_password}@{database_ip}:5432/{database_name}"
app.secret_key = CustomEnvironment.get_secret_key()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
ai_algo = Negamax(2)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    player_stats = db.relationship("PlayerStats", backref="user", lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def is_active(self):
        return self.is_active



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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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
                login_user(user)

            return redirect(url_for("profile_page"))

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
@login_required
def logout():
    login_datetime = session.get("login_datetime")
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    login_date_for_user = PlayerStats.query.filter_by(
        user_id=user.id, login_datetime=login_datetime
    ).first()
    login_date_for_user.logout_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    login_date_for_user.wins = session.get("wins")
    login_date_for_user.loses = session.get("loses")
    login_date_for_user.ties = session.get("ties")
    login_date_for_user.credits = session.get("credits")
    db.session.commit()
    session.clear()
    logout_user()

    return """
    <script>
        alert('You have been logged out. Please log in if you want to play again.');
        window.location.href = "{}";
    </script>
    """.format(
        url_for("login")
    )

def get_total_time(day, username):
    user = User.query.filter_by(username=username).first()

    total_time = db.session.query(
        func.sum(func.extract('epoch', PlayerStats.logout_datetime - PlayerStats.login_datetime))
    ).join(User).filter(
        func.date(PlayerStats.login_datetime) == day,
        PlayerStats.logout_datetime.isnot(None),
        User.id == user.id
    ).scalar()

    # Convert total_time from seconds to a more suitable format (e.g., HH:MM:SS)
    hours = int(total_time // 3600) if total_time else 0
    minutes = int((total_time % 3600) // 60) if total_time else 0
    seconds = int(total_time % 60) if total_time else 0

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@app.route("/player_stats", methods=['GET', 'POST'])
def player_stats():
    date_object = date.today()
    selected_date = request.form.get('selected_date')
    if selected_date:
        date_object = datetime.strptime(selected_date, '%Y-%m-%d')
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    total_played_time = get_total_time(date_object, username)
    total = PlayerStats.query.filter(PlayerStats.user_id == user.id).all()
    user_wins_today = db.session.query(func.sum(PlayerStats.wins)).filter(func.date(PlayerStats.login_datetime) == date_object, PlayerStats.user_id == user.id).scalar()
    user_loses_today = db.session.query(func.sum(PlayerStats.loses)).filter(func.date(PlayerStats.login_datetime) == date_object, PlayerStats.user_id == user.id).scalar()
    user_ties_today = db.session.query(func.sum(PlayerStats.ties)).filter(func.date(PlayerStats.login_datetime) == date_object, PlayerStats.user_id == user.id).scalar()
    return render_template("player_stats.html", user_wins_today=user_wins_today, user_loses_today=user_loses_today, user_ties_today=user_ties_today, total_played_time=total_played_time, total=total)

def custom_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if there are users in the database
        if User.query.count() == 0:
            # If no users found, allow access to the route
            return f(*args, **kwargs)
        
        # If there are users, check if the user is authenticated
        if not current_user.is_authenticated:
            # Redirect to the login page
            return redirect(url_for('login'))

        # User is authenticated, allow access to the route
        return f(*args, **kwargs)

    return decorated_function

@app.route("/profile")
@custom_login_required
def profile_page():
    username = current_user.username
    login_datetime = session.get("login_datetime")
    user = User.query.filter_by(username=username).first()
    login_date_for_user = PlayerStats.query.filter_by(
        user_id=user.id, login_datetime=login_datetime
    ).first()
    login_date_for_user.logout_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    login_date_for_user.wins = session.get("wins")
    login_date_for_user.loses = session.get("loses")
    login_date_for_user.ties = session.get("ties")
    login_date_for_user.credits = session.get("credits")
    db.session.commit()

    return render_template("profile.html", username=username)


@app.route("/game", methods=["GET", "POST"])
def play_game():
    session['less_than_three_credits_and_game_is_over'] = False
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
        winner_msg = game.winner()
        game_msg = winner_msg[0]
        result = winner_msg[1]
        if result == 0:
            session["ties"] += 1
        elif result == 1:
            session["loses"] += 1
        elif result == 2:
            session["wins"] += 1
            session["credits"] += 4
        game.board = [0 for i in range(9)]
        session["check_if_game_is_on"] = False
        if session['credits'] < 3:
            session['less_than_three_credits_and_game_is_over'] = True
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
            less_than_three_credits_and_game_is_over=session.get(
                "less_than_three_credits_and_game_is_over"
            ),
        )
    )
    session["game_board"] = ",".join(map(str, game.board))
    return response


def run_web_app():
    app.run(debug=True, host="0.0.0.0")
