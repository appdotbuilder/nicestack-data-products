from datetime import datetime, timedelta
import logging
from app.data_product_service import create_data_product, get_data_products_count
from app.models import DataProductCreate


logger = logging.getLogger(__name__)


def seed_sample_data():
    """Seed the database with sample data products if empty."""
    try:
        # Only seed if database is empty
        if get_data_products_count() > 0:
            logger.info("Database already contains data products, skipping seed")
            return

        sample_data = [
            {
                "schema_name": "customer_analytics",
                "description": "Customer behavior and segmentation analysis data",
                "owner": "analytics-team@company.com",
                "creation_date": datetime.utcnow() - timedelta(days=30),
            },
            {
                "schema_name": "sales_performance",
                "description": "Sales metrics, targets, and performance tracking",
                "owner": "sales-ops@company.com",
                "creation_date": datetime.utcnow() - timedelta(days=25),
            },
            {
                "schema_name": "marketing_campaigns",
                "description": "Campaign performance, attribution, and ROI analysis",
                "owner": "marketing-team@company.com",
                "creation_date": datetime.utcnow() - timedelta(days=20),
            },
            {
                "schema_name": "product_usage",
                "description": "Product feature usage, user engagement metrics",
                "owner": "product-team@company.com",
                "creation_date": datetime.utcnow() - timedelta(days=15),
            },
            {
                "schema_name": "financial_reporting",
                "description": "Revenue, costs, and financial KPI tracking",
                "owner": "finance-team@company.com",
                "creation_date": datetime.utcnow() - timedelta(days=10),
            },
            {
                "schema_name": "operational_metrics",
                "description": "System performance, uptime, and operational data",
                "owner": "devops-team@company.com",
                "creation_date": datetime.utcnow() - timedelta(days=5),
            },
        ]

        for data in sample_data:
            try:
                data_product_data = DataProductCreate(**data)
                create_data_product(data_product_data)
                logger.info(f"Created sample data product: {data['schema_name']}")
            except Exception as e:
                logger.error(f"Failed to create sample data product {data['schema_name']}: {e}")

        logger.info(f"Successfully seeded {len(sample_data)} sample data products")

    except Exception as e:
        logger.error(f"Error seeding sample data: {e}")
