from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..utils.security import get_current_user
from ..services.ai_service import stream_ai_assistant
from ..schemas.ai_profile import AssistantRequest

router = APIRouter()

@router.post("/assistant")
def ai_assistant(req: AssistantRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # StreamingResponse sends text chunks to the frontend as they arrive
    # This makes the response feel instant instead of waiting for the full reply
    return StreamingResponse(
        stream_ai_assistant(req.question, current_user.id, db),
        media_type="text/plain"
    )
