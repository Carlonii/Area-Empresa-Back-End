import os
import sys

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.database import engine
from sqlalchemy import text

def main():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS domain VARCHAR;"))
            conn.commit()
            print("Row 'domain' added or already exists.")
        except Exception as e:
            print("Error altering table:", e)

if __name__ == "__main__":
    main()
