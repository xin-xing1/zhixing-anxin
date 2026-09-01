# -*- coding: utf-8 -*-
"""学生端路由：注册 / 登录 / 个人信息 / 仪表盘 / 题目提交 / 材料 / 小组 / 通知 / AI助手"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import verify_password, get_password_hash, create_student_token, get_current_student
from .chat import ask_ai

router = APIRouter(prefix="/api/student", tags=["学生端"])

# 材料访问级别权重：A 可访问全部，B 可访问 B/C，C 仅可访问 C
_LEVEL_WEIGHT = {"C": 0, "B": 1, "A": 2}


def _material_visible(material_level: str, student_category: str) -> bool:
    return _LEVEL_WEIGHT.get(student_category, 0) >= _LEVEL_WEIGHT.get(material_level, 0)


def _student_visible_assignments(db: Session, student: models.Student):
    """返回面向该学生的题目列表（ALL 或匹配其类别）"""
    return db.query(models.Assignment).filter(
        (models.Assignment.target_category == "ALL") |
        (models.Assignment.target_category == student.category)
    ).order_by(models.Assignment.created_at.desc()).all()


# ---------- 学生注册 ----------
@router.post("/auth/register", response_model=schemas.StudentTokenResponse)
def student_register(data: schemas.StudentRegisterRequest, db: Session = Depends(get_db)):
    name = (data.name or "").strip()
    student_no = (data.student_no or "").strip()
    password = data.password or ""
    if not name or not student_no or not password:
        raise HTTPException(status_code=400, detail="姓名、学号、密码均为必填项")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于6位")
    dup = db.query(models.Student).filter(
        (models.Student.student_no == student_no) | (models.Student.username == student_no)
    ).first()
    if dup:
        raise HTTPException(status_code=400, detail="该学号已注册")
    student = models.Student(
        name=name,
        student_no=student_no,
        username=student_no,
        password_hash=get_password_hash(password),
        category="C",
        group_id=None,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    token = create_student_token(student.id)
    return schemas.StudentTokenResponse(access_token=token, student=student)


# ---------- 学生登录 ----------
@router.post("/auth/login", response_model=schemas.StudentTokenResponse)
def student_login(data: schemas.StudentLoginRequest, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(
        (models.Student.username == data.username) | (models.Student.student_no == data.username)
    ).first()
    if not student or not student.password_hash or not verify_password(data.password, student.password_hash):
        raise HTTPException(status_code=401, detail="学号或密码错误")
    token = create_student_token(student.id)
    return schemas.StudentTokenResponse(access_token=token, student=student)


# ---------- 个人信息 ----------
@router.get("/me", response_model=schemas.StudentMeOut)
def student_me(db: Session = Depends(get_db), student: models.Student = Depends(get_current_student)):
    group = None
    if student.group_id:
        g = db.query(models.Group).filter(models.Group.id == student.group_id).first()
        if g:
            member_count = db.query(models.Student).filter(models.Student.group_id == g.id).count()
            group = schemas.StudentGroupBrief(
                id=g.id, name=g.name, alias=g.alias, level=g.level, leader=g.leader,
                avg_score=g.avg_score, member_count=member_count, completion=g.completion,
            )
    return schemas.StudentMeOut(student=student, group=group)


# ---------- 学生仪表盘 ----------
@router.get("/dashboard", response_model=schemas.StudentDashboardOut)
def student_dashboard(db: Session = Depends(get_db), student: models.Student = Depends(get_current_student)):
    assignments = _student_visible_assignments(db, student)
    total = len(assignments)
    done = 0
    for a in assignments:
        sub = db.query(models.Submission).filter(
            models.Submission.assignment_id == a.id,
            models.Submission.student_id == student.id,
        ).first()
        if sub and sub.status != "pending":
            done += 1
    pending = max(0, total - done)
    material_count = db.query(models.Material).count()  # 前端按级别过滤展示
    unread = db.query(models.Notification).filter(models.Notification.is_read.is_(False)).count()
    return schemas.StudentDashboardOut(
        student=student,
        pending_count=pending,
        done_count=done,
        total_count=total,
        material_count=material_count,
        unread_notice_count=unread,
    )


# ---------- 我的题目与提交 ----------
@router.get("/assignments", response_model=list[schemas.StudentAssignmentOut])
def student_assignments(db: Session = Depends(get_db), student: models.Student = Depends(get_current_student)):
    result = []
    for a in _student_visible_assignments(db, student):
        sub = db.query(models.Submission).filter(
            models.Submission.assignment_id == a.id,
            models.Submission.student_id == student.id,
        ).first()
        result.append(schemas.StudentAssignmentOut(
            id=a.id,
            title=a.title,
            type=a.type,
            content=a.content,
            options=a.options,
            deadline=a.deadline,
            target_category=a.target_category,
            created_at=a.created_at,
            my_submission=sub.content if sub else None,
            my_score=sub.score if sub else None,
            my_status=sub.status if sub else "pending",
            submitted_at=sub.submitted_at if sub else None,
        ))
    return result


@router.post("/assignments/{assignment_id}/submit")
def student_submit(assignment_id: int, data: schemas.SubmissionIn, db: Session = Depends(get_db),
                   student: models.Student = Depends(get_current_student)):
    a = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="题目不存在")
    if a.target_category != "ALL" and a.target_category != student.category:
        raise HTTPException(status_code=403, detail="该题目不面向您的学生类别")
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="提交内容不能为空")
    sub = db.query(models.Submission).filter(
        models.Submission.assignment_id == assignment_id,
        models.Submission.student_id == student.id,
    ).first()
    if sub:
        sub.content = data.content
        sub.status = "submitted"
        sub.score = None
    else:
        sub = models.Submission(
            assignment_id=assignment_id,
            student_id=student.id,
            content=data.content,
            status="submitted",
        )
        db.add(sub)
    # 同步学生任务完成数
    if student.tasks_done < student.tasks_total:
        student.tasks_done = min(student.tasks_total, student.tasks_done + 1)
    db.commit()
    return {"message": "提交成功"}


# ---------- 我的材料 ----------
@router.get("/materials", response_model=list[schemas.StudentMaterialOut])
def student_materials(db: Session = Depends(get_db), student: models.Student = Depends(get_current_student)):
    materials = db.query(models.Material).order_by(models.Material.created_at.desc()).all()
    return [schemas.StudentMaterialOut(
        id=m.id, title=m.title, type=m.type, level_required=m.level_required,
        url=m.url, description=m.description, created_at=m.created_at,
    ) for m in materials if _material_visible(m.level_required, student.category)]


# ---------- 我的小组 ----------
@router.get("/group")
def student_group(db: Session = Depends(get_db), student: models.Student = Depends(get_current_student)):
    if not student.group_id:
        return {"group": None, "members": []}
    g = db.query(models.Group).filter(models.Group.id == student.group_id).first()
    if not g:
        return {"group": None, "members": []}
    members = db.query(models.Student).filter(models.Student.group_id == g.id).all()
    return {
        "group": schemas.StudentGroupBrief(
            id=g.id, name=g.name, alias=g.alias, level=g.level, leader=g.leader,
            avg_score=g.avg_score,
            member_count=len(members),
            completion=g.completion,
        ).model_dump(),
        "members": [schemas.StudentOut.model_validate(m).model_dump() for m in members],
    }


# ---------- 通知 ----------
@router.get("/notifications", response_model=list[schemas.NotificationOut])
def student_notifications(db: Session = Depends(get_db), _: models.Student = Depends(get_current_student)):
    return db.query(models.Notification).order_by(models.Notification.created_at.desc()).all()


@router.post("/notifications/read-all")
def student_notifications_read_all(db: Session = Depends(get_db), _: models.Student = Depends(get_current_student)):
    db.query(models.Notification).update({models.Notification.is_read: True})
    db.commit()
    return {"message": "已全部标记为已读"}


# ---------- 学生 AI 助手 ----------
@router.post("/chat")
def student_chat(data: schemas.ChatIn, db: Session = Depends(get_db), student: models.Student = Depends(get_current_student)):
    user_msg = models.ChatMessage(student_id=student.id, role="user", content=data.message)
    db.add(user_msg)
    db.commit()

    history = db.query(models.ChatMessage).filter(
        models.ChatMessage.student_id == student.id
    ).order_by(models.ChatMessage.created_at.desc()).limit(10).all()
    messages = [{"role": m.role, "content": m.content} for m in reversed(history)]

    reply = ask_ai(messages)

    assistant_msg = models.ChatMessage(student_id=student.id, role="assistant", content=reply)
    db.add(assistant_msg)
    db.commit()
    return {"reply": reply}


@router.get("/chat/history", response_model=list[schemas.ChatOut])
def student_chat_history(db: Session = Depends(get_db), student: models.Student = Depends(get_current_student)):
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.student_id == student.id
    ).order_by(models.ChatMessage.created_at.asc()).limit(100).all()
