# -*- coding: utf-8 -*-
"""
Module: Feature Engineering & Quantitative Indicators
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    Trích xuất các đặc trưng phân tích kỹ thuật chuẩn mực, loại bỏ hoàn toàn
    data leakage và chuẩn hóa dữ liệu cho các mô hình học sâu.
"""

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange


class FeatureEngine:
    @staticmethod
    def add_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Trích xuất bộ đặc trưng kỹ thuật tài chính đa chiều (Multivariate Feature Matrix).
        Bảo đảm tính nhân quả (Causal), không có Lookahead Bias và không Data Leakage.
        """
        df = df.copy()

        # 1. Momentum Indicators
        rsi = RSIIndicator(close=df['close'], window=14)
        df['rsi'] = rsi.rsi()

        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()

        roc = ROCIndicator(close=df['close'], window=10)
        df['roc_10'] = roc.roc()

        # 2. Trend Indicators
        macd = MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()

        ema20 = EMAIndicator(close=df['close'], window=20).ema_indicator()
        ema50 = EMAIndicator(close=df['close'], window=50).ema_indicator()
        df['ema_20'] = ema20
        df['ema_50'] = ema50
        # Spread chuẩn hóa theo giá đóng cửa
        df['ema_spread_pct'] = ((ema20 - ema50) / df['close']) * 100.0

        # 3. Volatility Indicators
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        df['bb_pct'] = bb.bollinger_pband()

        atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
        df['atr_14'] = atr.average_true_range()
        df['atr_norm'] = (df['atr_14'] / df['close']) * 100.0

        # Normalized Candle Range
        df['hl_range_pct'] = ((df['high'] - df['low']) / df['close']) * 100.0

        # 4. Volume Dynamics (nếu có tick_volume)
        if 'tick_volume' in df.columns:
            vol_mean = df['tick_volume'].rolling(window=20).mean().bfill()
            df['vol_ratio'] = df['tick_volume'] / (vol_mean + 1e-6)

        # Loại bỏ các dòng NaN phát sinh do cửa sổ tính toán quá khứ
        df.dropna(inplace=True)
        return df
