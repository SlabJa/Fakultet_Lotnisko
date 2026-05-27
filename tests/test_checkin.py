from unittest.mock import Mock
import pytest
from src.checkin import SecurityScanner, CheckInDesk, BoardingGate
from src.booking import Ticket, Booking, Flight


class TestSecurityScanner:
    """Zestaw testów weryfikujących działanie skanera bezpieczeństwa na lotnisku."""

    @pytest.fixture
    def scanner(self):
        """Fixture dostarczający zainicjalizowany skaner bezpieczeństwa."""
        return SecurityScanner()

    @pytest.mark.parametrize("baggage", [
        [],
        ["Książka", "Laptop", "Ubrania"],
        ["Zabawka", "Klucze"]
    ])
    def test_scan_baggage_safe(self, scanner, baggage):
        """Testy pozytywne sprawdzające akceptację dozwolonego bagażu (w tym pustego)."""
        assert scanner.scan_baggage(baggage) is True

    @pytest.mark.parametrize("dangerous_baggage", [
        ["Książka", "Bron"],
        ["NARKOTYKI"],
        ["Ubrania", "Duza_butelka", "Laptop"],
        ["zapalniczka"]
    ])
    def test_scan_baggage_forbidden(self, scanner, dangerous_baggage):
        """Testy negatywne wykrywające przedmioty zakazane (z ignorowaniem wielkości liter)."""
        assert scanner.scan_baggage(dangerous_baggage) is False

    @pytest.mark.parametrize("invalid_type, expected_error", [
        ("String zamiast listy", TypeError),
        (123, TypeError),
        (None, TypeError),
        (["Książka", 123], TypeError)
    ])
    def test_scan_baggage_types(self, scanner, invalid_type, expected_error):
        """Testy weryfikujące rzucanie odpowiednich wyjątków przy błędnych strukturach danych."""
        with pytest.raises(expected_error):
            scanner.scan_baggage(invalid_type)


class TestCheckInDesk:
    """Zestaw testów dla stanowiska odprawy z wykorzystaniem atrap (Mock) skanera."""

    @pytest.fixture
    def checkin_env(self):
        """Fixture konfigurujący stanowisko odprawy oraz poprawnie opłaconą rezerwację."""
        mock_scanner = Mock(spec=SecurityScanner)
        desk = CheckInDesk(mock_scanner)

        flight = Flight("LO3801", total_seats=10)
        ticket = Ticket("Jan Kowalski", 30, 200.0)
        booking = Booking(flight, ticket)

        booking.confirm_reservation()
        booking.change_status("PAID")

        return desk, mock_scanner, booking

    def test_issue_boarding_pass_success(self, checkin_env):
        """Test pozytywny wystawienia karty pokładowej po udanej weryfikacji i skanowaniu."""
        desk, mock_scanner, booking = checkin_env
        mock_scanner.scan_baggage.return_value = True

        b_pass = desk.issue_boarding_pass(booking, "AB1234567", ["Laptop"])

        assert b_pass.startswith("PASS:")
        assert booking.pnr in b_pass
        assert "Jan Kowalski" in b_pass
        mock_scanner.scan_baggage.assert_called_once_with(["Laptop"])

    @pytest.mark.parametrize("invalid_passport", [
        "A1234567",
        "ABC123456",
        "ab1234567",
        "AB123456",
        "AB12345678",
    ])
    def test_invalid_passport_format(self, checkin_env, invalid_passport):
        """Testy negatywne sprawdzające walidację formatu numeru paszportu."""
        desk, _, booking = checkin_env
        with pytest.raises(ValueError):
            desk.issue_boarding_pass(booking, invalid_passport, [])

    def test_invalid_passport_type(self, checkin_env):
        """Test negatywny weryfikujący odporność na błędny typ danych paszportu."""
        desk, _, booking = checkin_env
        with pytest.raises(TypeError):
            desk.issue_boarding_pass(booking, 1234567, [])

    def test_security_rejection(self, checkin_env):
        """Test sprawdzający zablokowanie odprawy w przypadku odrzucenia bagażu przez skaner."""
        desk, mock_scanner, booking = checkin_env
        mock_scanner.scan_baggage.return_value = False

        with pytest.raises(PermissionError):
            desk.issue_boarding_pass(booking, "AB1234567", ["Narkotyki"])

    @pytest.mark.parametrize("wrong_status", ["DRAFT", "RESERVED", "CANCELLED"])
    def test_wrong_booking_status(self, checkin_env, wrong_status):
        """Testy negatywne weryfikujące zablokowanie odprawy dla nieopłaconych biletów."""
        desk, _, booking = checkin_env

        if wrong_status == "DRAFT":
            booking = Booking(Flight("LO", 1), Ticket("A", 1, 1))
        elif wrong_status == "RESERVED":
            booking = Booking(Flight("LO", 1), Ticket("A", 1, 1))
            booking.confirm_reservation()
        else:
            booking.change_status("CANCELLED")

        with pytest.raises(ValueError):
            desk.issue_boarding_pass(booking, "AB1234567", [])


class TestBoardingGate:
    """Zestaw testów autoryzacji wejścia na pokład przy samej bramce lotu."""

    @pytest.fixture
    def gate(self):
        """Fixture dostarczający czystą bramkę dla konkretnego lotu."""
        return BoardingGate("LO3801")

    def test_board_passenger_success(self, gate):
        """Test pozytywny udanego wejścia na pokład z prawidłową kartą pokładową."""
        assert gate.board_passenger("PASS:XYZ123:LO3801:Jan") is True
        assert "XYZ123" in gate.boarded_passengers

    def test_double_boarding(self, gate):
        """Test bezpieczeństwa blokujący próbę dwukrotnego użycia tej samej karty pokładowej."""
        gate.board_passenger("PASS:XYZ123:LO3801:Jan")
        with pytest.raises(RuntimeError):
            gate.board_passenger("PASS:XYZ123:LO3801:Jan")

    def test_wrong_flight(self, gate):
        """Test weryfikujący zablokowanie pasażera próbującego wejść do złego samolotu."""
        with pytest.raises(ValueError, match="Pasażer próbuje wejść na niewłaściwy lot"):
            gate.board_passenger("PASS:XYZ123:LH1234:Jan")

    @pytest.mark.parametrize("invalid_pass, expected_error", [
        ("TICKET:XYZ123:LO3801:Jan", ValueError),
        ("PASS:XYZ123:LO3801", ValueError),
        (12345, TypeError),
    ])
    def test_invalid_boarding_pass(self, gate, invalid_pass, expected_error):
        """Testy negatywne dla uszkodzonych lub sfabrykowanych kart pokładowych."""
        with pytest.raises(expected_error):
            gate.board_passenger(invalid_pass)
