import re


class SeatMap:
    """Klasa reprezentująca układ foteli i zarządzająca ich dostępnością w samolocie."""

    def __init__(self, rows, seats_per_row):
        """Inicjalizuje mapę miejsc na podstawie liczby rzędów i foteli w rzędzie."""
        if not isinstance(rows, int):
            raise TypeError("Liczba rzędów musi być liczbą całkowitą.")
        if rows <= 0:
            raise ValueError("Liczba rzędów musi być dodatnią liczbą całkowitą.")
        if not isinstance(seats_per_row, int) or not 1 <= seats_per_row <= 6:
            raise ValueError("Liczba miejsc w rzędzie musi być od 1 do 6 (A-F).")

        self.rows = rows
        self.seats_per_row = seats_per_row
        self.letters = "ABCDEF"[:seats_per_row]
        self.reserved_seats = set()

    def is_valid_seat(self, seat_number):
        """Weryfikuje poprawność formatu i istnienie danego miejsca na mapie samolotu."""
        if not isinstance(seat_number, str):
            raise TypeError("Numer miejsca musi być typu str.")

        match = re.match(r"^(\d+)([A-Z])$", seat_number)
        if not match:
            return False

        row, letter = int(match.group(1)), match.group(2)
        return 1 <= row <= self.rows and letter in self.letters

    def reserve_seat(self, seat_number):
        """Zajmuje wskazane miejsce, jeśli jest ono poprawne i dostępne do rezerwacji."""
        if not self.is_valid_seat(seat_number):
            raise ValueError(f"Niepoprawny numer miejsca: {seat_number}")

        if seat_number in self.reserved_seats:
            raise RuntimeError(f"Miejsce {seat_number} jest już zajęte.")

        self.reserved_seats.add(seat_number)

    def is_window_seat(self, seat_number):
        """Określa, czy podane miejsce znajduje się bezpośrednio przy oknie kadłuba."""
        if not self.is_valid_seat(seat_number):
            raise ValueError("Niepoprawny numer miejsca.")

        letter = seat_number[-1]
        return letter in ('A', self.letters[-1])
