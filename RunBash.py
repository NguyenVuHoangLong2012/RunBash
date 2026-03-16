import sys
import os
import subprocess
import shutil
import pathlib
import winreg
import enum
import json
import re
import urllib.request
import urllib.error
import socket
class ENV:
	def __init__(self, Name, Expand, Description):
		self.name = Name
		self.expand = Expand
		self.description = Description
class RegValueStatus(enum.Enum):
	EXISTS = enum.auto()
	NOT_FOUND = enum.auto()
	NO_PERMISSION = enum.auto()
	ERROR = enum.auto()
ENV_Meta = {
	"RUNBASH_BASH": ENV("RUNBASH_BASH", True, "Use to specify a custom Bash path."),
	"RUNBASH_DEFAULTFLAG": ENV("RUNBASH_DEFAULTFLAG", False, "Use to setup default flags passed to bash.")
}
def stripPath(Raw):
	try:
		if not os.path.isfile(Raw):
			Clean = Raw.strip()
			if os.path.isfile(Clean):
				return os.path.abspath(Clean)
			else:
				return os.path.abspath(Raw)
		else:
			return os.path.abspath(Raw)
	except Exception:
		return os.path.abspath(Raw)
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
	try:
		Bash = shutil.which("bash.exe")
	except Exception:
		Bash = None
	if Bash:
		return Bash
	for path in candidates:
			if os.path.isfile(path):
				return path
	return None
def expand_env(ENV_Value):
	try:
		Expanded = os.path.normpath(os.path.expandvars(stripPath(str(ENV_Value))))
		return Expanded
	except Exception:
		return ENV_Value
def checkENV(ENV_Value):
	try:
		ENV_Value = expand_env(ENV_Value)
		ENV_Value = os.path.expandvars(ENV_Value)
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
def isENV(ENV_Name):
	if ENV_Name.upper() not in ENV_Meta:
		print("Invalid environment variable name.")
		sys.exit(127)
	else:
		return None
def getENV(ENV_Name):
	Expand = ENV_Meta[ENV_Name].expand
	isENV(ENV_Name)
	Sources = [
		get_registry_value(winreg.HKEY_CURRENT_USER, r"Environment", ENV_Name),
		get_registry_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", ENV_Name)
	]	
	for Value in Sources:
		if not Value:
			continue
		if Expand:
			Value = checkENV(Value)
			if Value:
				return Value
		else:
			return Value
	return None
def getBASH():
	ENV = getENV("RUNBASH_BASH")
	if ENV is None:
		return findBash()
	else:
		return ENV
def getCurrentVersion():
	return "3.0"
def showVersion():
	print(f"RunBash version {getCurrentVersion()}")
	print("")
def showHelp():
	showVersion()
	print("Usage:")
	print("\"runbash.exe [flag...] path\\script.sh [args...] or runbash.exe [flag...] path\\script.bash [args...]\" to run with login shell.")
	print("\"runbash.exe --bash-using\" to check Bash path.")
	print("\"runbash.exe --show-env\" to show the all Environment variables or \"runbash.exe --show-env env_name\" to show the a specific Environment variable, if you have set.")
	print("\"runbash.exe --set-env env_name env_value\" to set the RUNBASH_BASH or RUNBASH_DEFAULTFLAG environment variables in the this program.")
	print("\"runbash.exe --delete-env env_name\" to delete the RUNBASH_BASH or RUNBASH_DEFAULTFLAG environment variable in the this program.")
	print("\"runbash.exe --version\" to check RunBash version.")
	print("\"runbash.exe --help\" to show this help.")
	print("\"runbash.exe --about\" to show all info.")
	print("\"runbash.exe --upgrade\" or \"runbash.exe --upgrade save_folder_path\" to check and download Latest version of RunBash if available.")
	print("Note, if you do not pass the Save_Folder_Path parameter to --upgrade the downloaded exe file will be saved in %TEMP%.")
	print("")
	print("Environment variables:")
	for ENV in ENV_Meta.values():
		print(f"Environment variables {ENV.name}:   {ENV.description}")
	print("")
	print("Home page:")
	print("https://github.com/nguyenvuhoanglong2012/runbash/")
	print("Download Latest version or see the Release note as:")
	print("https://github.com/NguyenVuHoangLong2012/RunBash/releases/")
	print("")
def bashUsing():
	BASH = getBASH()
	if BASH:
		print("Bash using:")
		print(BASH)
		print("")
	else:
		print("Bash not found")
		print("")
		sys.exit(2)
def showENV(All=True, ENV_Name=None):
	print("Environment variables:")
	if All:
		Found = False
		for Name in ENV_Meta.values():
			ENV_Value = getENV(Name.name)
			if ENV_Value:
				print(f"{Name.name}: {ENV_Value}")
				Found = True
		if not Found:
			print("Not set.")
			return None
	else:
		isENV(ENV_Name)
		ENV_Value = getENV(ENV_Name)
		if ENV_Value:
			print(f"{ENV_Name}: {ENV_Value}")
			return None
		else:
			print("Not set.")
			return None
def about():
	showHelp()
	bashUsing()
	showENV()
def setENV(ENV_Name, ENV_Value):
	isENV(ENV_Name)
	if ENV_Meta[ENV_Name].expand:
		ENV_Value_Checked = checkENV(ENV_Value)
	else:
		ENV_Value_Checked = ENV_Value
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
	except FileNotFoundError:
		return RegValueStatus.NOT_FOUND
	except PermissionError:
		return RegValueStatus.NO_PERMISSION
	except Exception:
		return RegValueStatus.ERROR
def check_value_deleted(Result, Root):
	if Result is None:
		print("RUNBASH_BASH deleted successfully.")
		sys.exit(0)
	elif Result == RegValueStatus.NO_PERMISSION:
		if Root == winreg.HKEY_LOCAL_MACHINE:
			print("Permission denied: Administrator rights required to delete RUNBASH_BASH.")
			sys.exit(2)
		else:
			print("Permission denied.")
			sys.exit(2)
	elif Result == RegValueStatus.NOT_FOUND:
		return None
	else:
		print("Error, cannot delete RUNBASH_BASH: ", Result)
		sys.exit(2)
def deleteENV(ENV_Name):
	isENV(ENV_Name)
	Targets = [
		(winreg.HKEY_CURRENT_USER, r"Environment"),
		(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
	]
	for Root, Path in Targets:
		Status = value_exists(Root, Path, ENV_Name)
		if Status == RegValueStatus.NO_PERMISSION:
			print("Permission denied when accessing environment variables.")
			sys.exit(2)
		if Status != RegValueStatus.EXISTS:
			continue
		Result = delete_value(Root, Path, ENV_Name)
		check_value_deleted(Result, Root)
	print(f"{ENV_Name} not found.")
	sys.exit(1)
def runBashScript(Win_File, Args, Flag=None):
	BASH = getBASH()
	if os.path.isfile(Win_File):
		if Win_File.lower().endswith((".sh", ".bash", ".zsh", ".bats")):
			if BASH is None:
				print("Bash not found.")
				sys.exit(127)
			else:	
				Win_Path = os.path.abspath(Win_File)
				Win_Path = os.path.normpath(Win_Path)
				Win_Path = pathlib.PureWindowsPath(Win_Path)
				if Win_Path.drive:
					Drive = Win_Path.drive[0].lower()
					Git_Bash_Path = "/" + Drive + "/" + "/".join(Win_Path.parts[1:]).replace("\\", "/")
				else:
					print("Invalid path.")
					sys.exit(2)
				RunScript = [BASH]
				if Flag:
					RunScript += Flag
				else:
					Flags = getENV("RUNBASH_DEFAULTFLAG")
					if Flags == "*":
						pass
					elif Flags:
						RunScript.extend(passDefaultFlag(Flags))
					else:
						RunScript.append("-l")
				RunScript += [Git_Bash_Path, *Args]
				try:
					Result = subprocess.run(RunScript, check=False, shell=False, close_fds=True)
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
		if Flag.startswith("-"):
			Flags.append(Flag)
		else:
			break
	return Flags
def passDefaultFlag(Flags):
	return [Flag.strip() for Flag in re.split(";", Flags) if Flag.strip()]
def getLatestVersion():
	UserName = "nguyenvuhoanglong2012"
	RepoName = "RunBash"
	URL = f"https://api.github.com/repos/{UserName}/{RepoName}/releases/latest"
	try:
		print("Checking for updates...")
		Request = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json", "User-Agent": "RunBash"})
		with urllib.request.urlopen(Request, timeout=5) as Response:
			Data = json.loads(Response.read().decode())
		if Data.get("draft", False) == False and Data.get("prerelease", False) == False:
			Tag = Data.get("tag_name", "")
			if not Tag:
				return None
			Match = re.search(r"\d+(?:\.\d+)+", Tag)
			if Match:
				Version = Match.group()
				Target = None
				for Asset in Data.get("assets", []):
					if Asset.get("name", "").endswith(".exe"):
						Target = Asset
						break
				if Target is None:
					return None
				return {
					"LatestVersion": Version,
					"Changelog": Data.get("body", ""),
					"Name": Target.get("name", ""),
					"Size": Target.get("size", 0),
					"DownloadURL": Target.get("browser_download_url", None)
				}
			else:
				print("Error, unable to extract version number.")
				sys.exit(2)
		else:
			return None
	except socket.timeout:
		print("Server is not responding.")
		sys.exit(2)
	except urllib.error.HTTPError as Error:
		print(f"HTTP error: {Error.code} {Error.reason}")
		sys.exit(2)
	except urllib.error.URLError as Error:
		print("Error, cannot connect to server, try checking your internet network.", Error.reason)
		sys.exit(2)
	except Exception as Error:
		print("Error, unable to check latest version:", Error)
		sys.exit(2)
def formatSize(Size):
	try:
		Units = ["B", "KB", "MB", "GB", "TB"]
		Size = float(Size)
		for Unit in Units:
			if Size < 1024 or Unit == Units[-1]:
				if Unit == "B":
					return f"{int(Size)} {Unit}"
				return f"{Size:.2f} {Unit}"
			Size /= 1024
	except Exception:
		return "unknown"
def getCurrentEXE():
	if getattr(sys, "frozen", False):
		return sys.executable
	else:
		return None
def downloadUpdate(URL, Name, Size, DefaultSaveFolder=True, SaveFolder=None):
	try:
		SavePath = None
		if DefaultSaveFolder:
			SaveFolder = os.path.expandvars("%TEMP%")
			SaveFolder = os.path.abspath(SaveFolder)
		else:
			if not SaveFolder:
				print("Invalid save folder.")
				sys.exit(1)
		SaveFolder = os.path.abspath(SaveFolder)
		SaveFolder = os.path.normpath(SaveFolder)
		if os.path.isdir(SaveFolder):
			SavePath = os.path.join(SaveFolder, Name)
		else:
			print("The path does not exist.")
			sys.exit(1)
		print(f"Downloading {Name} ({formatSize(Size)})")
		print(f"From {URL}")
		print(f"To {SavePath}")
		urllib.request.urlretrieve(URL, SavePath)
		print("Checking size...")
		Downloaded_Size = os.path.getsize(SavePath)
		if Size > 0 and Downloaded_Size != Size:
			print("Error, file size mismatch.")
			if SavePath and os.path.exists(SavePath):
				os.remove(SavePath)
			sys.exit(2)
		else:
			print("Done.")
			print("Download complete.")
			return SavePath
	except Exception as Error:
		print("Error, download error:", Error)
		if SavePath and os.path.exists(SavePath):
			Current_EXE = getCurrentEXE()
			if Current_EXE:
				Current_EXE = os.path.abspath(Current_EXE)
				if os.path.normcase(SavePath.lower()) == os.path.normcase(Current_EXE.lower()):
					sys.exit(2)
			os.remove(SavePath)
		sys.exit(2)
def update(UpdateFile):
	try:
		print("Updating...")
		if not os.path.isfile(UpdateFile):
			print("Downloaded update file not found.")
			sys.exit(1)
		Current_EXE = getCurrentEXE()
		if Current_EXE:
			Current_EXE = os.path.abspath(Current_EXE)
			if not os.access(Current_EXE, os.W_OK):
				print("You need admin rights to do this.")
				sys.exit(2)
			TEMP_Folder = os.path.expandvars("%TEMP%")
			TEMP_Folder = os.path.abspath(TEMP_Folder)
			TEMP_EXE = os.path.join(TEMP_Folder, os.path.basename(Current_EXE))
			if os.path.normcase(os.path.dirname(Current_EXE).lower()) == os.path.normcase(TEMP_Folder.lower()):
				print("Error, you need to run \"RunBash.EXE --upgrade\" in another directory to be able to update.")
				sys.exit(2)
			BatchScript = "@echo off && " + " && ".join([
				"timeout /t 2 >nul",
				"ping -n 3 127.0.0.1 >nul",
				f"move /y \"{Current_EXE}\" \"{TEMP_Folder}\"",
				"if errorlevel 1 exit /b 1",
				f"copy /y \"{UpdateFile}\" \"{Current_EXE}\"",
				f"if errorlevel 1 move /y \"{TEMP_EXE}\" \"{Current_EXE}\" && exit /b 1",
				f"del /q /f \"{TEMP_EXE}\"",
				f"del /q /f \"{UpdateFile}\"",
				"echo Done.",
				"echo RunBash updated successfully.",
				"timeout /t 2 >nul"
			])
			subprocess.Popen(["cmd", "/c", BatchScript], close_fds=True)
			sys.exit(0)
		else:
			Current_PY = os.path.abspath(__file__)
			if not os.path.isfile(Current_PY):
				print("Error, cannot update because the original program was not found.")
				sys.exit(1)
			Current_Dir = os.path.dirname(Current_PY)
			Target_EXE = os.path.join(Current_Dir, os.path.basename(UpdateFile))
			if os.path.abspath(UpdateFile) == os.path.abspath(Target_EXE):
				print("EXE already exists in this directory.")
				sys.exit(0)
			print(f"Copying {os.path.basename(UpdateFile)} to: {Target_EXE}")
			shutil.copy(UpdateFile, Target_EXE)
			print(f"Removing {UpdateFile}")
			os.remove(UpdateFile)
			print("Done.")
			print("RunBash updated successfully.")
			sys.exit(0)
	except Exception as Error:
		print("Error, unable to update:", Error)
		sys.exit(2)
def compareVersion(Current, Latest):
	Current = tuple(map(int, Current.split(".")))
	Latest = tuple(map(int, Latest.split(".")))
	if Current >= Latest:
		return False
	else:
		return True
def checkUpdate(DefaultSaveFolder=True, SaveFolder=None):
	try:
		Data = getLatestVersion()
		if Data is None:
			print("There are no updates available, you are using the latest version.")
			sys.exit(0)
		Latest_Version = Data.get("LatestVersion", None)
		Current_Version = getCurrentVersion()
		ChangesLog = Data.get("Changelog", "Not available")
		File_Name = Data.get("Name", "")
		File_Size = Data.get("Size", 0)
		DownloadURL = Data.get("DownloadURL", "")
		if Latest_Version is None:
			print("There are no updates available, you are using the latest version.")
			sys.exit(0)
		if compareVersion(Current_Version, Latest_Version):
			print(f"New version available, RunBash version {Latest_Version} is available.")
			print(f"Current version: {Current_Version}")
			print(f"Latest version: {Latest_Version}")
			print("Changes:")
			print("")
			print(f"{ChangesLog}")
			print("")
			SavePath = downloadUpdate(DownloadURL, File_Name, File_Size, DefaultSaveFolder, SaveFolder)
			update(SavePath)
		else:
			print("There are no updates available, you are using the latest version.")
			sys.exit(0)
	except Exception as Error:
		print("Error while checking updates:", Error)
		sys.exit(2)
def main():
	try:
		if len(sys.argv) < 2:
			about()
			sys.exit(0)
		else:
			Script = sys.argv[1]
			Args = sys.argv[2:]
			if Script.lower() == "--version":
				showVersion()
				sys.exit(0)
			elif Script.lower() == "--help":
				showHelp()
				sys.exit(0)
			elif Script.lower() == "--bash-using":
				bashUsing()
				sys.exit(0)
			elif Script.lower() == "--show-env":
				if len(sys.argv) < 3:
					showENV(True)
					sys.exit(0)
				else:
					showENV(False, sys.argv[2])
					sys.exit(0)
			elif Script.lower() == "--about":
				about()
				sys.exit(0)
			elif Script.lower() == "--set-env":
				if len(sys.argv) < 4:
					print("--set-env is missing parameters.")
					sys.exit(2)
				else:
					setENV(sys.argv[2], sys.argv[3])
			elif Script.lower() == "--delete-env":
				if len(sys.argv) < 3:
					print("--delete-env is missing parameters.")
					sys.exit(2)
				else:
					deleteENV(sys.argv[2])
			elif Script.lower() == "--upgrade":
				if len(sys.argv) < 3:
					checkUpdate(DefaultSaveFolder=True)
				else:
					checkUpdate(DefaultSaveFolder=False, SaveFolder=sys.argv[2])
			elif Script.startswith("-"):
				Flag = detectFlag(sys.argv[1:])
				Script_Index = len(Flag) + 1
				if len(sys.argv) <= Script_Index:
					BASH = getBASH()
					if BASH is None:
						print("Bash not found.")
						sys.exit(127)
					try:
						Result = subprocess.run([BASH, *Flag], check=False, shell=False, close_fds=True)
						sys.exit(Result.returncode)
					except Exception as Error:
						print("Error, an unknown error occurred: ", Error)
						sys.exit(127)
				Script = stripPath(sys.argv[Script_Index])
				Args = sys.argv[Script_Index + 1:]
				runBashScript(Script, Args, Flag)
			else:
				Script = stripPath(Script)
				runBashScript(Script, Args, None)
	except Exception as Error:
		print("Fatal error: ", Error)
		sys.exit(127)
if __name__ == "__main__":
	main()