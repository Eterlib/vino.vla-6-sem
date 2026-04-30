from pathlib import Path
from zipfile import ZipFile
def task_docs():
	files = [*Path('.').glob("*/*.rst")] + [*Path('.').glob("*/*.py")]
	for name, path in zip(['base_doc', 'homedir_doc'], ['./','-/']):
		yield {
		"actions": ['sphinx-build -M html docs {path + "_build}'],
		'file_dep': files,
		'targets' :['HTMLIDX']
	
	}
	
def task_erase():
	return {
		"actions": ['rm -rf  _build'],
}

def zipfunc(path, outfile):
	with zipfIle("f.zip", "w") as zf:
		for file in Path(path).glob("**"):
			zf.write(file)
	
def task_zip():
	return {
		"actions": [(zipfunc, ["_build", "f.zip"])],
		'task_dep' : ['docs'],
		'file_dep': ['_buid/html/index.html'],
		'targets' : ["f.zip"]
}



