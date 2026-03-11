import sys
import zlib
from pathlib import Path

repo = Path(sys.argv[1])

heads = repo / ".git" / "refs" / "heads"

if len(sys.argv) == 2:
    for branch in heads.iterdir():
        print(branch.name)

if len(sys.argv) > 2:

    branch = sys.argv[2]

    ref_path = repo / ".git" / "refs" / "heads" / branch
    commit_hash = ref_path.read_text().strip()

    obj_path = repo / ".git" / "objects" / commit_hash[:2] / commit_hash[2:]

    data = zlib.decompress(obj_path.read_bytes())

    header, _, content = data.partition(b'\x00')

    print(content.decode())
