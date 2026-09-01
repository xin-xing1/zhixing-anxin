# -*- coding: utf-8 -*-
"""后端初始化自检脚本"""
import traceback
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import init_db, SessionLocal
    from app.seed import seed_data
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    print("数据库初始化成功")

    # 验证数据
    from app.database import SessionLocal as SL
    from app import models
    db2 = SL()
    print("用户数:", db2.query(models.User).count())
    print("学生数:", db2.query(models.Student).count())
    print("小组数:", db2.query(models.Group).count())
    print("材料数:", db2.query(models.Material).count())
    print("题目数:", db2.query(models.Assignment).count())
    db2.close()
    print("数据校验通过")
except Exception:
    traceback.print_exc()
    sys.exit(1)
