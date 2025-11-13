import csv, logging

logging.basicConfig(filename="reader.log", level=logging.INFO)

def read_csv(filename):
    try:
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)
        logging.info("CSV read successfully.")
    except FileNotFoundError:
        logging.error(f"{filename} not found!")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

read_csv("students.csv")
