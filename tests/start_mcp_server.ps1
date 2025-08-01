
# This script starts the MCP server and keeps it running in the background

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status
)

$MCPPath = "c:\mcp"
$LogDir = "$MCPPath\data\logs"
$ServiceName = "PersonalMCPServer"

function Install-MCPAutostart {
    Write-Host "Installing MCP Server autostart..." -ForegroundColor Green
    
    # Create scheduled task for autostart
    $Action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$MCPPath\start_mcp_server.ps1`" -Start"
    $Trigger = New-ScheduledTaskTrigger -AtLogon
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    
    Register-ScheduledTask -TaskName $ServiceName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force
    
    Write-Host "✅ MCP Server autostart installed successfully!" -ForegroundColor Green
    Write-Host "The server will start automatically when you log in to Windows." -ForegroundColor Yellow
}

function Uninstall-MCPAutostart {
    Write-Host "Uninstalling MCP Server autostart..." -ForegroundColor Yellow
    
    try {
        Unregister-ScheduledTask -TaskName $ServiceName -Confirm:$false
        Write-Host "✅ MCP Server autostart removed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Could not remove autostart task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-MCPServer {
    Write-Host "Starting MCP Server..." -ForegroundColor Green
    
    # Check if already running
    $existing = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*mcp_server.py*" }
    if ($existing) {
        Write-Host "⚠️ MCP Server appears to already be running (PID: $($existing.Id))" -ForegroundColor Yellow
        return
    }
    
    # Ensure log directory exists
    if (!(Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    
    # Start the server
    Set-Location $MCPPath
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile = "$LogDir\mcp_server_$timestamp.log"
    
    Start-Process -FilePath "python" -ArgumentList "mcp_server.py" -WindowStyle Hidden -RedirectStandardOutput $logFile -RedirectStandardError $logFile
    
    Start-Sleep -Seconds 2
    
    # Verify it started
    $newProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*mcp_server.py*" }
    if ($newProcess) {
        Write-Host "✅ MCP Server started successfully! (PID: $($newProcess.Id))" -ForegroundColor Green
        Write-Host "📝 Logs: $logFile" -ForegroundColor Cyan
    }
    else {
        Write-Host "❌ Failed to start MCP Server. Check logs: $logFile" -ForegroundColor Red
    }
}

function Stop-MCPServer {
    Write-Host "Stopping MCP Server..." -ForegroundColor Yellow
    
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*mcp_server.py*" }
    
    if ($processes) {
        foreach ($proc in $processes) {
            try {
                Stop-Process -Id $proc.Id -Force
                Write-Host "✅ Stopped MCP Server process (PID: $($proc.Id))" -ForegroundColor Green
            }
            catch {
                Write-Host "❌ Failed to stop process $($proc.Id): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "ℹ️ No MCP Server processes found running" -ForegroundColor Blue
    }
}

function Get-MCPStatus {
    Write-Host "MCP Server Status:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    # Check if scheduled task exists
    try {
        $task = Get-ScheduledTask -TaskName $ServiceName -ErrorAction Stop
        Write-Host "🔄 Autostart: ENABLED ($($task.State))" -ForegroundColor Green
    }
    catch {
        Write-Host "🔄 Autostart: DISABLED" -ForegroundColor Red
    }
    
    # Check if server is running
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*mcp_server.py*" }
    
    if ($processes) {
        Write-Host "🟢 Server Status: RUNNING" -ForegroundColor Green
        foreach ($proc in $processes) {
            Write-Host "   PID: $($proc.Id), Started: $($proc.StartTime)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "🔴 Server Status: NOT RUNNING" -ForegroundColor Red
    }
    
    # Check recent log files
    if (Test-Path $LogDir) {
        $recentLogs = Get-ChildItem -Path $LogDir -Filter "mcp_server_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        if ($recentLogs) {
            Write-Host "📝 Recent Logs:" -ForegroundColor Gray
            foreach ($log in $recentLogs) {
                Write-Host "   $($log.Name) ($($log.LastWriteTime))" -ForegroundColor Gray
            }
        }
    }
}

# Main execution logic
if ($Install) {
    Install-MCPAutostart
}
elseif ($Uninstall) {
    Uninstall-MCPAutostart
}
elseif ($Start) {
    Start-MCPServer
}
elseif ($Stop) {
    Stop-MCPServer
}
elseif ($Status) {
    Get-MCPStatus
}
else {
    Write-Host "Personal MCP Server Management Script" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start_mcp_server.ps1 -Install    # Install autostart (runs at Windows login)"
    Write-Host "  .\start_mcp_server.ps1 -Start      # Start the server now"
    Write-Host "  .\start_mcp_server.ps1 -Stop       # Stop the server"
    Write-Host "  .\start_mcp_server.ps1 -Status     # Check server status"
    Write-Host "  .\start_mcp_server.ps1 -Uninstall  # Remove autostart"
    Write-Host ""
    Write-Host "Quick setup:" -ForegroundColor Green
    Write-Host "  1. .\start_mcp_server.ps1 -Install"
    Write-Host "  2. .\start_mcp_server.ps1 -Start"
    Write-Host ""
    Get-MCPStatus
}
