import random
import sys
import os
import time
from collections import deque
from algorithms import a_star_time, a_star_transfers, format_time

class TSPSolver:
    def __init__(self, graph, criterion, start_time_sec):
        self.graph = graph
        self.criterion = criterion
        self.start_time_sec = start_time_sec
        self.route_cache = {}  # slownik do wynikow A*

    def _get_route(self, node_a, node_b, current_time):
        cache_key = (node_a, node_b, current_time)
        if cache_key in self.route_cache:
            return self.route_cache[cache_key]

        # mute printow
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = open(os.devnull, 'w'), open(os.devnull, 'w')
        
        try:
            if self.criterion in ['t', 'At']:
                path = a_star_time(self.graph, node_a, node_b, current_time)
            else:
                path = a_star_transfers(self.graph, node_a, node_b, current_time)
        finally:
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout, sys.stderr = old_stdout, old_stderr

        # brak trasy
        if not path:
            self.route_cache[cache_key] = (float('inf'), float('inf'), [])
            return self.route_cache[cache_key]

        # obliczanie kosztu
        arrival_time = path[-1][1].arrival_time
        if self.criterion in ['t', 'At']:
            cost = arrival_time - current_time
        else:
            cost = 0
            curr_trip = None
            for _, edge in path:
                if not edge.is_transfer:
                    if curr_trip is not None and curr_trip != edge.trip_id:
                        cost += 1
                    curr_trip = edge.trip_id
        
        self.route_cache[cache_key] = (cost, arrival_time, path)
        return self.route_cache[cache_key]

    def evaluate_permutation(self, start_node, perm):
        curr_time = self.start_time_sec
        full_route_stops = [start_node] + list(perm) + [start_node] # trasa z powtorem
        full_path_edges = []

        # zlozenie trasy
        for i in range(len(full_route_stops) - 1):
            A = full_route_stops[i]
            B = full_route_stops[i+1]
            
            _, arr_time, edges = self._get_route(A, B, curr_time)
            
            if arr_time == float('inf') or not edges:
                return float('inf'), []
            
            curr_time = arr_time
            full_path_edges.extend(edges)

        # koszt trasy calk
        if self.criterion in ['t', 'At']:
            total_cost = full_path_edges[-1][1].arrival_time - self.start_time_sec
        else:
            total_cost = 0
            curr_trip = None
            for _, edge in full_path_edges:
                if not edge.is_transfer:
                    if curr_trip is not None and curr_trip != edge.trip_id:
                        total_cost += 1
                    curr_trip = edge.trip_id

        return total_cost, full_path_edges

    def solve(self, start_node, stops_list, limit_tabu=True, use_aspiration=True, use_sampling=True):
        print(f"Rozpoczynam Tabu Search (TSP) z {start_node} przez {len(stops_list)} przystanków...")
        start_compute_time = time.time()

        current_sol = list(stops_list)
        best_sol = current_sol.copy()
        best_cost, best_path = self.evaluate_permutation(start_node, best_sol)

        # def listy tabu
        # Podpunkt (a): brak ograniczen 
        # Podpunkt (b): kolejka fifo o ograniczonej dl
        max_tabu_size = max(5, len(stops_list) * 2) if limit_tabu else None
        tabu_list = deque(maxlen=max_tabu_size) 

        MAX_ITER = 20 # kryterium stopu 
        
        for iteration in range(MAX_ITER):
            # generoowanie sadziedztwa przez swap
            neighbors = []
            for i in range(len(current_sol)):
                for j in range(i + 1, len(current_sol)):
                    neighbor = current_sol.copy()
                    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                    neighbors.append(neighbor)
            
            # strategoia probkowania
            if use_sampling and len(neighbors) > 10:
                neighbors = random.sample(neighbors, 10)
            
            best_neighbor = None
            best_neighbor_cost = float('inf')
            best_neighbor_path = []

            for neighbor in neighbors:
                cost, path = self.evaluate_permutation(start_node, neighbor)
                
                is_tabu = tuple(neighbor) in tabu_list
                
                # kryterium aspiracji jesli rozwiazanie jest tabu ale lepsze to i tak je wybieramy
                if is_tabu and use_aspiration and cost < best_cost:
                    is_tabu = False

                # lepszy sasiad, ktory nie jest tabu lub spelnia kryterium aspiracji
                if not is_tabu and cost < best_neighbor_cost:
                    best_neighbor_cost = cost
                    best_neighbor = neighbor
                    best_neighbor_path = path

            if best_neighbor is None:
                break

            # akt rozwiazania i akta tabu
            current_sol = best_neighbor
            tabu_list.append(tuple(current_sol))

            # Akt optimum
            if best_neighbor_cost < best_cost:
                best_cost = best_neighbor_cost
                best_sol = best_neighbor
                best_path = best_neighbor_path
                
        calc_time_ms = (time.time() - start_compute_time) * 1000
        
        # print wyniku
        print(f"\n--- WYNIK TABU SEARCH (TSP) ---")
        print(f"Najlepsza kolejność: {start_node} -> {' -> '.join(best_sol)} -> {start_node}")
        
        current_trip = None
        for u, edge in best_path:
            if edge.is_transfer:
                continue
            if current_trip != edge.trip_id:
                print(f"\n[POCIĄG] LINIA: {edge.route_name} (Wsiadasz w {self.graph.nodes[u].name} o {format_time(edge.departure_time)})")
                current_trip = edge.trip_id
            dep_str = format_time(edge.departure_time)
            arr_str = format_time(edge.arrival_time)
            print(f"  -> Dojazd do: {self.graph.nodes[edge.to_node].name:<25} | {dep_str} - {arr_str}")

        if self.criterion in ['t', 'At']:
            h = best_cost // 3600
            m = (best_cost % 3600) // 60
            sys.stderr.write(f"\nTabu Search zoptymalizowany koszt: {h}h {m}min ({best_cost} sek)\n")
        else:
            sys.stderr.write(f"\nTabu Search zoptymalizowany koszt: {best_cost} przesiadek\n")
        sys.stderr.write(f"Czas obliczeń: {calc_time_ms:.2f} ms\n")
        return best_sol, best_path