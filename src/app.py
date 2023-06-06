from flask import Flask, make_response, render_template, request, redirect, url_for, session
from tic_tac_toe_game.ai.negamax import Negamax
from tic_tac_toe_game.player import AIPlayer, HumanPlayer
from tic_tac_toe_game.tic_tac_toe import TicTacToe
from flask_sqlalchemy import SQLAlchemy
from config import CustomEnvironment
from datetime import date
database_ip = CustomEnvironment.get_database_ip()
database_name = CustomEnvironment.get_database_name()
database_password = CustomEnvironment.get_database_password()
database_user = CustomEnvironment.get_database_user()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_user}:{database_password}@{database_ip}:5432/{database_name}'
app.secret_key = CustomEnvironment.get_secret_key()
db = SQLAlchemy(app)
ai_algo = Negamax(2)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    login_dates = db.relationship('LoginDate', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class LoginDate(db.Model):
    __tablename__ = 'logindates'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    login_date = db.Column(db.Date)
    # play_time_in_minutes = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=10)
    wins = db.Column(db.Integer, default=0)
    loses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)

    def __init__(self, user_id, login_date):
        self.user_id = user_id
        self.login_date = login_date
        self.credits = 10
        self.wins = 0
        self.loses = 0 
        self.ties = 0

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
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = request.form['username']


            login_date_for_user = LoginDate.query.filter_by(user_id=user.id, login_date=date.today()).first()
            if login_date_for_user:
                login_date_for_user.credits = 10
                db.session.commit()
            else:
                new_login_date = LoginDate(user_id=user.id, login_date=date.today())
                db.session.add(new_login_date)
                db.session.commit()
                start_new_game = True
            return redirect(url_for('play_game'), start_new_game=start_new_game)

        else:
            return 'Invalid username or password!'

    return render_template('login.html')

@app.route('/logout')
def logout():
    response = make_response('Logged out')
    response.set_cookie('game_board', '', expires=0)
    return '''
    <script>
        alert('You have been logged out. Please log in if you want to play again.');
        window.location.href = "{}";
    </script>
    '''.format(url_for('login'))


@app.route("/game", methods=["GET", "POST"])
def play_game():
    check_if_game_is_over = True
    if "stats" in request.form:
        show_stats = True
    else:
        show_stats = False

    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    user_login_date = LoginDate.query.filter_by(user_id=user.id, login_date=date.today()).first()

    game = TicTacToe([HumanPlayer(), AIPlayer(ai_algo)])
    game_cookie = request.cookies.get("game_board")
    if game_cookie:
        check_if_game_is_over = False
        game.board = [int(x) for x in game_cookie.split(",")]
    if "choice" in request.form:
        game.play_move(request.form["choice"])
        if not game.is_over():
            ai_move = game.get_move()
            game.play_move(ai_move)
    if "reset" in request.form:
        if user_login_date.credits > 2:
            check_if_game_is_over = False
            user_login_date.credits -= 3
            db.session.commit()
        else:
            return redirect(url_for('logout'))

        game.board = [0 for i in range(9)]
    if "credits" in request.form:
        user_login_date.credits = 10
        db.session.commit()


    if game.is_over():
        msg = game.winner()
        game_msg = msg[0]
        points = msg[1]
        user_login_date.credits += points
        result = msg[2]
        if result == 0:
            msg_text = "tie"
            user_login_date.ties += 1
            check_if_game_is_over = True
            db.session.commit()
        elif result == 1:
            msg_text = "Computer wins"
            user_login_date.loses += 1
            check_if_game_is_over = True
            db.session.commit()
        elif result == 2:
            msg_text = "You win"
            user_login_date.wins += 1
            check_if_game_is_over = True
            db.session.commit()
    else:
        game_msg = "play move"
        check_if_game_is_over = False
    
    response = make_response(render_template(
        "game.html", 
        game=game, 
        msg=msg_text, 
        user_credits=user_login_date.credits, 
        user_wins=user_login_date.wins, 
        user_loses=user_login_date.loses, 
        user_ties=user_login_date.ties, 
        check_if_game_is_over=check_if_game_is_over, 
        show_stats=show_stats
        ))
    c = ",".join(map(str, game.board))
    response.set_cookie("game_board", c)
    return response


def run_web_app():
    app.run(debug=True, host="0.0.0.0")
