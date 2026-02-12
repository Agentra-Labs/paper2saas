import os
import sys
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from paper2saas.utils import shared_db
from sqlalchemy import inspect, text


def analyze_db():
    print("Connecting to database...")
    # Check what kind of DB we have
    print(f"DB Type: {type(shared_db).__name__}")

    # Try to get engine
    engine = getattr(shared_db, "engine", None)
    if not engine:
        engine = getattr(shared_db, "db_engine", None)

    if not engine:
        print("Could not find engine or db_engine on shared_db object.")
        print(dir(shared_db))
        return

    inspector = inspect(engine)

    tables = inspector.get_table_names()
    print(f"Found {len(tables)} tables:")
    for table in tables:
        print(f" - {table}")

        # Optional: count rows
        try:
            with engine.connect() as conn:
                # Use text() for compatible SQL execution
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"   (Rows: {count})")
        except Exception as e:
            print(f"   (Could not count rows: {e})")


if __name__ == "__main__":
    analyze_db()
