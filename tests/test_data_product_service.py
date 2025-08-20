import pytest
from datetime import datetime, timedelta
from app.database import reset_db
from app.data_product_service import (
    get_all_data_products,
    get_data_product_by_id,
    get_data_product_by_schema_name,
    create_data_product,
    update_data_product,
    delete_data_product,
    get_data_products_count,
)
from app.models import DataProductCreate, DataProductUpdate


@pytest.fixture()
def new_db():
    """Create a fresh database for each test."""
    reset_db()
    yield
    reset_db()


def test_get_all_data_products_empty(new_db):
    """Test retrieving all data products when database is empty."""
    products = get_all_data_products()
    assert products == []


def test_create_data_product_basic(new_db):
    """Test creating a basic data product."""
    data_product_data = DataProductCreate(
        schema_name="sales_analytics", description="Sales data analysis schema", owner="john.doe@company.com"
    )

    created_product = create_data_product(data_product_data)

    assert created_product.id is not None
    assert created_product.schema_name == "sales_analytics"
    assert created_product.description == "Sales data analysis schema"
    assert created_product.owner == "john.doe@company.com"
    assert created_product.creation_date is not None
    assert created_product.created_at is not None
    assert created_product.updated_at is not None


def test_create_data_product_minimal(new_db):
    """Test creating a data product with minimal required fields."""
    data_product_data = DataProductCreate(schema_name="minimal_schema", owner="owner@company.com")

    created_product = create_data_product(data_product_data)

    assert created_product.id is not None
    assert created_product.schema_name == "minimal_schema"
    assert created_product.description is None
    assert created_product.owner == "owner@company.com"


def test_create_data_product_with_custom_creation_date(new_db):
    """Test creating a data product with a specific creation date."""
    custom_date = datetime(2023, 6, 15, 10, 30, 0)
    data_product_data = DataProductCreate(
        schema_name="custom_date_schema", owner="owner@company.com", creation_date=custom_date
    )

    created_product = create_data_product(data_product_data)

    assert created_product.creation_date == custom_date


def test_create_data_product_duplicate_schema_name(new_db):
    """Test that creating a data product with duplicate schema name raises error."""
    data_product_data = DataProductCreate(schema_name="duplicate_schema", owner="owner@company.com")

    create_data_product(data_product_data)

    # Try to create another with same schema name
    duplicate_data = DataProductCreate(schema_name="duplicate_schema", owner="another@company.com")

    with pytest.raises(ValueError, match="already exists"):
        create_data_product(duplicate_data)


def test_get_all_data_products_ordering(new_db):
    """Test that data products are returned ordered by creation date descending."""
    # Create products with different creation dates
    old_date = datetime.now() - timedelta(days=2)
    recent_date = datetime.now() - timedelta(days=1)

    old_product = create_data_product(
        DataProductCreate(schema_name="old_schema", owner="owner@company.com", creation_date=old_date)
    )

    recent_product = create_data_product(
        DataProductCreate(schema_name="recent_schema", owner="owner@company.com", creation_date=recent_date)
    )

    products = get_all_data_products()

    assert len(products) == 2
    # Most recent first
    assert products[0].id == recent_product.id
    assert products[1].id == old_product.id


def test_get_data_product_by_id_exists(new_db):
    """Test retrieving a data product by ID when it exists."""
    created_product = create_data_product(DataProductCreate(schema_name="test_schema", owner="owner@company.com"))

    retrieved_product = get_data_product_by_id(created_product.id)

    assert retrieved_product is not None
    assert retrieved_product.id == created_product.id
    assert retrieved_product.schema_name == "test_schema"


def test_get_data_product_by_id_not_exists(new_db):
    """Test retrieving a data product by ID when it doesn't exist."""
    retrieved_product = get_data_product_by_id(999)
    assert retrieved_product is None


def test_get_data_product_by_id_none_input(new_db):
    """Test retrieving a data product with None ID."""
    retrieved_product = get_data_product_by_id(None)
    assert retrieved_product is None


def test_get_data_product_by_schema_name_exists(new_db):
    """Test retrieving a data product by schema name when it exists."""
    created_product = create_data_product(DataProductCreate(schema_name="unique_schema", owner="owner@company.com"))

    retrieved_product = get_data_product_by_schema_name("unique_schema")

    assert retrieved_product is not None
    assert retrieved_product.id == created_product.id
    assert retrieved_product.schema_name == "unique_schema"


def test_get_data_product_by_schema_name_not_exists(new_db):
    """Test retrieving a data product by schema name when it doesn't exist."""
    retrieved_product = get_data_product_by_schema_name("nonexistent_schema")
    assert retrieved_product is None


def test_get_data_product_by_schema_name_empty_input(new_db):
    """Test retrieving a data product with empty schema name."""
    retrieved_product = get_data_product_by_schema_name("")
    assert retrieved_product is None


def test_update_data_product_basic(new_db):
    """Test updating a data product with basic changes."""
    created_product = create_data_product(
        DataProductCreate(
            schema_name="original_schema", description="Original description", owner="original@company.com"
        )
    )

    updates = DataProductUpdate(
        schema_name="updated_schema", description="Updated description", owner="updated@company.com"
    )

    updated_product = update_data_product(created_product.id, updates)

    assert updated_product is not None
    assert updated_product.id == created_product.id
    assert updated_product.schema_name == "updated_schema"
    assert updated_product.description == "Updated description"
    assert updated_product.owner == "updated@company.com"
    assert updated_product.updated_at > created_product.updated_at


def test_update_data_product_partial(new_db):
    """Test updating only some fields of a data product."""
    created_product = create_data_product(
        DataProductCreate(
            schema_name="partial_schema", description="Original description", owner="original@company.com"
        )
    )

    updates = DataProductUpdate(description="Only description updated")

    updated_product = update_data_product(created_product.id, updates)

    assert updated_product is not None
    assert updated_product.schema_name == "partial_schema"  # Unchanged
    assert updated_product.description == "Only description updated"  # Changed
    assert updated_product.owner == "original@company.com"  # Unchanged


def test_update_data_product_not_exists(new_db):
    """Test updating a data product that doesn't exist."""
    updates = DataProductUpdate(description="New description")
    updated_product = update_data_product(999, updates)
    assert updated_product is None


def test_update_data_product_none_id(new_db):
    """Test updating a data product with None ID."""
    updates = DataProductUpdate(description="New description")
    updated_product = update_data_product(None, updates)
    assert updated_product is None


def test_update_data_product_duplicate_schema_name(new_db):
    """Test that updating to a duplicate schema name raises error."""
    # Create two products
    create_data_product(DataProductCreate(schema_name="schema_one", owner="owner@company.com"))

    product2 = create_data_product(DataProductCreate(schema_name="schema_two", owner="owner@company.com"))

    # Try to update product2 to use product1's schema name
    updates = DataProductUpdate(schema_name="schema_one")

    with pytest.raises(ValueError, match="already exists"):
        update_data_product(product2.id, updates)


def test_update_data_product_same_schema_name(new_db):
    """Test that updating a product to keep the same schema name works."""
    created_product = create_data_product(
        DataProductCreate(schema_name="same_schema", description="Original description", owner="owner@company.com")
    )

    updates = DataProductUpdate(
        schema_name="same_schema",  # Same name
        description="Updated description",
    )

    updated_product = update_data_product(created_product.id, updates)

    assert updated_product is not None
    assert updated_product.schema_name == "same_schema"
    assert updated_product.description == "Updated description"


def test_delete_data_product_exists(new_db):
    """Test deleting a data product that exists."""
    created_product = create_data_product(DataProductCreate(schema_name="to_be_deleted", owner="owner@company.com"))

    success = delete_data_product(created_product.id)
    assert success

    # Verify it's deleted
    retrieved_product = get_data_product_by_id(created_product.id)
    assert retrieved_product is None


def test_delete_data_product_not_exists(new_db):
    """Test deleting a data product that doesn't exist."""
    success = delete_data_product(999)
    assert not success


def test_delete_data_product_none_id(new_db):
    """Test deleting a data product with None ID."""
    success = delete_data_product(None)
    assert not success


def test_get_data_products_count(new_db):
    """Test getting the count of data products."""
    # Initially empty
    assert get_data_products_count() == 0

    # Add some products
    create_data_product(DataProductCreate(schema_name="schema_1", owner="owner@company.com"))

    create_data_product(DataProductCreate(schema_name="schema_2", owner="owner@company.com"))

    assert get_data_products_count() == 2


def test_full_crud_workflow(new_db):
    """Test complete CRUD workflow."""
    # Create
    data_product_data = DataProductCreate(
        schema_name="full_crud_test", description="Testing full CRUD", owner="test@company.com"
    )

    created_product = create_data_product(data_product_data)
    assert created_product.id is not None

    # Read
    retrieved_product = get_data_product_by_id(created_product.id)
    assert retrieved_product is not None
    assert retrieved_product.schema_name == "full_crud_test"

    # Update
    updates = DataProductUpdate(description="Updated in CRUD test", owner="updated@company.com")

    updated_product = update_data_product(created_product.id, updates)
    assert updated_product is not None
    assert updated_product.description == "Updated in CRUD test"
    assert updated_product.owner == "updated@company.com"

    # Delete
    success = delete_data_product(created_product.id)
    assert success

    # Verify deletion
    final_product = get_data_product_by_id(created_product.id)
    assert final_product is None
