# Runs the app:
# Loads old data
# Adds new ones
# Displays results
# Saves back to JSON


from tracker import add_expense, get_expenses, total_expenses, remove_expense, remove_expense_all_name
from utils import save_to_json, load_from_json

old_data = load_from_json()

for item in old_data:
    add_expense(item["name"], item["amount"])

# remove_expense("coffee", 100)
remove_expense_all_name("Lunch")
# add_expense("Lunch", 200)

# Show results

all_expenses = get_expenses()
for expense in all_expenses:
    print(f" Title : {expense["name"]}, Amount : {expense["amount"]}")
print("Total Expense:", total_expenses())

# Save new changes
save_to_json(get_expenses())
