import os
from scripts.loader import read_csv, clean_data, load_to_sql, load_to_mongo

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "students.csv")
SQL_DB_PATH = os.path.join(BASE_DIR, "school.db")

def run_pipeline():
    print("=== Starting Mini-ETL Pipeline ===")
    
    # 1. EXTRACT
    raw_data = read_csv(CSV_PATH)
    
    if not raw_data:
        print("Pipeline aborted due to missing data.")
        return

    # 2. TRANSFORM
    cleaned_data = clean_data(raw_data)
    
    print("\n--- Preview of Cleaned Data ---")
    for item in cleaned_data[:2]: # Print first 2 for check
        print(item)
    print("-------------------------------\n")

    # 3. LOAD (Choose one or both!)
    
    # ----- Load to SQL -----
    # load_to_sql(cleaned_data, SQL_DB_PATH)
    
    # ----- Load to MongoDB -----
    # Uncomment below if you have Mongo running locally
    load_to_mongo(cleaned_data)

    print("\n=== Pipeline Finished Successfully ===")

if __name__ == "__main__":
    # Ensure requirements are installed:
    # pip install sqlalchemy pymongo
    run_pipeline()