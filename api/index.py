# Vercel serverless function entry point
import sys
from pathlib import Path

# Add parent directory to path to import the FastAPI app
sys.path.insert(0, str(Path(__file__).parent.parent))

from static.server import app

# Export the FastAPI app for Vercel
handler = app

# Made with Bob
