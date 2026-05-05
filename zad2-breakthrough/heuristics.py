def eval_material(state, player):
    """Strategia 1: Przewaga materialna"""
    b_count = sum(row.count('B') for row in state.board)
    w_count = sum(row.count('W') for row in state.board)
    
    if player == 'B':
        return b_count - w_count
    else:
        return w_count - b_count

def eval_race(state, player):
    """Strategia 2: Wyścig do mety"""
    b_farthest = 0
    w_farthest = state.rows - 1
    
    # Szukamy najbardziej wysuniętych pionków
    for r in range(state.rows):
        for c in range(state.cols):
            if state.board[r][c] == 'B':
                b_farthest = max(b_farthest, r)
            elif state.board[r][c] == 'W':
                w_farthest = min(w_farthest, r)
    
    # Max win - jeśli ktoś dotarł na ostatnie pole
    if b_farthest == state.rows - 1:
        return 99999 if player == 'B' else -99999
    if w_farthest == 0:
        return 99999 if player == 'W' else -99999

    # Odległość do mety (im mniej, tym lepiej)
    b_dist = (state.rows - 1) - b_farthest
    w_dist = w_farthest - 0
    
    # Wynik = dystans wroga - nasz dystans 
    # (dodatni wynik oznacza, że jesteśmy bliżej mety niż wróg)
    if player == 'B':
        return w_dist - b_dist
    else:
        return b_dist - w_dist

def eval_pressure(state, player):
    """Strategia 3: Presja terytorialna"""
    b_score = 0
    w_score = 0
    
    for r in range(state.rows):
        for c in range(state.cols):
            if state.board[r][c] == 'B':
                # Gracz B dostaje więcej punktów za wysokie indeksy wierszy
                b_score += (r + 1) ** 2
            elif state.board[r][c] == 'W':
                # Gracz W dostaje więcej punktów za niskie indeksy wierszy
                w_score += (state.rows - r) ** 2
                
    if player == 'B':
        return b_score - w_score
    else:
        return w_score - b_score

def eval_hybrid(state, player, alpha=1.0, beta=10.0, gamma=2.0):
    """Połączenie wszystkich strategii oceny (domyślna zoptymalizowana ewaluacja)"""
    # Szybkie sprawdzenie wygranej na podstawie krawędzi
    if 'B' in state.board[state.rows - 1]: return 99999 if player == 'B' else -99999
    if 'W' in state.board[0]: return 99999 if player == 'W' else -99999

    # Zbieranie danych o planszy
    # Ponieważ już mamy w tym pliku rozdzielone metody wyliczające wszystko z osobna, 
    # możemy je po prostu zsumować używając odpowiednich współczynników:
    h1 = eval_material(state, player)
    h2 = eval_race(state, player)
    h3 = eval_pressure(state, player)

    # Zabezpieczenie przed brakiem pionków (całkowita anihilacja) - sprawdzamy ilość pionków przeciwnika
    if h1 >= 16: return 99999 # Jeśli przeciwnik stracił wszystko (np. mamy +16 różnicy), to wygrana. Ten warunek można ulepszyć w razie potrzeby.

    return (alpha * h1) + (beta * h2) + (gamma * h3)