from pathlib import Path
import zlib
import sys




for obj in Path( sys.argv[1]).glob( ".git/objects/??/*"):
	print( obj)
	data = zlib.decompress( obj.read_bytes())
	head, _, tail = data.partition(b'\x00')
	king, size = head.split()
	match king.decode():
		case 'commit':
			print(tail.decode())