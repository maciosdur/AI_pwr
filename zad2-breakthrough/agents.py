import math

class MinimaxAgent:
    def __init__(self, color, max_depth, heuristic_func, **heuristic_kwargs):
        self.color = color
        self.max_depth = max_depth
        self.heuristic_func = heuristic_func
        self.heuristic_kwargs = heuristic_kwargs
        self.visited_nodes = 0

    def get_best_move(self, state):
        self.visited_nodes = 0
        # Agent szuka ruchu dla swojego koloru, więc zaczyna od węzła MAX
        _, best_state = self._minimax(state, self.max_depth, -math.inf, math.inf, True, self.color)
        return best_state, self.visited_nodes

    def _minimax(self, state, depth, alpha, beta, is_maximizing, player_color):
        self.visited_nodes += 1

        if depth == 0 or state.is_terminal():
            # Przekazujemy dodatkowe wagi do funkcji heurystycznej
            score = self.heuristic_func(state, player_color, **self.heuristic_kwargs)
            # Premia za szybką wygraną: im wyższe `depth` (zostało więcej kroków do limitu), tym szybciej
            if score > 50000:
                score += depth * 1000
            elif score < -50000:
                score -= depth * 1000
            return score, state

        if is_maximizing:
            max_eval = -math.inf
            best_state = None
            for child in state.get_possible_moves(player_color):
                eval_val, _ = self._minimax(child, depth - 1, alpha, beta, False, player_color)
                if eval_val > max_eval:
                    max_eval = eval_val
                    best_state = child
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break  # Alfa-beta cięcie
            return max_eval, best_state
        else:
            min_eval = math.inf
            best_state = None
            enemy_color = 'W' if player_color == 'B' else 'B'
            for child in state.get_possible_moves(enemy_color):
                eval_val, _ = self._minimax(child, depth - 1, alpha, beta, True, player_color)
                if eval_val < min_eval:
                    min_eval = eval_val
                    best_state = child
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break  # Alfa-beta cięcie
            return min_eval, best_state