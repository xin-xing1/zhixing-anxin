# WSGI entry - used for PythonAnywhere / Render / Railway
import sys

# Add the project's backend directory to the path
project_dir = r"C:\Users\Lenovo\Desktop\知行安信平台\backend"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app.main import app  # noqa: E402

application = app  # WSGI requirement
