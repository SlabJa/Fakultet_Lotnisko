import unittest
from src.validators import validate_email, validate_phone, validate_pnr, validate_card_luhn


class TestValidatorsUnittest(unittest.TestCase):

    def setUp(self):
        pass

    # --- TESTY DLA E-MAIL ---
    def test_validate_email_correct(self):
        """Testy pozytywne dla poprawnych i zróżnicowanych formatów adresów e-mail."""
        self.assertTrue(validate_email("user@example.com"))
        self.assertTrue(validate_email("passenger.name+tag@airline.pl"))

    def test_validate_email_incorrect_format(self):
        """Testy negatywne dla błędnych adresów e-mail."""
        self.assertFalse(validate_email("plainaddress"))
        self.assertFalse(validate_email("@missing-username.com"))
        self.assertFalse(validate_email("user@example."))

    def test_validate_email_wrong_type(self):
        """Test negatywny sprawdzający odporność na błędny typ danych (e-mail)."""
        with self.assertRaises(TypeError):
            validate_email(12345)

    # --- TESTY DLA TELEFONU (MIĘDZYNARODOWE) ---
    def test_validate_phone_correct(self):
        """Testy pozytywne dla poprawnych, międzynarodowych formatów telefonów."""
        self.assertTrue(validate_phone("123456789"))            # PL bez kierunkowego
        self.assertTrue(validate_phone("+48 123 456 789"))      # PL z kierunkowym i spacjami
        self.assertTrue(validate_phone("+1-800-555-0199"))      # US z myślnikami
        self.assertTrue(validate_phone("+44 (20) 7946 0958"))   # UK z nawiasami
        self.assertTrue(validate_phone("+81345678901"))         # JP ciągiem

    def test_validate_phone_incorrect_format(self):
        """Testy negatywne dla telefonów o niepoprawnej długości lub ze złymi znakami."""
        self.assertFalse(validate_phone("123456"))              # Za krótki (<7 cyfr)
        self.assertFalse(validate_phone("+1234567890123456"))   # Za długi (>15 cyfr)
        self.assertFalse(validate_phone("123a45678"))           # Zawiera literę
        self.assertFalse(validate_phone("++48123456789"))       # Podwójny plus na początku

    def test_validate_phone_wrong_type(self):
        """Test negatywny sprawdzający rzucanie TypeError dla telefonu."""
        with self.assertRaises(TypeError):
            validate_phone(None)

    # --- TESTY DLA PNR ---
    def test_validate_pnr_correct(self):
        """Testy pozytywne dla poprawnych, 6-znakowych kodów PNR."""
        self.assertTrue(validate_pnr("WAW123"))
        self.assertTrue(validate_pnr("9X8Y7Z"))

    def test_validate_pnr_incorrect(self):
        """Testy negatywne dla błędnych kodów PNR (nieprawidłowe znaki lub długość)."""
        self.assertFalse(validate_pnr("waw123"))    # Małe litery
        self.assertFalse(validate_pnr("WAW12"))     # Za krótki
        self.assertFalse(validate_pnr("WAW1234"))   # Za długi

    def test_validate_pnr_wrong_type(self):
        """Test negatywny sprawdzający rzucanie TypeError dla kodu PNR."""
        with self.assertRaises(TypeError):
            validate_pnr(123456)

    # --- TESTY DLA ALGORYTMU LUHNA (KARTY PŁATNICZE) ---
    def test_luhn_correct_cards(self):
        """Testy pozytywne dla prawidłowych numerów kart (zgodnych z algorytmem Luhna)."""
        self.assertTrue(validate_card_luhn("4111-1111-1111-1111"))  # Prawdziwa testowa Visa
        self.assertTrue(validate_card_luhn("5111111111111118"))     # Prawdziwy testowy MasterCard

    def test_luhn_incorrect_cards(self):
        """Testy negatywne dla błędnych numerów kart (zła cyfra kontrolna lub długość)."""
        self.assertFalse(validate_card_luhn("49927398717"))     # Zła cyfra kontrolna
        self.assertFalse(validate_card_luhn("1234"))            # Za krótka
        self.assertFalse(validate_card_luhn("not-a-number-strings"))

    def test_luhn_wrong_type(self):
        """Test negatywny sprawdzający rzucanie TypeError przy walidacji karty."""
        with self.assertRaises(TypeError):
            validate_card_luhn(["49927398716"])

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
