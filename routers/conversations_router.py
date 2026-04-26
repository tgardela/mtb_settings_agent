from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any

from database import get_db
from models import Conversation, User
from routers.auth_router import get_current_user

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationCreate(BaseModel):
    messages: List[Any]


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    messages: Optional[List[Any]] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[ConversationResponse])
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Conversation).filter(Conversation.user_id == current_user.id).all()


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(request: ConversationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = Conversation(user_id=current_user.id, messages=request.messages)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
