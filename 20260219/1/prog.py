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

def show_tree(repo, tree_hash):

    obj_path = repo / ".git" / "objects" / tree_hash[:2] / tree_hash[2:]

    import zlib
    data = zlib.decompress(obj_path.read_bytes())

    header, _, content = data.partition(b'\x00')

    i = 0

    while i < len(content):

        mode_end = content.find(b' ', i)
        name_end = content.find(b'\x00', mode_end)

        name = content[mode_end+1:name_end]

        sha = content[name_end+1:name_end+21].hex()

        print(name.decode())

        i = name_end + 21
