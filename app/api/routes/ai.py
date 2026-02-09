from fastapi import APIRouter, Depends

from app.core.deps import require_premium
from app.schemas.ai import AIRequest, AIResponse
from app.services import ai as ai_service

router = APIRouter()


@router.post("/chat", response_model=AIResponse)
def chat(payload: AIRequest, current_user=Depends(require_premium)):
    reply = ai_service.chat([msg.model_dump() for msg in payload.messages])
    return AIResponse(reply=reply)
