import pytest
from src.loyalty import LoyaltyAccount

class TestLoyaltyProgram:
    """Zestaw testów jednostkowych weryfikujących logikę biznesową programu lojalnościowego."""

    @pytest.fixture
    def account(self):
        """Fixture dostarczający czyste konto lojalnościowe przed każdym testem."""
        return LoyaltyAccount("FF-9988", "Anna Nowak")

    @pytest.mark.parametrize("miles_to_add, expected_tier", [
        (0, "BRONZE"),
        (9999, "BRONZE"),
        (10000, "SILVER"),
        (10001, "SILVER"),
        (49999, "SILVER"),
        (50000, "GOLD"),
        (50001, "GOLD"),
        (100000, "GOLD")
    ])
    def test_tier_upgrade_boundaries(self, account, miles_to_add, expected_tier):
        """Testy wartości brzegowych (BVA) sprawdzające automatyczny awans między poziomami."""
        account.add_miles(miles_to_add)
        assert account.tier == expected_tier
        assert account.miles == miles_to_add

    @pytest.mark.parametrize("invalid_miles", [
        -1, -500,
        10.5, 50.0,
        "100", None, []
    ])
    def test_add_miles_invalid_type_or_value(self, account, invalid_miles):
        """Testy negatywne sprawdzające reakcję na niepoprawne typy i wartości mil."""
        with pytest.raises(ValueError):
            account.add_miles(invalid_miles)

    def test_redeem_miles_success(self, account):
        """Test sprawdzający poprawność wydawania mil oraz ewentualny spadek statusu konta."""
        account.add_miles(20000)
        account.redeem_miles(15000)
        
        assert account.miles == 5000
        assert account.tier == "BRONZE"

    def test_redeem_miles_insufficient(self, account):
        """Test negatywny sprawdzający blokadę operacji przy braku wystarczającego salda mil."""
        account.add_miles(5000)
        with pytest.raises(ValueError, match="Niewystarczająca liczba mil"):
            account.redeem_miles(6000)

    @pytest.mark.parametrize("tier_miles, expected_multiplier", [
        (5000, 1.0),
        (15000, 0.95),
        (60000, 0.9)
    ])
    def test_get_discount_multiplier(self, account, tier_miles, expected_multiplier):
        """Test weryfikujący prawidłowość naliczania mnożników zniżek dla każdego poziomu."""
        account.add_miles(tier_miles)
        assert account.get_discount_multiplier() == expected_multiplier

    @pytest.mark.parametrize("bad_id, bad_name", [
        (123, "Anna"),
        ("FF123", None)
    ])
    def test_account_creation_errors(self, bad_id, bad_name):
        """Testy negatywne sprawdzające walidację typów danych podczas tworzenia konta."""
        with pytest.raises(TypeError):
            LoyaltyAccount(bad_id, bad_name)