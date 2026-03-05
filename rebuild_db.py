from main.database.models import db
from main.database.base_class import Base
from main.app import app

# Initialize db — create tables for SQLAlchemy ORM models (e.g. Config via Base)
with app.app_context():
    # Drop and recreate all tables from the custom Base metadata
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    # Also handle any db.Model mapped tables
    db.drop_all()
    db.configure_mappers()
    db.create_all()

    # Seeds
    from main.database.models.build_db import (
        seed_site_settings,
        seed_data_candidates
    )
    excel_file_path = f'{app.root_path}/data/MyCandidate Seed Doc.xlsx'

    seed_site_settings(db, excel_file_path)
    seed_data_candidates(db, excel_file_path)
