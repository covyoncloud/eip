import os
from sqlalchemy import create_engine, String, Integer, Float, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://eip:eip@localhost:5432/eip"
)
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class WorkORM(Base):
    __tablename__ = "works"
    work_id: Mapped[str] = mapped_column(String, primary_key=True)
    business_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    title_normalized: Mapped[str] = mapped_column(String)
    title_raw: Mapped[str] = mapped_column(String)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True)
    artists: Mapped[list] = mapped_column(JSON, default=list)
    first_release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)