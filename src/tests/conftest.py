import os
import pathlib
import sys

# Override cookiecutter placeholders so pydantic-settings can parse them.
# These env vars must be set BEFORE any config module is imported.
os.environ.setdefault("PROJECT_HOST", "127.0.0.1")
os.environ.setdefault("PROJECT_PORT", "8080")

# Ensure src/ is on the Python path when pytest is invoked from src/
src_path = str(pathlib.Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)
