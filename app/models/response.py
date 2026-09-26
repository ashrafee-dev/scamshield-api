from pydantic import BaseModel, Field
from typing import Literal

class riskAssessment(BaseModel):
    label : Literal["Scam" , "Scam Likely" , "Safe"]
    score : Literal["High" , "Low" , "Medium"]
    certainty: int = Field(ge=0, le=100)
    reason: str = Field(min_length=1, max_length=2000)
