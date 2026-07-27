from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import ChatRequest, ChatResponse, UserInfo
from app.services.agent_service import AgentService
from app.services.analytics_service import AnalyticsService
from app.services.monday_service import get_monday_service
from app.utils.security import get_current_user
from app.database import get_db

router = APIRouter(prefix="/agent", tags=["agent"])
analytics_service = AnalyticsService()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user: UserInfo = Depends(get_current_user), db: Session = Depends(get_db)):
    monday_svc = get_monday_service()
    agent_service = AgentService(analytics_service, monday_svc)
    return await agent_service.chat(req.message, req.history, db)
