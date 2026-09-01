# -*- coding: utf-8 -*-
"""题目发布与提交路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/assignments", tags=["题目管理"])


@router.get("", response_model=list[schemas.AssignmentOut])
def list_assignments(
    type: str | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Assignment)
    if type:
        q = q.filter(models.Assignment.type == type)
    return q.order_by(models.Assignment.created_at.desc()).all()


@router.post("", response_model=schemas.AssignmentOut)
def create_assignment(
    data: schemas.AssignmentIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    assignment = models.Assignment(
        title=data.title, type=data.type, content=data.content, options=data.options,
        answer=data.answer, deadline=data.deadline, target_category=data.target_category,
        created_by=current_user.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(assignment)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{assignment_id}/submissions")
def submit_assignment(
    assignment_id: int,
    data: schemas.SubmissionIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="题目不存在")
    student = db.query(models.Student).filter(models.Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    submission = models.Submission(assignment_id=assignment_id, student_id=data.student_id, content=data.content)
    db.add(submission)
    db.commit()
    return {"message": "提交成功", "submission_id": submission.id}


@router.get("/{assignment_id}/submissions")
def list_submissions(assignment_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    submissions = db.query(models.Submission).filter(models.Submission.assignment_id == assignment_id).all()
    result = []
    for s in submissions:
        student = db.query(models.Student).filter(models.Student.id == s.student_id).first()
        result.append({
            "id": s.id, "student_id": s.student_id, "student_name": student.name if student else "未知",
            "content": s.content, "status": s.status, "score": s.score,
            "submitted_at": s.submitted_at.strftime("%Y-%m-%d %H:%M") if s.submitted_at else "",
        })
    return result
