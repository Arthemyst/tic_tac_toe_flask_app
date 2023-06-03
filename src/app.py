from flask import Flask, render_template
from tic_tac_toe_game.player import HumanPlayer, AIPlayer
from tic_tac_toe_game.tic_tac_toe import TicTacToe
from tic_tac_toe_game.ai.negamax import Negamax
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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
    resp = make_response(render_template('game.html', game=game, msg=msg))
    c = ",".join(map(str, game.board))
    resp.set_cookie("game_board", c)
    return resp

def run_web_app():
    app.run(debug=True, host='0.0.0.0')
    