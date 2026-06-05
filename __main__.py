"""Allow running the package with: python -m batch_loader"""
from batch_loader.cli import main
import sys

sys.exit(main() or 0)
