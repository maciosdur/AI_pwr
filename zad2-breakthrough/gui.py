import tkinter as tk
import math
import time

# Importujemy klasy z Twojego pliku z logiką
# UPEWNIJ SIĘ, że plik z logiką nazywa się logic.py
from logic import BreakthroughState, Game, initial_board

class BreakthroughGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Breakthrough AI - Minimax Visualization")
        
        # --- Parametry gry ---
        self.current_player = 'B'
        self.rounds = 0
        self.max_depth = 4
        
        # Inicjalizacja logiki z zaimportowanej planszy
        self.state = BreakthroughState(initial_board)
        self.game = Game(initial_board, max_depth=self.max_depth)
        
        # Aktualizujemy state w obiekcie game, aby oba wskazywały na to samo
        self.game.state = self.state 

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
        colors = ["#f0d9b5", "#b58863"] # Kolory jasny i ciemny szachownicy
        
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
                if piece != '_':
                    # Odstęp pionka od krawędzi pola
                    pad = 10
                    p_color = "#333333" if piece == 'B' else "#ffffff"
                    o_color = "#000000" if piece == 'W' else ""
                    self.canvas.create_oval(x0+pad, y0+pad, x1-pad, y1-pad, fill=p_color, outline=o_color, width=2)

    def update_ui(self):
        # 1. Rysuj planszę
        self.draw_board()
        
        # 2. Aktualizuj etykiety
        self.lbl_round.config(text=f"Runda: {self.rounds}")
        
        if self.current_player == 'B':
            self.lbl_turn.config(text="Tura: Gracz B (Idzie w dół)", fg="#333333")
        else:
            self.lbl_turn.config(text="Tura: Gracz W (Idzie w górę)", fg="#888888")

        # 3. Oblicz i wyświetl aktualną ocenę heurystyczną z perspektywy każdego gracza
        # Używamy ewaluacji hybrydowej z domyślnymi wagami z Twojej logiki
        eval_b = self.state.evaluate_hybrid('B')
        eval_w = self.state.evaluate_hybrid('W')
        
        self.lbl_eval_b.config(text=f"Ocena pozycji (B): {eval_b}")
        self.lbl_eval_w.config(text=f"Ocena pozycji (W): {eval_w}")

        # 4. Sprawdź warunek końca gry
        if self.state.is_terminal():
            winner = 'B' if self.state.is_winner('B') else 'W'
            self.lbl_status.config(text=f"Koniec gry! Wygrywa gracz: {winner}")
            self.btn_next.config(state="disabled")

    def play_turn(self):
        if self.state.is_terminal():
            return

        self.btn_next.config(state="disabled") # Blokada przycisku na czas myślenia AI
        self.master.update() # Wymuszenie odświeżenia UI

        start_time = time.time()
        
        # Wywołanie algorytmu Minimax z Twojej klasy Game
        _, best_next_state = self.game.minimax(
            self.state, self.max_depth, -math.inf, math.inf, True, self.current_player
        )
        
        print(f"Ruch przeliczony w {time.time() - start_time:.2f} s")

        if best_next_state is None:
            self.lbl_status.config(text=f"Brak ruchów dla gracza {self.current_player}!")
            return

        # Aktualizacja stanu
        self.state = best_next_state
        self.game.state = best_next_state
        
        # Zmiana gracza i licznika rund
        if self.current_player == 'W':
            self.rounds += 1
            
        self.current_player = 'W' if self.current_player == 'B' else 'B'

        self.update_ui()
        self.btn_next.config(state="normal") # Odblokowanie przycisku


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = BreakthroughGUI(root)
    root.mainloop()