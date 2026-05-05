import time
import sys
import inspect

# Zakładamy, że masz już utworzone poniższe pliki (zgodnie ze swoim planem)
from state import BreakthroughState
from agents import MinimaxAgent
from heuristics import eval_material, eval_hybrid, eval_race, eval_pressure

class GameRunner:
    def __init__(self, initial_board, agent_b, agent_w):
        self.state = BreakthroughState(initial_board)
        self.agents = {'B': agent_b, 'W': agent_w}
        self.rounds = 0

    def play(self):
        current_player = 'B'
        total_time = 0
        total_nodes = 0

        while not self.state.is_terminal():
            self.rounds += 1
            agent = self.agents[current_player]
            
            start_time = time.time()
            best_next_state, nodes = agent.get_best_move(self.state)
            elapsed = time.time() - start_time
            
            total_time += elapsed
            total_nodes += nodes
            
            if best_next_state is None:
                break
                
            self.state = best_next_state
            current_player = 'W' if current_player == 'B' else 'B'

        # Zgodnie z listą 2: Standardowe wyjście (STDOUT)
        self.state.print_board()
        winner = 'B' if self.state.is_winner('B') else 'W'
        print(f"Liczba rund: {self.rounds}")
        print(f"Zwyciezca: {winner}")
        
        # Zgodnie z listą 2: Standardowe wyjście błędów (STDERR)
        sys.stderr.write(f"Odwiedzone wezly: {total_nodes}\n")
        sys.stderr.write(f"Czas dzialania: {total_time:.4f}s\n")

        # Wypisanie informacji o agentach (strategia, głębokość, ew. wagi)
        for p in ['B', 'W']:
            agent = self.agents[p]
            h_name = getattr(agent.heuristic_func, '__name__', 'Nieznana/Custom')
            sys.stderr.write(f"Agent {p} - Glebokosc: {agent.max_depth}, Strategia: {h_name}\n")
            if h_name == 'eval_hybrid':
                sig = inspect.signature(agent.heuristic_func)
                weights = [f"{k}={v.default}" for k, v in sig.parameters.items() if k in ['alpha', 'beta', 'gamma']]
                sys.stderr.write(f"  -> Wagi: {', '.join(weights)}\n")

def read_board_from_stdin():
    """Funkcja próbująca załadować planszę ze stdin."""
    board = []
    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if line:
                row = line.split()
                if len(row) == 1 and len(line) == 8:
                    row = list(line)
                board.append(row)
            if len(board) == 8:
                break
    return board

if __name__ == "__main__":
    # 1. Próba wczytania ze standardowego wejścia
    initial_board = read_board_from_stdin()
    
    # 2. Jeśli brakuje danych ze stdin, używamy domyślnego ustawienia
    if not initial_board or len(initial_board) != 8:
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
    
    agent1 = MinimaxAgent('B', max_depth=4, heuristic_func=eval_race)
    agent2 = MinimaxAgent('W', max_depth=4, heuristic_func=eval_hybrid)
    
    runner = GameRunner(initial_board, agent1, agent2)
    runner.play()