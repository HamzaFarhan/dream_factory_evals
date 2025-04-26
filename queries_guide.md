# Dream Factory Benchmark Query Authoring Guide

## 1. Objective
This document is **the single source of truth** for creating and maintaining benchmark queries used in Dream Factory evaluations.  
Follow it verbatim when:
- Writing new **Level 4** queries.
- Adding / editing **Level 1 – 3** query JSON files.

## 2. Domains & Isolation
Queries are always scoped **per business domain**:

| Domain   | Allowed Tables Prefix |
|----------|-----------------------|
| HR       | `hr_`                 |
| Finance  | `finance_`            |
| Operations | `ops_`              |

A test agent evaluated on one domain **sees only that domain’s tables and documents**.  
Ignore RBAC or cross‑domain scenarios while authoring – stay inside the prefix.

## 3. Data Inventory (abridged)
Only include tables relevant to query design. For full field lists see `data/schema.md`.

### HR
- `hr_departments` ←→ `hr_employees` (has_many)  
- `hr_policies` ←→ `hr_departments` (belongs_to)

### Finance
- `finance_products` ←→ `finance_revenues`
- `finance_expenses`

### Operations
- `ops_machines` ←→ `ops_maintenance`

## 4. Available Tools (from `src/dream_factory_evals/df_mcp.py`)
All tools return JSON.

### 4.1 `get_table_schema`
```python
get_table_schema(table_name, base_url=None, dream_factory_api_key=None) -> dict
```
Returns the column definitions and relationships of a table.

### 4.2 `get_table_records`
```python
get_table_records(
    table_name,
    filter="",                    # SQL‑like WHERE clause
    fields="*",                   # "*" or comma list or list[str]
    limit=None, offset=0,
    order_field="",
    related=""                    # "", "*", str, or list[str]
) -> dict
```
Filter syntax (wrap each clause in **parentheses**):
```
AND | OR | NOT
=  !=  >  >=  <  <=  IN (...)  NOT IN (...) 
LIKE  CONTAINS  STARTS WITH  ENDS WITH
```
`related` performs **server‑side joins** using DreamFactory FK aliases such as  
`hr_departments_by_department_id`.  

### 4.3 `get_table_records_by_ids`
```python
get_table_records_by_ids(
    table_name,
    ids,                          # str | list[str]
    fields="*",
    related=""
) -> dict
```

## 5. Query JSON Contract
Each query object in `levels/<N>.json` **must** contain:

| Key | Type | Description |
|-----|------|-------------|
| `query_id` | str | Format `{domain}_l{level}_{seq}` (`finance_l3_7`) |
| `query` | str | Natural‑language question including role context |
| `expected_response` | dict | Canonical answer used for grading |
| `explanation` | str | Why this query is at this level |
| `tools_needed` | list[str] | Subset of {`get_table_schema`,`get_table_records`,`get_table_records_by_ids`} |
| `expected_tool_calls` | list[ {tool:str, params:dict} ] | Ordered minimal plan |
| `sample_solution` | str | One‑sentence outline of the approach |

Ordering of keys matters (same as table above).

## 6. Difficulty Levels & Templates

| Level | Purpose | Rules | NL Template |
|-------|---------|-------|-------------|
| **1 – Basic Retrieval** | Fetch one fact from one table OR one document section | • One tool call • No joins/calcs | *“As an HR user, what is the email of Alice Johnson?”* |
| **2 – Simple Join / Calc** | Join two structured sources **or** perform one arithmetic calculation | • ≤2 tool calls • Direct FK join via `related` OR simple math | *“As a Finance user, what is the revenue for Product 42 and its category?”* |
| **3 – Multi‑Source Integration** | Integrate ≥2 sources (at least one may be unstructured) and summarise or correlate | • Sequential or `related` joins allowed • May compute stats or produce grouped output | *“As an Operations user, correlate machine downtime with maintenance actions for Q1 2024.”* |
| **4 – Analytical Reasoning** | Multi‑hop analysis with recommendations or insights | • ≥3 distinct sources • Free‑form narrative output plus structured data • Expect multiple tool calls & intermediate reasoning | *“As a Finance manager, given revenues, costs and customer feedback for FY 2024, analyse profit decline and suggest improvements.”* |

## 7. Authoring Checklist
Before committing a query:

- [ ] Uses only tables within its domain prefix.  
- [ ] Complies with level rules (sources, joins, calculations).  
- [ ] `filter` clauses wrapped in parentheses and valid ANSI operators.  
- [ ] `expected_tool_calls` list is **minimal but sufficient**.  
- [ ] `expected_response` keys match information asked in `query`.  
- [ ] Naming follows `domain_l{level}_{seq}` and seq is unique.  
- [ ] `sample_solution` is one sentence (no SQL).  

## 8. Updating Existing JSON
When adjusting Level 1‑3 files:

1. Preserve ordering of query objects; append new ones at the end of that level.
2. Never delete an existing `query_id`; if a query is obsolete, mark it `"deprecated": true`.
3. Keep indentation two spaces, no trailing commas.
4. Run `python -m json.tool levels/<N>.json` before committing to validate.

## 9. Examples (concise)

### Level 2 – HR
```json
{
  "query_id": "hr_l2_6",
  "query": "As an HR analyst, which department does John Doe belong to?",
  "expected_response": { "employee": "John Doe", "department": "Marketing" },
  "explanation": "Simple FK join between employees and departments.",
  "tools_needed": ["get_table_records"],
  "expected_tool_calls": [
    {
      "tool": "get_table_records",
      "params": {
        "table_name": "hr_employees",
        "filter": "(first_name='John') AND (last_name='Doe')",
        "related": "hr_departments_by_department_id"
      }
    }
  ],
  "sample_solution": "Query HR_EMPLOYEES for John Doe with related HR_DEPARTMENTS."
}
```

### Level 4 – Finance (sketch)
```text
As a Finance manager, analyse Q1‑Q4 2023 revenue (finance_revenues), product mix (finance_products),
and CAPEX spends (finance_expenses) to identify profitability drivers and propose three actions.
```
Expected response should include:
```json
{
  "insights": [ "...", "...", "..." ],
  "top_drivers": [ {"category": "Software", "roi": 0.34}, ... ],
  "recommendations": [ "Increase marketing for ...", "Reduce capex on ..." ]
}
```
Tool plan (outline):

1. `get_table_records` on `finance_revenues` grouped by quarter.  
2. `get_table_records` on `finance_expenses` filtered `category='Capital'`.  
3. Join with `finance_products` via `product_id` to map categories.

---

Follow this guide strictly – all future query generation and updates are validated against it.