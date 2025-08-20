import pytest
from datetime import datetime
from app.database import reset_db
from app.data_product_service import (
    create_data_product,
    search_data_products_by_schema_name,
)
from app.models import DataProductCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_search_data_products_case_insensitive(new_db):
    """Test that search is case-insensitive."""
    # Create test data
    create_data_product(
        DataProductCreate(
            schema_name="sales_analytics",
            description="Sales data analysis",
            owner="alice@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    create_data_product(
        DataProductCreate(
            schema_name="marketing_metrics",
            description="Marketing performance data",
            owner="bob@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    create_data_product(
        DataProductCreate(
            schema_name="SALES_reports",
            description="Weekly sales reports",
            owner="charlie@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    # Test case-insensitive search
    results = search_data_products_by_schema_name("sales")
    assert len(results) == 2
    schema_names = [dp.schema_name for dp in results]
    assert "sales_analytics" in schema_names
    assert "SALES_reports" in schema_names

    # Test uppercase search
    results = search_data_products_by_schema_name("SALES")
    assert len(results) == 2

    # Test mixed case search
    results = search_data_products_by_schema_name("SaLeS")
    assert len(results) == 2


def test_search_data_products_partial_match(new_db):
    """Test that search works with partial matches."""
    create_data_product(
        DataProductCreate(
            schema_name="customer_analytics_v2",
            description="Customer data analysis version 2",
            owner="alice@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    create_data_product(
        DataProductCreate(
            schema_name="product_analytics",
            description="Product performance data",
            owner="bob@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    # Test partial match
    results = search_data_products_by_schema_name("analytics")
    assert len(results) == 2

    # Test more specific partial match
    results = search_data_products_by_schema_name("customer")
    assert len(results) == 1
    assert results[0].schema_name == "customer_analytics_v2"


def test_search_data_products_empty_term(new_db):
    """Test that empty search term returns all products."""
    create_data_product(
        DataProductCreate(
            schema_name="test_schema_1",
            description="Test schema 1",
            owner="alice@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    create_data_product(
        DataProductCreate(
            schema_name="test_schema_2",
            description="Test schema 2",
            owner="bob@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    # Test empty string
    results = search_data_products_by_schema_name("")
    assert len(results) == 2

    # Test whitespace only
    results = search_data_products_by_schema_name("   ")
    assert len(results) == 2


def test_search_data_products_no_matches(new_db):
    """Test search with no matching results."""
    create_data_product(
        DataProductCreate(
            schema_name="sales_data",
            description="Sales information",
            owner="alice@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    # Search for non-existent term
    results = search_data_products_by_schema_name("marketing")
    assert len(results) == 0


def test_search_data_products_ordering(new_db):
    """Test that search results are ordered by creation date descending."""
    # Create products with different creation dates
    create_data_product(
        DataProductCreate(
            schema_name="analytics_old",
            description="Older analytics schema",
            owner="alice@company.com",
            creation_date=datetime(2023, 1, 1),
        )
    )

    create_data_product(
        DataProductCreate(
            schema_name="analytics_new",
            description="Newer analytics schema",
            owner="bob@company.com",
            creation_date=datetime(2024, 1, 1),
        )
    )

    results = search_data_products_by_schema_name("analytics")
    assert len(results) == 2
    # Should be ordered by creation_date descending (newest first)
    assert results[0].schema_name == "analytics_new"
    assert results[1].schema_name == "analytics_old"


def test_search_data_products_edge_cases(new_db):
    """Test search with various edge cases."""
    create_data_product(
        DataProductCreate(
            schema_name="test_with_underscore",
            description="Test with underscore",
            owner="alice@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    create_data_product(
        DataProductCreate(
            schema_name="test-with-dash",
            description="Test with dash",
            owner="bob@company.com",
            creation_date=datetime.utcnow(),
        )
    )

    # Test searching for underscore
    results = search_data_products_by_schema_name("underscore")
    assert len(results) == 1
    assert results[0].schema_name == "test_with_underscore"

    # Test searching for dash
    results = search_data_products_by_schema_name("dash")
    assert len(results) == 1
    assert results[0].schema_name == "test-with-dash"

    # Test searching for partial with special characters
    results = search_data_products_by_schema_name("test")
    assert len(results) == 2
