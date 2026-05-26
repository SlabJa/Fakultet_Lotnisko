class LoyaltyAccount:
    """Klasa reprezentująca konto lojalnościowe pasażera."""
    
    def __init__(self, account_id, owner_name):
        """Inicjalizuje konto lojalnościowe z unikalnym ID oraz danymi właściciela."""
        if not isinstance(account_id, str):
            raise TypeError("ID konta musi być ciągiem znaków (str).")
        if not isinstance(owner_name, str):
            raise TypeError("Nazwa właściciela musi być ciągiem znaków (str).")
            
        self.account_id = account_id
        self.owner_name = owner_name
        self.miles = 0
        self.tier = "BRONZE"

    def add_miles(self, miles):
        """Dodaje zgromadzone mile do konta i uruchamia aktualizację poziomu członkostwa."""
        if type(miles) is not int or miles < 0:
            raise ValueError("Dodawane mile muszą być nieujemną liczbą całkowitą.")
        
        self.miles += miles
        self._update_tier()

    def redeem_miles(self, miles):
        """Pobiera mile z konta w celu wymiany na nagrody po zweryfikowaniu salda."""
        if type(miles) is not int or miles < 0:
            raise ValueError("Odejmowane mile muszą być nieujemną liczbą całkowitą.")
        
        if self.miles < miles:
            raise ValueError("Niewystarczająca liczba mil na koncie.")
            
        self.miles -= miles
        self._update_tier()

    def _update_tier(self):
        """Wewnętrzny mechanizm maszyny stanów weryfikujący progi dla poziomów lojalnościowych."""
        if self.miles >= 50000:
            self.tier = "GOLD"
        elif self.miles >= 10000:
            self.tier = "SILVER"
        else:
            self.tier = "BRONZE"

    def get_discount_multiplier(self):
        """Zwraca mnożnik ceny biletu (zniżkę) przypisany do aktualnego poziomu konta."""
        if self.tier == "GOLD":
            return 0.9
        elif self.tier == "SILVER":
            return 0.95
        return 1.0