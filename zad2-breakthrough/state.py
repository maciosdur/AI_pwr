class BreakthroughState:
    def __init__(self, board_matrix):
        # board_matrix to dwuwymiarowa tablica (lista list stringów)
        # np. [['B', 'B', ...], ['_', '_', ...], ..., ['W', 'W', ...]]
        self.board = board_matrix
        self.rows = len(board_matrix)
        self.cols = len(board_matrix[0]) if self.rows > 0 else 0

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
                        # Priorytetyzacja natychmiastowych wygranych do potężnych cięć Alfa-Beta
                        win_priority = 10 if (new_r == self.rows - 1 and player == 'B') or (new_r == 0 and player == 'W') else 0
                        # 1. Ruch prosto (puste pole)
                        if self.board[new_r][c] == '_':
                            # Zwykły ruch ma priorytet 0
                            moves_with_scores.append((win_priority + 0, self._create_new_state(r, c, new_r, c)))
                        
                        # 2. Skos w lewo
                        if c - 1 >= 0:
                            target = self.board[new_r][c - 1]
                            if target == '_':
                                moves_with_scores.append((win_priority + 0, self._create_new_state(r, c, new_r, c - 1)))
                            elif target == enemy:
                                # Bicie jest bardzo dobrym ruchem - dajemy priorytet 1
                                moves_with_scores.append((win_priority + 1, self._create_new_state(r, c, new_r, c - 1)))
                            
                        # 3. Skos w prawo
                        if c + 1 < self.cols:
                            target = self.board[new_r][c + 1]
                            if target == '_':
                                moves_with_scores.append((win_priority + 0, self._create_new_state(r, c, new_r, c + 1)))
                            elif target == enemy:
                                # Bicie - priorytet 1
                                moves_with_scores.append((win_priority + 1, self._create_new_state(r, c, new_r, c + 1)))
        
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