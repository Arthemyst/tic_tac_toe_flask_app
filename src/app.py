from flask import Flask, make_response, render_template, request, redirect, url_for, session
from tic_tac_toe_game.ai.negamax import Negamax
from tic_tac_toe_game.player import AIPlayer, HumanPlayer
from tic_tac_toe_game.tic_tac_toe import TicTacToe
from flask_sqlalchemy import SQLAlchemy
from config import CustomEnvironment

database_ip = CustomEnvironment.get_database_ip()
database_name = CustomEnvironment.get_database_name()
database_password = CustomEnvironment.get_database_password()
database_user = CustomEnvironment.get_database_user()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_user}:{database_password}@{database_ip}:5432/{database_name}'
app.secret_key = CustomEnvironment.get_secret_key()
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    credits = db.Column(db.Integer, default=10)
    wins = db.Column(db.Integer, default=0)
    loses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('login'))
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        user.credits, user.wins, user.loses, user.ties = 10, 0, 0, 0
        db.session.commit()
        if user and user.password == password:
            session['username'] = request.form['username']
            return redirect(url_for('play_game'))
        else:
            return 'Invalid username or password!'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

ai_algo = Negamax(2)


@app.route("/game", methods=["GET", "POST"])
def play_game():
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    game = TicTacToe([HumanPlayer(), AIPlayer(ai_algo)])
    game_cookie = request.cookies.get("game_board")
    if game_cookie:
        game.board = [int(x) for x in game_cookie.split(",")]
    if "choice" in request.form:
        game.play_move(request.form["choice"])
        if not game.is_over():
            ai_move = game.get_move()
            game.play_move(ai_move)
    if "reset" in request.form:
        if user.credits > 2:
            user.credits -= 3
        db.session.commit()
        game.board = [0 for i in range(9)]
    if "credits" in request.form:
        user.credits = 10
        db.session.commit()


    if game.is_over():
        msg = game.winner()
        game_msg = msg[0]
        points = msg[1]
        user.credits += points
        result = msg[2]
        if result == 0:
            user.ties += 1
        elif result == 1:
            user.loses += 1
        elif result == 2:
            user.wins += 1
        db.session.commit()
    else:
        game_msg = "play move"
    if user.credits > 0 and user.credits < 3 and game.is_over():
        return redirect(url_for('logout'))
    
    user_wins = user.wins
    user_loses = user.loses
    user_ties = user.ties

    response = make_response(render_template("game.html", game=game, msg=game_msg, user_credits=user.credits, user_wins=user_wins, user_loses=user_loses, user_ties=user_ties))
    c = ",".join(map(str, game.board))
    response.set_cookie("game_board", c)
    return response


def run_web_app():
    app.run(debug=True, host="0.0.0.0")
