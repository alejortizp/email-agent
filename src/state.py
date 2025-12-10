from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class Email(BaseModel):
    id: str = Field(..., description="The ID of the email")
    date: str = Field(..., description="The date the email was sent")
    sender: str = Field(..., description="The sender of the email")
    subject: str = Field(..., description="The subject of the email")
    body: str = Field(..., description="The body of the email")

class GraphState(TypedDict):
    current_email: Email | str
    email_category: str
    email_response: Email | str
    messages: Annotated[list[AnyMessage], add_messages]
