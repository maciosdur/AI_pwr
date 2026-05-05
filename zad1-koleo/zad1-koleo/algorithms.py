import heapq
import time
import sys
import math
from graph_builder import TimeDependentGraph


# FUNKCJE POMOCNICZE I HEURYSTYKA

def format_time(seconds: int) -> str:
    h = (seconds // 3600) % 24
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def fast_heuristic_time(node_lat, node_lon, target_lat, target_lon):
    dx = abs(node_lon - target_lon) * 70000
    dy = abs(node_lat - target_lat) * 111000
    
    # odl manh
    dist_m = dx + dy
    
    # v maks 50 km/h = 13.9 m/s
    return dist_m / 13 * 4

def get_start_and_end_nodes(graph: TimeDependentGraph, start_name: str, end_name: str):
    start_stops = [s_id for s_id, node in graph.nodes.items() if node.name == start_name]
    end_stops = set(s_id for s_id, node in graph.nodes.items() if node.name == end_name)
    return start_stops, end_stops


# 1. ALGORYTM DIJKSTRY (CZAS) 

def dijkstra_time(graph: TimeDependentGraph, start_name: str, end_name: str, start_time_sec: int):
    start_nodes, end_nodes = get_start_and_end_nodes(graph, start_name, end_name)
    if not start_nodes or not end_nodes:
        return None

    # kolejka: (czas_dotarcia, aktualny_węzeł, aktualny_trip_id) 
    pq = []
    # slownik odwiedzonych: (stop_id, trip_id) -> min_czas_dotarcia 
    best_time = {}
    parent = {}

    for start_node in start_nodes:
        heapq.heappush(pq, (start_time_sec, start_node, None))
        best_time[(start_node, None)] = start_time_sec

    start_compute_time = time.time()
    target_state = None

    while pq:
        curr_time, u, curr_trip = heapq.heappop(pq) 

        if curr_time > best_time.get((u, curr_trip), float('inf')):
            continue

        if u in end_nodes:
            target_state = (u, curr_trip)
            break

        for edge in graph.adjacency.get(u, []): 
            if edge.is_transfer:
                # zmiana peronu +180s
                nxt_time = curr_time + 180
                nxt_trip = "TRANSFER"
                if nxt_time < best_time.get((edge.to_node, nxt_trip), float('inf')):
                    best_time[(edge.to_node, nxt_trip)] = nxt_time
                    parent[(edge.to_node, nxt_trip)] = (u, curr_trip, edge)
                    heapq.heappush(pq, (nxt_time, edge.to_node, nxt_trip))
            else:
                # pociag
                is_changing_trains = (curr_trip is not None and curr_trip != "TRANSFER" and curr_trip != edge.trip_id)
                min_departure_allowed = curr_time + (180 if is_changing_trains else 0)

                if edge.departure_time >= min_departure_allowed:
                    nxt_time = edge.arrival_time
                    nxt_trip = edge.trip_id
                    if nxt_time < best_time.get((edge.to_node, nxt_trip), float('inf')):
                        best_time[(edge.to_node, nxt_trip)] = nxt_time
                        parent[(edge.to_node, nxt_trip)] = (u, curr_trip, edge)
                        heapq.heappush(pq, (nxt_time, edge.to_node, nxt_trip))

    calc_time_ms = (time.time() - start_compute_time) * 1000
    if not target_state: return None
    
    return _reconstruct_and_print(graph, parent, target_state, start_name, end_name, start_time_sec, best_time[target_state], calc_time_ms, "Czas przejazdu")


# 2. ALGORYTM A* (CZAS) 


def a_star_time(graph: TimeDependentGraph, start_name: str, end_name: str, start_time_sec: int):
    start_nodes, end_nodes = get_start_and_end_nodes(graph, start_name, end_name)
    if not start_nodes or not end_nodes: return None

    # liczymy srodek stacji na poczatku
    target_lat = sum(graph.nodes[n].lat for n in end_nodes) / len(end_nodes)
    target_lon = sum(graph.nodes[n].lon for n in end_nodes) / len(end_nodes)

    # kolejka: (f_score, czas_dotarcia, aktualny_węzeł, aktualny_trip_id)
    pq = []
    best_time = {}
    parent = {}

    for start_node in start_nodes:
        h = fast_heuristic_time(graph.nodes[start_node].lat, graph.nodes[start_node].lon, target_lat, target_lon)
        heapq.heappush(pq, (start_time_sec + h, start_time_sec, start_node, None))
        best_time[(start_node, None)] = start_time_sec

    start_compute_time = time.time()
    target_state = None

    while pq:
        f_score, curr_time, u, curr_trip = heapq.heappop(pq)

        if curr_time > best_time.get((u, curr_trip), float('inf')): continue

        if u in end_nodes:
            target_state = (u, curr_trip)
            break

        for edge in graph.adjacency.get(u, []):
            if edge.is_transfer:
                nxt_time = curr_time + 180
                nxt_trip = "TRANSFER"
                if nxt_time < best_time.get((edge.to_node, nxt_trip), float('inf')):
                    best_time[(edge.to_node, nxt_trip)] = nxt_time
                    parent[(edge.to_node, nxt_trip)] = (u, curr_trip, edge)
                    
                    # Szybka heurystyka
                    h = fast_heuristic_time(graph.nodes[edge.to_node].lat, graph.nodes[edge.to_node].lon, target_lat, target_lon)
                    heapq.heappush(pq, (nxt_time + h, nxt_time, edge.to_node, nxt_trip))
            else:
                is_changing_trains = (curr_trip is not None and curr_trip != "TRANSFER" and curr_trip != edge.trip_id)
                min_departure_allowed = curr_time + (180 if is_changing_trains else 0)

                if edge.departure_time >= min_departure_allowed:
                    nxt_time = edge.arrival_time
                    nxt_trip = edge.trip_id
                    if nxt_time < best_time.get((edge.to_node, nxt_trip), float('inf')):
                        best_time[(edge.to_node, nxt_trip)] = nxt_time
                        parent[(edge.to_node, nxt_trip)] = (u, curr_trip, edge)
                        
                        # Szybka heurystyka
                        h = fast_heuristic_time(graph.nodes[edge.to_node].lat, graph.nodes[edge.to_node].lon, target_lat, target_lon)
                        heapq.heappush(pq, (nxt_time + h, nxt_time, edge.to_node, nxt_trip))
                        
    calc_time_ms = (time.time() - start_compute_time) * 1000
    if not target_state: return None
    return _reconstruct_and_print(graph, parent, target_state, start_name, end_name, start_time_sec, best_time[target_state], calc_time_ms, "Czas przejazdu (A*)")


# 3. ALGORYTM A* (PRZESIADKI)

def a_star_transfers(graph: TimeDependentGraph, start_name: str, end_name: str, start_time_sec: int):
    start_nodes, end_nodes = get_start_and_end_nodes(graph, start_name, end_name)
    if not start_nodes or not end_nodes: return None

    target_lat = sum(graph.nodes[n].lat for n in end_nodes) / len(end_nodes)
    target_lon = sum(graph.nodes[n].lon for n in end_nodes) / len(end_nodes)

    # ogroma kara za przesiadke - gwarancja ze mniej przesiadek bedzie lepsze niz wiecej przesiadek
    TRANSFER_PENALTY = 3600 * 8

    # kolejka: (f_score, g_score_kary, czas_dotarcia, aktualny_węzeł, aktualny_trip_id, liczba_przesiadek)
    pq = []
    # (stop_id, trip_id) -> min_g_score
    best_cost = {} 
    parent = {}

    for start_node in start_nodes:
        h = fast_heuristic_time(graph.nodes[start_node].lat, graph.nodes[start_node].lon, target_lat, target_lon)
        # g_score_kary początkowo to start_time_sec (bez kar)
        heapq.heappush(pq, (start_time_sec + h, start_time_sec, start_time_sec, start_node, None, 0))
        best_cost[(start_node, None)] = start_time_sec

    start_compute_time = time.time()
    target_state = None

    while pq:
        f_score, g_score, curr_time, u, curr_trip, curr_transfers = heapq.heappop(pq)

        # jesli gorzej to ignoruemy
        if g_score > best_cost.get((u, curr_trip), float('inf')):
            continue

        if u in end_nodes:
            target_state = (u, curr_trip)
            break

        for edge in graph.adjacency.get(u, []):
            if edge.is_transfer:
                nxt_time = curr_time + 180
                nxt_trip = "TRANSFER" if curr_trip is not None else None
                nxt_transfers = curr_transfers
                
                # zmiana peronu +180s ale bez kary
                nxt_g_score = g_score + 180 
                
                if nxt_g_score < best_cost.get((edge.to_node, nxt_trip), float('inf')):
                    best_cost[(edge.to_node, nxt_trip)] = nxt_g_score
                    parent[(edge.to_node, nxt_trip)] = (u, curr_trip, edge)
                    h = fast_heuristic_time(graph.nodes[edge.to_node].lat, graph.nodes[edge.to_node].lon, target_lat, target_lon)
                    heapq.heappush(pq, (nxt_g_score + h, nxt_g_score, nxt_time, edge.to_node, nxt_trip, nxt_transfers))
            else:
                is_changing_trains = (curr_trip is not None and curr_trip != "TRANSFER" and curr_trip != edge.trip_id)
                min_departure_allowed = curr_time + (180 if is_changing_trains else 0)

                if edge.departure_time >= min_departure_allowed:
                    nxt_time = edge.arrival_time
                    nxt_trip = edge.trip_id
                    
                    is_new_ride = (curr_trip is not None and curr_trip != edge.trip_id)
                    nxt_transfers = curr_transfers + (1 if is_new_ride else 0)
                    
                    # dodajemy kare jesli nowy ride
                    travel_time = edge.arrival_time - curr_time
                    penalty = TRANSFER_PENALTY if is_new_ride else 0
                    nxt_g_score = g_score + travel_time + penalty

                    if nxt_g_score < best_cost.get((edge.to_node, nxt_trip), float('inf')):
                        best_cost[(edge.to_node, nxt_trip)] = nxt_g_score
                        parent[(edge.to_node, nxt_trip)] = (u, curr_trip, edge)
                        h = fast_heuristic_time(graph.nodes[edge.to_node].lat, graph.nodes[edge.to_node].lon, target_lat, target_lon)
                        heapq.heappush(pq, (nxt_g_score + h, nxt_g_score, nxt_time, edge.to_node, nxt_trip, nxt_transfers))

    calc_time_ms = (time.time() - start_compute_time) * 1000
    if not target_state: return None
    
    # odzyskanie wartosci
    path = []
    curr = target_state
    final_time = 0
    while curr in parent:
        prev_u, prev_trip, edge = parent[curr]
        if final_time == 0:
            final_time = edge.arrival_time 
        path.append((prev_u, edge))
        curr = (prev_u, prev_trip)
    path.reverse()
    
    actual_transfers = 0
    current_trip_check = None
    for _, edge in path:
        if not edge.is_transfer:
            if current_trip_check is not None and current_trip_check != edge.trip_id:
                actual_transfers += 1
            current_trip_check = edge.trip_id

    return _reconstruct_and_print(graph, parent, target_state, start_name, end_name, start_time_sec, final_time, calc_time_ms, f"Przesiadki ({actual_transfers})")


# ==========================================
# WSPÓLNA REKONSTRUKCJA I WYPISYWANIE
# ==========================================

def _reconstruct_and_print(graph, parent, target_state, start_name, end_name, start_time_sec, end_time_sec, calc_time_ms, criterion_name):
    # rekonstrukacja od tylu
    path = []
    curr = target_state
    while curr in parent:
        prev_u, prev_trip, edge = parent[curr]
        path.append((prev_u, edge))
        curr = (prev_u, prev_trip)
    path.reverse()

    print(f"\n{'='*50}")
    print(f"TRASA: {start_name} -> {end_name}")
    print(f"{'='*50}")
    
    current_trip = None
    for u, edge in path:
        if edge.is_transfer:
            print(f"  [Pieszo] Przejście pieszo na stacji {graph.nodes[u].name} (ok. 3 minuty)")
            continue
            
        if current_trip != edge.trip_id:
            print(f"\n[POCIĄG] LINIA: {edge.route_name} (Wsiadasz o {format_time(edge.departure_time)})")
            current_trip = edge.trip_id
            
        dep_str = format_time(edge.departure_time)
        arr_str = format_time(edge.arrival_time)
        stop_name = graph.nodes[edge.to_node].name
        print(f"  -> Dojazd do: {stop_name:<25} | {dep_str} - {arr_str}")

    total_travel_time_min = (end_time_sec - start_time_sec) / 60
    sys.stderr.write(f"\n--- Statystyki ---\n")
    sys.stderr.write(f"Zoptymalizowane kryterium ({criterion_name}): {total_travel_time_min:.2f} minut\n")
    sys.stderr.write(f"Czas obliczeń: {calc_time_ms:.2f} ms\n")
    
    return path