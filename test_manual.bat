@echo off
chcp 65001 > nul
title VQuant Manual Test Suite
cd /d "c:\KLTNN"
python manual_test.py
pause
