---
description: Creating evals.py files for level 4 domains
---

# Workflow: Creating evals.py for Level 4 Domains

This workflow provides a systematic approach to creating evals.py files for level 4 domains (HR, Finance, Ops) in the dream_factory_evals project, using the level 3 files as reference.

## Step 1: Set Up Directory and Examine Reference Files

1. Ensure output_types.py for the domain is already created. If not, first use the workflow for creating output_types.py files.

2. Look at the level 3 evals.py for the same domain as a reference:
   ```python
   # For HR
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level3/hr/evals.py", StartLine=0, EndLine=500)
   
   # For Finance
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level3/finance/evals.py", StartLine=0, EndLine=500)
   
   # For Ops
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level3/ops/evals.py", StartLine=0, EndLine=500)
   ```

3. Check the level 4 output_types.py for the domain you're working on:
   ```python
   # For Finance
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level4/finance/output_types.py", StartLine=0, EndLine=500)
   
   # For Ops
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level4/ops/output_types.py", StartLine=0, EndLine=500)
   ```

4. Study the level 4 queries in 4.json for the specific domain:
   ```python
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/levels/4.json", StartLine=0, EndLine=1500)
   ```

## Step 2: Create or Update the evals.py File

1. Set up imports and basic structure:
   ```python
   # Example for Finance
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level4/finance/evals.py", StartLine=0, EndLine=50)
   
   # If file doesn't exist or needs updating
   replace_file_content(
       TargetFile="/Users/hamza/dev/dream_factory_evals/evals/level4/finance/evals.py",
       Instruction="Setting up base structure for level 4 Finance evals",
       ReplacementChunks=[{
           "AllowMultiple": true,
           "TargetContent": "# Existing content if any...",
           "ReplacementContent": """from __future__ import annotations

import argparse
from datetime import date as date_

import logfire
from pydantic_ai.models import KnownModelName
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    Role,
    ToolCall,
    evaluate,
)

from .output_types import (
    # Import all required output types
)

_ = logfire.configure()


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")
"""
       }]
   )
   ```

## Step 3: Import Output Types

1. Review all models defined in output_types.py that will be needed for your test cases

2. Add all necessary imports from output_types.py:
   ```python
   replace_file_content(
       TargetFile="/path/to/evals.py",
       Instruction="Adding imports for output types",
       ReplacementChunks=[{
           "AllowMultiple": true,
           "TargetContent": "from .output_types import (\n    # Import all required output types\n)",
           "ReplacementContent": """from .output_types import (
    ModelClass1,
    ModelClass2,
    ModelClass3,
    # Add all needed models in alphabetical order
)"""
       }]
   )
   ```

## Step 4: Implement Test Cases

1. Study the level 4 queries and responses to understand the test cases needed

2. Create the dataset with test cases, implementing one case at a time:
   ```python
   finance_dataset = Dataset[Query, QueryResult](
       cases=[
           Case(
               name="finance_l4_1",
               inputs=Query(
                   query="Query text from 4.json",
                   output_type=ExpectedOutputType,  # Top level response type
               ),
               expected_output=QueryResult(
                   result=ExpectedOutputType(
                       # Fill in with expected output data structure from 4.json
                   ),
                   tool_calls=[
                       # Fill in expected tool calls
                       ToolCall(
                           tool_name="get_table_records",
                           params={
                               # Add appropriate parameters
                           },
                       ),
                   ],
               ),
           ),
           # Implement other cases similarly
       ],
       evaluators=[EvaluateResult(), EvaluateToolCalls()],
   )
   ```

## Step 5: Add or Preserve the main() Function

1. If the file already has a main function, preserve it. Otherwise, add a standard main function:
   ```python
   # don't change this
   def main():
       parser = argparse.ArgumentParser(description="Run <DOMAIN> evaluations")
       parser.add_argument(
           "--model",
           type=str,
           required=True,
           help="Model name to evaluate. Examples:\\n"
           "  OpenAI: 'openai:gpt-4-turbo', 'openai:gpt-4o'\\n"
           "  Anthropic: 'anthropic:claude-3-5-sonnet-latest', 'anthropic:claude-3-opus-latest'\\n"
           "  Google: 'google-gla:gemini-1.5-pro', 'google-gla:gemini-1.5-flash'",
       )
       args = parser.parse_args()

       evaluate(model=args.model, dataset=<domain>_dataset, user_role=Role.<DOMAIN>, level=4)


   if __name__ == "__main__":
       models: list[KnownModelName] = ["openai:gpt-4.1-mini", "openai:gpt-4.1-nano"]
       for model in models:
           evaluate(model=model, dataset=<domain>_dataset, user_role=Role.<DOMAIN>, level=4)
   ```

## Step 6: Test and Validate

1. Ensure all expected test cases match the structure in 4.json
2. Verify that all necessary imports are included
3. Check that the main function is properly implemented

## Implementation Notes

1. **No RESULT_TYPES constant needed**: Unlike level 3, you do not need to define FINANCE_RESULT_TYPES or OPS_RESULT_TYPES.

2. **Follow Python style conventions**:
   - Use Python 3.12+ conventions
   - Use `|` instead of `Union` for type annotations
   - Use descriptive variable names
   - Import all necessary models from output_types.py

3. **Tool calls implementation**:
   - Ensure tool calls match the expected parameters
   - Check that table names, filters, and related fields are correct

4. **Consistency with 4.json**:
   - The expected responses must match the structure in 4.json
   - Pay attention to nested objects and their field names

5. **Customizing by domain**:
   - For HR: Use `Role.HR` in the evaluate function
   - For Finance: Use `Role.FINANCE` in the evaluate function
   - For Ops: Use `Role.OPS` in the evaluate function

## Example Structure

```python
from __future__ import annotations

import argparse
from datetime import date as date_

import logfire
from pydantic_ai.models import KnownModelName
from pydantic_evals import Case, Dataset

from dream_factory_evals.df_agent import (
    EvaluateResult,
    EvaluateToolCalls,
    Query,
    QueryResult,
    Role,
    ToolCall,
    evaluate,
)

from .output_types import (
    # All required model classes from output_types.py
)

_ = logfire.configure()


def date(year: int, month: int, day: int) -> str:
    return date_(year, month, day).strftime("%Y-%m-%d")


domain_dataset = Dataset[Query, QueryResult](
    cases=[
        Case(
            name="domain_l4_1",
            inputs=Query(
                query="First query text from 4.json",
                output_type=Model1Response,
            ),
            expected_output=QueryResult(
                result=Model1Response(...),
                tool_calls=[...],
            ),
        ),
        # More test cases...
    ],
    evaluators=[EvaluateResult(), EvaluateToolCalls()],
)


# don't change this
def main():
    parser = argparse.ArgumentParser(description="Run Domain evaluations")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name to evaluate. Examples:\n"
        "  OpenAI: 'openai:gpt-4-turbo', 'openai:gpt-4o'\n"
        "  Anthropic: 'anthropic:claude-3-5-sonnet-latest', 'anthropic:claude-3-opus-latest'\n"
        "  Google: 'google-gla:gemini-1.5-pro', 'google-gla:gemini-1.5-flash'",
    )
    args = parser.parse_args()

    evaluate(model=args.model, dataset=domain_dataset, user_role=Role.DOMAIN, level=4)


if __name__ == "__main__":
    models: list[KnownModelName] = ["openai:gpt-4.1-mini", "openai:gpt-4.1-nano"]
    for model in models:
        evaluate(model=model, dataset=domain_dataset, user_role=Role.DOMAIN, level=4)
```
