# kotahitanga-bridge.ps1
# こたひたんが・ブリッジ — PowerShell ↔ SymPy Bridge
# PASS/FAIL → Python JSON → K値

$ErrorActionPreference = "Stop"

function Invoke-KotahitangaSymPy {
    <#
    .SYNOPSIS
    PowerShell の PASS/FAIL 結果を Python SymPy に渡して こたひたんが（K値）を計算
    
    .PARAMETER PassFlags
    @{ "層" = $true; "しん" = $true; ... } 形式の Hashtable
    
    .PARAMETER Weights
    @{ "w層" = 1; "wしん" = 1.5; ... } 形式のウェイト（省略時は均等）
    
    .EXAMPLE
    $flags = @{
        "層" = $true
        "しん" = $true
        "こう" = $true
        "つな" = $false
        "うご" = $true
        "かん" = $true
        "みち" = $true
    }
    Invoke-KotahitangaSymPy -PassFlags $flags
    
    # 出力: { "K": 0.8571, "K_percent": 85.71, "status": "PASS", ... }
    #>
    param(
        [Parameter(Mandatory = $true)]
        [hashtable] $PassFlags,
        
        [Parameter(Mandatory = $false)]
        [hashtable] $Weights = $null
    )
    
    # Python ファイルの場所
    $PythonScript = Join-Path (Get-Location) "kotahitanga_sympy.py"
    
    if (-not (Test-Path $PythonScript)) {
        throw "kotahitanga_sympy.py not found at: $PythonScript"
    }
    
    # Python 実行可能か確認
    $PythonExe = if ((Get-Command python -ErrorAction SilentlyContinue)) { "python" } `
                 elseif ((Get-Command python3 -ErrorAction SilentlyContinue)) { "python3" } `
                 else { throw "Python not found in PATH" }
    
    # JSON payload を作成
    $payload = @{
        pass_flags = $PassFlags
    }
    if ($Weights) {
        $payload["weights"] = $Weights
    }
    
    $jsonInput = $payload | ConvertTo-Json -Compress
    
    # Python に JSON を渡して実行
    try {
        $jsonOutput = $jsonInput | & $PythonExe $PythonScript
        $result = $jsonOutput | ConvertFrom-Json
        return $result
    }
    catch {
        throw "SymPy execution failed: $_"
    }
}


function Format-KotahitangaReport {
    <#
    .SYNOPSIS
    こたひたんが結果をフォーマットして表示
    #>
    param(
        [Parameter(Mandatory = $true)]
        [PSCustomObject] $Result,
        
        [Parameter(Mandatory = $false)]
        [string] $Title = "こたひたんが・レポート"
    )
    
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $Title" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    if ($Result.error) {
        Write-Host "❌ エラー: $($Result.error)" -ForegroundColor Red
        return
    }
    
    # K値と％
    $K = $Result.K
    $K_percent = $Result.K_percent
    $status = $Result.status
    
    $statusColor = switch ($status) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        default { "Gray" }
    }
    
    Write-Host "  Unity Score (K): " -NoNewline
    Write-Host "$K" -ForegroundColor Cyan -NoNewline
    Write-Host " ($K_percent%)" -ForegroundColor Cyan
    
    Write-Host "  Status: " -NoNewline
    Write-Host "$status" -ForegroundColor $statusColor
    
    Write-Host "  Pass Count: " -NoNewline
    Write-Host "$($Result.pass_count) / $($Result.total_count)" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "  ７次元状態："
    Write-Host "  ─────────────────────────────────────────"
    
    $dimensions = @("層", "しん", "こう", "つな", "うご", "かん", "みち")
    $names = @("Layer", "Identity", "Structure", "Topology", "Rhythm", "Security", "Navigation")
    
    for ($i = 0; $i -lt $dimensions.Count; $i++) {
        $dim = $dimensions[$i]
        $name = $names[$i]
        $passed = $Result.dimensions.$dim
        
        $symbol = if ($passed) { "✓" } else { "✗" }
        $color = if ($passed) { "Green" } else { "Red" }
        
        Write-Host "    $symbol $dim ($name)" -ForegroundColor $color
    }
    
    Write-Host ""
    Write-Host "  SymPy Formula: K = (Σ w_i * D_i) / (Σ w_i)" -ForegroundColor Gray
    Write-Host ""
}


# エクスポート
Export-ModuleMember -Function Invoke-KotahitangaSymPy, Format-KotahitangaReport
