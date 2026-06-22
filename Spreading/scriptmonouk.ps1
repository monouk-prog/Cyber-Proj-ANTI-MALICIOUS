# ==============================================================================
# FUNCTION DEFINITIONS
# ==============================================================================
function Go-Down {
    param (
        [int]$Number
    )
    for ($i = 1; $i -le $Number; $i++) {
        $wshell.Sendkeys("{DOWN}")
        Start-Sleep -Milliseconds 5
    }
}

# ==============================================================================
# 1. DEFINE CONFIGURATION VARIABLES
# ==============================================================================
$query = "https://t.me/ForTheStudents/14"

# ==============================================================================
# 2. PROCESS MANAGEMENT (RESET TELEGRAM)
# ==============================================================================
# Force stop Telegram and WAIT until it is completely closed
Stop-Process -Name "Telegram" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2 

# Launch Telegram from the standard AppData roaming directory
Set-Location $env:APPDATA
Start-Process "Telegram Desktop\Telegram.exe"

# Wait for Telegram to initialize and render its GUI completely
Start-Sleep -Seconds 3

# ==============================================================================
# 3. INTERACTION INITIALIZATION
# ==============================================================================
# Create the COM object to handle simulated keypresses
$wshell = New-Object -ComObject WScript.Shell

# CRITICAL FIX: Cast to [void] to suppress output pop-ups in compiled EXEs
[void]$wshell.AppActivate("Telegram")
Start-Sleep -Seconds 1 # Give the window focus a moment to register

# Move focus to the correct area within the Telegram layout
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{DOWN}")

# ==============================================================================
# 4. MAIN INTERACTION LOOP
# ==============================================================================
for ($i = 1; $i -le 10; $i++) {
    # Open input or navigation parameters
    $wshell.Sendkeys("{ENTER}")
    $wshell.Sendkeys("{ENTER}")
    
    # Type out the target query string
    $wshell.Sendkeys($query)
    $wshell.Sendkeys("{ENTER}")

    # Back out or reset UI states
    $wshell.Sendkeys("{ESC}")
    $wshell.Sendkeys("{ESC}")
    
    # CRITICAL FIX: Cast to [void] inside the loop to prevent the "True" pop-up 
    # from triggering every single time the script attempts to re-focus Telegram.
    [void]$wshell.AppActivate("Telegram") 
    
    # Execute the layout navigation function
    Go-Down -Number $i
}
