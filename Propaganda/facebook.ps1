# 1. Load Windows Forms and Drawing assemblies FIRST
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 2. Define the Keyboard and Mouseactions classes
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class KeyBoard {
	[DllImport("user32.dll")]
	public static extern void keybd_event(byte bvK, byte bScan, uint dwFlags, uint dwExtraInfo);
	public const byte VK_LWIN = 0x5B;
	public const byte VK_UP = 0x26;
	public const uint KEYEVENTF_KEYUP = 0x0002;

	public static void MaximizeWindow() {
		keybd_event(VK_LWIN, 0, 0, 0);
		keybd_event(VK_UP, 0, 0, 0);
		keybd_event(VK_UP, 0, KEYEVENTF_KEYUP, 0);
		keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0);
	}
}

public class Mouseactions {
    [DllImport("user32.dll")]
    public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);

    public const int MOUSEEVENTF_LEFTDOWN = 0x02;
    public const int MOUSEEVENTF_LEFTUP = 0x04;

    public static void LeftDown() {
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
    }

    public static void LeftUP() {
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    }
}
"@

# 3. Open Browser (Try Chrome, Fallback to Edge)
$URL = "facebook.com"

try {
    # Check if chrome.exe exists in the environment path or common locations
    $BrowserPath = Get-Command "chrome.exe" -ErrorAction Stop
    Start-Process "chrome.exe" $URL
} 
catch {
    # If Chrome fails or isn't found, fall back to Edge
    Start-Process "msedge.exe" $URL
}

$wshell = New-Object -ComObject Wscript.Shell

# 4. Wait for the browser to load (adjust seconds if needed)
Start-Sleep -Seconds 6

# Readjust maximize and zoom
[KeyBoard]::MaximizeWindow()
[KeyBoard]::MaximizeWindow()
[KeyBoard]::MaximizeWindow()
[KeyBoard]::MaximizeWindow()
[KeyBoard]::MaximizeWindow()
[KeyBoard]::MaximizeWindow()
$wshell.SendKeys("^0")

# Get max position for mouse
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(8000,205)
$position = [System.Windows.Forms.Cursor]::Position
$maxmx = $position.X

# 5. Move the mouse and perform the click action
$postbutton = $maxmx/2
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($postbutton, 200)

[Mouseactions]::LeftDown()
[Mouseactions]::LeftUP()  # Fixed case to match C# definition (LeftUP)
Start-Sleep -Seconds 3

# Automated Navigation
$wshell.SendKeys("https://www.facebook.com/100089462335127/posts/pfbid0dJV9cdjedwg1zjQbVgRHUobfv7ZLGH2GZ6339ZbvYmRteCXut1cqhXRfi5m7BYXFl/?mibextid=wwXIfr")
Start-Sleep 6
for ($i = 1; $i -le 17; $i++) {
	$wshell.SendKeys("{TAB}")
}
$wshell.SendKeys("{ENTER}")
Start-Sleep 3
for ($i = 1; $i -le 8; $i++) {
	$wshell.SendKeys("{TAB}")
}
$wshell.Sendkeys("{ENTER}")
$wshell.Sendkeys("{ESC}")
