# Dream Factory Evaluations

## Table of Contents

- [Overview](#overview)
- [Database Schema](#database-schema)
  - [Tables](#tables)
  - [Roles & Access Control](#roles--access-control)
- [Implementation](#implementation)
  - [1. MCP Server](#1-mcp-server)
  - [2. Evaluation System](#2-evaluation-system)
  - [3. Value Proposition](#3-value-proposition)
- [Running Evaluations](#running-evaluations)
- [Creating Leaderboards](#creating-leaderboards)
- [Example Queries](#example-queries)

## Overview

We are evaluating how an `Agent` uses the `DreamFactory` `MCP` server.

**What we evaluate for each query:**

1. **Actual output** - The structured response from the agent
2. **Tool calls** - Number and parameters of MCP tool calls made
3. **Duration** - Time taken to complete the query
4. **Cost** - Resource consumption metrics

This evaluation framework helps assess agent performance across different complexity levels and roles.

## Database Schema

### Tables

We have **8 tables** in our database organized by business function:

| **HR Tables** | **Finance Tables** | **Operations Tables** |
|---------------|--------------------|-----------------------|
| `hr_employees` | `finance_expenses` | `ops_machines` |
| `hr_departments` | `finance_products` | `ops_maintenance` |
| `hr_policies` | `finance_revenues` | |

### Roles & Access Control

We have **4 roles** with different access permissions:

| Role | Access Level | Available Tables |
|------|-------------|------------------|
| `CEO` | **All tables** | All 8 tables |
| `HR` | **HR only** | `hr_employees`, `hr_departments`, `hr_policies` |
| `Finance` | **Finance only** | `finance_expenses`, `finance_products`, `finance_revenues` |
| `Ops` | **Operations only** | `ops_machines`, `ops_maintenance` |

Each role has its own API key for authentication and authorization.

## Implementation

### 1. MCP Server

The MCP server (`src/dream_factory_evals/df_mcp.py`) provides a standardized interface to DreamFactory APIs.

**Configuration:** The server uses `DREAM_FACTORY_BASE_URL` and `DREAM_FACTORY_API_KEY` environment variables.

#### Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `get_table_schema` | Retrieves table structure and field types | `table_name` |
| `get_table_records` | Fetches records with filtering, pagination, joining | `table_name`, `filter`, `fields`, `limit`, `offset`, `order_field`, `related` |
| `get_table_records_by_ids` | Retrieves specific records by ID | `table_name`, `ids`, `fields`, `related` |
| `calculate_sum` | Computes sum of numerical values | `values` |
| `calculate_difference` | Calculates difference between numbers | `num1`, `num2` |
| `calculate_mean` | Computes arithmetic mean | `values` |

#### RBAC Implementation

Role-Based Access Control (RBAC) is enforced at the API level:

- **Server-side enforcement:** If an agent tries to access unauthorized tables, the server returns an error
- **Client-side filtering:** We filter available tables based on role before agent execution

**Workaround for table discovery:**

> **Note:** Non-CEO roles are not authorized to call the `list_table_names` tool, which is why it's implemented as a plain function rather than an MCP tool and must be called manually with CEO privileges.

1. Use `CEO` API key to call `list_table_names`
2. Filter tables by role prefix (e.g., `hr_` for HR role)
3. Include filtered table list in agent's system prompt

### 2. Evaluation System

We have **4 complexity levels** with **3-5 queries per role** at each level.

#### Evaluation Structure

Each evaluation case contains:

```python
{
    "query_id": "hr_l1_1",
    "query": "How many employees are there?",
    "expected_response": {...},
    "expected_tool_calls": [...]
}
```

#### The Pydantic Solution

**Problem:** LLM responses vary even for identical queries:
- `100` vs `100.0` vs `"One Hundred"` vs `"There are 100 employees"`

**Solution:** Use Pydantic models to enforce structured outputs:

```python
from pydantic import BaseModel
from pydantic_evals import Case

class EmployeeCount(BaseModel):
    number_of_employees: int

case = Case(
    name="hr_l1_1",
    inputs=Query(
        query="How many employees are there?",
        output_type=EmployeeCount
    ),
    expected_output=QueryResult(
        result=EmployeeCount(number_of_employees=100)
    )
)
```

#### Handling Free-Form Text

For strategic recommendations and analysis, we use semantic comparison:

```python
class Analysis(BaseModel):
    better_performing_category: Literal["Software", "Electronics"]
    revenue_to_marketing_efficiency: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Analysis):
            return NotImplemented
        return (
            self.better_performing_category == other.better_performing_category
            and are_strings_similar(
                self.revenue_to_marketing_efficiency, 
                other.revenue_to_marketing_efficiency
            )
        )
```

The `are_strings_similar()` function uses a small LLM to compare semantic meaning rather than exact text matching.

#### Complex Evaluation Example

Here's a Level 4 finance query with multi-part analysis:

```python
class RevenueComparison(BaseModel):
    quarterly_comparison: dict[Literal["Software", "Electronics"], CategoryPerformance]
    marketing_expenses: MarketingExpenses
    analysis: Analysis
    strategic_recommendation: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RevenueComparison):
            return NotImplemented
        return (
            self.quarterly_comparison == other.quarterly_comparison
            and self.marketing_expenses == other.marketing_expenses
            and self.analysis == other.analysis
            and are_strings_similar(self.strategic_recommendation, other.strategic_recommendation)
        )

case = Case(
    name="finance_l4_1",
    inputs=Query(
        query=(
            "Compare Q4 2023 vs Q4 2024 revenue performance for 'Software' and 'Electronics' products. "
            "Calculate growth rates and identify which category performed better. "
            "Also analyze total 'Marketing' expenses for both quarters. "
            "Provide one strategic recommendation based on the revenue-to-marketing spend efficiency."
        ),
        output_type=RevenueComparison
    ),
    expected_output=QueryResult(
        result=RevenueComparison(
            quarterly_comparison={
                "Software": CategoryPerformance(
                    Q4_2023_revenue=15420.33,
                    Q4_2024_revenue=28750.12,
                    growth_rate_percentage=86.4
                ),
                "Electronics": CategoryPerformance(
                    Q4_2023_revenue=13831.28,
                    Q4_2024_revenue=34569.61,
                    growth_rate_percentage=149.9
                )
            },
            marketing_expenses=MarketingExpenses(
                Q4_2023=2450.75,
                Q4_2024=3200.50
            ),
            analysis=Analysis(
                better_performing_category="Electronics",
                revenue_to_marketing_efficiency="Electronics showed 149.9% growth vs 86.4% for Software, while marketing spend increased only 30.6%"
            ),
            strategic_recommendation="Allocate more marketing budget to Electronics products in Q1 2025, as they demonstrate superior growth response to marketing investment."
        )
    )
)
```

#### Tool Call Evaluation

We also evaluate the **MCP tool calls** made by the agent:

```python
expected_tool_calls = [
    ToolCall(
        tool_name="get_table_records",
        params={
            "table_name": "finance_revenues",
            "filter": "((quarter='Q4') AND (year=2023)) OR ((quarter='Q4') AND (year=2024))",
            "fields": ["product_category", "revenue", "quarter", "year"]
        }
    ),
    ToolCall(
        tool_name="get_table_records", 
        params={
            "table_name": "finance_expenses",
            "filter": "((quarter='Q4') AND (year=2023) AND (category='Marketing')) OR ((quarter='Q4') AND (year=2024) AND (category='Marketing'))"
        }
    )
]
```

#### Dataset Organization

Each role/level combination has its own dataset:

```
evals/
├── level1/
│   ├── finance/evals.py
│   ├── hr/evals.py
│   └── ops/evals.py
├── level2/
│   ├── finance/evals.py
│   ├── hr/evals.py
│   └── ops/evals.py
└── ...
```

Each directory contains:
- `evals.py` - Dataset with test cases
- `output_types.py` - Pydantic models for structured outputs

### 3. Value Proposition

This evaluation framework provides several key insights:

1. **Structured Output Validation** - Using Pydantic models ensures consistent, comparable results across different LLM runs

2. **Semantic Text Comparison** - For free-form text, we use LLM-based semantic comparison rather than exact string matching

3. **Tool Usage Analysis** - Detailed tracking of MCP tool calls helps optimize agent efficiency

4. **Role-Based Evaluation** - Testing different access levels ensures proper RBAC implementation

5. **Complexity Scaling** - Four difficulty levels help identify where agents start to struggle

## Running Evaluations

### CLI Interface

The evaluation system provides a CLI tool for running evaluations:

```bash
# Basic usage
uv run src/dream_factory_evals/run_eval.py <model> <role> <level>

# Examples
uv run src/dream_factory_evals/run_eval.py "openai:gpt-4.1-mini" hr 2
uv run src/dream_factory_evals/run_eval.py "anthropic:claude-4-sonnet-20250514" finance 3
uv run src/dream_factory_evals/run_eval.py "google-gla:gemini-2.0-flash" ops 1
```

### CLI Options

```bash
# Custom report name
uv run src/dream_factory_evals/run_eval.py "openai:gpt-4.1-mini" hr 2 --report-name "my-custom-test"

# Custom prompt file
uv run src/dream_factory_evals/run_eval.py "openai:gpt-4.1-mini" hr 2 --prompt-name "advanced_prompt.txt"

# Adjust retry and tool call limits
uv run src/dream_factory_evals/run_eval.py "openai:gpt-4.1-mini" hr 2 --max-tool-calls 30 --retries 5
```

### Environment Variables

Configure defaults using environment variables:

```bash
export PROMPT_NAME="basic_prompt.txt"
export MAX_TOOL_CALLS="20"
export RETRIES="3"
```

### List Available Options

```bash
# List all available models
uv run src/dream_factory_evals/run_eval.py list-models

# List all available roles  
uv run src/dream_factory_evals/run_eval.py list-roles
```

### Comparing Models

```bash
# Test multiple models on the same dataset
for model in "openai:gpt-4.1-mini" "anthropic:claude-4-sonnet-20250514" "google-gla:gemini-2.0-flash"; do
    uv run src/dream_factory_evals/run_eval.py "$model" hr 2
done
```

## Creating Leaderboards

After running evaluations, you can create leaderboards to compare model performance across multiple evaluation reports.

### CLI Interface

```bash
# Basic leaderboard creation
uv run src/dream_factory_evals/create_leaderboard.py create <leaderboard_name> <report_name1> <report_name2> [...]

# Example: Compare HR Level 1 performance across models
uv run src/dream_factory_evals/create_leaderboard.py create "hr-level-1-comparison" \
  "openai:gpt-4o-hr-level-1" \
  "openai:gpt-4o-mini-hr-level-1" \
  "anthropic:claude-3-sonnet-hr-level-1"
```

### Leaderboard Outputs

The CLI generates two files in the `scores/` directory:

1. **Summary Leaderboard** (`<leaderboard_name>.csv`):
   - Aggregated metrics per model
   - Average score, accuracy, tool calls, and duration
   - Total scores and query counts
   - Ranked by average score (descending)

2. **Detailed Results** (`detailed_<leaderboard_name>.csv`):
   - All individual query results
   - Useful for deep-dive analysis

### Example Workflow

```bash
# 1. Run evaluations for multiple models
uv run src/dream_factory_evals/run_eval.py "openai:gpt-4o" hr 1
uv run src/dream_factory_evals/run_eval.py "openai:gpt-4o-mini" hr 1
uv run src/dream_factory_evals/run_eval.py "anthropic:claude-3-sonnet" hr 1

# 2. Create leaderboard
uv run src/dream_factory_evals/create_leaderboard.py create "hr-level-1-leaderboard" \
  "openai:gpt-4o-hr-level-1" \
  "openai:gpt-4o-mini-hr-level-1" \
  "anthropic:claude-3-sonnet-hr-level-1"

# 3. View results
cat scores/hr-level-1-leaderboard.csv
```

### Leaderboard Metrics

| Metric | Description |
|--------|-------------|
| `avg_score` | Average score across all queries (accuracy × 2 + correct_tool_calls) |
| `avg_accuracy` | Average accuracy percentage |
| `avg_tool_calls` | Average number of correct tool calls |
| `avg_duration` | Average query completion time |
| `total_score` | Sum of all scores |
| `query_count` | Total number of queries evaluated |

## Example Queries

### Level 1 Query (Basic)
```python
Query: "How many employees are there?"
Expected Output: EmployeeCount(number_of_employees=100)
Expected Tool Calls: [get_table_records(table_name="hr_employees")]
```

### Level 2 Query (Joining)
```python
Query: "What department does Alice Johnson work in?"
Expected Output: EmployeeDepartment(employee="Alice Johnson", department="Sales")
Expected Tool Calls: [
    get_table_records(
        table_name="hr_employees",
        filter="(first_name='Alice') AND (last_name='Johnson')",
        related="hr_departments_by_department_id"
    )
]
```

### Level 4 Query (Complex Analysis)
```python
Query: "Compare Q4 2023 vs Q4 2024 revenue performance..."
Expected Output: RevenueComparison(
    quarterly_comparison={...},
    marketing_expenses={...},
    analysis={...},
    strategic_recommendation="..."
)
Expected Tool Calls: [
    get_table_records(...),  # Revenue data
    get_table_records(...),  # Marketing expenses
    calculate_difference(...),  # Growth calculations
]
```

---

**Key Innovation:** The combination of Pydantic-enforced structured outputs with semantic text comparison creates a robust evaluation framework that can handle both precise numerical results and nuanced textual analysis. Additionally, the automated leaderboard generation system enables seamless comparison of model performance across multiple evaluation runs, providing actionable insights for model selection and optimization.