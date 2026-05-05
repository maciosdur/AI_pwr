import sys
from datetime import datetime
from gtfs_parser import GTFSDataParser
from graph_builder import TimeDependentGraph
from algorithms import a_star_time, a_star_transfers, dijkstra_time
from tsp_tabu import TSPSolver

def time_str_to_seconds(time_str: str) -> int:
    #funk pom
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def main():
    # dane wejsciowe
    przystanek_A = "Wrocław Główny"
    # przystanek_A = "Lubawka"
    # przystanek_B = "Świdnica Miasto"          
    przystanek_B = "Jelenia Góra"          
    kryterium = "Ap"       # kryterium: 't' dijkstra czasu, 'Ap' A* przesiadki, 'At' A* czas 
    czas_rozpoczecia = "20:30:00"     
    
    start_time_sec = time_str_to_seconds(czas_rozpoczecia)
    
    data_podrozy = datetime(2026, 3, 24)

    parser = GTFSDataParser(data_dir=".") 
    parser.parse_all()

    graph = TimeDependentGraph()
    graph.build_graph(parser, data_podrozy, days_to_load=2)

    if kryterium == "t":
        print(f"\nUruchamiam algorytm Dijkstry (kryterium czasu)...")
        dijkstra_time(graph, przystanek_A, przystanek_B, start_time_sec)
    elif kryterium == "Ap":
        a_star_transfers(graph, przystanek_A, przystanek_B, start_time_sec)
    elif kryterium == "At":
        a_star_time(graph, przystanek_A, przystanek_B, start_time_sec)
    else:
        print("Nieznane kryterium optymalizacji. Wybierz 't', 'Ap' lub 'At'.", file=sys.stderr)
        
        
    #tabusearch
    przystanek_startowy = "Wrocław Główny"
    przystanki_do_odwiedzenia = ["Legnica", "Wrocław Mikołajów", "Mrozów", "Lubawka", "Zgorzelec"] # lista stacji do odwiedzenia 

    tsp = TSPSolver(graph, criterion="t", start_time_sec=start_time_sec)

    tsp.solve(
        start_node=przystanek_startowy, 
        stops_list=przystanki_do_odwiedzenia,
        limit_tabu=True,        # b
        # limit_tabu=False,        # b
        use_aspiration=True,    # c
        # use_aspiration=False,    # c
        use_sampling=True       # d
        # use_sampling=False       # d
    )

if __name__ == "__main__":
    main()