import math
import time
import sys

class BreakthroughState:
    def __init__(self, board_matrix):
        # board_matrix to dwuwymiarowa tablica (lista list stringów)
        # np. [['B', 'B', ...], ['_', '_', ...], ..., ['W', 'W', ...]]
        self.board = board_matrix
        self.rows = len(board_matrix)
        self.cols = len(board_matrix[0]) if self.rows > 0 else 0

    def eval_material(self, player):
        """Strategia 1: Przewaga materialna"""
        b_count = sum(row.count('B') for row in self.board)
        w_count = sum(row.count('W') for row in self.board)
        
        if player == 'B':
            return b_count - w_count
        else:
            return w_count - b_count

    def eval_race(self, player):
        """Strategia 2: Wyścig do mety"""
        b_farthest = 0
        w_farthest = self.rows - 1
        
        # Szukamy najbardziej wysuniętych pionków
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'B':
                    b_farthest = max(b_farthest, r)
                elif self.board[r][c] == 'W':
                    w_farthest = min(w_farthest, r)
        
        # Odległość do mety (im mniej, tym lepiej)
        b_dist = (self.rows - 1) - b_farthest
        w_dist = w_farthest - 0
        
        # Wynik = dystans wroga - nasz dystans 
        # (dodatni wynik oznacza, że jesteśmy bliżej mety niż wróg)
        if player == 'B':
            return w_dist - b_dist
        else:
            return b_dist - w_dist

    def eval_pressure(self, player):
        """Strategia 3: Presja terytorialna"""
        b_score = 0
        w_score = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'B':
                    # Gracz B dostaje więcej punktów za wysokie indeksy wierszy
                    # Podnosimy do kwadratu, żeby nagradzać pionki bliżej mety
                    b_score += (r + 1) ** 2
                elif self.board[r][c] == 'W':
                    # Gracz W dostaje więcej punktów za niskie indeksy wierszy
                    w_score += (self.rows - r) ** 2
                    
        if player == 'B':
            return b_score - w_score
        else:
            return w_score - b_score

    def evaluate_hybrid(self, player, alpha=1.0, beta=10.0, gamma=2.0):
        # Szybkie sprawdzenie wygranej na podstawie krawędzi
        if 'B' in self.board[self.rows - 1]: return 99999 if player == 'B' else -99999
        if 'W' in self.board[0]: return 99999 if player == 'W' else -99999

        b_count, w_count = 0, 0
        b_farthest, w_farthest = 0, self.rows - 1
        b_score, w_score = 0, 0

        # JEDNO przejście po planszy zbierające wszystkie dane dla 3 strategii
        for r in range(self.rows):
            for c in range(self.cols):
                piece = self.board[r][c]
                if piece == 'B':
                    b_count += 1
                    if r > b_farthest: b_farthest = r
                    b_score += (r + 1) ** 2
                elif piece == 'W':
                    w_count += 1
                    if r < w_farthest: w_farthest = r
                    w_score += (self.rows - r) ** 2

        # Zabezpieczenie przed brakiem pionków (całkowita anihilacja)
        if w_count == 0: return 99999 if player == 'B' else -99999
        if b_count == 0: return 99999 if player == 'W' else -99999

        # H1: Materialna
        h1 = (b_count - w_count) if player == 'B' else (w_count - b_count)
        
        # H2: Wyścig
        b_dist = (self.rows - 1) - b_farthest
        w_dist = w_farthest
        h2 = (w_dist - b_dist) if player == 'B' else (b_dist - w_dist)
        
        # H3: Presja
        h3 = (b_score - w_score) if player == 'B' else (w_score - b_score)

        return (alpha * h1) + (beta * h2) + (gamma * h3)
    def is_winner(self, player):
        """Sprawdza, czy dany gracz osiągnął przeciwległą krawędź planszy."""
        if player == 'B' and 'B' in self.board[self.rows - 1]:
            return True
        if player == 'W' and 'W' in self.board[0]:
            return True
        # Sprawdzenie czy przeciwnikowi skończyły się pionki
        enemy = 'W' if player == 'B' else 'B'
        enemy_count = sum(row.count(enemy) for row in self.board)
        if enemy_count == 0:
            return True
        return False

    def is_terminal(self):
        """Sprawdza, czy gra dobiegła końca."""
        return self.is_winner('B') or self.is_winner('W')

    def get_possible_moves(self, player):
        moves_with_scores = []
        direction = 1 if player == 'B' else -1
        enemy = 'W' if player == 'B' else 'B'

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == player:
                    new_r = r + direction
                    
                    if 0 <= new_r < self.rows:
                        # 1. Ruch prosto (puste pole)
                        if self.board[new_r][c] == '_':
                            # Zwykły ruch ma priorytet 0
                            moves_with_scores.append((0, self._create_new_state(r, c, new_r, c)))
                        
                        # 2. Skos w lewo
                        if c - 1 >= 0:
                            target = self.board[new_r][c - 1]
                            if target == '_':
                                moves_with_scores.append((0, self._create_new_state(r, c, new_r, c - 1)))
                            elif target == enemy:
                                # Bicie jest bardzo dobrym ruchem - dajemy priorytet 1
                                moves_with_scores.append((1, self._create_new_state(r, c, new_r, c - 1)))
                            
                        # 3. Skos w prawo
                        if c + 1 < self.cols:
                            target = self.board[new_r][c + 1]
                            if target == '_':
                                moves_with_scores.append((0, self._create_new_state(r, c, new_r, c + 1)))
                            elif target == enemy:
                                # Bicie - priorytet 1
                                moves_with_scores.append((1, self._create_new_state(r, c, new_r, c + 1)))
        
        # Sortujemy ruchy malejąco po priorytecie (najpierw bicia)
        moves_with_scores.sort(key=lambda x: x[0], reverse=True)
        return [move[1] for move in moves_with_scores]

    def _create_new_state(self, r_from, c_from, r_to, c_to):
        """Tworzy głęboką kopię planszy i aplikuje ruch."""
        new_board = [row[:] for row in self.board]
        new_board[r_to][c_to] = new_board[r_from][c_from]
        new_board[r_from][c_from] = '_'
        # Zgodnie z listą: 'o' oznacza pole, z którego wykonano ostatni ruch
        # new_board[r_from][c_from] = 'o' # Odkomentuj, jeśli chcesz śledzić ślad
        return BreakthroughState(new_board)

    def print_board(self):
        for row in self.board:
            print(" ".join(row))
        print("-" * 20)


class Game:
    def __init__(self, start_board, max_depth=3):
        self.state = BreakthroughState(start_board)
        self.max_depth = max_depth
        self.visited_nodes = 0

    def minimax(self, state, depth, alpha, beta, is_maximizing, player_color):
        self.visited_nodes += 1

        if depth == 0 or state.is_terminal():
            return state.evaluate_hybrid(player_color), state

        if is_maximizing:
            max_eval = -math.inf
            best_state = None
            for child in state.get_possible_moves(player_color):
                eval_val, _ = self.minimax(child, depth - 1, alpha, beta, False, player_color)
                if eval_val > max_eval:
                    max_eval = eval_val
                    best_state = child
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break # Alfa-beta cięcie
            return max_eval, best_state
        else:
            min_eval = math.inf
            best_state = None
            enemy_color = 'W' if player_color == 'B' else 'B'
            for child in state.get_possible_moves(enemy_color):
                eval_val, _ = self.minimax(child, depth - 1, alpha, beta, True, player_color)
                if eval_val < min_eval:
                    min_eval = eval_val
                    best_state = child
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break # Alfa-beta cięcie
            return min_eval, best_state

    def play(self):
        current_player = 'B'
        rounds = 0
        
        start_time = time.time()

        while not self.state.is_terminal():
            rounds += 1
            print(f"Runda {rounds} - Ruch gracza: {current_player}")
            
            # Gracz szuka swojego najlepszego ruchu (dlatego is_maximizing = True)
            _, best_next_state = self.minimax(
                self.state, self.max_depth, -math.inf, math.inf, True, current_player
            )
            
            if best_next_state is None:
                print(f"Brak możliwych ruchów dla {current_player}. Koniec gry.")
                break
                
            self.state = best_next_state
            
            # Zmiana tury
            current_player = 'W' if current_player == 'B' else 'B'

        end_time = time.time()
        execution_time = end_time - start_time

        # --- WYPISANIE WYNIKÓW ZGODNIE Z POLECENIEM Z LISTY ---
        print("\n=== WYNIK KOŃCOWY ===")
        self.state.print_board()
        
        winner = 'B' if self.state.is_winner('B') else 'W'
        print(f"Liczba rund: {rounds}")
        print(f"Wygrał gracz: {winner}")
        
        # Wypisanie metryk na standardowe wyjście błędów (stderr)
        sys.stderr.write(f"Odwiedzone węzły drzewa: {self.visited_nodes}\n")
        sys.stderr.write(f"Czas działania (sekundy): {execution_time:.4f}\n")

initial_board = [
        ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
        ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
        ['_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_'],
        ['_', '_', '_', '_', '_', '_', '_', '_'],
        ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'],
        ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W']
    ]

# === URUCHOMIENIE ===
if __name__ == "__main__":
    # Standardowe ustawienie początkowe dla planszy 8x8
    

    # Uruchamiamy grę z głębokością przeszukiwania d=3
    game = Game(initial_board, max_depth=4)
    #game.play()