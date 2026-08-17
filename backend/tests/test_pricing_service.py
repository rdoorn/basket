"""Unit tests for the pricing port, mock adapter and pricing service."""
from app.domain.shopping import ShoppingListItem
from app.adapters.pricing.mock_provider import MockPricingProvider
from app.services.pricing_service import quote_all


def test_quote_all_returns_totals_per_store():
    items = [ShoppingListItem(name="macaroni", quantity=350, unit="g", source="supermarket")]
    quotes = quote_all(items, [MockPricingProvider("Albert Heijn"), MockPricingProvider("Picnic")])
    assert {q.store for q in quotes} == {"Albert Heijn", "Picnic"}
    for q in quotes:
        assert q.total == sum(i.line_total for i in q.items)


def test_mock_provider_is_deterministic():
    items = [ShoppingListItem(name="macaroni", quantity=350, unit="g")]
    a = MockPricingProvider("Albert Heijn").quote(items)
    b = MockPricingProvider("Albert Heijn").quote(items)
    assert a.items[0].unit_price == b.items[0].unit_price
    assert a.total == b.total


def test_mock_provider_differs_per_store_and_ingredient():
    items = [ShoppingListItem(name="macaroni", quantity=1, unit="g")]
    ah = MockPricingProvider("Albert Heijn").quote(items).items[0].unit_price
    pc = MockPricingProvider("Picnic").quote(items).items[0].unit_price
    assert ah != pc
    other = MockPricingProvider("Albert Heijn").quote(
        [ShoppingListItem(name="gehakt", quantity=1, unit="g")]
    ).items[0].unit_price
    assert ah != other


def test_line_total_uses_quantity_and_none_defaults_to_one():
    quote = MockPricingProvider("Albert Heijn").quote(
        [ShoppingListItem(name="zout", quantity=None, unit=None)]
    )
    item = quote.items[0]
    assert item.line_total == item.unit_price  # quantity None -> factor 1


def test_external_source_items_excluded_from_quotes():
    items = [
        ShoppingListItem(name="macaroni", quantity=350, unit="g", source="supermarket"),
        ShoppingListItem(name="gehakt", quantity=300, unit="g", source="external"),
    ]
    quotes = quote_all(items, [MockPricingProvider("Albert Heijn")])
    names = {i.name for i in quotes[0].items}
    assert names == {"macaroni"}


def test_quote_all_empty_providers_returns_empty():
    items = [ShoppingListItem(name="macaroni", quantity=1, unit="g")]
    assert quote_all(items, []) == []
