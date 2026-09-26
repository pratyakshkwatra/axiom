import os
import sys

# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.services.ingestion import run_sync

def seed_data():
    print("Starting mock data seed...")
    db = SessionLocal()
    try:
        # We use a dummy organization id "org-1"
        stats = run_sync("org-1", db)
        print(f"Seed complete! Stats: {stats}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
