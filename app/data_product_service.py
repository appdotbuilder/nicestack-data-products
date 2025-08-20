from typing import Optional
from datetime import datetime
from sqlmodel import select, desc
from app.database import get_session
from app.models import DataProduct, DataProductCreate, DataProductUpdate


def get_all_data_products() -> list[DataProduct]:
    """Retrieve all data products from the database, ordered by creation date descending."""
    with get_session() as session:
        statement = select(DataProduct).order_by(desc(DataProduct.creation_date))
        return list(session.exec(statement).all())


def get_data_product_by_id(data_product_id: Optional[int]) -> Optional[DataProduct]:
    """Retrieve a specific data product by ID."""
    if data_product_id is None:
        return None

    with get_session() as session:
        return session.get(DataProduct, data_product_id)


def get_data_product_by_schema_name(schema_name: str) -> Optional[DataProduct]:
    """Retrieve a data product by schema name."""
    if not schema_name:
        return None

    with get_session() as session:
        statement = select(DataProduct).where(DataProduct.schema_name == schema_name)
        return session.exec(statement).first()


def create_data_product(data_product_data: DataProductCreate) -> DataProduct:
    """Create a new data product."""
    with get_session() as session:
        # Check if schema name already exists
        existing = get_data_product_by_schema_name(data_product_data.schema_name)
        if existing is not None:
            raise ValueError(f"Data product with schema name '{data_product_data.schema_name}' already exists")

        db_data_product = DataProduct(
            schema_name=data_product_data.schema_name,
            description=data_product_data.description,
            owner=data_product_data.owner,
            creation_date=data_product_data.creation_date or datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(db_data_product)
        session.commit()
        session.refresh(db_data_product)
        return db_data_product


def update_data_product(data_product_id: Optional[int], updates: DataProductUpdate) -> Optional[DataProduct]:
    """Update an existing data product."""
    if data_product_id is None:
        return None

    with get_session() as session:
        db_data_product = session.get(DataProduct, data_product_id)
        if db_data_product is None:
            return None

        # Check schema name uniqueness if being updated
        if updates.schema_name is not None and updates.schema_name != db_data_product.schema_name:
            existing = get_data_product_by_schema_name(updates.schema_name)
            if existing is not None:
                raise ValueError(f"Data product with schema name '{updates.schema_name}' already exists")

        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_data_product, field, value)

        db_data_product.updated_at = datetime.utcnow()

        session.add(db_data_product)
        session.commit()
        session.refresh(db_data_product)
        return db_data_product


def delete_data_product(data_product_id: Optional[int]) -> bool:
    """Delete a data product by ID."""
    if data_product_id is None:
        return False

    with get_session() as session:
        db_data_product = session.get(DataProduct, data_product_id)
        if db_data_product is None:
            return False

        session.delete(db_data_product)
        session.commit()
        return True


def get_data_products_count() -> int:
    """Get the total count of data products."""
    with get_session() as session:
        statement = select(DataProduct)
        return len(list(session.exec(statement).all()))
