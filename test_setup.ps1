#!/usr/bin/env powershell
# Quick test for ESP32 + Docker setup on Windows

Write-Host "=== ESP32 + Docker MQTT Test ===" -ForegroundColor Cyan

# Test 1: Docker running?
Write-Host "`n[1] Checking Docker..." -ForegroundColor Yellow
$docker = docker ps 2>$null
if ($?) {
    Write-Host "✓ Docker is running" -ForegroundColor Green
} else {
    Write-Host "✗ Docker not running - start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Test 2: MQTT broker running?
Write-Host "`n[2] Checking MQTT Broker..." -ForegroundColor Yellow
$mqtt = docker ps --filter "name=mqtt_broker" --format "{{.Status}}" 2>$null
if ($mqtt -match "Up") {
    Write-Host "✓ MQTT Broker is running" -ForegroundColor Green
} else {
    Write-Host "✗ MQTT Broker not running" -ForegroundColor Red
    Write-Host "Start containers: docker compose up -d" -ForegroundColor Yellow
    exit 1
}

# Test 3: ESP32 Bridge running?
Write-Host "`n[3] Checking ESP32 Bridge..." -ForegroundColor Yellow
$bridge = docker ps --filter "name=esp32_bridge" --format "{{.Status}}" 2>$null
if ($bridge -match "Up") {
    Write-Host "✓ ESP32 Bridge is running" -ForegroundColor Green
} else {
    Write-Host "✗ ESP32 Bridge not running" -ForegroundColor Red
    exit 1
}

# Test 4: MQTT port open?
Write-Host "`n[4] Checking port 1883..." -ForegroundColor Yellow
$port = netstat -an 2>$null | Select-String ":1883" | Select-String "LISTEN"
if ($port) {
    Write-Host "✓ Port 1883 listening" -ForegroundColor Green
} else {
    Write-Host "⚠ Port 1883 not listening (firewall?)" -ForegroundColor Yellow
}

# Test 5: Bridge logs
Write-Host "`n[5] Bridge connection status..." -ForegroundColor Yellow
$logs = docker logs esp32_bridge 2>&1 | Select-String "Connected" | Select-Object -Last 1
if ($logs) {
    Write-Host "✓ $logs" -ForegroundColor Green
} else {
    Write-Host "? Check: docker logs esp32_bridge" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Docker Containers: Ready" -ForegroundColor Green
Write-Host "MQTT Broker: Port 1883" -ForegroundColor Green
Write-Host "ESP32 Status: Waiting for messages" -ForegroundColor Yellow
Write-Host "`nNext: Flash esp32_sketch.ino to your ESP32 board" -ForegroundColor Cyan
Write-Host "Then check logs: docker logs -f esp32_bridge" -ForegroundColor Cyan
