import pytest
from app.database import reset_db
from app.seed_data import seed_sample_data
from app.data_product_service import get_all_data_products, get_data_products_count, create_data_product
from app.models import DataProductCreate


@pytest.fixture()
def new_db():
    """Create a fresh database for each test."""
    reset_db()
    yield
    reset_db()


def test_seed_sample_data_on_empty_db(new_db):
    """Test that sample data is created when database is empty."""
    # Initially empty
    assert get_data_products_count() == 0

    # Seed data
    seed_sample_data()

    # Should have sample data
    count = get_data_products_count()
    assert count > 0

    # Verify specific sample schemas exist
    products = get_all_data_products()
    schema_names = {p.schema_name for p in products}

    expected_schemas = {
        "customer_analytics",
        "sales_performance",
        "marketing_campaigns",
        "product_usage",
        "financial_reporting",
        "operational_metrics",
    }

    assert expected_schemas.issubset(schema_names)


def test_seed_sample_data_skips_when_data_exists(new_db):
    """Test that seeding is skipped when data already exists."""
    # Create one data product
    create_data_product(DataProductCreate(schema_name="existing_schema", owner="existing@company.com"))

    initial_count = get_data_products_count()
    assert initial_count == 1

    # Try to seed
    seed_sample_data()

    # Count should remain unchanged
    final_count = get_data_products_count()
    assert final_count == initial_count


def test_sample_data_properties(new_db):
    """Test that sample data has expected properties."""
    seed_sample_data()

    products = get_all_data_products()
    assert len(products) > 0

    for product in products:
        # All products should have required fields
        assert product.schema_name is not None
        assert len(product.schema_name) > 0
        assert product.owner is not None
        assert len(product.owner) > 0
        assert product.creation_date is not None
        assert product.created_at is not None
        assert product.updated_at is not None

        # Owners should be email format (basic check)
        assert "@" in product.owner
        assert product.owner.endswith(".com")


def test_sample_data_uniqueness(new_db):
    """Test that sample data creates unique schema names."""
    seed_sample_data()

    products = get_all_data_products()
    schema_names = [p.schema_name for p in products]

    # All schema names should be unique
    assert len(schema_names) == len(set(schema_names))


def test_sample_data_ordering(new_db):
    """Test that sample data is created with varied creation dates."""
    seed_sample_data()

    products = get_all_data_products()
    creation_dates = [p.creation_date for p in products]

    # Should have multiple different dates (not all the same)
    unique_dates = set(date.date() for date in creation_dates)
    assert len(unique_dates) > 1  # Should span multiple days
