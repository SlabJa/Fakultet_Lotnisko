from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock
from src.booking import Ticket, Booking, Flight
from src.payment import PaymentProcessor, PaymentGateway, EmailService
from src.loyalty import LoyaltyAccount

scenarios('reservation_flow.feature')

@given(parsers.parse('Passenger "{name}" is {age:d} years old'), target_fixture="ctx")
def setup_passenger(name, age):
    return {"name": name, "age": age}

@given(parsers.parse('Passenger\'s loyalty account balance is "{miles}"'))
def setup_loyalty(ctx, miles):
    if miles == "NONE":
        ctx["loyalty_account"] = None
    else:
        account = LoyaltyAccount(f"FF-{ctx['name']}", ctx["name"])
        account.add_miles(int(miles))
        ctx["loyalty_account"] = account

@when(parsers.parse('Passenger selects flight "{flight}" with base price {base_price:f} PLN'))
def select_flight(ctx, flight, base_price):
    ctx["flight_obj"] = Flight(flight, total_seats=180)
    ctx["base_price"] = base_price

@when(parsers.parse('Chooses "{travel_class}" class and {baggage:f} kg of baggage'))
def configure_ticket(ctx, travel_class, baggage):
    ticket = Ticket(
        passenger_name=ctx["name"],
        age=ctx["age"],
        base_price=ctx["base_price"],
        travel_class=travel_class,
        baggage_weight=baggage
    )
    ctx["booking"] = Booking(ctx["flight_obj"], ticket)

@when('Confirms the reservation')
def confirm_reservation(ctx):
    ctx["booking"].confirm_reservation()

@when(parsers.parse('Pays for the booking with card "{card}"'))
def pay_for_booking(ctx, card):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.charge_card.return_value = True
    mock_email = Mock(spec=EmailService)
    mock_email.send_confirmation.return_value = True
    
    processor = PaymentProcessor(mock_gateway, mock_email)
    processor.process_booking_payment(
        booking=ctx["booking"], 
        card_number=card, 
        loyalty_account=ctx["loyalty_account"]
    )
    
    ctx["mock_gateway"] = mock_gateway

@then(parsers.parse('The final charged amount should be {expected_price:f} PLN'))
def verify_amount(ctx, expected_price):
    # Wyciągamy kwotę z historii wywołań mocka banku (args[1] to amount)
    charge_call = ctx["mock_gateway"].charge_card.call_args
    charged_amount = charge_call[0][1]
    assert charged_amount == expected_price

@then(parsers.parse('Booking status changes to "{expected_status}"'))
def verify_status(ctx, expected_status):
    assert ctx["booking"].status == expected_status