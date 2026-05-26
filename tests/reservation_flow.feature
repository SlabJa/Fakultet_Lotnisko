Feature: End-to-end Ticket Booking Process
  As a customer of the airline
  I want to configure my ticket, apply my loyalty discount, and pay
  So that I have a guaranteed seat on the flight

  Scenario Outline: Passenger books and pays for a flight
    Given Passenger "<name>" is <age> years old
    And Passenger's loyalty account balance is "<miles>"
    When Passenger selects flight "<flight>" with base price <base_price> PLN
    And Chooses "<travel_class>" class and <baggage> kg of baggage
    And Confirms the reservation
    And Pays for the booking with card "<card>"
    Then The final charged amount should be <expected_price> PLN
    And Booking status changes to "PAID"

    Examples:
      | name   | age | miles | flight | base_price | travel_class | baggage | card      | expected_price |
      # Dorosły, klasa ECONOMY, brak nadbagażu, BRAK KONTA LOJALNOŚCIOWEGO
      | John   | 30  | NONE  | LO123  | 200.0      | ECONOMY      | 15.0    | 1111-2222 | 200.0          |
      # Dziecko, klasa FIRST, status BRONZE (0 mil -> mnożnik 1.0)
      | Anna   | 8   | 0     | LH999  | 300.0      | FIRST        | 10.0    | 1111-2222 | 300.0          |
      # Senior, klasa BUSINESS, status GOLD (10% off)
      | Robert | 70  | 60000 | BA456  | 200.0      | BUSINESS     | 20.0    | 3333-4444 | 189.0          |
      # Dorosły, klasa ECONOMY, 25kg (+50 PLN nadbagażu), status SILVER (5% off)
      | Eve    | 25  | 15000 | LO123  | 200.0      | ECONOMY      | 25.0    | 5555-6666 | 237.5          |