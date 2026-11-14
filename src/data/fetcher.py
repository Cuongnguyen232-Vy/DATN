# -*- coding: utf-8 -*-
"""
Module: MT5 & Multi-source Market Data Fetcher
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    Dual-engine market data provider. Connects to MetaTrader 5 terminal with
    automatic symbol resolution (XAUUSD, XAUUSDm, GOLD), and features seamless
    instant offline fallback to standardized local historical cache when offline.
"""

import os
import sys
import time
import subprocess
import pandas as pd
import MetaTrader5 as mt5

from src.config import MT5_PATH, SYMBOL
from src.data.historical_loader import load_cached_data, ensure_offline_datasets, sync_and_append_candles


class MT5Fetcher:
    def __init__(self, symbol: str = None):
        self.symbol = symbol or SYMBOL
        self.connected_mt5 = False

    def is_terminal_running(self) -> bool:
        """Kiểm tra nhanh xem tiến trình terminal64.exe có đang chạy trên Windows hay không"""
        try:
            res = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq terminal64.exe"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return "terminal64.exe" in res.stdout.lower()
        except Exception:
            return False

    def initialize(self) -> bool:
        """
        Attempts connection to MT5 terminal if running. If MT5 is not open or offline,
        instantly activates offline research mode without blocking or crashing.
        """
        print(f"\n[DataEngine] Kiem tra trang thai he thong MT5...")
        
        terminal_active = self.is_terminal_running()
        if not terminal_active:
            print("[DataEngine] MetaTrader 5 Terminal chua duoc bat tren Desktop.")
            print(">> [DataEngine - Fallback]: Tu dong kich hoat Kho du lieu Offline Dataset (Cache chuan hoa).")
            ensure_offline_datasets()
            self.connected_mt5 = False
            return True

        # MT5 is running, attach to it
        try:
            print(f"[DataEngine] Phat hien MT5 Terminal dang hoat dong. Dang handshake...")
            if mt5.initialize(path=MT5_PATH, timeout=3000):
                self.connected_mt5 = True
                print(">> [Handshake MT5]: Ket noi thanh cong toi terminal MetaTrader 5!")
                # Verify and auto-resolve gold symbol
                for sym_candidate in [self.symbol, "XAUUSD", "XAUUSDm", "GOLD", "XAUUSD.a"]:
                    if mt5.symbol_select(sym_candidate, True):
                        self.symbol = sym_candidate
                        print(f">> [Symbol Resolved]: Da xac dinh ma cap tien hop le: '{self.symbol}'")
                        break
                return True
            else:
                err = mt5.last_error()
                print(f"[DataEngine] MT5 handshake loi: {err}. Chuyen sang che do Offline Dataset.")
        except Exception as e:
            print(f"[DataEngine] Ngoai le MT5: {e}")

        # Seamless fallback
        ensure_offline_datasets()
        self.connected_mt5 = False
        return True

    def fetch_data(self, timeframe, n_candles: int = 200) -> pd.DataFrame:
        """
        Fetches n_candles for the specified timeframe.
        Priority:
            1. MT5 Live Rates (if connected & authorized)
            2. High-precision Standardized Local Cache (Offline/Simulation)
        """
        if self.connected_mt5:
            try:
                mt5.symbol_select(self.symbol, True)
                rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, n_candles)
                if rates is not None and len(rates) > 0:
                    df = pd.DataFrame(rates)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df.dropna(inplace=True)
                    # Tự động cập nhật liên tục nến mới nhất vào kho dữ liệu CSV
                    sync_and_append_candles(df, timeframe)
                    return df
            except Exception as e:
                print(f"[DataEngine] Loi fetch MT5: {e}. Chuyen sang du lieu offline.")

        # Fallback to local cache
        tf_str = "H4" if (timeframe == 16388 or "4" in str(timeframe) or "H4" in str(timeframe)) else "M15"
        df_cached = load_cached_data(tf_str)
        if df_cached is not None and len(df_cached) > 0:
            return df_cached.tail(n_candles).copy().reset_index(drop=True)

        print("[DataEngine] Canh bao: Khong the tai du lieu ca Online va Offline!")
        return None

    def shutdown(self):
        if self.connected_mt5:
            mt5.shutdown()
            self.connected_mt5 = False
