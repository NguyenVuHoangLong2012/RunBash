import sys
import os
import subprocess
import shutil
import pathlib
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
Env = os.environ.get("RUNBASH_BASH")
if Env:
	if os.path.isfile(Env) and os.access(Env, os.X_OK):
		BASH = Env
	else:
		BASH = findBash()
else:
	BASH = findBash()
def version():
	print("RunBash version 1.9")
def showHelp():
	print("Using \"runbash.exe path\\script.sh [args...] or runbash.exe path\\script.bash [args...]\" to run a Bash script.")
	print("Using \"runbash.exe --login path\\script.sh [args...] or runbash.exe --login path\\script.bash [args...]\" to run with login shell.")
	print("Using \"runbash.exe --bash-using\" to check Bash path.")
	print("Using \"runbash.exe --environment-variables\" to show the Environment variables that you have set.")
	print("Using \"runbash.exe --version\" to check RunBash version.")
	print("Using \"runbash.exe --help\" to show this help.")
	print("Using \"runbash.exe --about\" to show all info.")
	print("Environment variables RUNBASH_BASH   Use custom bash path instead of auto-detect.")
	print("Home page:")
	print("https://github.com/nguyenvuhoanglong2012/runbash/")
	print("Download Latest version or see the Release note at:")
	print("https://github.com/NguyenVuHoangLong2012/RunBash/releases/")
def bashUsing():
	if BASH:
		print("Bash using:")
		print(BASH)
	else:
		print("Bash not found")
		sys.exit(2)
def showEnvironmentVariables():
	Environment = os.environ.get("RUNBASH_BASH")
	if  Environment is None:
		print("Environment variables:")
		print("Not set.")
		sys.exit(2)
	else:
		print("Environment variables:")
		print("RUNBASH_BASH:" + Environment)
def about():
	version()
	showHelp()
	bashUsing()
	showEnvironmentVariables()
def runBashScript(Win_File, Args, Login=False):
	if os.path.isfile(Win_File):
		if Win_File.lower().endswith((".sh", ".bash")):
			if BASH is None:
				print("Bash not found.")
				sys.exit(127)
			else:	
				Win_File = os.path.abspath(Win_File)
				Win_File = pathlib.PureWindowsPath(Win_File)
				if Win_File.drive:
					Drive = Win_File.drive[0].lower()
					Unix_File = "/" + Drive + "/" + "/".join(Win_File.parts[1:])
				else:
					print("Invalid path.")
					sys.exit(2)
				RunScript = [BASH]
				if Login:
					RunScript.append("-l")
				RunScript += [Unix_File, *Args]
				Result = subprocess.run(RunScript, check=False, shell=False)
				sys.exit(Result.returncode)
		else:
			print("File is not Bash Script.")
			sys.exit(2)
	else:
		print("File not found.")
		sys.exit(1)
def stripText(Raw):
	if not os.path.isfile(Raw):
		Clean = Raw.strip()
		if os.path.isfile(Clean):
			return Clean
		else:
			return Raw
	else:
		return Raw
def main():
	if len(sys.argv) < 2:
		about()
		sys.exit(0)
	else:
		Script = stripText(sys.argv[1])
		Args = sys.argv[2:]
		if Script.lower() == "--version":
			version()
			sys.exit(0)
		elif Script.lower() == "--help":
			showHelp()
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
				print("--login missing parameters.")
				sys.exit(2)
			else:
				Script = stripText(Args[0])
				Args = Args[1:]
				runBashScript(Script, Args, Login=True)
		else:
			runBashScript(Script, Args, Login=False)
if __name__ == "__main__":
	main()