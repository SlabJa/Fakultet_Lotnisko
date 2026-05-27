import re


class SecurityScanner:
    """System kontroli bezpieczeństwa weryfikujący zawartość bagażu pasażerów."""

    def __init__(self):
        self.forbidden_items = {"BRON", "NARKOTYKI", "MATERIALY_WYBUCHOWE", "OSTRZE", "ZAPALNICZKA", "DUZA_BUTELKA"}

    def scan_baggage(self, items_list):
        """Analizuje listę przedmiotów w bagażu pod kątem obecności materiałów zakazanych."""
        if not isinstance(items_list, list):
            raise TypeError("Bagaż musi być przekazany jako struktura listy (list).")

        for item in items_list:
            if not isinstance(item, str):
                raise TypeError("Każdy przedmiot w bagażu musi być typu tekstowego (str).")

            if item.upper() in self.forbidden_items:
                return False
        return True


class CheckInDesk:
    """Stanowisko odprawy biletowo-bagażowej weryfikujące dokumenty i wydające karty pokładowe."""

    def __init__(self, scanner):
        self.scanner = scanner

    def issue_boarding_pass(self, booking, passport_number, baggage_items):
        """Weryfikuje rezerwację, paszport i bagaż, a następnie generuje cyfrową kartę pokładową."""
        if booking.status != "PAID":
            raise ValueError("Do odprawy wymagany jest opłacony bilet (status PAID).")

        if not isinstance(passport_number, str):
            raise TypeError("Numer paszportu musi być typu tekstowego (str).")

        if not re.match(r"^[A-Z]{2}\d{7}$", passport_number):
            raise ValueError("Niepoprawny format numeru paszportu.")

        if not self.scanner.scan_baggage(baggage_items):
            raise PermissionError("Bagaż zatrzymany przez kontrolę bezpieczeństwa.")

        return f"PASS:{booking.pnr}:{booking.flight.flight_number}:{booking.ticket.passenger_name}"


class BoardingGate:
    """Bramka wejścia na pokład weryfikująca karty pokładowe i zarządzająca przepływem pasażerów."""

    def __init__(self, flight_number):
        self.flight_number = flight_number
        self.boarded_passengers = set()

    def board_passenger(self, boarding_pass):
        """Skanuje kartę pokładową i autoryzuje wejście pasażera na pokład samolotu."""
        if not isinstance(boarding_pass, str):
            raise TypeError("Karta pokładowa musi być ciągiem znaków (str).")

        if not boarding_pass.startswith("PASS:"):
            raise ValueError("Nieprawidłowy format karty pokładowej.")

        parts = boarding_pass.split(":")
        if len(parts) != 4:
            raise ValueError("Uszkodzona lub niekompletna karta pokładowa.")

        pnr = parts[1]
        flight_num = parts[2]

        if flight_num != self.flight_number:
            raise ValueError("Pasażer próbuje wejść na niewłaściwy lot.")

        if pnr in self.boarded_passengers:
            raise RuntimeError("Pasażer z tym kodem PNR jest już na pokładzie.")

        self.boarded_passengers.add(pnr)
        return True
