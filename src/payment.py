class PaymentGateway:
    """Zewnętrzna bramka płatnicza (symulacja interfejsu do banku)."""

    def charge_card(self, card_number, amount):
        print(f"Pobieranie {amount} PLN z karty {card_number}")
        return False


class EmailService:
    """Zewnętrzny serwis odpowiedzialny za wysyłanie powiadomień e-mail."""

    def send_confirmation(self, email, flight_number):
        print(f"Wysylanie wiadomosci o locie {flight_number} na email {email}")
        return False


class PaymentProcessor:
    """Procesor operacji finansowych integrujący rezerwację, zniżki i bramkę płatniczą."""

    def __init__(self, gateway, email_service):
        self.gateway = gateway
        self.email_service = email_service
        self.promo_codes = {"PROMO10": 0.10, "SUPER20": 0.20}

    def process_booking_payment(self, booking, card_number, promo_code=None, loyalty_account=None):
        """
        Procesuje płatność za rezerwację.
        Uwzględnia zniżki z programu lojalnościowego oraz kody rabatowe.
        """
        if booking.status != "RESERVED":
            raise RuntimeError("Można opłacić tylko rezerwację w stanie RESERVED.")

        amount = booking.ticket.calculate_price()

        # Aplikowanie zniżki z kodu promocyjnego
        if promo_code:
            if promo_code in self.promo_codes:
                discount = amount * self.promo_codes[promo_code]
                amount = amount - discount
            else:
                raise ValueError("Niepoprawny kod promocyjny.")

        # Aplikowanie zniżki z programu lojalnościowego (jeśli pasażer użył karty)
        if loyalty_account:
            amount = amount * loyalty_account.get_discount_multiplier()

        # Zaokrąglenie do 2 miejsc po przecinku (grosze)
        amount = round(amount, 2)

        # Finalizacja płatności
        payment_success = self.gateway.charge_card(card_number, amount)
        if not payment_success:
            raise PermissionError("Płatność odrzucona przez bank.")

        booking.change_status("PAID")
        email_sent = self.email_service.send_confirmation(
            booking.ticket.passenger_name,
            booking.flight.flight_number
        )
        return email_sent
