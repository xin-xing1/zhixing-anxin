# -*- coding: utf-8 -*-
"""AI 助手路由：对话 + 历史记录（预留 DeepSeek API，无 Key 时本地智能回复）"""
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["AI助手"])

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-chat"

# 本地知识库（教学平台相关问答）
LOCAL_KB = [
    ("登录", "教师账号为 wangxia，初始密码 123456，可在登录后修改密码。"),
    ("学生分类", "平台将学生分为 A、B、C 三类：A 类 18 人、B 类 22 人、C 类 10 人，按学习动力、习惯、态度等维度评估。"),
    ("材料权限", "课业材料按级别开放：A 类学生可访问全部材料；B 类可访问基础视频、进阶实验和实践案例；C 类仅可访问基础视频与实践案例。"),
    ("小组", "当前共有 5 个小组，排行榜按平均分排序，可对小组进行 1-5 星评分并填写评语。"),
    ("布置题目", "教师可以发布视频学习题目和知识点题目，可指定面向的学生类别与截止时间。"),
    ("雷达图", "学生情况查看页面支持点击学生姓名，查看六大维度学情雷达图。"),
    ("密码", "默认账号密码：教师 wangxia / 123456；学生账号默认为学号，初始密码 123456。"),
    ("平台", "知行安信教学平台面向安全工程专业教学管理，包含学生管理、课业管理、小组管理与 AI 助手功能。"),
]


def _local_reply(message: str) -> str:
    for keyword, answer in LOCAL_KB:
        if keyword in message:
            return answer
    return ("我是知行安信教学平台的 AI 助教。您可以问我关于学生分类、材料权限、小组管理、题目布置、"
            "雷达图查看等问题。如需更深度的回答，可在后端配置 DEEPSEEK_API_KEY 接入 DeepSeek 大模型。")


def ask_ai(messages: list[dict]) -> str:
    """调用 DeepSeek API，失败时回退本地知识库"""
    if DEEPSEEK_API_KEY:
        try:
            resp = httpx.post(
                DEEPSEEK_BASE_URL,
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                json={"model": MODEL_NAME, "messages": messages, "temperature": 0.7},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    return _local_reply(last_user)


@router.post("")
def chat(data: schemas.ChatIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 保存用户消息
    user_msg = models.ChatMessage(user_id=current_user.id, role="user", content=data.message)
    db.add(user_msg)
    db.commit()

    # 取最近对话上下文（教师）
    history = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.created_at.desc()).limit(10).all()
    messages = [{"role": m.role, "content": m.content} for m in reversed(history)]

    reply = ask_ai(messages)

    assistant_msg = models.ChatMessage(user_id=current_user.id, role="assistant", content=reply)
    db.add(assistant_msg)
    db.commit()
    return {"reply": reply}


@router.get("/history", response_model=list[schemas.ChatOut])
def chat_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.created_at.asc()).limit(100).all()
