# Breakthrough - Minimax & Alfa-Beta

Projekt realizujący zadanie z przedmiotu *Sztuczna inteligencja i inżynieria wiedzy* (Lista 2).
Celem projektu jest implementacja algorytmu Minimax z alfa-beta cięciami grającego w grę planszową Breakthrough.

## Stan obecny (Zrealizowane punkty)

Zgodnie z wymaganiami zadania, w pliku `logic.py` zaimplementowano **wersję podstawową** gry. Obejmuje ona:

1. **Reprezentację stanu gry i generację ruchów (10 pkt):**
   - Klasa `BreakthroughState` przechowuje planszę w postaci dwuwymiarowej tablicy.
   - Posiada logikę rozpoznawania końca gry (`is_terminal`, `is_winner`).
   - Metoda `get_possible_moves` poprawnie generuje legalne ruchy (ruch do przodu na puste pole, bicie po skosie). Wykonywane jest tu również wstępne sortowanie ruchów (bicia mają wyższy priorytet), co poprawia działanie alfa-beta cięć.

2. **Heurystyki oceny stanu gry (20 pkt):**
   Zaimplementowano trzy różne strategie oceny dla każdego gracza:
   - **Przewaga materialna (`eval_material`):** Porównuje liczbę pionków gracza z liczbą pionków przeciwnika.
   - **Wyścig do mety (`eval_race`):** Mierzy odległość najbardziej wysuniętego pionka od linii końcowej (mety).
   - **Presja terytorialna (`eval_pressure`):** Wykorzystuje wagi pozycji (kwadrat odległości od bazy), silniej promując pionki znajdujące się głębiej na planszy przeciwnika.
   - Dodatkowo zaimplementowano funkcję **`evaluate_hybrid`**, która jest kombinacją liniową trzech powyższych strategii. Jest ona zoptymalizowana w taki sposób, by w jednym przejściu po planszy zebrać wszystkie dane.

3. **Algorytm Minimax z cięciami Alfa-Beta (30 + 40 pkt):**
   - Metoda `minimax` w klasie `Game` przeszukuje drzewo decyzyjne do wyznaczonej maksymalnej głębokości (`max_depth`).
   - Zastosowano mechanizm cięć alfa-beta, znacząco optymalizując proces przeglądania.
   - Symulowana jest rozrywka, gdzie gracz pierwszy gra według Minimax, a gracz drugi gra wykonując symetryczne optymalne ruchy w stosunku do tej samej heurystyki. 

4. **Wyświetlanie wyników:**
   - Na standardowe wyjście (STDOUT) wypisywana jest plansza końcowa, liczba rund i zwycięzca.
   - Na standardowe wyjście błędów (STDERR) wypisywana jest liczba odwiedzonych węzłów (metryka) oraz czas działania gry w sekundach.

## Co wymaga modyfikacji do pełnej zgodności ze specyfikacją / wersją rozszerzoną
Obecny kod stanowi solidną bazę i realizuje "wersję podstawową" w logice działania, jednak aby w pełni zaspokoić drobne wymagania wejścia-wyjścia z punktacji oraz osiągnąć cel wersji rozszerzonej, brakuje:
* **Czytania ze standardowego wejścia:** Program w obecnej formie używa hardkodowanej tablicy `initial_board`. Należy dodać odczyt ze `stdin`, a także możliwość konfiguracji parametru głębokości `d` oraz wybór heurystyki (np. jako argumenty CLI).
* **Znak 'o' na planszy:** Zadanie przewiduje oznaczanie pola, z którego wykonano ruch jako `_` lub `o` (w zależności od wariantu śledzenia ruchów) - zaimplementowano mechanizm w kodzie, ale obecnie jest zakomentowany (nadpisuje `_`).
* **Wersja rozszerzona (20 pkt):** Brakuje możliwości ustawienia dwóch różnych agentów grających różnymi strategiami / adaptujących swoją strategię.

## Uruchomienie programu

Aby uruchomić obecną wersję silnika Breakthrough:

```bash
python logic.py
```

Podczas gry, program będzie wypisywał kolejne rundy (dla debugowania), a na końcu działania:
- Planszę końcową
- Wypisze zwycięzcę
- Wypisze liczbę rund
- Zwróci informacje o metrykach algorytmu do `stderr`.
