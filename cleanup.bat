Here's a script to delete those two directories every 2 hours:
Batch Script (delete_dirs.bat):
batch@echo off
REM Delete the _diag and _work directories
rmdir /s /q "C:\R1\_diag"
rmdir /s /q "C:\R1\_work"

REM Recreate empty directories (optional, if the application needs them)
mkdir "C:\R1\_diag"
mkdir "C:\R1\_work"

REM Log the deletion timestamp
echo %date% %time% - Directories deleted >> "C:\R1\cleanup.log"
Key flags:

/s - Delete directory and all contents recursively
/q - Quiet mode (no prompts)

Alternative PowerShell version (delete_dirs.ps1):
powershell# Remove directories and recreate them
$diag = "C:\R1\_diag"
$work = "C:\R1\_work"

if (Test-Path $diag) {
    Remove-Item -Path $diag -Recurse -Force
    New-Item -ItemType Directory -Path $diag -Force | Out-Null
}

if (Test-Path $work) {
    Remove-Item -Path $work -Recurse -Force
    New-Item -ItemType Directory -Path $work -Force | Out-Null
}

# Log the action
Add-Content -Path "C:\R1\cleanup.log" -Value "$(Get-Date) - Directories deleted"
To schedule every 2 hours:

Open Task Scheduler
Click Create Basic Task
Name it "Clean R1 Directories"
Trigger tab: Set to run at startup, then set to repeat every 2 hours
Action tab:

For batch: C:\R1\delete_dirs.bat
For PowerShell: powershell.exe -ExecutionPolicy Bypass -File "C:\R1\delete_dirs.ps1"


General tab: Check "Run with highest privileges"
