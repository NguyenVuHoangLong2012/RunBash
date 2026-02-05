import sys
import os
import subprocess
import shutil
import pathlib
import winreg
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
def get_registry_value(root, path, name):
	try:
		with winreg.OpenKey(root, path) as key:
			value, _ = winreg.QueryValueEx(key, name)
			return value
	except FileNotFoundError:
		return None
def expand_env(ENV_Value):
	Expanded = os.path.expandvars(ENV_Value)
	return Expanded
def checkENV(ENV_Value):
	ENV_Value = os.path.abspath(ENV_Value)
	if ENV_Value:
		if os.path.isfile(ENV_Value) and os.access(ENV_Value, os.X_OK):
			if os.path.basename(ENV_Value).lower() == "bash.exe":
				return ENV_Value
			else:
				return None
		else:
			return None
	else:
		return None
def getENV(ENV_Name):
	Sources = [
		get_registry_value(winreg.HKEY_CURRENT_USER, r"Environment", ENV_Name),
		get_registry_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", ENV_Name),
		os.environ.get(ENV_Name)
	]	
	for Value in Sources:
		if not Value:
			continue
		Value = expand_env(Value)
		Value = checkENV(Value)
		if Value:
			return Value
	return None
ENV = getENV("RUNBASH_BASH")
if ENV is None:
	BASH = findBash()
else:
	BASH = ENV
def version():
	print("RunBash version 2.0")
def showHelp():
	print("Using \"runbash.exe Flag path\\script.sh [args...] or runbash.exe Flag path\\script.bash [args...]\" to run with login shell.")
	print("Using \"runbash.exe --bash-using\" to check Bash path.")
	print("Using \"runbash.exe --environment-variables\" to show the Environment variables that you have set.")
	print("Using \"runbash.exe --version\" to check RunBash version.")
	print("Using \"runbash.exe --help\" to show this help.")
	print("Using \"runbash.exe --about\" to show all info.")
	print("Environment variables RUNBASH_BASH   Use custom bash path instead of auto-detect.")
	print("Home page:")
	print("https://github.com/nguyenvuhoanglong2012/runbash/")
	print("Download Latest version or see the Release note as:")
	print("https://github.com/NguyenVuHoangLong2012/RunBash/releases/")
def bashUsing():
	if BASH:
		print("Bash using:")
		print(BASH)
	else:
		print("Bash not found")
		sys.exit(2)
def showEnvironmentVariables():
	Environment = getENV("RUNBASH_BASH")
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
def runBashScript(Win_File, Args, Flag=None):
	if os.path.isfile(Win_File):
		if Win_File.lower().endswith((".sh", ".bash")):
			if BASH is None:
				print("Bash not found.")
				sys.exit(127)
			else:	
				Win_Path = os.path.abspath(Win_File)
				Win_Path = pathlib.PureWindowsPath(Win_Path)
				if Win_Path.drive:
					Drive = Win_Path.drive[0].lower()
					Git_Bash_Path = "/" + Drive + "/" + "/".join(Win_Path.parts[1:])
				else:
					print("Invalid path.")
					sys.exit(2)
				RunScript = [BASH]
				if Flag:
					RunScript.append(Flag)
				RunScript += [Git_Bash_Path, *Args]
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
		elif Script[0] == "-" or Script[0] == "/":
			if len(sys.argv) < 3:
				print(f"{Script} missing parameters.")
				sys.exit(2)
			else:
				Flag = sys.argv[1]
				Script = stripText(Args[0])
				Args = Args[1:]
				runBashScript(Script, Args, Flag)
		else:
			runBashScript(Script, Args, None)
if __name__ == "__main__":
	main()