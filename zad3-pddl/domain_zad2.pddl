(define (domain robot-vacuum)
  (:requirements :strips :typing :negative-preconditions)

  (:types
    robot room - object
  )

  (:predicates
    (at ?r - robot ?p - room)
    (dirty ?p - room)
    (clean ?p - room)
    (connected ?p1 - room ?p2 - room)
  )

  ;; Przemieszcza robota miedzy polacznymi pokojami
  (:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (and
      (at ?r ?from)
      (connected ?from ?to)
    )
    :effect (and
      (at ?r ?to)
      (not (at ?r ?from))
    )
  )

  ;; Sprząta brudny pokoj w ktorym znajduje sie robot
  (:action clean
    :parameters (?r - robot ?p - room)
    :precondition (and
      (at ?r ?p)
      (dirty ?p)
      (not (clean ?p))
    )
    :effect (and
      (clean ?p)
      (not (dirty ?p))
    )
  )
)