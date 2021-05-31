import os
import subprocess

# Folder.create(path, uid, gid, permission)

class Folder:
	@staticmethod
	def create(path, uid, gid, permission):
	
		os.mkdir(path)
		os.chmod(path, permission)
		p_chown = subprocess.Popen(["sudo", "/bin/chown", f"{uid}:{gid}", path])
		p_chown.wait()
