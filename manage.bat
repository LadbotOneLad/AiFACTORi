@echo off
REM ESP32 Docker Management - Windows Batch

setlocal enabledelayedexpansion

:menu
cls
echo.
echo === ESP32 MQTT Docker Manager ===
echo.
echo 1. Start containers
echo 2. Stop containers
echo 3. View ESP32 Bridge logs
echo 4. View MQTT logs
echo 5. Test setup
echo 6. Restart containers
echo 7. Exit
echo.
set /p choice="Enter choice [1-7]: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto logs_bridge
if "%choice%"=="4" goto logs_mqtt
if "%choice%"=="5" goto test
if "%choice%"=="6" goto restart
if "%choice%"=="7" goto end

goto menu

:start
cls
echo Starting containers...
docker compose up -d
echo.
echo Waiting for services to start...
timeout /t 3 /nobreak
docker ps
pause
goto menu

:stop
cls
echo Stopping containers...
docker compose down
echo Done.
pause
goto menu

:logs_bridge
cls
echo ESP32 Bridge logs (Press Ctrl+C to stop):
echo.
docker logs -f esp32_bridge
goto menu

:logs_mqtt
cls
echo MQTT Broker logs (Press Ctrl+C to stop):
echo.
docker logs -f mqtt_broker
goto menu

:test
cls
echo Running setup test...
echo.
powershell -ExecutionPolicy Bypass -File test_setup.ps1
echo.
pause
goto menu

:restart
cls
echo Restarting containers...
docker compose down
timeout /t 2 /nobreak
docker compose up -d
echo.
docker ps
pause
goto menu

:end
exit /b 0
