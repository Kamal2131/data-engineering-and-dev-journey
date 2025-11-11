# Handles:
# JSON read/write
# Utility helpers

import json


def save_to_json(data, filename="expenses.json"):
    """Save expenses data to json file"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_from_json(filename="expenses.json"):
    """Load expenses data from json file"""

    try :
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
