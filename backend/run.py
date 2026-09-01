# -*- coding: utf-8 -*-
"""一键启动脚本：python run.py"""
import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("  知行安信教学平台 后端服务")
    print("  访问地址: http://127.0.0.1:8000")
    print("  API 文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
