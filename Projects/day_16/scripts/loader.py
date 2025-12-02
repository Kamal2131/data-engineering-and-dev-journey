import csv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from pymongo import MongoClient

# --- EXTRACT ---
def read_csv(filepath):
    """Reads a CSV file into a list of dictionaries."""
    print(f"Reading data from {filepath}...")
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        print(f"Successfully read {len(data)} raw records.")
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []

# --- TRANSFORM ---
def clean_data(raw_records):
    """Cleans and transforms raw CSV data."""
    print("Cleaning and transforming data...")
    cleaned = []
    for record in raw_records:
        # Create a copy to avoid modifying original data incidentally
        clean_record = record.copy() 
        
        # Transformation 1: Convert marks to integer
        # Using try/except to handle potential bad data
        try:
            clean_record["marks"] = int(clean_record["marks"].strip())
        except ValueError:
             print(f"Warning: Could not convert marks for {clean_record['name']}. Setting to 0.")
             clean_record["marks"] = 0
             
        # Transformation 2: Title case city and trim whitespace
        clean_record["city"] = clean_record["city"].strip().title()
        
        # Transformation 3: Title case name just in case
        clean_record["name"] = clean_record["name"].strip().title()
        
        cleaned.append(clean_record)
        
    print(f"Transformed {len(cleaned)} records.")
    return cleaned

# --- LOAD (OPTION A: SQL/SQLite) ---
# SQLAlchemy Setup
Base = declarative_base()

class StudentSQL(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    marks = Column(Integer)
    city = Column(String)

def load_to_sql(cleaned_data, db_name="school.db"):
    """Loads cleaned data into SQLite using SQLAlchemy."""
    print(f"Loading data into SQL database: {db_name}...")
    
    # Create engine and tables
    engine = create_engine(f"sqlite:///{db_name}")
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Prepare objects
        student_objects = []
        for row in cleaned_data:
            student_objects.append(
                StudentSQL(name=row["name"], marks=row["marks"], city=row["city"])
            )
        
        # Bulk insert (more efficient than adding one by one)
        session.add_all(student_objects)
        session.commit()
        print(f"Successfully loaded {len(student_objects)} records into SQL.")
    except Exception as e:
        session.rollback()
        print(f"Error loading to SQL: {e}")
    finally:
        session.close()

# --- LOAD (OPTION B: MongoDB) ---
def load_to_mongo(cleaned_data, connection_string="mongodb://localhost:27017", db_name="school", collection_name="students_etl"):
    """Loads cleaned data into MongoDB."""
    print(f"Loading data into Mongo database: {db_name}.{collection_name}...")
    
    try:
        client = MongoClient(connection_string)
        db = client[db_name]
        collection = db[collection_name]
        
        # Mongo can insert list of dicts directly
        result = collection.insert_many(cleaned_data)
        print(f"Successfully loaded {len(result.inserted_ids)} records into MongoDB.")
        client.close()
    except Exception as e:
        print(f"Error loading to MongoDB: {e}")