(define (problem robot-vacuum-p1)
  (:domain robot-vacuum)

  (:objects
    robot1 - robot
    pokoj1 pokoj2 pokoj3 - room
  )

  (:init
    (at robot1 pokoj1)
    (dirty pokoj1)
    (dirty pokoj2)
    (dirty pokoj3)
    (connected pokoj1 pokoj2)
    (connected pokoj2 pokoj1)
    (connected pokoj2 pokoj3)
    (connected pokoj3 pokoj2)
  )

  (:goal (and
    (clean pokoj1)
    (clean pokoj2)
    (clean pokoj3)
  ))
)