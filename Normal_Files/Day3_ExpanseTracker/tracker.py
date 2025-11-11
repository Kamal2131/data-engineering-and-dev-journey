# Handles:
# Data storage
# Expense operations

expenses = []

def add_expense(name, amount):
    """Add an expanse with name and amount"""
    expenses.append({"name": name, "amount": amount})

def get_expenses():
    """Return list of expenses"""
    return expenses

def remove_expense(name, amount):
    """Remove an expense by matching name and amount."""
    for e in expenses:
        if e["name"] == name and e["amount"] == amount:
            expenses.remove(e)
            return True
    return False

def remove_expense_all_name(name):
    """Remove ALL expenses that match the given name."""
    global expenses
    expenses = [e for e in expenses if e["name"] != name]

def total_expenses():
    """Return total expenses"""
    return sum(e["amount"] for e in expenses)
