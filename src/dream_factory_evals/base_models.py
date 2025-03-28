from pydantic import BaseModel, Field


class Success(BaseModel):
    success: bool = Field(description="Whether the agent has successfully completed the main task.")
    response_message: str = Field(description="A message to the user about the result of the current/main task.")
    response_data: str = Field(description="The data returned for the current/main task.")


class Task(BaseModel):
    main_task: str
