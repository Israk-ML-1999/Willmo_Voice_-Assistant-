from fastapi import APIRouter, HTTPException
from app.micro_goals.llm_service import Micro_goal
from app.micro_goals.request import micro_goal_response, micro_goal_request

router = APIRouter()
micro_goal= Micro_goal()     

@router.post("/micro_goal", response_model=micro_goal_response)
async def create_daily_plan(request: micro_goal_request):
    try:
        response = micro_goal.create_daily_plan(request.dict())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
