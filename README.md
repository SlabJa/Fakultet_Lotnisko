# Airline Booking & Check-In System

A comprehensive airline ticket booking and airport check-in management system implemented in Python with unit and BDD tests.

## Features

* Ticket booking and dynamic pricing (age, class, baggage)
* Loyalty program management (earning miles, tiers, and discounts)
* Flight seating management and automatic seat assignment
* Airport check-in, security baggage scanning, and boarding gate validation
* Data persistence (save to and load from JSON files, export to CSV)

## Project Structure

```text
project_root/
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

## Installation
Clone the repository
Ensure you have **Python 3.12** installed on your system.
Install dependencies (if necessary): pip install -r requirements.txt

## Running Tests
Run all tests with: pytest

For detailed output and BDD steps: pytest -v
To check branch coverage: pytest --cov=src --cov-branch