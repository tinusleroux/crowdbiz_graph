import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path to allow for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def diagnose_summary_tables():
    """
    Connects to the database and checks if the summary tables contain data.
    """
    print("--- Running Data Diagnostic Script ---")
    
    # Load environment variables from .env file in the project root
    dotenv_path = os.path.join(project_root, '.env')
    if not os.path.exists(dotenv_path):
        print("❌ Error: .env file not found in the project root.")
        print("Please create it by copying .env.example and filling in your Supabase credentials.")
        return
        
    load_dotenv(dotenv_path=dotenv_path)

    # This import needs the sys.path modification above
    from app.core.database import get_database_manager

    try:
        db = get_database_manager()
        print("✅ Successfully connected to the database.")
    except Exception as e:
        print(f"❌ Failed to connect to the database: {e}")
        print("Please ensure your .env file is configured correctly with SUPABASE_URL and SUPABASE_API_KEY.")
        return

    tables_to_check = ["network_status", "organization_summary"]
    all_tables_ok = True

    for table_name in tables_to_check:
        print(f"\n--- Checking table: '{table_name}' ---")
        try:
            # Use PostgREST to get a count
            count_result = db.client.table(table_name).select('*', count='exact').limit(0).execute()
            count = count_result.count
            
            if count > 0:
                print(f"✅ Found {count} rows.")
            else:
                print(f"⚠️ Found 0 rows. This is likely the cause of the empty UI.")
                all_tables_ok = False

        except Exception as e:
            print(f"❌ An error occurred while checking '{table_name}': {e}")
            all_tables_ok = False
    
    print("\n--- Diagnosis Complete ---")
    if all_tables_ok:
        print("✅ All summary tables contain data. The issue might be in the Streamlit UI code.")
    else:
        print("❌ One or more summary tables are empty. They need to be rebuilt.")
        print("You can rebuild them by running: python run.py refresh")


if __name__ == "__main__":
    diagnose_summary_tables()
