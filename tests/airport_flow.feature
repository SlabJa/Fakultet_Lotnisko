Feature: End-to-end Airport Experience
  As a passenger arriving at the airport with a ticket
  I want to go through check-in, security, and the boarding gate
  So that I can board my plane safely

  Scenario Outline: Passenger goes through check-in, security, and boarding
    Given Passenger "<name>" has a "PAID" booking for flight "<flight>"
    When Passenger presents passport "<passport>" at check-in
    And Drops off a bag containing "<item>"
    Then Check-in process resolves with "<desk_result>"
    And If successful, passenger attempts to board gate "<gate_flight>"
    Then Boarding gate resolves with "<gate_result>"

    Examples:
      | name  | flight | passport  | item   | desk_result     | gate_flight | gate_result |
      # Wszystko poprawne
      | John  | LO3801 | AB1234567 | Book   | SUCCESS         | LO3801      | SUCCESS     |
      # Zły format paszportu (Check-in rzuca ValueError)
      | Anna  | LO3801 | 123456    | Book   | ValueError      | LO3801      | SKIPPED     |
      # Zakazany przedmiot (Security blokuje, PermissionError)
      | Bob   | LH1234 | CD9876543 | OSTRZE | PermissionError | LH1234      | SKIPPED     |
      # Pasażer idzie do złej bramki (Check-in SUCCESS, Gate rzuca ValueError)
      | Eve   | LO3801 | EF1122334 | Laptop | SUCCESS         | LH1234      | ValueError  |