import os, sys, shutil, ctypes

# ── PYINSTALLER DIRECTORY FIX ─────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ──────────────────────────────────────────────────────────────────────────────

FILENAME = "open_telegram.bat"
SHORTCUT_NAME = "OpenTelegram.bat"
BAT_SOURCE_PATH = os.path.join(SCRIPT_DIR, FILENAME)

BATCH_CONTENT = """@echo off
:: ============================================
:: open_telegram.bat
:: Launches Telegram Desktop on Windows
:: ============================================

set TELEGRAM_PATH=%APPDATA%\\Telegram Desktop\\Telegram.exe
if exist "%TELEGRAM_PATH%" (
    start "" "%TELEGRAM_PATH%"
    exit /b 0
)

set TELEGRAM_PATH_ALT=%LOCALAPPDATA%\\Telegram Desktop\\Telegram.exe
if exist "%TELEGRAM_PATH_ALT%" (
    start "" "%TELEGRAM_PATH_ALT%"
    exit /b 0
)

set TELEGRAM_PATH_PF=%ProgramFiles%\\Telegram Desktop\\Telegram.exe
if exist "%TELEGRAM_PATH_PF%" (
    start "" "%TELEGRAM_PATH_PF%"
    exit /b 0
)

echo Telegram not found. Please check the installation path.
pause
"""

STARTUP_FOLDERS = [
    # User-level Startup folder
    os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup"),
    # System-wide Startup folder (Requires Admin)
    os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
]

def is_elevated():
    try: 
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: 
        return False

def relaunch_as_admin():
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
        relaunch_as_admin()

    print("=== Creating Local Batch File ===")
    try:
        with open(BAT_SOURCE_PATH, "w", encoding="utf-8") as bat_file:
            bat_file.write(BATCH_CONTENT)
        print(f"[OK] Generated local file -> {BAT_SOURCE_PATH}")
    except Exception as e:
        sys.exit(f"[ERROR] Failed to write local batch file: {e}")

    print("\n=== Deploying to Startup Folders ===")
    for folder in STARTUP_FOLDERS:
        if not os.path.isdir(folder):
            print(f"[SKIP] Directory does not exist: {folder}")
            continue
            
        destination = os.path.join(folder, SHORTCUT_NAME)
        try:
            shutil.copy2(BAT_SOURCE_PATH, destination)
            print(f"[OK] Installed -> {destination}")
        except Exception as e:
            print(f"[ERROR] Failed copying to {folder}: {e}")

    print("\nProcess finished successfully.")