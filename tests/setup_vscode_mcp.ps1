
# This script configures VSCode to use the MCP server globally across all workspaces

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status
)

$VSCodeUserDir = "$env:APPDATA\Code\User"
$VSCodeSettingsFile = "$VSCodeUserDir\settings.json"
$MCPConfigSource = "c:\mcp\global_mcp_config.json"

function Install-GlobalMCPConfig {
    Write-Host "Installing global MCP configuration for VSCode..." -ForegroundColor Green
    
    # Ensure VSCode User directory exists
    if (!(Test-Path $VSCodeUserDir)) {
        Write-Host "❌ VSCode User directory not found: $VSCodeUserDir" -ForegroundColor Red
        Write-Host "Please ensure VSCode is installed and has been run at least once." -ForegroundColor Yellow
        return
    }
    
    # Load existing settings
    $settings = @{}
    if (Test-Path $VSCodeSettingsFile) {
        try {
            $content = Get-Content $VSCodeSettingsFile -Raw
            $settings = $content | ConvertFrom-Json -AsHashtable
            Write-Host "✅ Loaded existing VSCode settings" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️ Could not parse existing settings.json, creating new one" -ForegroundColor Yellow
            $settings = @{}
        }
    }
    
    # Add MCP configuration
    $settings["github.copilot.chat.mcp.enabled"] = $true
    $settings["github.copilot.chat.mcp.configFile"] = $MCPConfigSource
    
    # Ensure other important MCP settings are enabled
    $settings["github.copilot.chat.followUps"] = "always"
    $settings["github.copilot.chat.edits.codesearch.suggestions"] = $true
    $settings["github.copilot.chat.edits.temporalContext.enabled"] = $true
    $settings["github.copilot.nextEditSuggestions.enabled"] = $true
    
    # Save updated settings
    try {
        $settings | ConvertTo-Json -Depth 10 | Set-Content $VSCodeSettingsFile -Encoding UTF8
        Write-Host "✅ VSCode global settings updated successfully!" -ForegroundColor Green
        Write-Host "📁 Settings file: $VSCodeSettingsFile" -ForegroundColor Cyan
        Write-Host "🔧 MCP config file: $MCPConfigSource" -ForegroundColor Cyan
    }
    catch {
        Write-Host "❌ Failed to update VSCode settings: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Uninstall-GlobalMCPConfig {
    Write-Host "Removing global MCP configuration from VSCode..." -ForegroundColor Yellow
    
    if (!(Test-Path $VSCodeSettingsFile)) {
        Write-Host "ℹ️ No VSCode settings file found" -ForegroundColor Blue
        return
    }
    
    try {
        $content = Get-Content $VSCodeSettingsFile -Raw
        $settings = $content | ConvertFrom-Json -AsHashtable
        
        # Remove MCP-related settings
        $settings.Remove("github.copilot.chat.mcp.enabled")
        $settings.Remove("github.copilot.chat.mcp.configFile")
        
        # Save updated settings
        $settings | ConvertTo-Json -Depth 10 | Set-Content $VSCodeSettingsFile -Encoding UTF8
        Write-Host "✅ MCP configuration removed from VSCode settings" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to update VSCode settings: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Get-MCPConfigStatus {
    Write-Host "VSCode MCP Configuration Status:" -ForegroundColor Cyan
    Write-Host "===============================" -ForegroundColor Cyan
    
    # Check if VSCode is installed
    if (!(Test-Path $VSCodeUserDir)) {
        Write-Host "❌ VSCode not found or not configured" -ForegroundColor Red
        return
    }
    
    Write-Host "✅ VSCode installation found" -ForegroundColor Green
    Write-Host "📁 User directory: $VSCodeUserDir" -ForegroundColor Gray
    
    # Check settings file
    if (!(Test-Path $VSCodeSettingsFile)) {
        Write-Host "⚠️ No settings.json file found" -ForegroundColor Yellow
        return
    }
    
    try {
        $content = Get-Content $VSCodeSettingsFile -Raw
        $settings = $content | ConvertFrom-Json -AsHashtable
        
        # Check MCP settings
        $mcpEnabled = $settings["github.copilot.chat.mcp.enabled"]
        $mcpConfigFile = $settings["github.copilot.chat.mcp.configFile"]
        
        if ($mcpEnabled -eq $true) {
            Write-Host "✅ MCP enabled in VSCode" -ForegroundColor Green
        }
        else {
            Write-Host "❌ MCP not enabled in VSCode" -ForegroundColor Red
        }
        
        if ($mcpConfigFile) {
            Write-Host "📄 MCP config file: $mcpConfigFile" -ForegroundColor Gray
            if (Test-Path $mcpConfigFile) {
                Write-Host "✅ MCP config file exists" -ForegroundColor Green
            }
            else {
                Write-Host "❌ MCP config file not found" -ForegroundColor Red
            }
        }
        else {
            Write-Host "❌ No MCP config file specified" -ForegroundColor Red
        }
        
        # Check other relevant settings
        $otherSettings = @{
            "github.copilot.chat.followUps"                     = $settings["github.copilot.chat.followUps"]
            "github.copilot.chat.edits.codesearch.suggestions"  = $settings["github.copilot.chat.edits.codesearch.suggestions"]
            "github.copilot.chat.edits.temporalContext.enabled" = $settings["github.copilot.chat.edits.temporalContext.enabled"]
        }
        
        Write-Host "`nOther Copilot settings:" -ForegroundColor Gray
        foreach ($key in $otherSettings.Keys) {
            $value = $otherSettings[$key]
            $status = if ($value -eq $true) { "✅" } elseif ($value -eq $false) { "❌" } else { "⚠️" }
            Write-Host "  $status $key`: $value" -ForegroundColor Gray
        }
        
    }
    catch {
        Write-Host "❌ Could not parse settings.json: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution logic
if ($Install) {
    Install-GlobalMCPConfig
}
elseif ($Uninstall) {
    Uninstall-GlobalMCPConfig
}
elseif ($Status) {
    Get-MCPConfigStatus
}
else {
    Write-Host "VSCode Global MCP Configuration Setup" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\setup_vscode_mcp.ps1 -Install    # Configure VSCode to use MCP globally"
    Write-Host "  .\setup_vscode_mcp.ps1 -Status     # Check current configuration"
    Write-Host "  .\setup_vscode_mcp.ps1 -Uninstall  # Remove MCP configuration"
    Write-Host ""
    Write-Host "This script configures VSCode to use your MCP server across ALL workspaces." -ForegroundColor Green
    Write-Host ""
    Get-MCPConfigStatus
}
