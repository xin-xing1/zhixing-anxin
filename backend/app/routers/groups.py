# -*- coding: utf-8 -*-
"""小组管理路由：列表 / 成员 / 创建 / 更新 / 删除 / 评分"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/groups", tags=["小组管理"])


def _to_group_out(g: models.Group, db: Session) -> schemas.GroupOut:
    member_count = db.query(models.Student).filter(models.Student.group_id == g.id).count()
    return schemas.GroupOut(
        id=g.id, name=g.name, alias=g.alias, level=g.level, leader=g.leader,
        avg_score=g.avg_score, member_count=member_count, completion=g.completion,
        submitted=g.submitted,
    )


@router.get("", response_model=list[schemas.GroupOut])
def list_groups(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    groups = db.query(models.Group).order_by(models.Group.avg_score.desc()).all()
    return [_to_group_out(g, db) for g in groups]


@router.post("", response_model=schemas.GroupOut)
def create_group(data: schemas.GroupCreate, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    if not data.name:
        raise HTTPException(status_code=400, detail="小组名称必填")
    g = models.Group(
        name=data.name,
        alias=data.alias or "",
        level=data.level or "B",
        leader=data.leader or "",
        completion=data.completion or 0,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return _to_group_out(g, db)


@router.get("/{group_id}", response_model=schemas.GroupOut)
def get_group(group_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="小组不存在")
    return _to_group_out(g, db)


@router.put("/{group_id}", response_model=schemas.GroupOut)
def update_group(group_id: int, data: schemas.GroupUpdate, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="小组不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(g, field, value)
    db.commit()
    db.refresh(g)
    return _to_group_out(g, db)


@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="小组不存在")
    members = db.query(models.Student).filter(models.Student.group_id == group_id).count()
    if members > 0:
        raise HTTPException(status_code=400, detail=f"小组仍有 {members} 名成员，请先移出全部成员后再删除")
    db.delete(g)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{group_id}/members")
def add_members(group_id: int, data: schemas.GroupMembersIn, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="小组不存在")
    added = 0
    for sid in data.student_ids:
        stu = db.query(models.Student).filter(models.Student.id == sid).first()
        if stu:
            stu.group_id = group_id
            added += 1
    db.commit()
    return {"message": f"已加入 {added} 名学生"}


@router.delete("/{group_id}/members/{student_id}")
def remove_member(group_id: int, student_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    stu = db.query(models.Student).filter(
        models.Student.id == student_id, models.Student.group_id == group_id).first()
    if not stu:
        raise HTTPException(status_code=404, detail="该学生不在本小组")
    stu.group_id = None
    db.commit()
    return {"message": "已移出小组"}


@router.get("/{group_id}/members", response_model=list[schemas.StudentOut])
def group_members(group_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Student).filter(models.Student.group_id == group_id).all()


@router.get("/{group_id}/ratings", response_model=list[schemas.GroupRatingOut])
def list_ratings(group_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.GroupRating).filter(models.GroupRating.group_id == group_id).order_by(
        models.GroupRating.created_at.desc()).all()


@router.post("/{group_id}/ratings", response_model=schemas.GroupRatingOut)
def submit_rating(
    group_id: int,
    data: schemas.GroupRatingIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="小组不存在")
    if not 1 <= data.stars <= 5:
        raise HTTPException(status_code=400, detail="星级须为 1-5")
    rating = models.GroupRating(group_id=group_id, teacher_id=current_user.id, stars=data.stars, comment=data.comment)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating
