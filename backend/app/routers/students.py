# -*- coding: utf-8 -*-
"""学生管理路由：列表 / 分类 / 详情 / 新增 / 修改 / 删除 / 注册"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user, get_password_hash

router = APIRouter(prefix="/api/students", tags=["学生管理"])


@router.get("", response_model=list[schemas.StudentOut])
def list_students(
    category: str | None = Query(default=None),
    group_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Student)
    if category:
        q = q.filter(models.Student.category == category)
    if group_id:
        q = q.filter(models.Student.group_id == group_id)
    if keyword:
        q = q.filter(models.Student.name.like(f"%{keyword}%"))
    return q.order_by(models.Student.category, models.Student.id).all()


@router.get("/categories")
def category_counts(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    """A/B/C 类学生人数与占比"""
    total = db.query(models.Student).count()
    result = []
    for cat in ["A", "B", "C"]:
        cnt = db.query(models.Student).filter(models.Student.category == cat).count()
        result.append({"category": cat, "count": cnt, "ratio": round(cnt / total * 100, 1) if total else 0})
    return result


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student


@router.post("", response_model=schemas.StudentOut)
def create_student(data: schemas.StudentUpdate, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    if not data.name:
        raise HTTPException(status_code=400, detail="姓名必填")
    # 生成学生登录账号：优先使用传入 username，未传则用学号，再未传则自动生成
    student_no = data.student_no or f"2023X{db.query(models.Student).count() + 1:03d}"
    username = data.username or student_no
    if db.query(models.Student).filter(models.Student.username == username).first():
        raise HTTPException(status_code=400, detail=f"登录账号 {username} 已存在")
    password = data.password or "123456"
    student = models.Student(
        name=data.name,
        student_no=student_no,
        username=username,
        password_hash=get_password_hash(password),
        category=data.category or "C",
        group_id=data.group_id,
        dim_motivation=data.dim_motivation or 0,
        dim_habit=data.dim_habit or 0,
        dim_attitude=data.dim_attitude or 0,
        dim_character=data.dim_character or 0,
        dim_collaboration=data.dim_collaboration or 0,
        dim_stress=data.dim_stress or 0,
        video_progress=data.video_progress or 0,
        tasks_done=data.tasks_done or 0,
        tasks_total=data.tasks_total or 0,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, data: schemas.StudentUpdate, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    payload = data.model_dump(exclude_unset=True)
    if "password" in payload and payload["password"]:
        payload["password_hash"] = get_password_hash(payload.pop("password"))
    elif "password" in payload:
        payload.pop("password")
    for field, value in payload.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(student)
    db.commit()
    return {"message": "删除成功"}
