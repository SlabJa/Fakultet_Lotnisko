# Airline Booking & Check-In System

A comprehensive airline ticket booking and airport check-in management system implemented in Python with unittest, pytest and BDD tests.

## Features

* Ticket booking and pricing (age, class, baggage)
* Loyalty program management (earning miles, tiers, and discounts)
* Flight seating management and automatic seat assignment
* Airport check-in, security baggage scanning, and boarding gate validation
* Data persistence (save to and load from JSON files, export to CSV)

## Project Structure

```text
project/
├── src/
│   ├── __init__.py
│   ├── booking.py
│   ├── checkin.py
│   ├── loyalty.py
│   ├── payment.py
│   ├── seating.py
│   ├── storage.py
│   └── validators.py
├── tests/
│   ├── __init__.py
│   ├── airport_flow.feature
│   ├── reservation_flow.feature
│   ├── test_bdd_airport_flow.py
│   ├── test_bdd_reservation_flow.py
│   ├── test_booking.py
│   ├── test_checkin.py
│   ├── test_loyalty.py
│   ├── test_payment.py
│   ├── test_seating.py
│   ├── test_storage.py
│   └── test_validators.py
├── requirements.txt
└── README.md
```

## Installation
1. Clone the repository
2. Ensure you have **Python 3.12** installed on your system.
3. Install dependencies (if necessary): pip install -r requirements.txt

## Running Tests
* Run all tests with:   pytest

* For detailed output and BDD steps:    pytest -v
* To generate html report:              pytest html
* To check branch coverage:             pytest --cov=src --cov-branch

## Additional code quality checks
* **Pylint** (Static analysis and code quality rating): pylint ./src ./tests
* **Vulture** (Dead code detection):                    vulture ./src
* **Flake8** (Style & PEP 8 enforcement):               flake8 ./src ./tests