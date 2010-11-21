from distutils.core import setup
import py2exe

#setup(console=['o3dconverter.py'],options={"py2exe":{"bundle-files":1}})
setup(
		name='flyffstuff',
		version='1',
		console=['o3dconverter.py'],
		options = {'py2exe': {'bundle_files': 1, "optimize": 2, "compressed":1,"excludes":["doctext","pdb","unittest","difflib"]}},
		zipfile = None,
     )
