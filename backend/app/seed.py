# -*- coding: utf-8 -*-
"""种子数据：初始化教师账号、学生、小组、材料、题目、通知"""
from sqlalchemy.orm import Session
from . import models
from .auth import get_password_hash


def seed_data(db: Session):
    # ---------- 教师账号 ----------
    if db.query(models.User).count() == 0:
        db.add(models.User(
            username="wangxia",
            password_hash=get_password_hash("123456"),
            name="王霞",
            role="teacher",
        ))

    # ---------- 小组 ----------
    groups = [
        {"name": "第一组", "alias": "绿色先锋组", "level": "A", "leader": "张三", "avg_score": 92.5, "completion": 95, "submitted": True},
        {"name": "第二组", "alias": "环保卫士组", "level": "B", "leader": "李四", "avg_score": 88.3, "completion": 88, "submitted": True},
        {"name": "第三组", "alias": "生态守护组", "level": "C", "leader": "王五", "avg_score": 85.7, "completion": 82, "submitted": True},
        {"name": "第四组", "alias": "蓝天护卫队", "level": "B", "leader": "赵六", "avg_score": 83.2, "completion": 79, "submitted": False},
        {"name": "第五组", "alias": "碧水先锋队", "level": "C", "leader": "钱七", "avg_score": 78.9, "completion": 75, "submitted": False},
    ]
    if db.query(models.Group).count() == 0:
        for g in groups:
            db.add(models.Group(**g))

    db.flush()

    # ---------- 学生（50 人：A 18 / B 22 / C 10） ----------
    if db.query(models.Student).count() == 0:
        # A 类学生 18 人
        a_students = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
                      "郑一", "冯二", "陈三", "褚四", "卫五", "蒋六", "沈七", "韩八", "杨九", "朱十"]
        # B 类学生 22 人
        b_students = ["秦一", "尤二", "许三", "何四", "吕五", "施六", "张七", "孔八",
                      "曹九", "严十", "华一", "金二", "魏三", "陶四", "姜五", "戚六",
                      "谢七", "邹八", "喻九", "柏十", "水一", "窦二"]
        # C 类学生 10 人
        c_students = ["章三", "云四", "苏五", "潘六", "葛七", "奚八", "范九", "彭十", "郎一", "鲁二"]

        _seq = {"A": 0, "B": 0, "C": 0}

        def _add_student(name, category, group_index, base):
            _seq[category] += 1
            student_no = f"2023{category}{_seq[category]:03d}"
            db.add(models.Student(
                name=name,
                student_no=student_no,
                username=student_no,                       # 学生登录账号 = 学号
                password_hash=get_password_hash("123456"),  # 初始密码 123456
                category=category,
                group_id=group_index,
                dim_motivation=max(30, min(98, base["motivation"] + (len(name) * 2 % 11 - 5))),
                dim_habit=max(30, min(98, base["habit"] + (len(name) * 3 % 9 - 4))),
                dim_attitude=max(30, min(98, base["attitude"] + (len(name) % 7 - 3))),
                dim_character=max(30, min(98, base["character"] + (len(name) * 5 % 13 - 6))),
                dim_collaboration=max(30, min(98, base["collaboration"] + (len(name) * 2 % 9 - 4))),
                dim_stress=max(30, min(98, base["stress"] + (len(name) * 4 % 11 - 5))),
                video_progress=max(30, min(100, base["video"] + (len(name) * 3 % 15 - 7))),
                tasks_done=base["tasks_done"],
                tasks_total=10,
            ))

        bases = {
            "A": {"motivation": 88, "habit": 82, "attitude": 90, "character": 85, "collaboration": 70, "stress": 65, "video": 90, "tasks_done": 9},
            "B": {"motivation": 72, "habit": 68, "attitude": 78, "character": 75, "collaboration": 60, "stress": 58, "video": 70, "tasks_done": 7},
            "C": {"motivation": 55, "habit": 50, "attitude": 62, "character": 60, "collaboration": 48, "stress": 45, "video": 50, "tasks_done": 5},
        }
        for i, name in enumerate(a_students):
            _add_student(name, "A", (i % 5) + 1, bases["A"])
        for i, name in enumerate(b_students):
            _add_student(name, "B", (i % 5) + 1, bases["B"])
        for i, name in enumerate(c_students):
            _add_student(name, "C", (i % 5) + 1, bases["C"])

    # ---------- 课业材料 ----------
    if db.query(models.Material).count() == 0:
        materials = [
            {"title": "安全工程导论（基础课程视频）", "type": "video", "level_required": "C", "url": "/materials/videos/anquan-gongcheng-daolun.mp4", "description": "安全工程专业入门导论课程，涵盖安全科学基本原理与发展历程。"},
            {"title": "水污染控制技术（基础课程视频）", "type": "video", "level_required": "C", "url": "/materials/videos/shuiwuran-kongzhi.mp4", "description": "水污染控制核心技术与工程案例讲解。"},
            {"title": "大气污染治理（基础课程视频）", "type": "video", "level_required": "C", "url": "/materials/videos/daqiwuran-zhili.mp4", "description": "大气污染物治理工艺与技术路线。"},
            {"title": "固体废物处理（基础课程视频）", "type": "video", "level_required": "C", "url": "/materials/videos/guti-feiwu-chuli.mp4", "description": "固体废物资源化处理与处置技术。"},
            {"title": "进阶实验指导：安全监测实验", "type": "lab", "level_required": "B", "url": "/materials/labs/anquan-jiance-lab.pdf", "description": "面向 B 类及以上学生的进阶实验指导书。"},
            {"title": "进阶实验指导：安全影响评价", "type": "lab", "level_required": "B", "url": "/materials/labs/yingxiang-pingjia-lab.pdf", "description": "环境影响评价方法与实操训练。"},
            {"title": "拔高研究论文：安全工程前沿", "type": "paper", "level_required": "A", "url": "/materials/papers/qianyan-paper.pdf", "description": "安全工程领域前沿研究论文合集，仅对 A 类学生开放。"},
            {"title": "拔高研究论文：零信任安全架构", "type": "paper", "level_required": "A", "url": "/materials/papers/zero-trust-paper.pdf", "description": "零信任安全架构在工业控制领域的应用研究。"},
            {"title": "实践项目案例：校园安全巡检", "type": "case", "level_required": "C", "url": "/materials/cases/xiaoyuan-xunjian.zip", "description": "校园安全巡检实践项目案例包，供各层次学生参考。"},
            {"title": "实践项目案例：应急演练方案", "type": "case", "level_required": "C", "url": "/materials/cases/yingji-yanlian.zip", "description": "突发事件应急演练完整方案与评估模板。"},
        ]
        for m in materials:
            db.add(models.Material(**m))

    # ---------- 题目 ----------
    if db.query(models.Assignment).count() == 0:
        assignments = [
            {"title": "视频学习题目：安全工程导论观后感", "type": "video", "content": "观看《安全工程导论》视频后，结合课程内容谈谈你对安全工程专业定位的理解（不少于300字）。", "answer": "", "deadline": "2026-09-15 23:59", "target_category": "ALL"},
            {"title": "知识点题目：安全监测技术要点", "type": "knowledge", "content": "简述安全监测技术的主要方法，并说明其在环境风险预警中的作用。", "answer": "", "deadline": "2026-09-18 23:59", "target_category": "ALL"},
            {"title": "视频学习题目：水污染控制技术应用", "type": "video", "content": "结合《水污染控制技术》视频，分析某工业园区废水处理工艺的优缺点。", "answer": "", "deadline": "2026-09-22 23:59", "target_category": "B"},
            {"title": "知识点题目：安全影响评价流程", "type": "knowledge", "content": "请画出安全影响评价的完整流程图，并解释各环节的关键控制点。", "answer": "", "deadline": "2026-09-25 23:59", "target_category": "A"},
        ]
        teacher = db.query(models.User).filter(models.User.username == "wangxia").first()
        for a in assignments:
            db.add(models.Assignment(**a, created_by=teacher.id if teacher else 1))

    # ---------- 通知 ----------
    if db.query(models.Notification).count() == 0:
        notifications = [
            {"title": "新通知：9月课程安排已发布", "content": "本月课程安排已更新，请同学们及时查看课业情况模块。"},
            {"title": "作业提醒：安全工程导论观后感", "content": "《视频学习题目：安全工程导论观后感》将于 9月15日 截止提交。"},
            {"title": "小组任务：第四组、第五组尚未提交", "content": "请相关小组组长尽快组织提交项目材料。"},
        ]
        for n in notifications:
            db.add(models.Notification(**n))

    db.commit()
