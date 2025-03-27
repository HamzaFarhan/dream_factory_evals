# Level 1 Approach Note

For Level 1 queries, the primary goal is to test basic single-table lookups—no joins, minimal logic, and a single filter condition. Each query focuses on one table in the schema (Finance, HR, or Operations). The LLM (or any agent) simply needs to:
 1. Identify the correct table.
 2. Apply the specified filter (e.g., WHERE product_id = 1).
 3. Retrieve the requested columns.
 4. Return a concise result that matches the expected ground truth.

# Level 2 Approach Note

For Level 2 queries, the objective is to evaluate the model's ability to perform simple joins or basic inferences. These queries require combining data from two tables using common keys or executing straightforward calculations. Each query includes clear steps such as filtering, joining, and computing arithmetic where needed.

# Level 3 Approach Note

For Level 3 queries, the focus shifts to more complex scenarios that require multi-table joins, grouping, aggregations, and basic inferences. These queries simulate real-world scenarios where data must be integrated from multiple sources (and sometimes even across domains) to produce a cohesive result. Each query includes detailed instructions—such as join conditions, filter criteria, and calculation formulas—to define the expected output and ground truth steps clearly.

# Level 4 Approach Note

For Level 4 queries, we shift to complex, analytical scenarios that require multi-step reasoning, integration of data from multiple tables, and even text analysis. These queries simulate real-world decision-making where a model must not only retrieve and calculate numerical values but also provide qualitative insights and recommendations based on trends, anomalies, and correlations. The queries include detailed instructions such as join conditions, filtering criteria, calculation formulas, and inference steps.