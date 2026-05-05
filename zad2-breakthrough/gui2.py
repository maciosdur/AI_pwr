import tkinter as tk
import math
import time

from state import BreakthroughState
from agents import MinimaxAgent
from heuristics import eval_hybrid, eval_race, eval_pressure, eval_material, eval_threat

class BreakthroughGUI:
    def __init__(self, master, history, stats):
        self.master = master
        self.master.title("Breakthrough AI - Minimax Visualization")
        
        # --- Parametry gry ---
        self.history = history
        self.stats = stats
        self.current_step = 0
        
        # Inicjalizacja na pierwszym stanie (początkowym)
        self.state = self.history[self.current_step]

        # --- Budowa Interfejsu ---
        self.create_widgets()
        self.update_ui()

    def create_widgets(self):
        # Główny kontener
        self.main_frame = tk.Frame(self.master, padx=10, pady=10)
        self.main_frame.pack()

        # Płótno (Canvas) na planszę
        self.cell_size = 60
        self.canvas_size = self.cell_size * 8
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=5, padx=(0, 20))

        # --- Panel Boczny (Statystyki) ---
        font_large = ("Helvetica", 14, "bold")
        font_normal = ("Helvetica", 12)

        self.lbl_round = tk.Label(self.main_frame, text="Runda: 0", font=font_large)
        self.lbl_round.grid(row=0, column=1, sticky="w", pady=(0, 10))

        self.lbl_turn = tk.Label(self.main_frame, text="Tura: Gracz B (Czarny)", font=font_large, fg="black")
        self.lbl_turn.grid(row=1, column=1, sticky="w", pady=(0, 20))

        self.lbl_eval_b = tk.Label(self.main_frame, text="Ocena (B): 0", font=font_normal)
        self.lbl_eval_b.grid(row=2, column=1, sticky="w")

        self.lbl_eval_w = tk.Label(self.main_frame, text="Ocena (W): 0", font=font_normal)
        self.lbl_eval_w.grid(row=3, column=1, sticky="w", pady=(0, 20))

        # Przyciski kontrolne
        self.btn_next = tk.Button(self.main_frame, text="Wykonaj Ruch", command=self.play_turn, font=font_normal, bg="#4CAF50", fg="white", width=15)
        self.btn_next.grid(row=4, column=1, sticky="nw")

        self.lbl_status = tk.Label(self.main_frame, text="", font=font_normal, fg="red")
        self.lbl_status.grid(row=5, column=0, columnspan=2, pady=10)

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#f0d9b5", "#b58863"] # Kolory szachownicy
        
        for r in range(self.state.rows):
            for c in range(self.state.cols):
                # Rysowanie kwadratu
                x0 = c * self.cell_size
                y0 = r * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                color = colors[(r + c) % 2]
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

                # Rysowanie pionka
                piece = self.state.board[r][c]
                if piece == 'o':
                    # Oznaczenie pola z którego wykonano ostatni ruch
                    pad = 25
                    self.canvas.create_oval(x0+pad, y0+pad, x1-pad, y1-pad, fill="#ff9800", outline="")
                elif piece != '_':
                    # Odstęp pionka od krawędzi pola
                    pad = 10
                    p_color = "#333333" if piece == 'B' else "#ffffff"
                    o_color = "#000000" if piece == 'W' else ""
                    self.canvas.create_oval(x0+pad, y0+pad, x1-pad, y1-pad, fill=p_color, outline=o_color, width=2)

    def update_ui(self):
        # 1. Rysuj planszę
        self.draw_board()
        
        # 2. Aktualizuj etykiety
        self.lbl_round.config(text=f"Ruch nr: {self.current_step}")
        
        current_player = 'B' if self.current_step % 2 == 0 else 'W'
        
        if self.current_step == len(self.history) - 1 and self.state.is_terminal():
            winner = 'B' if self.state.is_winner('B') else 'W'
            self.lbl_status.config(text=f"Koniec gry! Wygrywa gracz: {winner}", fg="red")
            self.lbl_turn.config(text="Koniec gry", fg="red")
            self.btn_next.config(state="disabled")
        else:
            if current_player == 'B':
                self.lbl_turn.config(text="Tura: Gracz B (Idzie w dół)", fg="#333333")
            else:
                self.lbl_turn.config(text="Tura: Gracz W (Idzie w górę)", fg="#888888")
            
            if self.current_step > 0:
                prev_player, elapsed, nodes = self.stats[self.current_step - 1]
                self.lbl_status.config(text=f"Ruch {prev_player} wyliczony w {elapsed:.2f} s | Węzły: {nodes}", fg="blue")
            else:
                self.lbl_status.config(text="Gra gotowa do odtworzenia.", fg="blue")

        # 3. Oblicz i wyświetl aktualną ocenę heurystyczną z perspektywy każdego gracza
        eval_b = eval_hybrid(self.state, 'B')
        eval_w = eval_hybrid(self.state, 'W')
        
        self.lbl_eval_b.config(text=f"Ocena pozycji (B): {eval_b}")
        self.lbl_eval_w.config(text=f"Ocena pozycji (W): {eval_w}")

    def play_turn(self):
        if self.current_step < len(self.history) - 1:
            self.current_step += 1
            self.state = self.history[self.current_step]
            self.update_ui()


if __name__ == "__main__":
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

    print("Prekalkulacja całej gry. Proszę czekać...")
    state = BreakthroughState(initial_board)
    agent_b = MinimaxAgent('B', max_depth=3, heuristic_func=eval_hybrid)
    agent_w = MinimaxAgent('W', max_depth=4, heuristic_func=eval_hybrid)
    
    history = [state]
    stats = []
    
    current_player = 'B'
    agents = {'B': agent_b, 'W': agent_w}
    
    while not state.is_terminal():
        agent = agents[current_player]
        start_time = time.time()
        best_next_state, nodes = agent.get_best_move(state)
        elapsed = time.time() - start_time
        
        if best_next_state is None:
            break
            
        stats.append((current_player, elapsed, nodes))
        state = best_next_state
        history.append(state)
        current_player = 'W' if current_player == 'B' else 'B'
        
    print(f"Prekalkulacja zakończona! Wygenerowano {len(history)-1} ruchów.")

    root = tk.Tk()
    root.resizable(False, False)
    app = BreakthroughGUI(root, history, stats)
    root.mainloop()