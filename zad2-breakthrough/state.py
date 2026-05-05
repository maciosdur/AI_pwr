class BreakthroughState:
    def __init__(self, board_matrix, last_origin=None):
        # board_matrix to dwuwymiarowa tablica (lista list stringów)
        # np. [['B', 'B', ...], ['_', '_', ...], ..., ['W', 'W', ...]]
        self.board = board_matrix
        self.rows = len(board_matrix)
        self.cols = len(board_matrix[0]) if self.rows > 0 else 0
        self.last_origin = last_origin

    def is_winner(self, player):
        """Sprawdza, czy dany gracz osiągnął przeciwległą krawędź planszy."""
        if player == 'B' and 'B' in self.board[self.rows - 1]:
            return True
        if player == 'W' and 'W' in self.board[0]:
            return True
            
        # Szybkie sprawdzenie, czy przeciwnikowi skończyły się pionki (early exit)
        enemy = 'W' if player == 'B' else 'B'
        for row in self.board:
            if enemy in row:
                return False
        return True

    def is_terminal(self):
        """Sprawdza, czy gra dobiegła końca."""
        return self.is_winner('B') or self.is_winner('W')

    def get_possible_moves(self, player):
        # Zamiast wrzucać wszystko do jednej listy i sortować, używamy "wiaderek" (buckets).
        # Unikamy dzięki temu kosztownego wywołania sort()
        wins_capture = []
        wins_normal = []
        captures = []
        normals = []
        
        direction = 1 if player == 'B' else -1
        enemy = 'W' if player == 'B' else 'B'
        
        rows = self.rows
        cols = self.cols
        board = self.board
        win_row = rows - 1 if player == 'B' else 0

        for r in range(rows):
            for c in range(cols):
                if board[r][c] == player:
                    new_r = r + direction
                    
                    if 0 <= new_r < rows:
                        is_win = (new_r == win_row)
                        
                        # 1. Ruch prosto (puste pole)
                        if board[new_r][c] in ('_', 'o'):
                            new_state = self._create_new_state(r, c, new_r, c)
                            if is_win:
                                wins_normal.append(new_state)
                            else:
                                normals.append(new_state)
                        
                        # 2. Skos w lewo
                        if c - 1 >= 0:
                            target = board[new_r][c - 1]
                            if target in ('_', 'o'):
                                new_state = self._create_new_state(r, c, new_r, c - 1)
                                if is_win:
                                    wins_normal.append(new_state)
                                else:
                                    normals.append(new_state)
                            elif target == enemy:
                                new_state = self._create_new_state(r, c, new_r, c - 1)
                                if is_win:
                                    wins_capture.append(new_state)
                                else:
                                    captures.append(new_state)
                            
                        # 3. Skos w prawo
                        if c + 1 < cols:
                            target = board[new_r][c + 1]
                            if target in ('_', 'o'):
                                new_state = self._create_new_state(r, c, new_r, c + 1)
                                if is_win:
                                    wins_normal.append(new_state)
                                else:
                                    normals.append(new_state)
                            elif target == enemy:
                                new_state = self._create_new_state(r, c, new_r, c + 1)
                                if is_win:
                                    wins_capture.append(new_state)
                                else:
                                    captures.append(new_state)
        
        # Zwracamy połączone zbiory (priorytet zachowany metodą bez sortowania)
        return wins_capture + wins_normal + captures + normals

    def _create_new_state(self, r_from, c_from, r_to, c_to):
        """Tworzy głęboką kopię planszy i aplikuje ruch."""
        new_board = [row[:] for row in self.board]
        
        if self.last_origin is not None:
            old_r, old_c = self.last_origin
            if new_board[old_r][old_c] == 'o':
                new_board[old_r][old_c] = '_'
        else:
            for r in range(self.rows):
                for c in range(self.cols):
                    if new_board[r][c] == 'o':
                        new_board[r][c] = '_'
                    
        new_board[r_to][c_to] = new_board[r_from][c_from]
        new_board[r_from][c_from] = 'o'
        return BreakthroughState(new_board, last_origin=(r_from, c_from))

    def print_board(self):
        for row in self.board:
            print(" ".join(row))
        print("-" * 20)