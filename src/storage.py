import json
import csv


class BookingStorage:
    """Klasa odpowiedzialna za operacje wejścia/wyjścia (I/O) dla systemu rezerwacji."""

    def __init__(self, filepath="bookings.json"):
        """Inicjalizuje menedżera pamięci masowej z domyślną ścieżką do bazy JSON."""
        self.filepath = filepath

    def save_to_json(self, booking_data):
        """Zapisuje strukturę słownikową z danymi rezerwacyjnymi do pliku JSON."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(booking_data, f, indent=4)
            return True
        except IOError as e:
            raise IOError(f"Błąd zapisu do pliku: {e}") from e

    def load_from_json(self):
        """Odczytuje i parsuje dane rezerwacyjne z pliku JSON. Zwraca pusty słownik przy braku pliku."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as exc:
            raise ValueError("Plik uszkodzony lub niepoprawny format JSON.") from exc

    def export_to_csv(self, csv_filepath, bookings_list):
        """Generuje manifest pasażerów w formacie CSV na potrzeby załogi lotniczej."""
        if not bookings_list:
            raise ValueError("Brak danych do eksportu.")

        try:
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["PNR", "Lot", "Pasazer", "Status"])

                for b in bookings_list:
                    writer.writerow([b.pnr, b.flight.flight_number, b.ticket.passenger_name, b.status])
            return True
        except IOError as exc:
            raise IOError("Nie udało się wyeksportować danych do pliku CSV.") from exc
