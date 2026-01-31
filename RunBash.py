import sys
import os
import subprocess
import shutil
def findBash():
	candidates = [
		r"C:\Program Files\Git\bin\bash.exe",
		r"C:\Program Files\Git\usr\bin\bash.exe",
		r"C:\Program Files (x86)\Git\bin\bash.exe",
		r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
	]
	Bash = shutil.which("bash")
	if Bash:
		return Bash
	else:
		for path in candidates:
			if os.path.isfile(path):
				return path
		return None
BASH = os.environ.get("RUNBASH_BASH") or findBash()
def version():
	print("RunBash version 1.8")
def help():
	print("Using \"runbash.exe path\\script.sh [args...] or runbash.exe path\\script.bash [args...]\" to run a Bash script.")
	print("Using \"runbash.exe --login path\\script.sh [args...] or runbash.exe --login path\\script.bash [args...]\" to run with login shell.")
	print("Using \"runbash.exe --bash-using\" to check Bash path.")
	print("Using \"runbash.exe --environment-variables\" to show the Environment variables that you have set.")
	print("Using \"runbash.exe --version\" to check RunBash version.")
	print("Using \"runbash.exe --help\" to show this help.")
	print("Using \"runbash.exe --about\" to show all info.")
	print("Environment variables RUNBASH_BASH   Use custom bash path instead of auto-detect.")
def bashUsing():
	if BASH:
		print("Bash using:")
		print(BASH)
	else:
		print("Bash not found")
def showEnvironmentVariables():
	Environment = os.environ.get("RUNBASH_BASH")
	if  Environment is None:
		print("Environment variables:")
		print("Not set.")
	else:
		print("Environment variables:")
		print("RUNBASH_BASH:" + Environment)
def about():
	version()
	help()
	bashUsing()
	showEnvironmentVariables()
def sendBashScript(File, Args, Login=False):
	if os.path.isfile(File):
		if File.lower().endswith((".sh", ".bash")):
			if BASH is None:
				print("Bash not found.")
				sys.exit(127)
			else:	
				File = os.path.abspath(File)
				SendScript = [BASH]
				if Login:
					SendScript.append("-l")
				SendScript += [File, *Args]
				Result = subprocess.run(SendScript, check=False, shell=False)
				sys.exit(Result.returncode)
		else:
			print("File is not Bash Script.")
			sys.exit(2)
	else:
		print("File not found.")
		sys.exit(1)
def runScript(Script, Args, Login=False):
	Script = Script.replace("\\", "/")
	sendBashScript(Script, Args, Login)
def main():
	if len(sys.argv) < 2:
		about()
		sys.exit(0)
	else:
		Script = sys.argv[1].strip()
		Args = sys.argv[2:]
		if Script.lower() == "--version":
			version()
			sys.exit(0)
		elif Script.lower() == "--help":
			help()
			sys.exit(0)
		elif Script.lower() == "--bash-using":
			bashUsing()
			sys.exit(0)
		elif Script.lower() == "--environment-variables":
			showEnvironmentVariables()
			sys.exit(0)
		elif Script.lower() == "--about":
			about()
			sys.exit(0)
		elif Script.lower() == "--login":
			if len(sys.argv) < 3:
				print("Missing parameters.")
				sys.exit(2)
			else:
				Script = Args[0].strip()
				Args = Args[1:]
				runScript(Script, Args, Login=True)
		else:
			runScript(Script, Args, Login=False)
main()