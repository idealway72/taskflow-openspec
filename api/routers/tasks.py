from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from api.database import get_db
from api import models, schemas, auth

router = APIRouter(tags=["tasks"])


@router.get("/teams/{team_id}/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    team_id: int,
    filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.require_team_member(team_id, current_user)
    q = db.query(models.Task).filter(models.Task.team_id == team_id)
    if filter == "me":
        q = q.filter(models.Task.assignee_id == current_user.id)
    elif filter == "unassigned":
        q = q.filter(models.Task.assignee_id.is_(None))
    return q.order_by(models.Task.created_at.desc()).all()


@router.post("/teams/{team_id}/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(
    team_id: int,
    body: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    auth.require_team_member(team_id, current_user)
    task = models.Task(
        team_id=team_id,
        title=body.title,
        status="TODO",
        creator_id=current_user.id,
        assignee_id=body.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    auth.require_team_member(task.team_id, current_user)
    return task


@router.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    body: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    auth.require_team_member(task.team_id, current_user)
    if body.title is not None:
        task.title = body.title
    if "assignee_id" in body.model_fields_set:
        task.assignee_id = body.assignee_id
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/status", response_model=schemas.TaskOut)
def update_task_status(
    task_id: int,
    body: schemas.TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    auth.require_team_member(task.team_id, current_user)
    task.status = body.status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"}})
    auth.require_team_member(task.team_id, current_user)
    team = db.query(models.Team).filter(models.Team.id == task.team_id).first()
    if task.creator_id != current_user.id and team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail={"error": {"code": "FORBIDDEN", "message": "권한이 없습니다"}})
    db.delete(task)
    db.commit()
