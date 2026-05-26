import pytest
from src.seating import SeatMap

class TestSeatMap:
    """Zestaw testów jednostkowych weryfikujących logikę zarządzania miejscami w samolocie."""
    
    @pytest.fixture
    def standard_plane(self):
        """Fixture konfigurujący standardowy układ miejsc (np. Boeing/Airbus, 3x3)."""
        return SeatMap(30, 6)
        
    @pytest.fixture
    def small_plane(self):
        """Fixture konfigurujący układ miejsc dla małego samolotu regionalnego (2x2)."""
        return SeatMap(10, 4)

    @pytest.mark.parametrize("rows, seats, expected_exception", [
        (0, 6, ValueError),
        (-5, 6, ValueError),
        (30, 0, ValueError),
        (30, 7, ValueError),
        ("30", 6, TypeError),
    ])
    def test_invalid_initialization(self, rows, seats, expected_exception):
        """Testy wartości brzegowych weryfikujące poprawność parametrów konstrukcyjnych."""
        with pytest.raises((ValueError, TypeError)):
            SeatMap(rows, seats)

    @pytest.mark.parametrize("seat, expected", [
        ("1A", True), ("30F", True), ("15C", True),
        ("0A", False), ("31A", False),
        ("15G", False), ("1Z", False),
        ("A15", False), ("15", False), ("A", False),
    ])
    def test_is_valid_seat(self, standard_plane, seat, expected):
        """Testy krzyżowe dla poprawnych i niepoprawnych koordynatów miejsc."""
        assert standard_plane.is_valid_seat(seat) == expected

    def test_is_valid_seat_type_error(self, standard_plane):
        """Test negatywny sprawdzający odporność na nieprawidłowy typ danych miejsca."""
        with pytest.raises(TypeError):
            standard_plane.is_valid_seat(15)

    def test_reserve_seat_success(self, standard_plane):
        """Test pozytywny sprawdzający możliwość poprawnej rezerwacji fotela."""
        standard_plane.reserve_seat("12B")
        assert "12B" in standard_plane.reserved_seats

    def test_reserve_seat_already_taken(self, standard_plane):
        """Test negatywny weryfikujący blokadę podwójnej rezerwacji tego samego miejsca."""
        standard_plane.reserve_seat("12B")
        with pytest.raises(RuntimeError):
            standard_plane.reserve_seat("12B")

    def test_reserve_invalid_seat(self, standard_plane):
        """Test negatywny blokujący próbę rezerwacji nieistniejącego fotela."""
        with pytest.raises(ValueError):
            standard_plane.reserve_seat("99Z")

    @pytest.mark.parametrize("seat, is_window", [
        ("1A", True), ("1F", True),
        ("1B", False), ("1C", False),
    ])
    def test_window_seat_standard_plane(self, standard_plane, seat, is_window):
        """Test logiczny wykrywający fotele przy oknie w standardowym kadłubie."""
        assert standard_plane.is_window_seat(seat) == is_window

    @pytest.mark.parametrize("seat, is_window", [
        ("1A", True), ("1D", True),
        ("1B", False), ("1C", False),
    ])
    def test_window_seat_small_plane(self, small_plane, seat, is_window):
        """Test logiczny wykrywający fotele przy oknie w małym samolocie (dynamiczna kalkulacja)."""
        assert small_plane.is_window_seat(seat) == is_window