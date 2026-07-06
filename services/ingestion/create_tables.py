"""Crée les tables en base à partir des modèles SQLAlchemy.
Usage : python create_tables.py
"""
from ingestion.adapters.db import Base, engine

def main() -> None:
    Base.metadata.create_all(engine)
    print("Tables créées.")

if __name__ == "__main__":
    main()