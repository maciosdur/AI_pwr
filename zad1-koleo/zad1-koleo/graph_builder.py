from datetime import datetime
from datetime import timedelta
from gtfs_parser import GTFSDataParser

class Edge:
    def __init__(self, to_node: str, dep_time: int, arr_time: int, trip_id: str, route_name: str, is_transfer: bool = False):
        self.to_node = to_node
        self.departure_time = dep_time  
        self.arrival_time = arr_time    
        self.trip_id = trip_id
        self.route_name = route_name
        self.is_transfer = is_transfer
        self.travel_time = arr_time - dep_time if not is_transfer else 0

    def __repr__(self):
        edge_type = "PRZESIADKA" if self.is_transfer else f"Linia {self.route_name}"
        return f"Edge(->{self.to_node}, {edge_type})"

class Node:
    def __init__(self, stop_id: str, name: str, lat: float, lon: float):
        self.stop_id = stop_id
        self.name = name
        self.lat = lat
        self.lon = lon

class TimeDependentGraph:
    def __init__(self):
        self.nodes = {}       # stop_id -> node
        self.adjacency = {}   # stop_id -> lista edge

    def build_graph(self, parser: GTFSDataParser, start_date: datetime, days_to_load: int = 2):
        print(f"budowanie grafu dla {days_to_load} dni, start {start_date.strftime('%Y-%m-%d')}")
        
        # nodes bez zmian
        for stop_id, stop_info in parser.stops.items():
            self.nodes[stop_id] = Node(stop_id, stop_info["name"], stop_info["lat"], stop_info["lon"])
            self.adjacency[stop_id] = []

        # dodawanie krawedzi dla kazdego dnia w zakresie days_to_load
        for day_offset in range(days_to_load):
            current_date = start_date + timedelta(days=day_offset)
            time_shift_sec = day_offset * 24 * 3600  # plus 24h za kazdy dzien
            
            for trip_id, stops in parser.stop_times.items():
                trip_info = parser.trips.get(trip_id)
                if not trip_info:
                    continue
                    
                service_id = trip_info["service_id"]
                route_name = trip_info["route_name"]

                # jesli nie jest aktywny pomijamy
                if not parser.is_service_active(service_id, current_date):
                    continue
                
                # tworzenie krawedzi
                for i in range(len(stops) - 1):
                    current_stop = stops[i]
                    next_stop = stops[i+1]
                    
                    # przesuniecie czasu
                    shifted_dep_time = current_stop["departure_sec"] + time_shift_sec
                    shifted_arr_time = next_stop["arrival_sec"] + time_shift_sec
                    
                    edge = Edge(
                        to_node=next_stop["stop_id"],
                        dep_time=shifted_dep_time,
                        arr_time=shifted_arr_time,
                        trip_id=trip_id,
                        route_name=route_name,
                        is_transfer=False
                    )
                    #dodanie krawedzi do grafu
                    self.adjacency[current_stop["stop_id"]].append(edge)

        # krawedzie przesiadkowe dla kazdych peronow na tej samej stacji
        for parent_station, platforms in parser.stations_to_platforms.items():
            if len(platforms) > 1:
                for p1 in platforms:
                    for p2 in platforms:
                        if p1 != p2:
                            self.adjacency[p1].append(Edge(p2, 0, 0, "TRANSFER", "Pieszo", True))

        print(f"koniec budowy, l wierzcholkow: {len(self.nodes)} - l krawedzi: {sum(len(edges) for edges in self.adjacency.values())}")

# --- Przykładowe użycie ---
if __name__ == "__main__":
    parser = GTFSDataParser(".")
    parser.parse_all()
    target_date = datetime(2026, 3, 24)
    graph = TimeDependentGraph()
    graph.build_graph(parser, target_date)
    print(f"Krawędzie wychodzące z pierwszego węzła: {list(graph.adjacency.values())[0][:3]}, nazwa pierwszego węzła: {list(graph.nodes.values())[0].name}, liczba krawędzi z pierwszego węzła: {len(list(graph.adjacency.values())[0])}")
    # 1413380,248,Wrocław Główny,,51.097917,17.037957,1,,
    # 1474861,,Wrocław Główny,,51.097917,17.037957,0,1413380,II
    # 1474640,,Wrocław Główny,,51.097917,17.037957,0,1413380,IV
    # 1474738,,Wrocław Główny,,51.097917,17.037957,0,1413380,I
    # 1536277,,Wrocław Główny,,51.097917,17.037957,0,1413380,VI
    # 1474679,,Wrocław Główny,,51.097917,17.037957,0,1413380,
    # 1536279,,Wrocław Główny,,51.097917,17.037957,0,1413380,III
    # 1474651,,Wrocław Główny,,51.097917,17.037957,0,1413380,V
    print(f"krawędzie wychodzące z węzła o ID '1474861': {graph.adjacency.get('1474861', [])}")
    wroclaw_edges = graph.adjacency.get('1474640', [])
    print(f"\n--- Znaleziono {len(wroclaw_edges)} krawędzi z węzła '1474640' (Wrocław Główny - peron IV) ---")
    for edge in wroclaw_edges:
        # Funkcja pomocnicza do zamiany sekund na HH:MM:SS 
        dep_time_str = f"{edge.departure_time // 3600:02d}:{(edge.departure_time % 3600) // 60:02d}:{edge.departure_time % 60:02d}"
        arr_time_str = f"{edge.arrival_time // 3600:02d}:{(edge.arrival_time % 3600) // 60:02d}:{edge.arrival_time % 60:02d}"
        
        print(f"Kierunek -> Węzeł {edge.to_node} ({graph.nodes[edge.to_node].name})")
        print(f"  Linia (route_name): {edge.route_name}")
        print(f"  Trip ID:          {edge.trip_id}")
        print(f"  Czas odjazdu:     {dep_time_str} (sekundy: {edge.departure_time})")
        print(f"  Czas przyjazdu:   {arr_time_str} (sekundy: {edge.arrival_time})")
        print(f"  Czas przejazdu:   {edge.travel_time} sekund")
        print(f"  Czy przesiadka?:  {edge.is_transfer}")
        print("-" * 50)