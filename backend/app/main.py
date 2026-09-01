# -*- coding: utf-8 -*-
"""FastAPI 主入口"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db, SessionLocal
from .seed import seed_data
from .routers import auth, dashboard, students, groups, materials, assignments, chat, notifications, student

app = FastAPI(
    title="知行安信教学平台 API",
    description="知行安信教学平台后端服务",
    version="1.0.0",
)

# CORS：允许本地前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态资源目录（材料文件存放处）
import os
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 注册路由
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(students.router)
app.include_router(groups.router)
app.include_router(materials.router)
app.include_router(assignments.router)
app.include_router(chat.router)
app.include_router(notifications.router)
app.include_router(student.router)


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"service": "知行安信教学平台", "docs": "/docs", "status": "running"}
