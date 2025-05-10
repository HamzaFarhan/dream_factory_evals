---
description: Creating output_types.py files for level 4 domains
---

# Workflow: Creating output_types.py for Level 4 Domains

This workflow provides a systematic approach to creating output_types.py files for level 4 domains (HR, Finance, Ops) in the dream_factory_evals project.

## Step 1: Analyze the Query Structure in 4.json

1. Open and examine the level 4 queries file:
   ```python
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/levels/4.json", StartLine=0, EndLine=500)
   ```

2. For Finance or Ops sections, adjust line ranges appropriately:
   ```python
   # For Finance section
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/levels/4.json", StartLine=450, EndLine=650)
   
   # For Ops section
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/levels/4.json", StartLine=650, EndLine=1500)
   ```

3. For each query in the domain section, carefully study the "expected_response" structure

## Step 2: Examine Reference Files

1. Look at the level 3 output_types.py for the same domain as reference:
   ```python
   # For HR
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level3/hr/output_types.py", StartLine=0, EndLine=500)
   
   # For Finance
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level3/finance/output_types.py", StartLine=0, EndLine=500)
   
   # For Ops
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level3/ops/output_types.py", StartLine=0, EndLine=500)
   ```

   > **IMPORTANT:** The level3 output_types.py files should be used as a definitive reference for implementation patterns, including how string comparisons are handled in `__eq__` methods and other important structural elements.

2. Check if there's already a skeleton file for the domain:
   ```python
   # Example for Finance
   view_file(AbsolutePath="/Users/hamza/dev/dream_factory_evals/evals/level4/finance/output_types.py", StartLine=0, EndLine=200)
   ```

## Step 3: Extract Common and Base Models

1. Identify entities that appear across multiple queries
2. Create base models for these reusable entities
3. Define fields with appropriate types following Python 3.12+ conventions:
   - Use `|` instead of `Union`
   - Use builtins like `list`, `dict` instead of imports from `typing`
   - Use `| None` instead of `Optional`
   - Make optional fields have default values (`None`)

## Step 4: Create Query-Specific Models

1. For each query in the domain:
   - Analyze the structure of the expected response
   - Create models for each nested object
   - Build the top-level response model
   - Use clear naming that matches the JSON structure

2. Group models by their respective queries and add comments to separate sections

## Step 5: Implementation

1. Import and implement the `are_strings_similar` function for string comparison:
   ```python
   # Add to the imports section
   from dream_factory_evals.df_agent import are_strings_similar
   ```

2. Implement `__eq__` methods for models with string fields that should be compared with similarity rather than exact equality:
   ```python
   def __eq__(self, other: object) -> bool:
       if not isinstance(other, YourModelName):
           return NotImplemented
       return (
           are_strings_similar(self.string_field1, other.string_field1)
           and are_strings_similar(self.string_field2, other.string_field2)
           and self.non_string_field == other.non_string_field
       )
   ```

3. Create or update the output_types.py file with your models:
   ```python
   # Example for Finance
   replace_file_content(
       TargetFile="/Users/hamza/dev/dream_factory_evals/evals/level4/finance/output_types.py",
       Instruction="Creating output types for level 4 Finance queries",
       ReplacementChunks=[{"AllowMultiple": false, "TargetContent": "...", "ReplacementContent": "..."}]
   )
   ```

## Design Principles

1. Use modern Python type annotations (`|` instead of `Union`)
2. Prefer composition over inheritance
3. Make fields optional (`None` default) when they might not always be present
4. Use descriptive names that match the JSON structure
5. Group related models logically
6. Add comments to improve readability
7. For dates, use str, not datetime
8. Implement `__eq__` methods for models with string fields that should be compared with similarity rather than exact equality
9. Use `are_strings_similar` from `dream_factory_evals.df_agent` for fuzzy string matching in `__eq__` methods 

## Example Implementation Structure

```python
from typing import Annotated

from pydantic import BaseModel, Field

from dream_factory_evals.df_agent import are_strings_similar

date = Annotated[str, Field(description="format: YYYY-MM-DD")] # use this for dates


# Common models
class BaseEntity(BaseModel):
    id: int
    name: str


# Query 1 models
class Query1SubModel(BaseModel):
    field1: str
    field2: int


class Query1Response(BaseModel):
    main_data: list[Query1SubModel]
    summary: str
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Query1Response):
            return NotImplemented
        return (
            self.main_data == other.main_data
            and are_strings_similar(self.summary, other.summary)
        )


# Query 2 models
# ...


# Query 3 models
# ...
```