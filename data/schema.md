Table: HR_DEPARTMENTS
- department_id: int (PK)
- name: string
- manager_id: int

Table: HR_EMPLOYEES
- employee_id: int (PK)
- first_name: string
- last_name: string
- email: string
- date_joined: date
- department_id: int (FK)
- role: string

Table: HR_POLICIES
- policy_id: int (PK)
- title: string
- description: string
- effective_date: date
- department_id: int (FK)

Table: FINANCE_PRODUCTS
- product_id: int (PK)
- name: string
- description: string
- category: string

Table: FINANCE_REVENUES
- revenue_id: int (PK)
- product_id: int (FK)
- revenue_amount: decimal
- revenue_date: date
- quarter: int
- year: int

Table: FINANCE_EXPENSES
- expense_id: int (PK)
- description: string
- amount: decimal
- expense_date: date
- category: string

Table: OPS_MACHINES
- machine_id: int (PK)
- machine_name: string
- location: string
- status: string
- installation_date: date

Table: OPS_MAINTENANCE
- maintenance_id: int (PK)
- machine_id: int (FK)
- maintenance_date: date
- maintenance_action: string
- anomaly_detected: boolean
- notes: string
