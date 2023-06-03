from abc import ABC, abstractclassmethod
from copy import deepcopy


class TwoPlayerGame(ABC):
    @abstractclassmethod
    def possible_moves(self):
        pass

    @abstractclassmethod
    def make_move(self, move):
        pass

    @abstractclassmethod
    def is_over(self):
        pass

    def play(self, nmoves=1000, verbose=True):

        history = []

        if verbose:
            self.show()

        for self.nmove in range(1, nmoves + 1):

            if self.is_over():
                break

            move = self.player.ask_move(self)
            history.append((deepcopy(self), move))
            self.make_move(move)

            if verbose:
                print(
                    "\nMove #%d: player %d plays %s :"
                    % (self.nmove, self.current_player, str(move))
                )
                self.show()

            self.switch_player()

        history.append(deepcopy(self))

        return history

    @property
    def opponent_index(self):
        return 2 if (self.current_player == 1) else 1

    @property
    def player(self):
        return self.players[self.current_player - 1]

    @property
    def opponent(self):
        return self.players[self.opponent_index - 1]

    def switch_player(self):
        self.current_player = self.opponent_index

    def copy(self):
        return deepcopy(self)

    def get_move(self):
        return self.player.ask_move(self)

    def play_move(self, move):
        result = self.make_move(move)
        self.switch_player()
        return result
    