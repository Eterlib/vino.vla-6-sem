import sys
from pathlib import Path

repo = Path(sys.argv[1])

heads = repo / ".git" / "refs" / "heads"

for branch in heads.iterdir():
    print(branch.name)
