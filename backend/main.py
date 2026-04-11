"""Backend entry point for direct execution and PyInstaller packaging."""
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=8765)
