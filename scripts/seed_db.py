"""Seed the database with initial activities data."""
import os
import sys
from pathlib import Path
from sqlmodel import Session, create_engine, select, SQLModel

# Ensure `src` is on path for imports when running this script directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from models import Activity


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data.db")
engine = create_engine(DATABASE_URL)


INITIAL_ACTIVITIES = [
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
    },
    {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
    },
    {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
    },
]


def seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for a in INITIAL_ACTIVITIES:
            exists = session.exec(
                select(Activity).where(Activity.name == a["name"])  # type: ignore
            ).first()
            if not exists:
                act = Activity(**a)
                session.add(act)
        session.commit()


if __name__ == "__main__":
    seed()
