function Go-Down {
    param (
        [int]$Number
    )
    for ($i = 1; $i -le $Number; $i++) {
        $wshell.Sendkeys("{DOWN}")
        Start-Sleep -Milliseconds 05# Tiny delay so Windows registers individual key presses
    }
}

# 1. Define the search term
$query = "https://t.me/ForTheStudents/11"

# Force stop Telegram and WAIT until it is completely dead
Stop-Process -Name "Telegram" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2 

# 2. Start Telegram
Set-Location $env:APPDATA
Start-Process "Telegram Desktop\Telegram.exe"

# 3. Wait for Telegram to initialize (Give it 5 seconds to load completely)
Start-Sleep -Seconds 3

# 4. Create the COM object to send keys
$wshell = New-Object -ComObject WScript.Shell

# CRITICAL FIX: Explicitly bring the Telegram window to the front/focus
$wshell.AppActivate("Telegram")
Start-Sleep -Seconds 1 # Give the focus a moment to register

# 5. Send navigation keys
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{UP}")
$wshell.SendKeys("{DOWN}")

# 6. Loop to type the query
for ($i = 1; $i -le 10; $i++) {
    $wshell.Sendkeys("{ENTER}")
    $wshell.Sendkeys("{ENTER}")
    $wshell.Sendkeys($query)
    $wshell.Sendkeys("{ENTER}")

    $wshell.Sendkeys("{ESC}")
    $wshell.Sendkeys("{ESC}")
    
    # Re-activate Telegram just in case it lost focus during the loop
    $wshell.AppActivate("Telegram") 
    Go-Down -Number $i
}
