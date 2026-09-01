# -*- coding: utf-8 -*-
"""SQLAlchemy 数据模型定义"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """系统用户（教师/管理员）"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    name = Column(String(64), nullable=False)          # 真实姓名，如 王霞
    role = Column(String(32), default="teacher")        # teacher / admin
    avatar = Column(String(256), default="")
    created_at = Column(DateTime, default=datetime.now)


class Student(Base):
    """学生信息"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    student_no = Column(String(32), unique=True, index=True)   # 学号
    username = Column(String(64), unique=True, index=True, nullable=True)  # 学生登录账号
    password_hash = Column(String(256), default="")            # 学生登录密码哈希
    category = Column(String(8), nullable=False)               # A / B / C
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    # 六大维度学情评分（0-100），对应前端雷达图
    dim_motivation = Column(Float, default=0)     # 学习动力
    dim_habit = Column(Float, default=0)          # 学习习惯
    dim_attitude = Column(Float, default=0)       # 学习态度
    dim_character = Column(Float, default=0)      # 性格能力
    dim_collaboration = Column(Float, default=0)  # 团队协作
    dim_stress = Column(Float, default=0)         # 抗压能力
    video_progress = Column(Float, default=0)     # 视频学习进度 %
    tasks_done = Column(Integer, default=0)       # 已完成任务数
    tasks_total = Column(Integer, default=0)      # 总任务数
    created_at = Column(DateTime, default=datetime.now)

    group = relationship("Group", back_populates="students")


class Group(Base):
    """小组"""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)          # 第一组
    alias = Column(String(64), default="")             # 绿色先锋组
    level = Column(String(8), default="B")             # A / B / C 等级
    leader = Column(String(64), default="")            # 组长
    avg_score = Column(Float, default=0)               # 平均分
    completion = Column(Float, default=0)              # 完成度 %
    submitted = Column(Boolean, default=False)         # 是否已提交
    created_at = Column(DateTime, default=datetime.now)

    students = relationship("Student", back_populates="group")
    ratings = relationship("GroupRating", back_populates="group")


class Material(Base):
    """课业材料（按学生类别分级授权）"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    type = Column(String(32), nullable=False)          # video / lab / paper / case
    level_required = Column(String(8), default="C")    # A / B / C 最低访问级别
    url = Column(String(256), default="")              # 资源地址或文件名
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)


class Assignment(Base):
    """教师布置的题目"""
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    type = Column(String(32), nullable=False)          # video / knowledge
    content = Column(Text, default="")                 # 题目内容
    options = Column(Text, default="")                 # JSON 选项（选择题）
    answer = Column(Text, default="")                  # 参考答案（可空）
    deadline = Column(String(32), default="")          # 截止时间
    target_category = Column(String(8), default="ALL") # 面向学生类别 A/B/C/ALL
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)


class Submission(Base):
    """学生题目提交记录"""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    content = Column(Text, default="")
    score = Column(Float, nullable=True)
    status = Column(String(16), default="pending")     # pending / submitted / graded
    submitted_at = Column(DateTime, default=datetime.now)


class GroupRating(Base):
    """小组星级评分与评语"""
    __tablename__ = "group_ratings"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stars = Column(Integer, default=5)                 # 1-5 星
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)

    group = relationship("Group", back_populates="ratings")


class ChatMessage(Base):
    """AI 助手对话记录"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)      # 教师提问时为 users.id
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)  # 学生提问时为 students.id
    role = Column(String(16), nullable=False)          # user / assistant
    content = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)


class Notification(Base):
    """系统通知"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    content = Column(Text, default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
