import json
from pathlib import Path

data_dir = Path("data")

data_file = data_dir / "finance_expenses.json"

data = json.loads(data_file.read_text())

capital_expenses_2022 = [
    expense for expense in data if expense["category"] == "Capital" and expense["expense_date"].startswith("2022-")
]

print(sum(expense["amount"] for expense in capital_expenses_2022))
