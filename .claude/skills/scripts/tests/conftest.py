import sys
from pathlib import Path

# Add the scripts directory to sys.path so tests can import sibling modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
