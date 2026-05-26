import uuid
from src.seating import SeatMap

class Flight:
    """Klasa reprezentująca lot i zarządzająca dostępnością miejsc na podstawie mapy pokładu."""
    
    def __init__(self, flight_number, total_seats=180, seats_per_row=None, seat_map=None):
        """Inicjalizuje obiekt lotu z mapą miejsc (własną, automatyczną lub o określonej szerokości rzędu)."""
        if seat_map:
            self.seat_map = seat_map
            self.total_seats = seat_map.rows * seat_map.seats_per_row
        else:
            if total_seats <= 0:
                raise ValueError("Lot musi mieć co najmniej jedno miejsce.")
            
            # Jeśli szerokość rzędu nie została podana, dopasowujemy ją do rozmiaru samolotu
            if seats_per_row is None:
                seats_per_row = min(6, total_seats)
                
            if not (1 <= seats_per_row <= 6):
                raise ValueError("Liczba miejsc w rzędzie musi być od 1 do 6 (A-F).")
            
            # Wymaganą liczbę rzędów dla żądanej pojemności
            rows = max(1, (total_seats + seats_per_row - 1) // seats_per_row)
            self.seat_map = SeatMap(rows, seats_per_row)
            self.total_seats = rows * seats_per_row
            
        self.flight_number = flight_number

    @property
    def reserved_seats(self):
        """Dynamicznie zlicza zajęte fotele bezpośrednio z aktualnego stanu mapy miejsc."""
        return len(self.seat_map.reserved_seats)

    def has_available_seats(self):
        """Sprawdza, czy w samolocie są jeszcze wolne miejsca."""
        return self.reserved_seats < self.total_seats

    def reserve_seat(self, seat_number=None):
        """Blokuje konkretny fotel lub automatycznie przydziela pierwsze wolne miejsce od przodu."""
        if not self.has_available_seats():
            raise LookupError("Brak wolnych miejsc na ten lot.")
        
        if seat_number:
            self.seat_map.reserve_seat(seat_number)
            return seat_number
        else:
            # Szukanie pierwszego wolnego miejsca
            for r in range(1, self.seat_map.rows + 1):
                for l in self.seat_map.letters:
                    candidate = f"{r}{l}"
                    if candidate not in self.seat_map.reserved_seats:
                        self.seat_map.reserve_seat(candidate)
                        return candidate
            raise LookupError("Brak wolnych miejsc na ten lot.")

    def release_seat(self, seat_number):
        """Zwalnia wskazane miejsce na mapie pokładu samolotu."""
        if not seat_number:
            raise ValueError("Należy podać numer miejsca do zwolnienia.")
            
        if seat_number in self.seat_map.reserved_seats:
            self.seat_map.reserved_seats.remove(seat_number)
        else:
            raise ValueError(f"Miejsce {seat_number} nie jest aktualnie zajęte.")


class Ticket:
    """Klasa reprezentująca bilet pasażera z uwzględnieniem klas podróży oraz polityki bagażowej."""
    
    def __init__(self, passenger_name, age, base_price, travel_class="ECONOMY", baggage_weight=0.0):
        """Inicjalizuje bilet wraz z walidacją typów i wartości wejściowych."""
        if not isinstance(age, (int, float)):
            raise TypeError("Wiek musi być liczbą (int lub float).")
        if age < 0:
            raise ValueError("Wiek musi być liczbą nieujemną.")
            
        if not isinstance(base_price, (int, float)):
            raise TypeError("Cena bazowa musi być liczbą (int lub float).")
        if base_price < 0:
            raise ValueError("Cena bazowa musi być liczbą nieujemną.")
            
        if travel_class not in ["ECONOMY", "BUSINESS", "FIRST"]:
            raise ValueError("Niepoprawna klasa podróży.")
            
        if not isinstance(baggage_weight, (int, float)):
            raise TypeError("Waga bagażu musi być liczbą (int lub float).")
        if baggage_weight < 0:
            raise ValueError("Waga bagażu musi być liczbą nieujemną.")

        self.passenger_name = passenger_name
        self.age = age
        self.base_price = base_price
        self.travel_class = travel_class
        self.baggage_weight = baggage_weight

    def calculate_price(self):
        """Wylicza ostateczną cenę biletu uwzględniając zniżki wiekowe, klasę oraz nadbagaż."""
        if self.age < 2:
            ticket_price = 0.0
        elif self.age < 12:
            ticket_price = self.base_price * 0.5
        elif self.age >= 65:
            ticket_price = self.base_price * 0.7
        else:
            ticket_price = float(self.base_price)

        if self.travel_class == "BUSINESS":
            ticket_price += ticket_price * 0.50
        elif self.travel_class == "FIRST":
            ticket_price += ticket_price * 1.00

        baggage_fee = 0.0
        if self.travel_class == "ECONOMY" and self.baggage_weight > 20.0:
            overweight = self.baggage_weight - 20.0
            baggage_fee = overweight * 10.0

        return round(ticket_price + baggage_fee, 2)

    def has_free_meal(self):
        """Sprawdza, czy pasażerowi przysługuje darmowy catering na pokładzie (tylko klasa FIRST)."""
        return self.travel_class == "FIRST"


class Booking:
    """Klasa zarządzająca pełnym cyklem życia oraz maszyną stanów rezerwacji."""
    
    def __init__(self, flight, ticket):
        """Inicjalizuje proces rezerwacji w stanie DRAFT i generuje unikalny kod PNR."""
        self.flight = flight
        self.ticket = ticket
        self.status = "DRAFT"
        self.assigned_seat = None
        self.pnr = str(uuid.uuid4()).upper()[:6]

        self._allowed_transitions = {
            "DRAFT": ["RESERVED"],
            "RESERVED": ["PAID", "CANCELLED"],
            "PAID": ["CANCELLED"],
            "CANCELLED": []
        }

    def confirm_reservation(self, seat_number=None):
        """Zmienia status ze szkicu na rezerwację i przypisuje konkretny fotel pasażerowi."""
        if self.status != "DRAFT":
            raise RuntimeError("Można zarezerwować tylko szkic (DRAFT).")
        self.assigned_seat = self.flight.reserve_seat(seat_number)
        self.change_status("RESERVED")

    def change_status(self, new_status):
        """Dokonuje przejścia do nowego stanu po zweryfikowaniu reguł biznesowych."""
        if new_status not in self._allowed_transitions:
            raise ValueError(f"Nieznany stan: {new_status}")

        if new_status in self._allowed_transitions[self.status]:
            if new_status == "CANCELLED" and self.status in ["RESERVED", "PAID"]:
                self.flight.release_seat(self.assigned_seat)
            self.status = new_status
        else:
            raise RuntimeError(f"Niedozwolone przejście z {self.status} do {new_status}")