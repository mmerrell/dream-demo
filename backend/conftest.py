import sys
from pathlib import Path

# Add the backend directory to the path so imports work
sys.path.insert(0, str(Path(__file__).parent / "app"))