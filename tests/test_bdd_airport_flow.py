from pytest_bdd import scenarios, given, when, then, parsers
from src.checkin import SecurityScanner, CheckInDesk, BoardingGate
from src.booking import Ticket, Booking, Flight

scenarios('airport_flow.feature')


@given(parsers.parse('Passenger "{name}" has a "PAID" booking for flight "{flight}"'), target_fixture="airport_ctx")
def setup_airport_context(name, flight):
    flight_obj = Flight(flight, total_seats=150)
    ticket = Ticket(name, 30, 200.0)
    booking = Booking(flight_obj, ticket)
    booking.confirm_reservation()
    booking.change_status("PAID")

    scanner = SecurityScanner()
    desk = CheckInDesk(scanner)

    return {
        "booking": booking,
        "desk": desk,
        "desk_error": None,
        "boarding_pass": None,
        "gate_error": None
    }


@when(parsers.parse('Passenger presents passport "{passport}" at check-in'))
def present_passport(airport_ctx, passport):
    airport_ctx["passport"] = passport


@when(parsers.parse('Drops off a bag containing "{item}"'))
def drop_baggage(airport_ctx, item):
    try:
        b_pass = airport_ctx["desk"].issue_boarding_pass(
            airport_ctx["booking"],
            airport_ctx["passport"],
            [item]
        )
        airport_ctx["boarding_pass"] = b_pass
        airport_ctx["desk_error"] = "SUCCESS"
    except Exception as e:
        airport_ctx["desk_error"] = e.__class__.__name__


@then(parsers.parse('Check-in process resolves with "{desk_result}"'))
def verify_checkin_result(airport_ctx, desk_result):
    assert airport_ctx["desk_error"] == desk_result


@then(parsers.parse('If successful, passenger attempts to board gate "{gate_flight}"'))
def attempt_boarding(airport_ctx, gate_flight):
    if airport_ctx["desk_error"] != "SUCCESS":
        airport_ctx["gate_error"] = "SKIPPED"
        return

    gate = BoardingGate(gate_flight)
    try:
        gate.board_passenger(airport_ctx["boarding_pass"])
        airport_ctx["gate_error"] = "SUCCESS"
    except Exception as e:
        airport_ctx["gate_error"] = e.__class__.__name__


@then(parsers.parse('Boarding gate resolves with "{gate_result}"'))
def verify_gate_result(airport_ctx, gate_result):
    assert airport_ctx["gate_error"] == gate_result
