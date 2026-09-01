# -*- coding: utf-8 -*-
"""通知路由：列表 / 标记已读 / 新增"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("", response_model=list[schemas.NotificationOut])
def list_notifications(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Notification).order_by(models.Notification.created_at.desc()).all()


@router.post("/{notice_id}/read")
def mark_read(notice_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    notice = db.query(models.Notification).filter(models.Notification.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    notice.is_read = True
    db.commit()
    return {"message": "已标记为已读"}


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    db.query(models.Notification).update({models.Notification.is_read: True})
    db.commit()
    return {"message": "全部已读"}
