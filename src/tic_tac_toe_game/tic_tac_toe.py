from tic_tac_toe_game.two_player_game import TwoPlayerGame
from typing import List
from tic_tac_toe_game.constants import WIN_LINES
class TicTacToe(TwoPlayerGame):

    def __init__(self, players):
        self.players: List = players
        self.board: List = [0 for i in range(9)]
        self.current_player: int = 1

    def possible_moves(self):
        return [i + 1 for i, e in enumerate(self.board) if e == 0]

    def make_move(self, move):
        self.board[int(move) - 1] = self.current_player

    def unmake_move(self, move):  # optional method (speeds up the AI)
        self.board[int(move) - 1] = 0

    def lose(self, who=None):
        """ Has the opponent "three in line ?" """
        if who is None:
            who = self.opponent_index
        wins = [all([(self.board[c - 1] == who) for c in line]) for line in WIN_LINES]
        return any(wins)

    def is_over(self):
        return (
            (self.possible_moves() == [])
            or self.lose()
            or self.lose(who=self.current_player)
        )

    def show(self):
        print(
            "\n"
            + "\n".join(
                [
                    " ".join([[".", "O", "X"][self.board[3 * j + i]] for i in range(3)])
                    for j in range(3)
                ]
            )
        )

    def spot_string(self, i, j):
        return ["_", "O", "X"][self.board[3 * j + i]]

    def scoring(self):
        opp_won = self.lose()
        i_won = self.lose(who=self.current_player)
        if opp_won and not i_won:
            return -100
        if i_won and not opp_won:
            return 100
        return 0

    def winner(self):
        if self.lose(who=2):
            return "AI Wins"
        return "Tie"
    