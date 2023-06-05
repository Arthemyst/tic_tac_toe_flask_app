from flask import Flask, make_response, render_template, request, redirect, url_for

from tic_tac_toe_game.ai.negamax import Negamax
from tic_tac_toe_game.player import AIPlayer, HumanPlayer
from tic_tac_toe_game.tic_tac_toe import TicTacToe
from flask_sqlalchemy import SQLAlchemy
postgres_ip = '172.19.0.2'
app = Flask(__name__)
# Set the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@{postgres_ip}:5432/postgres'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

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
            return 'Username already exists!'
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
        if user and user.password == password:
            return 'Logged in successfully!'
        else:
            return 'Invalid username or password!'
    return render_template('login.html')


ai_algo = Negamax(2)


@app.route("/game", methods=["GET", "POST"])
def play_game():
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
        game.board = [0 for i in range(9)]
    if game.is_over():
        msg = game.winner()
    else:
        msg = "play move"
    resp = make_response(render_template("game.html", game=game, msg=msg))
    c = ",".join(map(str, game.board))
    resp.set_cookie("game_board", c)
    return resp


def run_web_app():
    app.run(debug=True, host="0.0.0.0")
