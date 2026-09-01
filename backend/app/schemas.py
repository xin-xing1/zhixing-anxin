# -*- coding: utf-8 -*-
"""Pydantic 请求/响应模型"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------- 认证 ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    name: str
    role: str
    avatar: str = ""

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- 学生 ----------
class StudentOut(BaseModel):
    id: int
    name: str
    student_no: str = ""
    username: str = ""
    category: str
    group_id: Optional[int] = None
    dim_motivation: float = 0
    dim_habit: float = 0
    dim_attitude: float = 0
    dim_character: float = 0
    dim_collaboration: float = 0
    dim_stress: float = 0
    video_progress: float = 0
    tasks_done: int = 0
    tasks_total: int = 0

    class Config:
        from_attributes = True


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    student_no: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    category: Optional[str] = None
    group_id: Optional[int] = None
    dim_motivation: Optional[float] = None
    dim_habit: Optional[float] = None
    dim_attitude: Optional[float] = None
    dim_character: Optional[float] = None
    dim_collaboration: Optional[float] = None
    dim_stress: Optional[float] = None
    video_progress: Optional[float] = None
    tasks_done: Optional[int] = None
    tasks_total: Optional[int] = None


# ---------- 学生端 ----------
class StudentLoginRequest(BaseModel):
    username: str
    password: str


class StudentRegisterRequest(BaseModel):
    name: str
    student_no: str
    password: str


class StudentTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student: StudentOut


class StudentGroupBrief(BaseModel):
    id: int
    name: str
    alias: str = ""
    level: str = "B"
    leader: str = ""
    avg_score: float = 0
    member_count: int = 0
    completion: float = 0


class StudentMeOut(BaseModel):
    student: StudentOut
    group: Optional[StudentGroupBrief] = None


class StudentAssignmentOut(BaseModel):
    id: int
    title: str
    type: str
    content: str = ""
    options: str = ""
    deadline: str = ""
    target_category: str = "ALL"
    created_at: datetime
    my_submission: Optional[str] = None
    my_score: Optional[float] = None
    my_status: str = "pending"
    submitted_at: Optional[datetime] = None


class StudentMaterialOut(BaseModel):
    id: int
    title: str
    type: str
    level_required: str
    url: str = ""
    description: str = ""
    created_at: datetime


class StudentDashboardOut(BaseModel):
    student: StudentOut
    pending_count: int = 0
    done_count: int = 0
    total_count: int = 0
    material_count: int = 0
    unread_notice_count: int = 0


# ---------- 小组 ----------
class GroupOut(BaseModel):
    id: int
    name: str
    alias: str = ""
    level: str = "B"
    leader: str = ""
    avg_score: float = 0
    member_count: int = 0
    completion: float = 0
    submitted: bool = False

    class Config:
        from_attributes = True


class GroupRatingIn(BaseModel):
    stars: int = 5
    comment: str = ""


class GroupRatingOut(BaseModel):
    id: int
    group_id: int
    stars: int
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str
    alias: str = ""
    level: str = "B"
    leader: str = ""
    completion: float = 0


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    level: Optional[str] = None
    leader: Optional[str] = None
    completion: Optional[float] = None


class GroupMembersIn(BaseModel):
    student_ids: list[int]


# ---------- 材料 ----------
class MaterialOut(BaseModel):
    id: int
    title: str
    type: str
    level_required: str
    url: str = ""
    description: str = ""
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- 题目 ----------
class AssignmentIn(BaseModel):
    title: str
    type: str
    content: str = ""
    options: str = ""
    answer: str = ""
    deadline: str = ""
    target_category: str = "ALL"


class AssignmentOut(BaseModel):
    id: int
    title: str
    type: str
    content: str = ""
    options: str = ""
    answer: str = ""
    deadline: str = ""
    target_category: str = "ALL"
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionIn(BaseModel):
    student_id: Optional[int] = None
    content: str = ""


# ---------- AI 对话 ----------
class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- 通知 ----------
class NotificationOut(BaseModel):
    id: int
    title: str
    content: str = ""
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
