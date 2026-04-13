cd "C:\Users\Admin\OneDrive\Desktop\~E14-"

# Health check
Write-Host "=== SYSTEM HEALTH ===" -ForegroundColor Cyan
docker-compose ps

# Service logs (last 5 lines each)
Write-Host "`n=== E14_ORACLE ===" -ForegroundColor Green
docker-compose logs e14_oracle --tail 5

Write-Host "`n=== E14_LIVE ===" -ForegroundColor Green
docker-compose logs e14_live --tail 5

Write-Host "`n=== E14_DRIFTWATCHER ===" -ForegroundColor Green
docker-compose logs e14_driftwatcher --tail 5

Write-Host "`n=== E14_TASKMANAGER ===" -ForegroundColor Green
docker-compose logs e14_taskmanager --tail 5

# Quick status
Write-Host "`n=== QUICK CHECK ===" -ForegroundColor Yellow
docker-compose logs e14_live --tail 1 | Select-String "EXECUTED|QUEUED"
docker-compose logs e14_oracle --tail 1 | Select-String "K="
docker-compose logs e14_driftwatcher --tail 1 | Select-String "K="
