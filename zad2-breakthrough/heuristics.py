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

def eval_threat(state, player):
    """Strategia 4: Zagrożenie (Defensywna)"""
    b_safe = 0
    b_hanging = 0
    w_safe = 0
    w_hanging = 0
    
    for r in range(state.rows):
        for c in range(state.cols):
            piece = state.board[r][c]
            if piece == 'B':
                threatened = False
                # Sprawdzanie czy W atakuje B (W porusza się w górę, czyli może być na r+1)
                if r + 1 < state.rows:
                    if c - 1 >= 0 and state.board[r+1][c-1] == 'W': threatened = True
                    if c + 1 < state.cols and state.board[r+1][c+1] == 'W': threatened = True
                        
                protected = False
                # Sprawdzanie czy inne B chronią ten pionek (czy są na r-1)
                if r - 1 >= 0:
                    if c - 1 >= 0 and state.board[r-1][c-1] == 'B': protected = True
                    if c + 1 < state.cols and state.board[r-1][c+1] == 'B': protected = True
                        
                if threatened and not protected:
                    b_hanging += 1
                else:
                    b_safe += 1
                    
            elif piece == 'W':
                threatened = False
                # Sprawdzanie czy B atakuje W (B porusza się w dół, czyli może być na r-1)
                if r - 1 >= 0:
                    if c - 1 >= 0 and state.board[r-1][c-1] == 'B': threatened = True
                    if c + 1 < state.cols and state.board[r-1][c+1] == 'B': threatened = True
                        
                protected = False
                # Sprawdzanie czy inne W chronią ten pionek (czy są na r+1)
                if r + 1 < state.rows:
                    if c - 1 >= 0 and state.board[r+1][c-1] == 'W': protected = True
                    if c + 1 < state.cols and state.board[r+1][c+1] == 'W': protected = True
                        
                if threatened and not protected:
                    w_hanging += 1
                else:
                    w_safe += 1

    b_score = b_safe - b_hanging
    w_score = w_safe - w_hanging
    
    if player == 'B':
        return b_score - w_score
    else:
        return w_score - b_score

def eval_hybrid(state, player, alpha=1.0, beta=10.0, gamma=2.0, delta=5.0):
    """Połączenie wszystkich strategii oceny (domyślna zoptymalizowana ewaluacja)"""
    # Szybkie sprawdzenie wygranej na podstawie krawędzi
    if 'B' in state.board[state.rows - 1]: return 99999 if player == 'B' else -99999
    if 'W' in state.board[0]: return 99999 if player == 'W' else -99999

    # Zbieranie danych o planszy
    h1 = eval_material(state, player) if alpha != 0 else 0
    h2 = eval_race(state, player) if beta != 0 else 0
    h3 = eval_pressure(state, player) if gamma != 0 else 0
    h4 = eval_threat(state, player) if delta != 0 else 0


    return (alpha * h1) + (beta * h2) + (gamma * h3) + (delta * h4)

def eval_adaptive(state, player):
    """Strategia 5: Adaptacyjna (Smart)
    Zmienia wagi heurystyk w zależności od etapu gry (odległości do mety).
    Na początku skupia się na materiale i strukturze (presji/obronie).
    W końcówce (gdy któryś gracz jest blisko wygranej) ignoruje materiał i rzuca wszystko do wyścigu.
    """
    # Szybkie sprawdzenie wygranej na podstawie krawędzi
    if 'B' in state.board[state.rows - 1]: return 99999 if player == 'B' else -99999
    if 'W' in state.board[0]: return 99999 if player == 'W' else -99999

    # Obliczenie postępu gry (game_progress od 0.0 do 1.0)
    b_farthest = 0
    w_farthest = state.rows - 1
    for r in range(state.rows):
        for c in range(state.cols):
            if state.board[r][c] == 'B': b_farthest = max(b_farthest, r)
            elif state.board[r][c] == 'W': w_farthest = min(w_farthest, r)
    
    b_progress = b_farthest / (state.rows - 1)
    w_progress = ((state.rows - 1) - w_farthest) / (state.rows - 1)
    
    # Postęp gry to maksymalne zaawansowanie kogokolwiek na planszy
    game_progress = max(b_progress, w_progress) 

    # adaptacja wag
    alpha = 15.0 * (1.0 - game_progress)           # Materiał: spada od 15 do 0
    beta  = 5.0 + (150.0 * (game_progress ** 3))   # Wyścig: rośnie wykładniczo od 5 do 155
    gamma = 5.0 * (1.0 - game_progress)            # Presja: spada od 5 do 0
    delta = 6.0 * (1.0 - (game_progress * 0.5))    # Zagrożenie: spada lekko z 6 do 3

    h1 = eval_material(state, player)
    h2 = eval_race(state, player)
    h3 = eval_pressure(state, player)
    h4 = eval_threat(state, player)

    return (alpha * h1) + (beta * h2) + (gamma * h3) + (delta * h4)