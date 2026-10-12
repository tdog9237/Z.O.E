@echo off
title Z.O.E - Wilsonian RG Braid 1.01B MoE Multimodal AI Companion
color 0B
cd /d "d:\Antigravity\zoe-ai"

echo ======================================================================
echo           Z.O.E MULTIMODAL AI COMPANION (100%% LOCAL)
echo ======================================================================
echo   Architecture:  Continuous Wilsonian Neural RG Braid 1.01B MoE
echo   Checkpoint:    best_model_v37_apex_moe.pt (8-Expert Sparse MoE)
echo   Context:       4,096 Tokens (YaRN RoPE)
echo   Hardware VRAM: ~75%% Allocation on RTX 5070 Ti (8.84 GB / 11.94 GB)
echo   Features:      CUDA Faster-Whisper + FAISS GPU Vector Memory + Edge-TTS
echo   Web Interface: http://localhost:5001/
echo ======================================================================
echo.

set PYTHON="D:\Antigravity\Polymath\.venv\Scripts\python.exe"

if not exist %PYTHON% (
    echo [ERROR] Python environment not found at %PYTHON%
    pause
    exit /b 1
)

echo [1/2] Opening Z.O.E Web Interface...
start "Z.O.E Browser" cmd /c "timeout /t 4 >nul & start http://localhost:5001/"

echo [2/2] Starting Z.O.E Multimodal Server...
%PYTHON% zoe_server.py

pause
