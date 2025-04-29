Table: HR_DEPARTMENTS
- department_id: int (PK)
- name: string
- manager_id: int
- related: [{'alias': None,
  'name': 'hr_employees_by_department_id',
  'label': 'Hr Employees By Department Id',
  'description': None,
  'native': [],
  'type': 'has_many',
  'field': 'department_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'hr_employees',
  'ref_field': 'department_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'CASCADE',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False},
 {'alias': None,
  'name': 'hr_policies_by_department_id',
  'label': 'Hr Policies By Department Id',
  'description': None,
  'native': [],
  'type': 'has_many',
  'field': 'department_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'hr_policies',
  'ref_field': 'department_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'SET NULL',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False}]

Table: HR_EMPLOYEES
- employee_id: int (PK)
- first_name: string
- last_name: string
- email: string
- date_joined: date
- department_id: int (FK)
- role: string
- related: [{'alias': None,
  'name': 'hr_departments_by_department_id',
  'label': 'Hr Departments By Department Id',
  'description': None,
  'native': [],
  'type': 'belongs_to',
  'field': 'department_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'hr_departments',
  'ref_field': 'department_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'CASCADE',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False}]

Table: HR_POLICIES
- policy_id: int (PK)
- title: string
- description: string
- effective_date: date
- department_id: int (FK)
- related: [{'alias': None,
  'name': 'hr_departments_by_department_id',
  'label': 'Hr Departments By Department Id',
  'description': None,
  'native': [],
  'type': 'belongs_to',
  'field': 'department_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'hr_departments',
  'ref_field': 'department_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'SET NULL',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False}]

Table: FINANCE_PRODUCTS
- product_id: int (PK)
- name: string
- description: string
- category: string
- related: [{'alias': None,
  'name': 'finance_revenues_by_product_id',
  'label': 'Finance Revenues By Product Id',
  'description': None,
  'native': [],
  'type': 'has_many',
  'field': 'product_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'finance_revenues',
  'ref_field': 'product_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'CASCADE',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False}]

Table: FINANCE_REVENUES
- revenue_id: int (PK)
- product_id: int (FK)
- revenue_amount: decimal
- revenue_date: date
- quarter: int
- year: int
- related: [{'alias': None,
  'name': 'finance_products_by_product_id',
  'label': 'Finance Products By Product Id',
  'description': None,
  'native': [],
  'type': 'belongs_to',
  'field': 'product_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'finance_products',
  'ref_field': 'product_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'CASCADE',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False}]

Table: FINANCE_EXPENSES
- expense_id: int (PK)
- description: string
- amount: decimal
- expense_date: date
- category: string
- related: []

Table: OPS_MACHINES
- machine_id: int (PK)
- machine_name: string
- location: string
- status: string
- installation_date: date
- related: [{'alias': None,
  'name': 'ops_maintenance_by_machine_id',
  'label': 'Ops Maintenance By Machine Id',
  'description': None,
  'native': [],
  'type': 'has_many',
  'field': 'machine_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'ops_maintenance',
  'ref_field': 'machine_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'CASCADE',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False}]

Table: OPS_MAINTENANCE
- maintenance_id: int (PK)
- machine_id: int (FK)
- maintenance_date: date
- maintenance_action: string
- anomaly_detected: boolean
- notes: string
- related: [{'alias': None,
  'name': 'ops_machines_by_machine_id',
  'label': 'Ops Machines By Machine Id',
  'description': None,
  'native': [],
  'type': 'belongs_to',
  'field': 'machine_id',
  'is_virtual': False,
  'ref_service_id': 222,
  'ref_table': 'ops_machines',
  'ref_field': 'machine_id',
  'ref_on_update': 'NO ACTION',
  'ref_on_delete': 'CASCADE',
  'junction_service_id': None,
  'junction_table': None,
  'junction_field': None,
  'junction_ref_field': None,
  'always_fetch': False,
  'flatten': False,
  'flatten_drop_prefix': False}]
