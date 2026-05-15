import random
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api import models, schemas, auth

router = APIRouter(prefix="/teams", tags=["teams"])


def _generate_invite_code(db: Session) -> str:
    while True:
        code = (
            "".join(random.choices(string.ascii_uppercase, k=4))
            + "-"
            + "".join(random.choices(string.digits, k=4))
        )
        if not db.query(models.Team).filter(models.Team.invite_code == code).first():
            return code


@router.post("", response_model=schemas.TeamOut, status_code=201)
def create_team(
    body: schemas.TeamCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    invite_code = _generate_invite_code(db)
    team = models.Team(name=body.name, invite_code=invite_code, owner_id=current_user.id)
    db.add(team)
    db.flush()
    current_user.team_id = team.id
    db.commit()
    db.refresh(team)
    return team


@router.post("/join")
def join_team(
    body: schemas.TeamJoin,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.team_id is not None:
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "ALREADY_IN_TEAM", "message": "이미 다른 팀에 소속되어 있습니다"}},
        )
    team = db.query(models.Team).filter(models.Team.invite_code == body.invite_code).first()
    if not team:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "해당 초대코드를 찾을 수 없습니다"}},
        )
    current_user.team_id = team.id
    db.commit()
    db.refresh(team)
    member_count = db.query(models.User).filter(models.User.team_id == team.id).count()
    return {"team": {"id": team.id, "name": team.name, "member_count": member_count}, "redirect": f"/teams/{team.id}"}


@router.get("/{team_id}", response_model=schemas.TeamOut)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.require_team_member(team_id, current_user)
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    return team


@router.get("/{team_id}/members")
def get_members(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.require_team_member(team_id, current_user)
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    members = db.query(models.User).filter(models.User.team_id == team_id).all()
    return [
        {"id": m.id, "email": m.email, "is_owner": m.id == team.owner_id, "joined_at": m.created_at}
        for m in members
    ]


@router.delete("/{team_id}/leave")
def leave_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.require_team_member(team_id, current_user)
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    if team.owner_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "OWNER_CANNOT_LEAVE", "message": "팀 owner는 팀을 떠날 수 없습니다"}},
        )
    current_user.team_id = None
    db.commit()
    return {}
