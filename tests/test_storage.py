import unittest
from unittest.mock import patch, mock_open, Mock
from src.storage import BookingStorage


class TestBookingStorageIO(unittest.TestCase):
    """Zestaw testów jednostkowych weryfikujących operacje wejścia/wyjścia (I/O)."""

    def setUp(self):
        pass

    def test_save_to_json_success(self):
        """Test pozytywny sprawdzający poprawny zapis struktury słownikowej do pliku JSON."""
        storage = BookingStorage("test.json")
        dummy_data = {"pnr": "XYZ123", "status": "PAID"}

        with patch("builtins.open", mock_open()) as mocked_file:
            result = storage.save_to_json(dummy_data)
            self.assertTrue(result)
            mocked_file.assert_called_once_with("test.json", "w", encoding="utf-8")

    def test_save_to_json_io_error(self):
        """Test negatywny weryfikujący obsługę błędu podczas awarii zapisu na dysk."""
        storage = BookingStorage("test.json")
        with patch("builtins.open", side_effect=IOError("Brak miejsca na dysku")):
            with self.assertRaises(IOError):
                storage.save_to_json({"data": 1})

    def test_load_from_json_success(self):
        """Test pozytywny weryfikujący poprawny odczyt i parsowanie danych z pliku JSON."""
        storage = BookingStorage("test.json")
        valid_json = '{"pnr": "XYZ123", "status": "PAID"}'

        with patch("builtins.open", mock_open(read_data=valid_json)):
            result = storage.load_from_json()
            self.assertEqual(result, {"pnr": "XYZ123", "status": "PAID"})

    def test_load_from_json_file_not_found(self):
        """Test logiczny sprawdzający, czy brak pliku na dysku zwraca bezpieczny pusty słownik."""
        storage = BookingStorage("missing.json")
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = storage.load_from_json()
            self.assertEqual(result, {})

    def test_load_from_json_corrupted_format(self):
        """Test negatywny sprawdzający reakcję na uszkodzoną strukturę pliku JSON."""
        storage = BookingStorage("corrupted.json")
        with patch("builtins.open", mock_open(read_data="{invalid json}")):
            with self.assertRaises(ValueError):
                storage.load_from_json()

    def test_export_to_csv_success(self):
        """Test pozytywny weryfikujący poprawny eksport danych rezerwacji do pliku CSV."""
        storage = BookingStorage()

        # Atrapa rezerwacji
        mock_booking = Mock()
        mock_booking.pnr = "WAW123"
        mock_booking.flight.flight_number = "LO3801"
        mock_booking.ticket.passenger_name = "Anna Nowak"
        mock_booking.status = "PAID"

        with patch("builtins.open", mock_open()) as mocked_file:
            result = storage.export_to_csv("manifest.csv", [mock_booking])
            self.assertTrue(result)
            mocked_file.assert_called_once_with("manifest.csv", 'w', newline='', encoding='utf-8')

    def test_export_to_csv_empty_list_error(self):
        """Test negatywny blokujący próbę wygenerowania pustego manifestu (CSV)."""
        storage = BookingStorage()
        with self.assertRaises(ValueError):
            storage.export_to_csv("manifest.csv", [])

    def test_export_to_csv_io_error(self):
        """Test negatywny weryfikujący obsługę błędu wejścia/wyjścia podczas generowania CSV."""
        storage = BookingStorage()
        mock_booking = Mock()

        with patch("builtins.open", side_effect=IOError("Brak dostępu do dysku")):
            with self.assertRaises(IOError):
                storage.export_to_csv("manifest.csv", [mock_booking])

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
