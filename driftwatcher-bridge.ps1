# driftwatcher-bridge.ps1
# こたひたんが・どりふと見守り ブリッジ
# PowerShell Bridge for Drift Watcher
# Manages long-running K(t) monitoring process

$ErrorActionPreference = "Continue"

function Start-DriftWatcher {
    <#
    .SYNOPSIS
    Start Kotahitanja Drift Watcher in background.
    
    .PARAMETER Interval
    Check interval in milliseconds (default: 200ms)
    
    .PARAMETER MaxCycles
    Stop after N cycles (default: infinite)
    
    .PARAMETER Verbose
    Detailed phase output
    
    .EXAMPLE
    $job = Start-DriftWatcher -Interval 200 -Verbose
    Get-DriftWatcherOutput $job.Id
    Stop-DriftWatcher $job.Id
    #>
    param(
        [Parameter(Mandatory = $false)]
        [int] $Interval = 200,
        
        [Parameter(Mandatory = $false)]
        [int] $MaxCycles = $null,
        
        [Parameter(Mandatory = $false)]
        [switch] $Verbose = $false
    )
    
    $PythonScript = Join-Path (Get-Location) "kotahitanga_driftwatcher.py"
    
    if (-not (Test-Path $PythonScript)) {
        Write-Host "ERROR: kotahitanga_driftwatcher.py not found" -ForegroundColor Red
        return $null
    }
    
    $PythonExe = if ((Get-Command python -ErrorAction SilentlyContinue)) { "python" } `
                 elseif ((Get-Command python3 -ErrorAction SilentlyContinue)) { "python3" } `
                 else { $null }
    
    if (-not $PythonExe) {
        Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
        return $null
    }
    
    # Build command line
    $args = @("$PythonScript")
    $args += "--interval", ($Interval / 1000)  # Convert ms to seconds
    
    if ($MaxCycles) {
        $args += "--max-cycles", $MaxCycles
    }
    
    if ($Verbose) {
        $args += "--verbose"
    }
    
    Write-Host "Starting Drift Watcher (interval: ${Interval}ms)..." -ForegroundColor Cyan
    
    # Start background job
    $job = Start-Job -ScriptBlock {
        param($exe, $args)
        & $exe @args
    } -ArgumentList $PythonExe, $args
    
    Write-Host "✓ Watcher started (Job ID: $($job.Id))" -ForegroundColor Green
    return $job
}

function Get-DriftWatcherOutput {
    <#
    .SYNOPSIS
    Get output from running Drift Watcher.
    
    .EXAMPLE
    Get-DriftWatcherOutput -JobId 5
    #>
    param(
        [Parameter(Mandatory = $true)]
        [int] $JobId
    )
    
    $job = Get-Job -Id $JobId -ErrorAction SilentlyContinue
    
    if (-not $job) {
        Write-Host "Job $JobId not found" -ForegroundColor Red
        return
    }
    
    $output = Receive-Job -Job $job
    
    if ($output) {
        Write-Host ""
        Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
        Write-Host "Drift Watcher Output (Job $JobId)" -ForegroundColor Cyan
        Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
        $output | ForEach-Object { Write-Host $_ }
        Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
        Write-Host ""
    }
    
    if ($job.State -ne "Running") {
        Write-Host "Status: $($job.State)" -ForegroundColor Yellow
    }
}

function Stop-DriftWatcher {
    <#
    .SYNOPSIS
    Stop running Drift Watcher.
    
    .EXAMPLE
    Stop-DriftWatcher -JobId 5
    #>
    param(
        [Parameter(Mandatory = $true)]
        [int] $JobId
    )
    
    $job = Get-Job -Id $JobId -ErrorAction SilentlyContinue
    
    if (-not $job) {
        Write-Host "Job $JobId not found" -ForegroundColor Red
        return
    }
    
    Write-Host "Stopping Drift Watcher (Job $JobId)..." -ForegroundColor Yellow
    Stop-Job -Job $job
    Remove-Job -Job $job
    
    Write-Host "✓ Watcher stopped" -ForegroundColor Green
}

function Watch-Coherence {
    <#
    .SYNOPSIS
    Real-time coherence monitoring (blocking).
    Shows K(t) updates with rhythm indicators.
    
    .PARAMETER Seconds
    Duration to watch (default: 60)
    
    .EXAMPLE
    Watch-Coherence -Seconds 30
    #>
    param(
        [Parameter(Mandatory = $false)]
        [int] $Seconds = 60,
        
        [Parameter(Mandatory = $false)]
        [switch] $Verbose = $false
    )
    
    $PythonScript = Join-Path (Get-Location) "kotahitanga_driftwatcher.py"
    
    if (-not (Test-Path $PythonScript)) {
        Write-Host "ERROR: kotahitanga_driftwatcher.py not found" -ForegroundColor Red
        return
    }
    
    $PythonExe = if ((Get-Command python -ErrorAction SilentlyContinue)) { "python" } `
                 elseif ((Get-Command python3 -ErrorAction SilentlyContinue)) { "python3" } `
                 else { $null }
    
    if (-not $PythonExe) {
        Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
        return
    }
    
    # Calculate max cycles: 12 seconds per cycle
    $maxCycles = [math]::Ceiling($Seconds / 12)
    
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  こたひたんが・どりふと見守り — Live Monitor        ║" -ForegroundColor Cyan
    Write-Host "║  Duration: ${Seconds}s | Max cycles: $maxCycles" -ForegroundColor Cyan
    Write-Host "║  (Press Ctrl+C to stop)" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $args = @("$PythonScript", "--max-cycles", $maxCycles)
    
    if ($Verbose) {
        $args += "--verbose"
    }
    
    # Run blocking
    try {
        & $PythonExe @args
    }
    catch {
        Write-Host ""
        Write-Host "Monitor stopped." -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Export
Export-ModuleMember -Function Start-DriftWatcher, Get-DriftWatcherOutput, Stop-DriftWatcher, Watch-Coherence
