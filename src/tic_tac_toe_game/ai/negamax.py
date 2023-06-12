inf = float("infinity")


def negamax_algorithm(game, depth, original_depth, scoring, alpha=+inf, beta=-inf):

    if (depth == 0) or game.is_over():
        return scoring(game) * (1 + 0.001 * depth)

    else:
        possible_moves = game.possible_moves()

    state = game
    if depth == original_depth:
        state.ai_move = possible_moves[0]

    best_value = -inf

    for move in possible_moves:

        game = state.copy()
        game.make_move(move)
        game.switch_player()

        move_alpha = -negamax_algorithm(game, depth - 1, original_depth, scoring, -beta, -alpha)

        if best_value < move_alpha:
            best_value = move_alpha

        if alpha < move_alpha:
            alpha = move_alpha
            if depth == original_depth:
                state.ai_move = move
            if alpha >= beta:
                break


    return best_value


class Negamax:
    def __init__(self, depth, scoring=None, win_score=+inf):
        self.scoring = scoring
        self.depth = depth
        self.win_score = win_score

    def __call__(self, game):

        scoring = (
            self.scoring if self.scoring else (lambda g: g.scoring())
        )

        self.alpha = negamax_algorithm(
            game,
            self.depth,
            self.depth,
            scoring,
            -self.win_score,
            +self.win_score,
        )
        return game.ai_move
