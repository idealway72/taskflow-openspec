from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from api.database import get_db
from api import models, schemas, auth

router = APIRouter(tags=["messages"])


@router.get("/teams/{team_id}/messages")
def list_messages(
    team_id: int,
    since: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.require_team_member(team_id, current_user)
    q = db.query(models.Message).filter(models.Message.team_id == team_id)
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00")).replace(tzinfo=None)
            q = q.filter(models.Message.created_at > since_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail={"error": {"code": "VALIDATION_ERROR", "message": "since 파라미터 형식이 올바르지 않습니다"}})
    else:
        q = q.order_by(models.Message.created_at.desc()).limit(50)
        messages = q.all()
        messages.reverse()
        return [_msg_out(m) for m in messages]
    return [_msg_out(m) for m in q.order_by(models.Message.created_at.asc()).all()]


@router.post("/teams/{team_id}/messages", status_code=201)
def send_message(
    team_id: int,
    body: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.require_team_member(team_id, current_user)
    if len(body.content) > 1000:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "TOO_LONG", "message": "메시지는 1000자 이내로 입력하세요", "limit": 1000, "actual": len(body.content)}},
        )
    msg = models.Message(team_id=team_id, user_id=current_user.id, content=body.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _msg_out(msg)


@router.delete("/messages/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    if msg.user_id != current_user.id:
        raise HTTPException(status_code=403, detail={"error": {"code": "NOT_OWNER", "message": "본인의 메시지만 삭제할 수 있습니다"}})
    db.delete(msg)
    db.commit()


def _msg_out(m: models.Message) -> dict:
    return {
        "id": m.id,
        "user_id": m.user_id,
        "user_email": m.user.email,
        "content": m.content,
        "created_at": m.created_at.isoformat() + "Z",
    }
