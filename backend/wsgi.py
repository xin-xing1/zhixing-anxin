# WSGI entry - used for PythonAnywhere / Render / Railway
import os
import sys

# Add this backend directory to sys.path (cross-platform, no hardcoded path)
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app.main import app  # noqa: E402

application = app  # WSGI requirement
