# .15% SOLAR WAGYU — DIGITAL CUT
# E14 Master Control Console
# Run all checks and commands from PowerShell

$E14_HOME = "C:\Users\Admin\OneDrive\Desktop\~E14-"

# ════════════════════════════════════════════════════════════════
# INITIALIZE ENVIRONMENT
# ════════════════════════════════════════════════════════════════

function E14-Init {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║       .15% SOLAR WAGYU — DIGITAL CUT                       ║" -ForegroundColor Green
    Write-Host "║       E14 Master Control Console                           ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Home: $E14_HOME" -ForegroundColor Cyan
    Write-Host ""
    
    # Verify directory structure
    $dirs = @("manifests", "cli", "docs", "config")
    foreach ($dir in $dirs) {
        $path = Join-Path $E14_HOME $dir
        if (Test-Path $path) {
            Write-Host "✓ $dir/" -ForegroundColor Green
        } else {
            Write-Host "✗ $dir/ (missing)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

# ════════════════════════════════════════════════════════════════
# DOCKER OPERATIONS
# ════════════════════════════════════════════════════════════════

function E14-Docker-Status {
    Write-Host ""
    Write-Host "【層】DOCKER STATUS" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    
    $pods = kubectl get pods -f label=lock=90day-sync 2>$null
    if ($pods) {
        docker ps -f label=lock=90day-sync --format "table {{.Names}}\t{{.Status}}"
    } else {
        Write-Host "No Docker containers found. Use E14-Docker-Start to deploy."
    }
    
    Write-Host ""
}

function E14-Docker-Start {
    Write-Host ""
    Write-Host "Starting 14-engine Docker cluster..." -ForegroundColor Yellow
    Write-Host ""
    
    $compose = Join-Path $E14_HOME "manifests\docker-compose-14engines.yml"
    if (-not (Test-Path $compose)) {
        Write-Host "Error: docker-compose-14engines.yml not found" -ForegroundColor Red
        return
    }
    
    # Load environment
    $env_file = Join-Path $E14_HOME "config\.env.lock"
    if (Test-Path $env_file) {
        Get-Content $env_file | ForEach-Object {
            if ($_ -match "^([^=]+)=(.*)$") {
                [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
            }
        }
    }
    
    Set-Location (Split-Path $compose)
    docker compose -f (Split-Path $compose -Leaf) up -d
    
    Write-Host ""
    Write-Host "✓ Docker cluster starting" -ForegroundColor Green
    Start-Sleep -Seconds 5
    E14-Docker-Status
}

function E14-Docker-Stop {
    Write-Host ""
    Write-Host "Stopping Docker cluster..." -ForegroundColor Yellow
    
    $compose = Join-Path $E14_HOME "manifests\docker-compose-14engines.yml"
    if (Test-Path $compose) {
        Set-Location (Split-Path $compose)
        docker compose -f (Split-Path $compose -Leaf) down
        Write-Host "✓ Docker cluster stopped" -ForegroundColor Green
    }
    
    Write-Host ""
}

function E14-Docker-Logs {
    param([string]$Engine = "365")
    
    Write-Host ""
    Write-Host "Tailing logs for engine-$Engine..." -ForegroundColor Cyan
    Write-Host ""
    
    docker logs -f "engine-$Engine"
}

# ════════════════════════════════════════════════════════════════
# KUBERNETES OPERATIONS
# ════════════════════════════════════════════════════════════════

function E14-K8S-Deploy {
    Write-Host ""
    Write-Host "【こう】KUBERNETES DEPLOY" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Yellow
    Write-Host ""
    
    $manifest = Join-Path $E14_HOME "manifests\k8s-mu-orch-manifest.yaml"
    if (-not (Test-Path $manifest)) {
        Write-Host "Error: k8s-mu-orch-manifest.yaml not found" -ForegroundColor Red
        return
    }
    
    Write-Host "Applying K8s manifest..." -ForegroundColor Cyan
    kubectl apply -f $manifest
    
    Write-Host ""
    Write-Host "✓ Manifest applied" -ForegroundColor Green
    Write-Host "Waiting for pods to be ready..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    E14-K8S-Status
}

function E14-K8S-Status {
    Write-Host ""
    Write-Host "【層】K8S STATUS" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    
    $ns = "k8-mu-orch"
    $pods = kubectl get pods -n $ns -l app=te-papa-matihiko 2>$null
    
    if ($pods) {
        kubectl get pods -n $ns -l app=te-papa-matihiko -o wide
    } else {
        Write-Host "No K8s pods found. Use E14-K8S-Deploy to deploy." -ForegroundColor Yellow
    }
    
    Write-Host ""
}

function E14-K8S-Scale {
    param([int]$Replicas = 3)
    
    if ($Replicas -lt 1 -or $Replicas -gt 10) {
        Write-Host "Replicas must be 1-10" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "Scaling to $Replicas replicas..." -ForegroundColor Yellow
    kubectl scale statefulset k8-mu-orch-engines -n k8-mu-orch --replicas=$Replicas
    Write-Host "✓ Scaling command issued" -ForegroundColor Green
    
    Write-Host ""
}

function E14-K8S-Coherence {
    Write-Host ""
    Write-Host "【任務】COHERENCE CHECK" -ForegroundColor Magenta
    Write-Host "================================" -ForegroundColor Magenta
    Write-Host ""
    
    $coherence = Join-Path $E14_HOME "cli\k8-mu-orch-coherence.ps1"
    if (-not (Test-Path $coherence)) {
        Write-Host "Error: k8-mu-orch-coherence.ps1 not found" -ForegroundColor Red
        return
    }
    
    & $coherence -Verbose
}

# ════════════════════════════════════════════════════════════════
# GTOP CLI COMMANDS
# ════════════════════════════════════════════════════════════════

function E14-Gtop-Status {
    $gtop = Join-Path $E14_HOME "cli\gtop.ps1"
    if (Test-Path $gtop) {
        & $gtop status
    }
}

function E14-Gtop-Map {
    $gtop = Join-Path $E14_HOME "cli\gtop.ps1"
    if (Test-Path $gtop) {
        & $gtop map
    }
}

function E14-Gtop-K8-Status {
    $gtop_k8 = Join-Path $E14_HOME "cli\gtop-k8.ps1"
    if (Test-Path $gtop_k8) {
        & $gtop_k8 status
    }
}

function E14-Gtop-K8-Map {
    $gtop_k8 = Join-Path $E14_HOME "cli\gtop-k8.ps1"
    if (Test-Path $gtop_k8) {
        & $gtop_k8 map
    }
}

# ════════════════════════════════════════════════════════════════
# FULL SYSTEM CHECKS
# ════════════════════════════════════════════════════════════════

function E14-Check-All {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║           FULL SYSTEM COHERENCE CHECK                      ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "[1/4] Docker Status..." -ForegroundColor Yellow
    E14-Docker-Status
    Start-Sleep -Seconds 2
    
    Write-Host "[2/4] Kubernetes Status..." -ForegroundColor Yellow
    E14-K8S-Status
    Start-Sleep -Seconds 2
    
    Write-Host "[3/4] Engine Health (Docker)..." -ForegroundColor Yellow
    E14-Gtop-Status
    Start-Sleep -Seconds 2
    
    Write-Host "[4/4] Coherence Validation..." -ForegroundColor Yellow
    E14-K8S-Coherence
    
    Write-Host ""
    Write-Host "✓ System check complete" -ForegroundColor Green
    Write-Host ""
}

# ════════════════════════════════════════════════════════════════
# HELP & MENU
# ════════════════════════════════════════════════════════════════

function E14-Help {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║   E14 MASTER CONTROL CONSOLE — PowerShell Commands        ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    Write-Host "INITIALIZATION" -ForegroundColor Green
    Write-Host "  E14-Init                 Initialize console" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "DOCKER OPERATIONS" -ForegroundColor Green
    Write-Host "  E14-Docker-Status        Show running containers" -ForegroundColor Cyan
    Write-Host "  E14-Docker-Start         Start 14-engine cluster" -ForegroundColor Cyan
    Write-Host "  E14-Docker-Stop          Stop cluster" -ForegroundColor Cyan
    Write-Host "  E14-Docker-Logs <engine> Tail engine logs (default: 365)" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "KUBERNETES OPERATIONS" -ForegroundColor Yellow
    Write-Host "  E14-K8S-Deploy           Deploy to Kubernetes" -ForegroundColor Cyan
    Write-Host "  E14-K8S-Status           K8s pod status" -ForegroundColor Cyan
    Write-Host "  E14-K8S-Scale <n>        Scale to N replicas (1-10)" -ForegroundColor Cyan
    Write-Host "  E14-K8S-Coherence        7-dimension coherence check" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "MONITORING" -ForegroundColor Green
    Write-Host "  E14-Gtop-Status          Docker engine health" -ForegroundColor Cyan
    Write-Host "  E14-Gtop-Map             Docker topology" -ForegroundColor Cyan
    Write-Host "  E14-Gtop-K8-Status       K8s cluster health" -ForegroundColor Cyan
    Write-Host "  E14-Gtop-K8-Map          K8s topology" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "SYSTEM" -ForegroundColor Green
    Write-Host "  E14-Check-All            Full system check (Docker+K8s)" -ForegroundColor Cyan
    Write-Host "  E14-Help                 This menu" -ForegroundColor Cyan
    Write-Host ""
}

# Initialize on import
E14-Init
Write-Host "Ready. Type E14-Help for commands." -ForegroundColor Green
