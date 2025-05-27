from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


class Email(BaseModel):
    email: str


def sglang_model(model_name: str) -> Model:
    return OpenAIModel(
        model_name, provider=OpenAIProvider(base_url="http://34.66.87.55:30000/v1", api_key="EMPTY")
    )


agent = Agent(sglang_model("Qwen2.5"))
query = (
    "Extract the email address from the following text: "
    "'Please contact us at info@example.com for more information.'"
)
result = agent.run_sync(query, output_type=Email)
print(result.output.email)
