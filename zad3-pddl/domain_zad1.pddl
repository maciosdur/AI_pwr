(define (domain transport)
  (:requirements :strips :typing :negative-preconditions
                 :numeric-fluents :action-costs)

  (:types
    location vehicle package - object
    truck plane ship - vehicle
  )

  (:predicates
    (at ?obj - object ?loc - location)
    (in ?pkg - package ?veh - vehicle)
    (road-connected ?l1 - location ?l2 - location)
    (air-connected  ?l1 - location ?l2 - location)
    (sea-connected  ?l1 - location ?l2 - location)
    (can-road ?v - vehicle)
    (can-air  ?v - vehicle)
    (can-sea  ?v - vehicle)
  )

  (:functions
    (total-cost)
    (road-dist ?l1 - location ?l2 - location)
    (air-dist  ?l1 - location ?l2 - location)
    (sea-dist  ?l1 - location ?l2 - location)
  )

  ;; Zaladuj paczke do pojazdu
  (:action load
    :parameters (?pkg - package ?veh - vehicle ?loc - location)
    :precondition (and
      (at ?pkg ?loc)
      (at ?veh ?loc)
    )
    :effect (and
      (in ?pkg ?veh)
      (not (at ?pkg ?loc))
      (increase (total-cost) 1)
    )
  )

  ;; Rozladuj paczke z pojazdu
  (:action unload
    :parameters (?pkg - package ?veh - vehicle ?loc - location)
    :precondition (and
      (in ?pkg ?veh)
      (at ?veh ?loc)
    )
    :effect (and
      (at ?pkg ?loc)
      (not (in ?pkg ?veh))
      (increase (total-cost) 1)
    )
  )

  ;; Jedz ciezarowka (droga)
  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and
      (at ?t ?from)
      (can-road ?t)
      (road-connected ?from ?to)
    )
    :effect (and
      (at ?t ?to)
      (not (at ?t ?from))
      (increase (total-cost) (road-dist ?from ?to))
    )
  )

  ;; Lec samolotem (lotniczo)
  (:action fly
    :parameters (?p - plane ?from - location ?to - location)
    :precondition (and
      (at ?p ?from)
      (can-air ?p)
      (air-connected ?from ?to)
    )
    :effect (and
      (at ?p ?to)
      (not (at ?p ?from))
      (increase (total-cost) (air-dist ?from ?to))
    )
  )

  ;; Plyn statkiem (morze)
  (:action sail
    :parameters (?s - ship ?from - location ?to - location)
    :precondition (and
      (at ?s ?from)
      (can-sea ?s)
      (sea-connected ?from ?to)
    )
    :effect (and
      (at ?s ?to)
      (not (at ?s ?from))
      (increase (total-cost) (sea-dist ?from ?to))
    )
  )
)