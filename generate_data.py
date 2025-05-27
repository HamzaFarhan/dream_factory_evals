import json
import random
from datetime import date
from pathlib import Path
from typing import Any

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

DATA_DIR = Path(__file__).parent

EMPLOYEES_PER_DEPT = (5, 10)
POLICIES_PER_DEPT = (2, 3)
PRODUCTS = 20
REVENUES_PER_PRODUCT = (3, 6)
EXPENSES = 20
LOCATIONS = [fake.city() for _ in range(10)]
MACHINES_PER_LOC = (3, 6)
MAINT_PER_MACHINE = (2, 5)


# --- HR_DEPARTMENTS ---
departments = [
    {"department_id": i, "name": department, "manager_id": None}
    for i, department in enumerate(
        [
            "Sales",
            "Marketing",
            "Engineering",
            "HR",
            "Finance",
            "Operations",
            "Customer Service",
            "IT",
            "Legal",
            "Procurement",
            "R&D",
            "Administration",
            "Support",
            "Quality Assurance",
            "Logistics",
            "Business Development",
            "Strategy",
            "Compliance",
            "Production",
            "Innovation",
        ],
        start=1,
    )
]

# --- HR_EMPLOYEES ---
employees: list[dict[str, Any]] = []
emp_id = 1
for dept in departments:
    n = random.randint(*EMPLOYEES_PER_DEPT)
    dept_emps = []
    for _ in range(n):
        join_date = fake.date_between(start_date="-3y", end_date="today")
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        emp = {
            "employee_id": emp_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "date_joined": join_date.strftime("%Y-%m-%d"),
            "department_id": dept["department_id"],
            "role": "Manager" if len(dept_emps) == 0 else random.choice(["Staff", "Staff", "Staff", "Lead"]),
        }
        dept_emps.append(emp)
        employees.append(emp)
        emp_id += 1
    # Assign manager_id for department
    dept["manager_id"] = dept_emps[0]["employee_id"]

# --- HR_POLICIES ---
policies: list[dict[str, Any]] = []
policy_id = 1
for dept in departments:
    n = random.randint(*POLICIES_PER_DEPT)
    for _ in range(n):
        eff_date = fake.date_between(start_date="-2y", end_date="today")
        policies.append(
            {
                "policy_id": policy_id,
                "title": f"{dept['name']} Policy",
                "description": f"Policy details for {dept['name']} department.",
                "effective_date": eff_date.strftime("%Y-%m-%d"),
                "department_id": dept["department_id"],
            }
        )
        policy_id += 1

# --- FINANCE_PRODUCTS ---
products = [
    {
        "product_id": i + 1,
        "name": f"Product {i + 1}",
        "description": f"Description for Product {i + 1}.",
        "category": random.choice(["Electronics", "Software", "Hardware", "Service"]),
    }
    for i in range(PRODUCTS)
]

# --- FINANCE_REVENUES ---
revenues: list[dict[str, Any]] = []
revenue_id = 1
for prod in products:
    n = random.randint(*REVENUES_PER_PRODUCT)
    for _ in range(n):
        dt = fake.date_between(start_date="-2y", end_date="today")
        revenues.append(
            {
                "revenue_id": revenue_id,
                "product_id": prod["product_id"],
                "revenue_amount": round(random.uniform(500, 10000), 2),
                "revenue_date": dt.strftime("%Y-%m-%d"),
                "quarter": ((dt.month - 1) // 3) + 1,
                "year": dt.year,
            }
        )
        revenue_id += 1

# --- FINANCE_EXPENSES ---
expenses: list[dict[str, Any]] = []
expenses_dict = {
    "Operational": [
        "Office supplies",
        "Utilities",
        "Employee salaries",
        "Software subscriptions",
        "Marketing expenses",
    ],
    "Capital": [
        "Equipment purchase",
        "Building renovation",
        "Vehicle acquisition",
        "Land purchase",
        "Technology infrastructure",
    ],
    "Misc": [
        "Legal fees",
        "Charitable donations",
        "Employee training",
        "Travel expenses",
        "Consulting services",
    ],
}
for i in range(EXPENSES):
    dt = fake.date_between(start_date="-2y", end_date="today")
    category = random.choices(list(expenses_dict.keys()), weights=[0.45, 0.45, 0.10], k=1)[0]
    expense = random.choice(expenses_dict[category])
    expenses.append(
        {
            "expense_id": i + 1,
            "description": expense,
            "amount": round(random.uniform(100, 5000), 2),
            "expense_date": dt.strftime("%Y-%m-%d"),
            "category": category,
        }
    )

# --- OPS_MACHINES ---
machines: list[dict[str, Any]] = []
machine_id = 1
machine_locations = random.choices(LOCATIONS, k=len(departments))
for loc in machine_locations:
    n = random.randint(*MACHINES_PER_LOC)
    for _ in range(n):
        install_date = fake.date_between(start_date="-4y", end_date="today")
        machines.append(
            {
                "machine_id": machine_id,
                "machine_name": f"Machine {machine_id}",
                "location": loc,
                "status": random.choice(["Active", "Inactive", "Maintenance"]),
                "installation_date": install_date.strftime("%Y-%m-%d"),
            }
        )
        machine_id += 1

# --- OPS_MAINTENANCE ---
maintenances: list[dict[str, Any]] = []
actions_dict = {
    "Routine check": {
        False: ["Routine check completed."],
        True: ["Anomaly found during routine check."],
    },
    "Replaced part": {
        False: ["Replaced faulty sensor.", "Minor malfunction fixed."],
        True: ["Replacement failed.", "Part incompatible."],
    },
    "Calibration": {
        False: ["Calibration successful.", "System recalibrated."],
        True: ["Calibration unsuccessful.", "System recalibration failed."],
    },
    "Software update": {
        False: ["Software updated successfully.", "System rebooted successfully."],
        True: ["Software update failed.", "System reboot failed."],
    },
}
maint_id = 1
for m in machines:
    n = random.randint(*MAINT_PER_MACHINE)
    for _ in range(n):
        dt = fake.date_between(start_date=date.fromisoformat(m["installation_date"]), end_date="today")
        maintenance_action = random.choice(list(actions_dict.keys()))
        anomaly_detected = fake.boolean(chance_of_getting_true=20)
        notes = random.choice(actions_dict[maintenance_action][anomaly_detected])
        maintenances.append(
            {
                "maintenance_id": maint_id,
                "machine_id": m["machine_id"],
                "maintenance_date": dt.strftime("%Y-%m-%d"),
                "maintenance_action": maintenance_action,
                "anomaly_detected": anomaly_detected,
                "notes": notes,
            }
        )
        maint_id += 1


# --- Write to files ---
def write_json(filename: str, data: Any) -> None:
    Path(DATA_DIR / filename).write_text(json.dumps(data, indent=2))


write_json("hr_departments.json", departments)
write_json("hr_employees.json", employees)
write_json("hr_policies.json", policies)
write_json("finance_products.json", products)
write_json("finance_revenues.json", revenues)
write_json("finance_expenses.json", expenses)
write_json("ops_machines.json", machines)
write_json("ops_maintenance.json", maintenances)

print("Generated new, more realistic data in new_data/.")
