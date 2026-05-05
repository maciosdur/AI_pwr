import csv
from datetime import datetime

class GTFSDataParser:
    def __init__(self, data_dir="."):
        self.data_dir = data_dir
        
        self.calendar = {}
        self.calendar_dates = {}
        self.stops = {}
        self.stations_to_platforms = {}
        self.routes = {}
        self.trips = {}
        self.stop_times = {}  # trip_id -> lista postojow

    def parse_all(self):
        print("parsowanie start")
        self._load_calendar()
        self._load_calendar_dates()
        self._load_stops()
        self._load_routes()
        self._load_trips()
        self._load_stop_times()
        print("parsowanie koniec")


    # 1. Kalendarz i dni kursowania

    def _load_calendar(self):
        with open(f"{self.data_dir}/calendar.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.calendar[row["service_id"]] = row

    def _load_calendar_dates(self):
        with open(f"{self.data_dir}/calendar_dates.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                s_id = row["service_id"]
                date = row["date"]
                exc_type = int(row["exception_type"]) # 1 = dodany, 2 = usuniety
                
                if s_id not in self.calendar_dates:
                    self.calendar_dates[s_id] = {}
                self.calendar_dates[s_id][date] = exc_type

    def is_service_active(self, service_id: str, travel_date: datetime) -> bool:
        date_str = travel_date.strftime("%Y%m%d")
        
        # sprawdzenie wyjatkow z calendar_dates
        if service_id in self.calendar_dates and date_str in self.calendar_dates[service_id]:
            exception = self.calendar_dates[service_id][date_str]
            if exception == 1:
                return True
            elif exception == 2:
                return False
                
        # staly rozklad
        if service_id not in self.calendar:
            return False
            
        cal = self.calendar[service_id]
        if not (cal["start_date"] <= date_str <= cal["end_date"]):
            return False
            
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_name = weekdays[travel_date.weekday()]
        
        return cal[day_name] == "1"


    # 2. Przystanki (Stops)

    def _load_stops(self):
        with open(f"{self.data_dir}/stops.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stop_id = row["stop_id"]
                parent = row.get("parent_station", "").strip()
                
                self.stops[stop_id] = {
                    "name": row["stop_name"],
                    "lat": float(row["stop_lat"]),
                    "lon": float(row["stop_lon"]),
                    "parent_station": parent,
                    "location_type": row.get("location_type", "0")
                }
                
                # grupowanie peronow pod stacje (jesli istnieja)
                group_key = parent if parent else stop_id
                if group_key not in self.stations_to_platforms:
                    self.stations_to_platforms[group_key] = []
                self.stations_to_platforms[group_key].append(stop_id)


    # 3. Trasy i Kursy (Routes i Trips)

    def _load_routes(self):
        with open(f"{self.data_dir}/routes.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["route_short_name"].strip()
                if not name:
                    name = row["route_long_name"].strip()
                self.routes[row["route_id"]] = name

    def _load_trips(self):
        with open(f"{self.data_dir}/trips.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.trips[row["trip_id"]] = {
                    "route_id": row["route_id"],
                    "route_name": self.routes[row["route_id"]],
                    "service_id": row["service_id"]
                }


    # 4. Rozkłady jazdy (Stop Times) z konwersją czasu

    #metoda zamieniajaca czas w formacie HH:MM:SS na sekundy od polnocy
    @staticmethod
    def parse_time(time_str: str) -> int:
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    def _load_stop_times(self):
        with open(f"{self.data_dir}/stop_times.txt", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trip_id = row["trip_id"]
                
                stop_event = {
                    "stop_id": row["stop_id"],
                    "stop_sequence": int(row["stop_sequence"]),
                    "arrival_sec": self.parse_time(row["arrival_time"]),
                    "departure_sec": self.parse_time(row["departure_time"])
                }
                
                if trip_id not in self.stop_times:
                    self.stop_times[trip_id] = []
                self.stop_times[trip_id].append(stop_event)
                
        # sortowanie po stop_sequence dla kazdego trip_id
        for trip_id in self.stop_times:
            self.stop_times[trip_id].sort(key=lambda x: x["stop_sequence"])


if __name__ == "__main__":
    # przyklad uzycia
    parser = GTFSDataParser(data_dir=".")
    parser.parse_all()
    # 1004_398133,1,1,1,1,1,0,0,20260225,20260306 
    czy_jedzie = parser.is_service_active("1004_398133", datetime(2026, 3, 4))
    print(czy_jedzie)
    czy_jedzie = parser.is_service_active("1004_398133", datetime(2026, 3, 7))
    print(czy_jedzie)
    # 2808_400204,20260309,2 (usunięty 9 marca)
    # 2808_400204,1,1,1,1,1,1,1,20260308,20260317
    czy_jedzie = parser.is_service_active("2808_400204", datetime(2026, 3, 9))
    print(czy_jedzie)
    czy_jedzie = parser.is_service_active("2808_400204", datetime(2026, 3, 8))
    print(czy_jedzie)
    czy_jedzie = parser.is_service_active("2808_400204", datetime(2026, 3, 17))
    print(czy_jedzie)


    slowniki = {
            "calendar": parser.calendar,
            "calendar_dates": parser.calendar_dates,
            "stops": parser.stops,
            "stations_to_platforms": parser.stations_to_platforms,
            "routes": parser.routes,
            "trips": parser.trips,
            "stop_times": parser.stop_times
    }

    print("\n" + "="*50)
    print("PIERWSZE WARTOŚCI ZE SŁOWNIKÓW")
    print("="*50)

        
    for nazwa, slownik in slowniki.items():
            if slownik:  
                pierwszy_klucz = next(iter(slownik))
                pierwsza_wartosc = slownik[pierwszy_klucz]
                
                print(f"🔹 SŁOWNIK: {nazwa}")
                print(f"   Klucz:   {pierwszy_klucz}")
                print(f"   Wartość: {pierwsza_wartosc}\n")
            else:
                print(f"🔹 SŁOWNIK: {nazwa}")
                print("   (Słownik jest pusty)\n")

