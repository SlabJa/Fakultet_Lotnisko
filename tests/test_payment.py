import unittest
from unittest.mock import Mock
from src.booking import Ticket, Booking, Flight
from src.payment import PaymentProcessor, PaymentGateway, EmailService
from src.loyalty import LoyaltyAccount


class TestPaymentProcessorWithMocks(unittest.TestCase):
    """Zestaw testów dla procesora płatności z wykorzystaniem atrap (Mock) systemów zewnętrznych."""

    def setUp(self):
        """Przygotowuje środowisko przed każdym testem, inicjalizując atrapy i podstawową rezerwację."""
        self.mock_gateway = Mock(spec=PaymentGateway)
        self.mock_email = Mock(spec=EmailService)
        self.processor = PaymentProcessor(self.mock_gateway, self.mock_email)

        flight = Flight("LO3801", total_seats=10)
        ticket = Ticket("customer@test.com", 30, 200.0)
        self.booking = Booking(flight, ticket)
        self.booking.confirm_reservation()  # Wymagany stan do opłacenia: RESERVED

    def test_payment_success_flow(self):
        """Test pozytywny sprawdzający standardowy przepływ opłacenia biletu bez zniżek."""
        self.mock_gateway.charge_card.return_value = True
        self.mock_email.send_confirmation.return_value = True

        result = self.processor.process_booking_payment(self.booking, "1111-2222")

        self.assertTrue(result)
        self.assertEqual(self.booking.status, "PAID")
        self.mock_gateway.charge_card.assert_called_once_with("1111-2222", 200.0)

    def test_payment_with_valid_promo_codes(self):
        """Test sprawdzający poprawne obniżanie kwoty koszyka dla różnych kodów rabatowych."""
        self.mock_gateway.charge_card.return_value = True

        promo_scenarios = {
            "PROMO10": 180.0,
            "SUPER20": 160.0
        }

        for code, expected_amount in promo_scenarios.items():
            with self.subTest(promo_code=code):
                # Czystą rezerwacja dla każdej iteracji, aby uniknąć błędu stanu
                flight = Flight("LO3801", total_seats=10)
                ticket = Ticket("customer@test.com", 30, 200.0)
                fresh_booking = Booking(flight, ticket)
                fresh_booking.confirm_reservation()

                self.processor.process_booking_payment(fresh_booking, "1111-2222", promo_code=code)
                self.mock_gateway.charge_card.assert_called_with("1111-2222", expected_amount)

    def test_payment_with_invalid_promo_code(self):
        """Test negatywny weryfikujący zablokowanie transakcji przy użyciu nieistniejącego kodu."""
        with self.assertRaises(ValueError):
            self.processor.process_booking_payment(self.booking, "1111-2222", promo_code="FAKE_CODE")

        # Upewniamy się, że karta w ogóle nie została obciążona
        self.mock_gateway.charge_card.assert_not_called()

    def test_payment_rejected_by_bank(self):
        """Test negatywny sprawdzający obsługę odmowy autoryzacji ze strony bramki płatniczej."""
        self.mock_gateway.charge_card.return_value = False

        with self.assertRaises(PermissionError):
            self.processor.process_booking_payment(self.booking, "1111-2222")

        self.assertEqual(self.booking.status, "RESERVED")
        self.mock_email.send_confirmation.assert_not_called()

    def test_payment_with_loyalty_discount(self):
        """Test logiczny weryfikujący poprawną integrację zniżek z programu lojalnościowego."""
        self.mock_gateway.charge_card.return_value = True

        # Tworzymy konto ze statusem GOLD (10% zniżki)
        vip_account = LoyaltyAccount("FF-VIP", "customer@test.com")
        vip_account.add_miles(60000)

        self.processor.process_booking_payment(
            self.booking,
            "1111-2222",
            loyalty_account=vip_account
        )

        # 200 PLN bazowo - 10% zniżki = 180.0 PLN
        self.mock_gateway.charge_card.assert_called_with("1111-2222", 180.0)


if __name__ == "__main__":
    unittest.main()
