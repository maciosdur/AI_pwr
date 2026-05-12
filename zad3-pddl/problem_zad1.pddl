(define (problem transport-p1)
  (:domain transport)

  (:objects
    ;; Lokacje
    warszawa krakow gdansk hamburg rotterdam - location

    ;; Pojazdy
    truck1 truck2  - truck
    plane1         - plane
    ship1          - ship

    ;; Paczki
    paczka1 paczka2 paczka3 - package
  )

  (:init
    ;; Polozenie pojazdow
    (at truck1  warszawa)
    (at truck2  krakow)
    (at plane1  warszawa)
    (at ship1   gdansk)

    ;; Polozenie paczek
    (at paczka1 warszawa)
    (at paczka2 krakow)
    (at paczka3 warszawa)

    ;; Typy pojazdow
    (can-road truck1)
    (can-road truck2)
    (can-air  plane1)
    (can-sea  ship1)

    ;; Polaczenia drogowe (symetryczne)
    (road-connected warszawa krakow)
    (road-connected krakow  warszawa)
    (road-connected warszawa gdansk)
    (road-connected gdansk  warszawa)
    (road-connected krakow  gdansk)
    (road-connected gdansk  krakow)

    ;; Polaczenia lotnicze
    (air-connected warszawa hamburg)
    (air-connected hamburg  warszawa)
    (air-connected krakow   hamburg)
    (air-connected hamburg  krakow)

    ;; Polaczenia morskie
    (sea-connected gdansk    rotterdam)
    (sea-connected rotterdam gdansk)
    (sea-connected gdansk    hamburg)
    (sea-connected hamburg   gdansk)

    ;; Koszty drogowe (jednostki umowne)
    (= (road-dist warszawa krakow) 3)
    (= (road-dist krakow  warszawa) 3)
    (= (road-dist warszawa gdansk)  6)
    (= (road-dist gdansk  warszawa) 6)
    (= (road-dist krakow  gdansk)   7)
    (= (road-dist gdansk  krakow)   7)

    ;; Koszty lotnicze
    (= (air-dist warszawa hamburg) 20)
    (= (air-dist hamburg  warszawa) 20)
    (= (air-dist krakow   hamburg) 20)
    (= (air-dist hamburg  krakow)  20)

    ;; Koszty morskie
    (= (sea-dist gdansk    rotterdam) 8)
    (= (sea-dist rotterdam gdansk)    8)
    (= (sea-dist gdansk    hamburg)   4)
    (= (sea-dist hamburg   gdansk)    4)

    ;; Koszt poczatkowy
    (= (total-cost) 0)
  )

  (:goal (and
    (at paczka1 rotterdam)
    (at paczka2 hamburg)
    (at paczka3 krakow)
  ))

  (:metric minimize (total-cost))
)