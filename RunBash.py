import sys
import os
import subprocess
import shutil
import pathlib
import winreg
import enum
def get_registry_value(root, path, name):
	try:
		with winreg.OpenKey(root, path) as key:
			value, _ = winreg.QueryValueEx(key, name)
			return value
	except Exception:
		return None
def findBash():
	candidates = [
		r"C:\Program Files\Git\bin\bash.exe",
		r"C:\Program Files\Git\usr\bin\bash.exe",
		r"C:\Program Files (x86)\Git\bin\bash.exe",
		r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
	]
	Git_For_Windows = get_registry_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GitForWindows", "InstallPath")
	if Git_For_Windows:
		candidates.append(os.path.join(Git_For_Windows, r"bin\bash.exe"))
	try:
		Bash = shutil.which("bash")
	except Exception:
		Bash = None
	if Bash:
		return Bash
	else:
		for path in candidates:
			if os.path.isfile(path):
				return path
		return None
def expand_env(ENV_Value):
	try:
		Expanded = os.path.expandvars(str(ENV_Value))
		return Expanded
	except Exception:
		return ENV_Value
def checkENV(ENV_Value):
	try:
		ENV_Value = expand_env(ENV_Value)
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
	except Exception:
		return None
def getENV(ENV_Name):
	Sources = [
		get_registry_value(winreg.HKEY_CURRENT_USER, r"Environment", ENV_Name),
		get_registry_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", ENV_Name)
	]	
	for Value in Sources:
		if not Value:
			continue
		Value = checkENV(Value)
		if Value:
			return Value
	return None
def getBASH():
	ENV = getENV("RUNBASH_BASH")
	if ENV is None:
		return findBash()
	else:
		return ENV
class RegValueStatus(enum.Enum):
	EXISTS = enum.auto()
	NOT_FOUND = enum.auto()
	NO_PERMISSION = enum.auto()
	ERROR = enum.auto()
def version():
	print("RunBash version 2.4")
def showHelp():
	print("Using \"runbash.exe [flag...] path\\script.sh [args...] or runbash.exe [flag...] path\\script.bash [args...]\" to run with login shell.")
	print("Using \"runbash.exe --bash-using\" to check Bash path.")
	print("Using \"runbash.exe --show-env\" to show the Environment variables that you have set.")
	print("Using \"runbash.exe --set-env path_to_bash.exe\" to set the RUNBASH_BASH environment variables in the this program.")
	print("Using \"runbash.exe --delete-env\" to delete the RUNBASH_BASH environment variable in the this program.")
	print("Using \"runbash.exe --version\" to check RunBash version.")
	print("Using \"runbash.exe --help\" to show this help.")
	print("Using \"runbash.exe --about\" to show all info.")
	print("Environment variables RUNBASH_BASH   Use custom bash path instead of auto-detect.")
	print("Home page:")
	print("https://github.com/nguyenvuhoanglong2012/runbash/")
	print("Download Latest version or see the Release note as:")
	print("https://github.com/NguyenVuHoangLong2012/RunBash/releases/")
def bashUsing():
	BASH = getBASH()
	if BASH:
		print("Bash using:")
		print(BASH)
	else:
		print("Bash not found")
		sys.exit(2)
def showENV():
	Environment = getENV("RUNBASH_BASH")
	if  Environment is None:
		print("Environment variables:")
		print("Not set.")
	else:
		print("Environment variables:")
		print("RUNBASH_BASH: " + Environment)
def about():
	version()
	showHelp()
	bashUsing()
	showENV()
def setENV(ENV_Name, ENV_Value):
	ENV_Value_Checked = checkENV(ENV_Value)
	if ENV_Value_Checked:
		try:
			with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE) as Key:
				winreg.SetValueEx(Key, ENV_Name, 0, winreg.REG_SZ, ENV_Value_Checked)
				print(f"Environment variable {ENV_Name} set successfully.")
				sys.exit(0)
		except Exception as Error:
			print("Unable to create or write environment variables: ", Error)
			sys.exit(2)
	else:
		print("Invalid value: " + ENV_Value)
		sys.exit(2)
def value_exists(Root, Path, Value_Name):
	try:
		with winreg.OpenKey(Root, Path) as Key:
			winreg.QueryValueEx(Key, Value_Name)
			return RegValueStatus.EXISTS
	except FileNotFoundError:
		return RegValueStatus.NOT_FOUND
	except PermissionError:
		return RegValueStatus.NO_PERMISSION
	except Exception:
		return RegValueStatus.ERROR
def delete_value(Root, Path, Value_Name):
	try:
		with winreg.OpenKey(Root, Path, 0, winreg.KEY_SET_VALUE) as Key:
			winreg.DeleteValue(Key, Value_Name)
			return None
	except Exception as Error:
		return Error
def check_value_deleted(Result):
	if Result is None:
		print("RUNBASH_BASH deleted successfully.")
		sys.exit(0)
	else:
		print("Error, cannot delete RUNBASH_BASH: ", Result)
def deleteENV():
	Targets = [
		(winreg.HKEY_CURRENT_USER, r"Environment"),
		(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
	]
	for Root, Path in Targets:
		Status = value_exists(Root, Path, "RUNBASH_BASH")
		if Status != RegValueStatus.EXISTS:
			continue
		Result = delete_value(Root, Path, "RUNBASH_BASH")
		check_value_deleted(Result)
	print("RUNBASH_BASH not found.")
	sys.exit(1)
def runBashScript(Win_File, Args, Flag=None):
	BASH = getBASH()
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
					RunScript += Flag
				else:
					RunScript.append("-l")
				RunScript += [Git_Bash_Path, *Args]
				try:
					Result = subprocess.run(RunScript, check=False, shell=False)
					sys.exit(Result.returncode)
				except Exception as Error:
					print("Error, an unknown error occurred: ", Error)
					sys.exit(127)
		else:
			print("File is not Bash Script.")
			print(Win_File)
			sys.exit(2)
	else:
		print("File not found.")
		print(Win_File)
		sys.exit(1)
def detectFlag(Flag_List):
	Flags = []
	for Flag in Flag_List:
		if Flag.startswith(("-", "/")):
			Flags.append(Flag)
		else:
			break
	return Flags
def stripPath(Raw):
	try:
		if not os.path.isfile(Raw):
			Clean = Raw.strip()
			if os.path.isfile(Clean):
				return Clean
			else:
				return Raw
		else:
			return Raw
	except Exception:
		return Raw
def main():
	try:
		if len(sys.argv) < 2:
			about()
			sys.exit(0)
		else:
			Script = stripPath(sys.argv[1])
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
			elif Script.lower() == "--show-env":
				showENV()
				sys.exit(0)
			elif Script.lower() == "--about":
				about()
				sys.exit(0)
			elif Script.lower() == "--set-env":
				if len(sys.argv) < 3:
					print("--set-env is missing parameters.")
					sys.exit(2)
				else:
					setENV("RUNBASH_BASH", sys.argv[2])
			elif Script.lower() == "--delete-env":
				deleteENV()
			elif Script.startswith(("-", "/")):
				Flag = detectFlag(sys.argv[1:])
				Script_Index = len(Flag) + 1
				if len(sys.argv) <= Script_Index:
					BASH = getBASH()
					if BASH is None:
						print("Bash not found.")
						sys.exit(127)
					Result = subprocess.run([BASH, *Flag], check=False, shell=False)
					sys.exit(Result.returncode)
				Script = stripPath(sys.argv[Script_Index])
				Args = sys.argv[Script_Index + 1:]
				runBashScript(Script, Args, Flag)
			else:
				runBashScript(Script, Args, None)
	except Exception as Error:
		print("Fatal error: ", Error)
		sys.exit(127)
if __name__ == "__main__":
	main()