from pydantic import BaseModel, Field
from enum import Enum

class EmailCategory(str, Enum):
    product_enquiry = "product_enquiry"
    customer_complaint = "customer_complaint"
    customer_feedback = "customer_feedback"
    unrelated = "unrelated"

class CategorizerEmailOutput(BaseModel):
    category: EmailCategory = Field(..., description="The determined category of the email.")
    account_id: str = Field(None, description="Extracted account ID if present in the email.")
    product: str = Field(None, description="Extracted product name if mentioned in the email.")
    urgency: str = Field(None, description="Extracted urgency level if indicated in the email.")

