@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title VQuant 24-7 Sentinel Autonomous Engine
color 0A
cd /d "c:\KLTNN"

echo ======================================================================
echo    VQUANT 24/7 AUTONOMOUS SENTINEL - NEWS FILTER AND SIGNAL ENGINE
echo    Tac gia: Nguyen Manh Cuong _ B22DCCN099 (PTIT)
echo ======================================================================
echo.
echo Dang khoi dong he thong giam sat tin tuc va ban tin hieu 24/7...
echo Tin hieu se duoc tu dong ban truc tiep ve Telegram va MetaTrader 5 EA.
echo Nhan Ctrl+C de dung chuong trinh.
echo.

python -u src\engine\sentinel_service.py

echo.
echo Chuong trinh Sentinel da dung.
pause

