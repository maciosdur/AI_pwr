import random
import sys

from state import BreakthroughState
from agents import MinimaxAgent
from heuristics import eval_hybrid

# Domyślna plansza startowa
INITIAL_BOARD = [
    ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
    ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
    ['_', '_', '_', '_', '_', '_', '_', '_'],
    ['_', '_', '_', '_', '_', '_', '_', '_'],
    ['_', '_', '_', '_', '_', '_', '_', '_'],
    ['_', '_', '_', '_', '_', '_', '_', '_'],
    ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'],
    ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W']
]

def play_silent(agent_b, agent_w):
    """Przeprowadza grę w tle bez wypisywania wyników do terminala."""
    state = BreakthroughState(INITIAL_BOARD)
    agents = {'B': agent_b, 'W': agent_w}
    current_player = 'B'

    while not state.is_terminal():
        best_next_state, _ = agents[current_player].get_best_move(state)
        if best_next_state is None:
            break
        state = best_next_state
        current_player = 'W' if current_player == 'B' else 'B'

    return 'B' if state.is_winner('B') else 'W'

def run_simulation(num_candidates=10, depth=3):
    candidates = []
    # 1. Generowanie losowych zestawów wag do przetestowania
    for i in range(num_candidates):
        candidates.append({
            'id': i + 1,
            'alpha': round(random.uniform(0.0, 5.0), 2),   # Przewaga materiału
            'beta': round(random.uniform(10.0, 100.0), 2), # Wyścig
            'gamma': round(random.uniform(0.0, 5.0), 2),   # Presja
            'delta': round(random.uniform(0.0, 10.0), 2),  # Zagrożenie
            'wins': 0
        })

    print(f"Rozpoczynamy turniej (każdy z każdym) dla {num_candidates} losowych konfiguracji (Glebokosc={depth})...")
    print("-" * 50)
    
    # 2. Rozegranie meczów każdy z każdym (każda para gra 2 mecze: raz jako B, raz jako W)
    total_matches = num_candidates * (num_candidates - 1)
    match_num = 1
    
    for i in range(num_candidates):
        for j in range(num_candidates):
            if i == j:
                continue
                
            c1 = candidates[i]
            c2 = candidates[j]
            wagi1 = {k: v for k, v in c1.items() if k not in ['wins', 'id']}
            wagi2 = {k: v for k, v in c2.items() if k not in ['wins', 'id']}
            
            print(f"[{match_num}/{total_matches}] Kandydat {c1['id']} (B) vs Kandydat {c2['id']} (W) ...", end=" ", flush=True)
            
            agent_b = MinimaxAgent('B', max_depth=depth, heuristic_func=eval_hybrid, **wagi1)
            agent_w = MinimaxAgent('W', max_depth=depth, heuristic_func=eval_hybrid, **wagi2)
            
            winner = play_silent(agent_b, agent_w)
            if winner == 'B':
                c1['wins'] += 1
                print(f"Wygral B (Kandydat {c1['id']})")
            else:
                c2['wins'] += 1
                print(f"Wygral W (Kandydat {c2['id']})")
                
            match_num += 1
        
    # 3. Sortowanie wyników malejąco po liczbie zwycięstw
    candidates.sort(key=lambda x: x['wins'], reverse=True)
    
    print("\n=== WYNIKI SYMULACJI ===")
    max_wins = 2 * (num_candidates - 1)
    for i, config in enumerate(candidates):
        print(f"{i+1}. Wygrane: {config['wins']}/{max_wins} | alpha={config['alpha']}, beta={config['beta']}, gamma={config['gamma']}, delta={config['delta']} (ID: {config['id']})")
        
    print(f"\nNajlepsza znaleziona konfiguracja: {candidates[0]}")
    
if __name__ == '__main__':
    run_simulation(num_candidates=10, depth=3)