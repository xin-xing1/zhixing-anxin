# -*- coding: utf-8 -*-
"""仪表盘路由：统计卡片 + 班级概况 + 小组排行榜"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    total_students = db.query(models.Student).count()
    a_count = db.query(models.Student).filter(models.Student.category == "A").count()
    b_count = db.query(models.Student).filter(models.Student.category == "B").count()
    c_count = db.query(models.Student).filter(models.Student.category == "C").count()

    unread = db.query(models.Notification).filter(models.Notification.is_read == False).count()  # noqa: E712
    avg_video = db.query(func.avg(models.Student.video_progress)).scalar() or 0
    not_submitted = db.query(models.Group).filter(models.Group.submitted == False).count()  # noqa: E712
    pending_submissions = db.query(models.Submission).filter(models.Submission.status == "pending").count()

    # 最近 7 天通知新增数（演示：按最新 5 条统计）
    recent_notices = db.query(models.Notification).order_by(models.Notification.created_at.desc()).limit(5).count()

    return {
        "total_students": total_students,
        "a_count": a_count,
        "b_count": b_count,
        "c_count": c_count,
        "unread_notices": unread,
        "new_notices": recent_notices,
        "avg_video_progress": round(avg_video, 1),
        "groups_not_submitted": not_submitted,
        "pending_submissions": pending_submissions,
    }


@router.get("/groups", response_model=list[schemas.GroupOut])
def group_ranking(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    groups = db.query(models.Group).order_by(models.Group.avg_score.desc()).all()
    result = []
    for g in groups:
        member_count = db.query(models.Student).filter(models.Student.group_id == g.id).count()
        result.append(schemas.GroupOut(
            id=g.id, name=g.name, alias=g.alias, level=g.level, leader=g.leader,
            avg_score=g.avg_score, member_count=member_count, completion=g.completion,
            submitted=g.submitted,
        ))
    return result


@router.get("/category-analysis")
def category_analysis(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    """三类学生的六维能力均值对比（用于特点分析图）"""
    dims = ["dim_motivation", "dim_habit", "dim_attitude", "dim_character", "dim_collaboration", "dim_stress"]
    labels = ["学习动力", "学习习惯", "学习态度", "性格能力", "团队协作", "抗压能力"]
    result = {}
    for cat in ["A", "B", "C"]:
        rows = db.query(models.Student).filter(models.Student.category == cat).all()
        if not rows:
            continue
        values = []
        for d in dims:
            avg = sum(getattr(r, d) for r in rows) / len(rows)
            values.append(round(avg, 1))
        result[cat] = values
    return {"labels": labels, "data": result}
