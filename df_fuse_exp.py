import base64
import os
from dataclasses import dataclass
from typing import ClassVar

import logfire
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import langfuse_context
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

load_dotenv()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://cloud.langfuse.com/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
    f"Authorization=Basic {base64.b64encode(f'{os.environ["LANGFUSE_PUBLIC_KEY"]}:{os.environ["LANGFUSE_SECRET_KEY"]}'.encode()).decode()}"
)

logfire.configure(send_to_logfire=False)

langfuse = Langfuse()
DATASET_NAME = "hr_dataset"
AGENT_NAME = "hr_agent"


@dataclass
class HRDepartment:
    id: int
    name: str


@dataclass
class HREmployee:
    id: int
    name: str
    department: HRDepartment

    def __str__(self) -> str:
        return (
            f"<employee>\n"
            f"id: {self.id}\n"
            f"name: {self.name}\n"
            f"<department>\n"
            f"id: {self.department.id}\n"
            f"name: {self.department.name}\n"
            f"</department>\n"
            f"</employee>"
        )


@dataclass
class HR:
    employees: list[HREmployee]

    def __str__(self) -> str:
        return f"<employees>\n{'\n\n'.join(str(e) for e in self.employees)}\n</employees>"


class NumEmployees(BaseModel):
    num_employees: int
    _type_name: ClassVar[str] = "NumEmployees"


class Department(BaseModel):
    department_id: int
    department_name: str
    _type_name: ClassVar[str] = "Department"


# Map of model type names to actual model classes
MODEL_TYPE_MAP = {"NumEmployees": NumEmployees, "Department": Department}


class HRQuery(BaseModel):
    query: str
    deps: HR
    result_type: str  # Store as string for serialization


class HRQueryForAgent(BaseModel):
    query: str
    deps: HR
    result_type: type[NumEmployees] | type[Department]


hr = HR(
    employees=[
        HREmployee(id=1, name="John Doe", department=HRDepartment(id=1, name="Sales")),
        HREmployee(id=2, name="Jane Doe", department=HRDepartment(id=2, name="Marketing")),
        HREmployee(id=3, name="Jim Doe", department=HRDepartment(id=3, name="Engineering")),
    ]
)

data_set_items = [
    {
        "input": HRQuery(query="How many employees are there?", deps=hr, result_type="NumEmployees"),
        "expected_output": NumEmployees(num_employees=3),
    },
    {
        "input": HRQuery(query="What is the department of John Doe?", deps=hr, result_type="Department"),
        "expected_output": Department(department_id=1, department_name="Sales"),
    },
]


def create_dataset(dataset_name: str, data_set_items: list[dict]):
    langfuse.create_dataset(name=dataset_name)
    for data_set_item in data_set_items:
        langfuse.create_dataset_item(
            dataset_name=dataset_name,
            input=data_set_item["input"].model_dump(),
            expected_output=data_set_item["expected_output"].model_dump(),
        )


hr_agent = Agent(model="google-gla:gemini-2.0-flash", name=AGENT_NAME, deps_type=HR, instrument=True)


@hr_agent.system_prompt
async def get_employees(ctx: RunContext[HR]) -> str:
    return str(ctx.deps)


async def run_hr_query(query: HRQueryForAgent) -> NumEmployees | Department:
    res = await hr_agent.run(query.query, deps=query.deps, result_type=query.result_type)
    return res.data


async def evaluate(experiment_name: str):
    hr_dataset = langfuse.get_dataset(DATASET_NAME)
    for item in hr_dataset.items:
        with logfire.span(experiment_name) as span:
            trace_id = span.get_span_context().trace_id  # type: ignore
            trace_id = f"{trace_id:032x}"
            print(f"trace_id: {trace_id}")

            with item.observe(run_name=experiment_name, trace_id=trace_id) as _:
                # Convert the string result_type to the actual model class
                input_data = item.input
                input_hr_query = HRQuery(**input_data)

                # Create the agent query with the actual model class from the string
                agent_query = HRQueryForAgent(
                    query=input_hr_query.query,
                    deps=input_hr_query.deps,
                    result_type=MODEL_TYPE_MAP[input_hr_query.result_type],
                )

                output = await run_hr_query(query=agent_query)
                result_type_class = MODEL_TYPE_MAP[input_hr_query.result_type]

                langfuse.score(
                    trace_id=trace_id,
                    name=f"{AGENT_NAME}_evaluation",
                    value=result_type_class(**item.expected_output) == output,
                    data_type="BOOLEAN",
                )
        langfuse_context.flush()
        langfuse.flush()


if __name__ == "__main__":
    import asyncio

    # create_dataset(DATASET_NAME, data_set_items)
    asyncio.run(evaluate(experiment_name=f"{AGENT_NAME}_evaluation_1"))
