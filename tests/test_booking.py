import pytest
from src.booking import Ticket, Booking, Flight

class TestTicketBoundaryValues:
    """Testy logiczne wyliczania cen biletów na granicach przedziałów wiekowych."""

    @pytest.mark.parametrize("age, expected_price", [
        (1, 0.0),      # Niemowlę (granica <2 lat) -> zniżka 100%
        (2, 50.0),     # Dokładnie 2 lata (Dziecko) -> zniżka 50%
        (11, 50.0),    # Starsze dziecko (granica <12 lat) -> zniżka 50%
        (12, 100.0),   # Dokładnie 12 lat (Dorosły) -> 100% ceny bazowej
        (64, 100.0),   # Starszy dorosły (granica <65 lat) -> 100% ceny bazowej
        (65, 70.0),    # Dokładnie 65 lat (Senior) -> zniżka 30%
    ])
    def test_calculate_price_boundaries(self, age, expected_price):
        """Test poprawnego wyliczania ceny biletów na kluczowych granicach klas wiekowych."""
        ticket = Ticket("Jan Kowalski", age, 100.0)
        assert ticket.calculate_price() == expected_price

    @pytest.mark.parametrize("invalid_age, invalid_price, expected_exception", [
        (-1, 100, ValueError),
        (25, -50, ValueError),
        ("25", 100, TypeError),
        (25, "100", TypeError),
    ])
    def test_ticket_creation_errors(self, invalid_age, invalid_price, expected_exception):
        """Testy negatywne sprawdzające rzucanie wyjątków przy niepoprawnych danych biletowych."""
        with pytest.raises(expected_exception):
            Ticket("Test", invalid_age, invalid_price)


class TestFlightInventory:
    """Testy sprawdzające zarządzanie wolnymi miejscami oraz flotą samolotu."""

    def test_flight_overbooking(self):
        """Test negatywny: Próba rezerwacji ponad limit miejsc kończy się błędem."""
        flight = Flight("LO3801", total_seats=1)
        flight.reserve_seat()
        
        assert flight.has_available_seats() is False
        with pytest.raises(LookupError):
            flight.reserve_seat()

    def test_flight_release_seat(self):
        """Test sprawdzający, czy zwalnianie konkretnego miejsca działa poprawnie."""
        flight = Flight("LO3801", total_seats=5)
        
        # Automatycznie przydzielone miejsce
        assigned_seat = flight.reserve_seat() 
        flight.release_seat(assigned_seat) 
        
        assert flight.reserved_seats == 0

    def test_invalid_flight_creation(self):
        """Test negatywny: Tworzenie lotu z zerową lub ujemną liczbą miejsc."""
        with pytest.raises(ValueError):
            Flight("LO3801", total_seats=0)


class TestBookingStateTransitions:
    """Testy przejść między stanami rezerwacji (maszyny stanów biznesowych)."""

    @pytest.fixture
    def booking_ctx(self):
        """Fixture przygotowujący czysty kontekst rezerwacji lotu."""
        flight = Flight("LO3801", total_seats=2)
        ticket = Ticket("Anna Nowak", 30, 100.0)
        return Booking(flight, ticket)

    def test_successful_reservation_flow(self, booking_ctx):
        """Test poprawnego przejścia ze szkicu do rezerwacji (blokowanie fizycznego miejsca)."""
        assert booking_ctx.status == "DRAFT"
        booking_ctx.confirm_reservation()
        assert booking_ctx.status == "RESERVED"
        assert booking_ctx.flight.reserved_seats == 1

    def test_cancellation_releases_seat(self, booking_ctx):
        """Test sprawdzający, czy anulowanie rezerwacji poprawnie zwalnia zablokowane miejsce."""
        booking_ctx.confirm_reservation()
        booking_ctx.change_status("CANCELLED")
        assert booking_ctx.flight.reserved_seats == 0

    @pytest.mark.parametrize("current_state, illegal_next_state", [
        ("DRAFT", "PAID"),
        ("DRAFT", "CANCELLED"),
        ("CANCELLED", "RESERVED"),
    ])
    def test_illegal_transitions(self, booking_ctx, current_state, illegal_next_state):
        """Testy negatywne: wymuszenie zabronionego kroku w maszynie stanów."""
        if current_state == "RESERVED":
            booking_ctx.confirm_reservation()
        elif current_state == "CANCELLED":
            booking_ctx.confirm_reservation()
            booking_ctx.change_status("CANCELLED")

        with pytest.raises(RuntimeError):
            booking_ctx.change_status(illegal_next_state)


class TestTicketClassesAndBaggage:
    """Testy logiczne dla różnych klas podróży oraz polityki nadbagażu."""

    @pytest.mark.parametrize("age, travel_class, baggage, expected_price", [
        # --- Dorośli - 100% ceny bazowej ---
        (30, "ECONOMY", 20.0, 100.0),
        (30, "ECONOMY", 25.0, 150.0),
        (30, "BUSINESS", 15.0, 150.0),
        (30, "FIRST", 10.0, 200.0),
        
        # --- Dzieci - 50% zniżki ---
        (8, "ECONOMY", 20.0, 50.0),
        (8, "BUSINESS", 15.0, 75.0),
        (8, "FIRST", 10.0, 100.0),
        
        # --- Seniorzy - 30% zniżki ---
        (70, "ECONOMY", 20.0, 70.0),
        (70, "BUSINESS", 15.0, 105.0),
        (70, "FIRST", 10.0, 140.0),

        # --- Niemowlęta - 100% zniżki ---
        (1, "BUSINESS", 10.0, 0.0),
        (1, "FIRST", 10.0, 0.0),
    ])
    def test_class_pricing_and_baggage_fees(self, age, travel_class, baggage, expected_price):
        """Testuje krzyżowo, jak wiek, klasa podróży i waga bagażu wpływają na ostateczną cenę."""
        ticket = Ticket("Test Pasażer", age, 100.0, travel_class=travel_class, baggage_weight=baggage)
        assert ticket.calculate_price() == expected_price

    def test_first_class_catering(self):
        """Test sprawdzający przydział darmowego cateringu dla pierwszej klasy."""
        economy_ticket = Ticket("Adam", 30, 100.0, "ECONOMY")
        first_ticket = Ticket("Ewa", 30, 100.0, "FIRST")
        
        assert economy_ticket.has_free_meal() is False
        assert first_ticket.has_free_meal() is True

    @pytest.mark.parametrize("invalid_class, invalid_baggage, exception", [
        ("PREMIUM_ECONOMY", 10.0, ValueError),
        ("ECONOMY", -5.0, ValueError),
        ("ECONOMY", "15", TypeError),
    ])
    def test_invalid_class_or_baggage(self, invalid_class, invalid_baggage, exception):
        """Testy negatywne dla błędnych danych klasy lotu lub wagi nadawanego bagażu."""
        with pytest.raises(exception):
            Ticket("Test", 30, 100.0, travel_class=invalid_class, baggage_weight=invalid_baggage)


class TestBookingSeatIntegration:
    """Testy integracyjne łączące maszynę rezerwacji (Booking) z mapą pokładu samolotu (SeatMap)."""

    def test_confirm_reservation_with_specific_seat(self):
        """Test pozytywny: Rezerwacja udaje się na dokładnie wybrane przez pasażera miejsce."""
        from src.seating import SeatMap
        flight = Flight("LO3801", seat_map=SeatMap(10, 6))
        ticket = Ticket("Jan", 30, 100.0)
        booking = Booking(flight, ticket)
        
        booking.confirm_reservation("3B")
        
        assert booking.assigned_seat == "3B"
        assert "3B" in flight.seat_map.reserved_seats

    def test_confirm_reservation_automatic_assignment(self):
        """Test pozytywny: Brak wybranego miejsca skutkuje automatycznym przydziałem pierwszego wolnego fotelu."""
        from src.seating import SeatMap
        flight = Flight("LO3801", seat_map=SeatMap(5, 4))
        ticket = Ticket("Anna", 25, 100.0)
        booking = Booking(flight, ticket)
        
        booking.confirm_reservation() # Wywołanie bez podawania preferencji
        
        assert booking.assigned_seat == "1A" # Pierwsze wolne od przodu samolotu
        assert "1A" in flight.seat_map.reserved_seats

    def test_confirm_reservation_seat_already_taken(self):
        """Test negatywny: Próba rezerwacji zajętego już fotela kończy się błędem."""
        from src.seating import SeatMap
        flight = Flight("LO3801", seat_map=SeatMap(5, 4))
        ticket1 = Ticket("Jan", 30, 100.0)
        ticket2 = Ticket("Anna", 25, 100.0)
        
        booking1 = Booking(flight, ticket1)
        booking2 = Booking(flight, ticket2)
        
        booking1.confirm_reservation("2C")
        
        with pytest.raises(RuntimeError):
            booking2.confirm_reservation("2C") # Fotel 2C jest już zajęty przez Jana!

    def test_cancellation_frees_assigned_seat(self):
        """Test sprawdzający, czy anulowanie rezerwacji zwalnia dokładnie to przypisane miejsce na mapie."""
        from src.seating import SeatMap
        flight = Flight("LO3801", seat_map=SeatMap(5, 4))
        ticket = Ticket("Marek", 40, 100.0)
        booking = Booking(flight, ticket)
        
        booking.confirm_reservation("4D")
        assert "4D" in flight.seat_map.reserved_seats
        
        booking.change_status("CANCELLED")
        assert "4D" not in flight.seat_map.reserved_seats
        assert flight.reserved_seats == 0