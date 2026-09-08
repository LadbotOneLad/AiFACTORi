# Git Configuration for Windows — No Auth Failures

## Current Status

✓ User: E14 Docker  
✓ Email: e14@example.com  
✓ Remote: https://github.com/LadbotOneLad/AiFACTORi.git

## Problem

HTTPS Git on Windows often fails with:
- `Authentication failed`
- `401 Unauthorized`
- Credential manager issues
- SSL certificate errors

## Solution: SSH Keys (Recommended)

SSH is more reliable than HTTPS for GitHub on Windows.

### Step 1: Generate SSH Key (Windows PowerShell)

Open PowerShell as **Administrator**:

```powershell
# Generate key (press Enter 3 times for default options)
ssh-keygen -t ed25519 -C "e14@example.com"

# When prompted for filename, press Enter (default: C:\Users\YourUser\.ssh\id_ed25519)
# When prompted for passphrase, press Enter (no passphrase)
# When prompted to confirm passphrase, press Enter

# Verify key created:
dir $env:USERPROFILE\.ssh

# You should see:
# id_ed25519 (private key)
# id_ed25519.pub (public key)
```

### Step 2: Add SSH Key to GitHub

1. Copy your public key:
```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
```

2. Go to https://github.com/settings/keys

3. Click **New SSH key**

4. Title: `Windows Work Machine`

5. Paste key into "Key" field (Ctrl+V)

6. Click **Add SSH key**

7. Verify with GitHub password if prompted

### Step 3: Configure Git to Use SSH

```powershell
# Change from HTTPS to SSH
git remote set-url origin git@github.com:LadbotOneLad/AiFACTORi.git

# Verify:
git remote -v
# Should show: git@github.com:LadbotOneLad/AiFACTORi.git
```

### Step 4: Test SSH Connection

```powershell
ssh -T git@github.com
# Should show: "Hi LadbotOneLad! You've successfully authenticated..."

# If it hangs, you may need to start SSH agent:
# Get-Service ssh-agent | Start-Service
```

## Alternative: GitHub Personal Access Token (HTTPS)

If SSH doesn't work, use a Personal Access Token instead of password.

### Step 1: Create Personal Access Token

1. Go to https://github.com/settings/tokens/new

2. Select scopes:
   - ✓ `repo` (full control of private repositories)
   - ✓ `gist`
   - ✓ `workflow`

3. Copy the token (starts with `ghp_...`) — **save it securely**

### Step 2: Configure Git Credential Manager

```powershell
# Tell Git to store credentials
git config --global credential.helper manager-core

# Test push (will prompt for GitHub username + token as password)
git push
```

When prompted:
- Username: `LadbotOneLad`
- Password: Paste your Personal Access Token (Ctrl+V)

Windows will save it for future pushes.

## Configure Git Properly

```powershell
# Set your real info (update if needed)
git config --global user.name "E14 Docker"
git config --global user.email "e14@example.com"

# Set preferred editor (optional)
git config --global core.editor "notepad"

# Disable SSL verification (ONLY if you trust the network)
# git config --global http.sslVerify false

# View all config:
git config --global -l
```

## Commit and Push (All Together)

```powershell
# Navigate to project
cd C:\path\to\AiFACTORi

# Check what changed
git status

# Add all files
git add .

# Commit with message
git commit -m "Add ESP32 MQTT Docker integration for Windows

- Complete Docker Compose setup with MQTT broker
- ESP32 Arduino sketch with WiFi + sensors
- Python bridge service (paho-mqtt)
- Windows setup guides and automation scripts
- Quick-start and troubleshooting docs

Systems: temperature, humidity, motion sensors
Transport: WiFi → MQTT (port 1883) → XYO witness
Status: Ready for deployment" -m "" -m "Assisted-By: docker-agent"

# Push to GitHub
git push -u origin main
# (Or 'master' if that's your branch)

# Verify on GitHub
```

## Troubleshooting Git Failures

### "fatal: Authentication failed"

**HTTPS solution:**
```powershell
# Use credential manager
git config --global credential.helper manager-core

# Or clear stored credentials and retry
cmdkey /delete:git:https://github.com
# Then try push again (it will re-prompt)
```

**SSH solution:**
```powershell
# Verify SSH key exists
test-path $env:USERPROFILE\.ssh\id_ed25519

# Start SSH agent
Get-Service ssh-agent | Start-Service

# Add key to agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519

# Test:
ssh -T git@github.com
```

### "Connection timeout" / "Unable to connect"

Check firewall:
```powershell
# Test connectivity to GitHub
Test-NetConnection github.com -Port 22

# If fails, SSH is blocked. Use HTTPS instead:
git remote set-url origin https://github.com/LadbotOneLad/AiFACTORi.git
```

### "SSL: CERTIFICATE_VERIFY_FAILED"

```powershell
# Update Git and OpenSSL
git update-git-for-windows

# Or temporarily disable SSL (NOT recommended for production):
git config --global http.sslVerify false
```

### "Repository not found (404)"

```powershell
# Verify remote URL is correct
git remote -v

# If wrong, update it:
git remote set-url origin git@github.com:LadbotOneLad/AiFACTORi.git
# or
git remote set-url origin https://github.com/LadbotOneLad/AiFACTORi.git

# Verify you have access on GitHub:
# https://github.com/LadbotOneLad/AiFACTORi (public or your repo)
```

## Git Workflow (Windows)

### Daily work:

```powershell
# 1. See changes
git status

# 2. Stage files
git add .

# 3. Commit
git commit -m "Descriptive message about changes"

# 4. Push
git push

# 5. Pull latest (before starting work)
git pull
```

### If push fails after commit:

```powershell
# Pull first (merge any remote changes)
git pull origin main

# If conflicts:
# - Edit conflicting files
# - Resolve conflicts
# - git add .
# - git commit -m "Merge conflicts"

# Try push again
git push
```

## Verify Setup

```powershell
# Check user
git config --global user.name
# Should output: E14 Docker

# Check email
git config --global user.email
# Should output: e14@example.com

# Check remote
git remote -v
# Should output: git@github.com:LadbotOneLad/AiFACTORi.git (SSH)
# or https://github.com/LadbotOneLad/AiFACTORi.git (HTTPS)

# Test connection
if SSH:
  ssh -T git@github.com
if HTTPS:
  git ls-remote origin
# Both should succeed without prompting password

# Test commit + push
git status  # Check if clean
git log --oneline -3  # See last 3 commits
git branch  # See current branch
```

## Automated Workflow Script

Create `git-workflow.ps1`:

```powershell
param(
    [string]$message = "Update"
)

Write-Host "=== Git Workflow ===" -ForegroundColor Cyan

# Pull latest
Write-Host "Pulling latest..." -ForegroundColor Yellow
git pull

# Status
Write-Host "`nChanges:" -ForegroundColor Yellow
git status

# Stage all
Write-Host "`nStaging all files..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "Committing: $message" -ForegroundColor Yellow
git commit -m $message -m "" -m "Assisted-By: docker-agent"

# Push
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push

Write-Host "`n✓ Done!" -ForegroundColor Green
```

Usage:
```powershell
powershell -ExecutionPolicy Bypass -File git-workflow.ps1 -message "Add ESP32 setup"
```

## GitHub Actions (Optional)

Once repo is clean, set up CI/CD:

1. Go to https://github.com/LadbotOneLad/AiFACTORi/actions

2. Create workflow file: `.github/workflows/docker.yml`

3. Add Docker build/test on push

## Best Practices

✓ Commit frequently (small changes)  
✓ Use descriptive messages  
✓ Pull before push  
✓ Test locally before pushing  
✓ Never commit secrets (use .env files)  
✓ Use .gitignore for local files  

## Files to Never Commit

Already in `.gitignore`:
- `logs/`
- `__pycache__/`
- `.env` files
- `.venv/`
- `node_modules/`

Add if missing:
```
# credentials
config/.env.lock
config/.env.production

# large files
*.log
*.tmp
*.bak

# IDE
.vscode/
.idea/
*.swp
```

---

## Quick Reference

```powershell
# SSH Setup (recommended)
ssh-keygen -t ed25519 -C "e14@example.com"
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
# Paste at: https://github.com/settings/keys
git remote set-url origin git@github.com:LadbotOneLad/AiFACTORi.git

# Test
ssh -T git@github.com

# Commit + Push
git add .
git commit -m "Your message"
git push

# Troubleshoot
git config --global -l
git remote -v
git status
```

---

**Status**: Ready to commit  
**Next**: Run commit command above to push ESP32 files to GitHub
