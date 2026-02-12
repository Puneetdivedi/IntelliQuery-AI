import sys
print("Step 1: Script started")

try:
    from dotenv import load_dotenv
    print("Step 2: dotenv imported")
except ImportError:
    print("ERROR: dotenv not installed")

try:
    from sqlalchemy import create_engine
    print("Step 3: sqlalchemy imported")
except ImportError:
    print("ERROR: sqlalchemy not installed")

try:
    # Try importing project modules
    sys.path.insert(0, ".")
    from src.config.settings import Settings
    print("Step 4: Settings imported")
    Settings.validate()
    print("Step 5: Settings validated (Env vars OK)")
except Exception as e:
    print(f"ERROR in Settings: {e}")

try:
    from src.database.connection import test_connection
    print("Step 6: Connection module imported")
    if test_connection():
        print("Step 7: DB Connection SUCCESS")
    else:
        print("Step 7: DB Connection FAILED (Is PostgreSQL running?)")
except Exception as e:
    print(f"ERROR in Connection: {e}")

print("Diagnostic complete")
