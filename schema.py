import operator
from typing import Annotated, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class engine(TypedDict):
    uid:int
    interested_subjects:str
    response:Annotated[list[BaseMessage], operator.add] 
    no_of_questions:int
    evaluation_of_user:list[dict]
    
class evaluation(BaseModel):
    option_selected:str = Field(description="The option chosen by student (A, B, C, or D)")
    learning_preference:str = Field(description="Visual, Hands-on Code, Deep Theory, or Quick Summary")
    insights:str = Field(description="Additional insights about the student's learning style and preferences")
    