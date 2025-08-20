from app.database import create_tables
from app.seed_data import seed_sample_data
import app.data_products


def startup() -> None:
    # this function is called before the first request
    create_tables()
    seed_sample_data()
    app.data_products.create()
