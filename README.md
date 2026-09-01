# 知行安信教学平台

基于零信任架构的机场智能终端安全服务教学平台

安全工程专业 · 零信任轻量级DDoS防护教学环境

## 功能

- 教师端：仪表盘、学生管理、学生情况、课业材料、布置题目、分组管理、AI 助教
- 学生端：登录注册、我的仪表盘、作业提交、材料查看、通知、AI 答疑
- 身份体系：JWT 双身份令牌（教师/学生）

## 架构

前端：单文件 `前端.html`（HTML + CSS + JS）

后端：FastAPI + SQLite + SQLAlchemy

## 本地运行

```bash
cd backend
pip install -r requirements.txt
mkdir -p static
cp ../前端.html static/
cp ../static/* static/ 2>/dev/null || true
python run.py
```

访问 http://127.0.0.1:8000/static/前端.html

## 部署

前端 → GitHub Pages  
后端 → PythonAnywhere / Render / Railway

## 技术栈

FastAPI · SQLite · SQLAlchemy · JWT · bcrypt · Python 3.11
