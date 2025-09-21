from pydantic import BaseModel,Field
from typing import Optional,List, Any, Dict


class micro_goal_request(BaseModel):
    big_goal: str 
    age: int 
    userdata: str
    tasks: Optional[List[Dict[Any,Any]]] = None

class DayPlan(BaseModel):
    category: str
    title: str
    goal: str

class micro_goal_response(BaseModel):
    big_goal: str
    day_plan: List[DayPlan]
