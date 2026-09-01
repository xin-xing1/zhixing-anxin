# -*- coding: utf-8 -*-
"""一键启动脚本：python run.py
支持环境变量 PORT（默认 8000，云端可设为 7860）
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print("=" * 50)
    print("  知行安信教学平台 后端服务")
    print(f"  访问地址: http://0.0.0.0:{port}")
    print("  API 文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
