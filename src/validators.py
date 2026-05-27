import re


def validate_email(email):
    """
    Waliduje format adresu e-mail za pomocą wyrażenia regularnego.
    Rzuca TypeError, jeśli przekazany argument nie jest ciągiem znaków.
    """
    if not isinstance(email, str):
        raise TypeError("Adres e-mail musi być typu str.")

    # Przykladowy regex pozwalajacy na litery i znaki w adresie
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if re.match(pattern, email):
        return True
    return False


def validate_phone(phone):
    """
    Waliduje międzynarodowy numer telefonu.
    Akceptuje opcjonalny znak '+' na początku oraz od 7 do 15 cyfr.
    Dozwolone są spacje, myślniki i nawiasy.
    """
    if not isinstance(phone, str):
        raise TypeError("Numer telefonu musi być typu str.")

    # Usuwanie dozwolonych znaków separujących
    cleaned_phone = re.sub(r"[\s\-\(\)]", "", phone)
    pattern = r"^\+?\d{7,15}$"

    if re.match(pattern, cleaned_phone):
        return True
    return False


def validate_pnr(pnr):
    """
    Waliduje kod rezerwacji (PNR).
    Musi mieć dokładnie 6 znaków, składać się tylko z wielkich liter i cyfr.
    """
    if not isinstance(pnr, str):
        raise TypeError("PNR musi być typu str.")
    pattern = r"^[A-Z0-9]{6}$"
    return bool(re.match(pattern, pnr))


def validate_card_luhn(card_number):
    """
    Waliduje numer karty płatniczej algorytmem Luhna.
    Działa poprawnie dla każdej długości karty (13-19 cyfr).
    """
    if not isinstance(card_number, str):
        raise TypeError("Numer karty musi być typu str.")

    # Usuwanie myślnikow i spacji
    cleaned = re.sub(r"[\s-]", "", card_number)

    if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
        return False

    # Odwracenie ciagu
    reversed_digits = cleaned[::-1]
    total_sum = 0

    for idx, digit_char in enumerate(reversed_digits):
        digit = int(digit_char)

        # Indeks 1 to druga cyfra od końca, indeks 3 to czwarta, itd.
        if idx % 2 == 1:
            digit = digit * 2
            if digit > 9:
                digit -= 9

        total_sum += digit

    return total_sum % 10 == 0
