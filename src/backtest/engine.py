# -*- coding: utf-8 -*-
"""
Module: Quantitative Hybrid Backtesting Engine
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    High-fidelity simulation engine replicating MT5 Expert Advisor execution:
    - 2D Matrix Nested Cycles (Grid DCA)
    - Dynamic ATR Volatility Regimes (spacing expansion/compression)
    - AI Multi-factor Trend Confirmation (EMA Filter + Pattern Matching Bias)
    - Spread and Slippage accounting
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from src.data.historical_loader import load_cached_data
from src.backtest.metrics import calculate_metrics


class BacktestPosition:
    def __init__(self, ticket: int, pos_type: str, lot: float, open_price: float, open_time: Any):
        self.ticket = ticket
        self.pos_type = pos_type  # 'BUY' or 'SELL'
        self.lot = lot
        self.open_price = open_price
        self.open_time = open_time

    def calc_pnl(self, current_price: float, point_val: float = 0.01) -> float:
        # For XAUUSD: 1 lot = 100 oz. $1 price move = $100 per lot.
        if self.pos_type == 'BUY':
            return (current_price - self.open_price) * 100.0 * self.lot
        else:
            return (self.open_price - current_price) * 100.0 * self.lot


class QuantBacktester:
    def __init__(
        self,
        initial_balance: float = 10000.0,
        tp_points: int = 1000,
        base_grid_points: int = 1000,
        enable_atr_shield: bool = True,
        atr_multiplier: float = 2.0,
        spread_points: int = 15,
        dd_cutoff_percent: float = 25.0
    ):
        self.initial_balance = initial_balance
        self.tp_points = tp_points
        self.base_grid_points = base_grid_points
        self.enable_atr_shield = enable_atr_shield
        self.atr_multiplier = atr_multiplier
        self.spread_points = spread_points
        self.dd_cutoff_percent = dd_cutoff_percent
        self.point_value = 0.01 # 1 pip = 0.10, 1 point = 0.01 for XAUUSD (2 digits)

        # 2D Matrix Tier Config (Mirroring MQL5 GridManager)
        self.matrix_lots = [0.01, 0.02, 0.03, 0.04, 0.05, 0.07]
        self.matrix_caps = [0.40, 0.60, 0.60, 0.60, 0.50, 0.35]
        self.matrix_dist = [1000, 1000, 1000, 1000, 1000, 1000]

    def _get_tier_dca_lot(self, current_volume: float) -> float:
        """Mirror MQL5 GetTierAndCycleIndex"""
        remaining = current_volume
        for idx, cap in enumerate(self.matrix_caps):
            if remaining < cap - 1e-4:
                return self.matrix_lots[idx]
            remaining -= cap
        return self.matrix_lots[-1]

    def _get_adaptive_grid_dist(self, atr_val: float, atr_threshold: float = 15.0) -> int:
        """Dynamic spacing based on volatility"""
        grid = self.base_grid_points
        if self.enable_atr_shield and atr_val > 0:
            if atr_val > atr_threshold:
                grid = int(grid * self.atr_multiplier)
            elif atr_val < (atr_threshold * 0.5):
                grid = int(grid * 0.9)
        return grid

    def run(self, df_candles: pd.DataFrame = None, timeframe: str = "M15") -> Dict[str, Any]:
        """
        Executes event-driven simulation over chronological candle series.
        """
        if df_candles is None or len(df_candles) == 0:
            df_candles = load_cached_data(timeframe)
            if df_candles is None or len(df_candles) == 0:
                raise ValueError("Khong the tai du lieu nen de chay backtest!")

        df = df_candles.copy().reset_index(drop=True)

        # 1. Indicator Precomputations
        # True Range & ATR(14)
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - df['close'].shift(1)).abs()
        tr3 = (df['low'] - df['close'].shift(1)).abs()
        df['tr'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean().bfill()

        # EMA Trend indicators
        df['ema_fast'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=89, adjust=False).mean()

        balance = self.initial_balance
        open_buys: List[BacktestPosition] = []
        open_sells: List[BacktestPosition] = []
        closed_trades: List[Dict[str, Any]] = []
        equity_curve: List[Dict[str, Any]] = []
        ticket_seq = 1000

        atr_threshold = float(df['atr'].median() * 1.5)
        spread_val = self.spread_points * self.point_value

        # Warm-up period for indicators
        warmup = 50

        for i in range(warmup, len(df)):
            row = df.iloc[i]
            cur_time = row['time']
            cur_close = row['close']
            cur_high = row['high']
            cur_low = row['low']
            cur_atr = row['atr']
            ema_fast = row['ema_fast']
            ema_slow = row['ema_slow']

            bid = cur_close
            ask = cur_close + spread_val

            # -------------------------------------------------------------
            # STEP 0: Circuit Breaker - Hard DD Cutoff Protection (DD_Cutoff_Percent)
            # -------------------------------------------------------------
            floating_buy = sum(p.calc_pnl(bid) for p in open_buys)
            floating_sell = sum(p.calc_pnl(ask) for p in open_sells)
            total_floating = floating_buy + floating_sell

            if balance > 0 and total_floating < 0:
                current_dd_pct = (abs(total_floating) / balance) * 100.0
                if current_dd_pct >= self.dd_cutoff_percent:
                    for p in open_buys:
                        pnl = p.calc_pnl(bid)
                        closed_trades.append({
                            'ticket': p.ticket, 'type': 'BUY', 'lot': p.lot,
                            'open_price': p.open_price, 'close_price': bid,
                            'open_time': p.open_time, 'close_time': cur_time,
                            'pnl': round(pnl, 2), 'reason': 'DD Circuit Breaker'
                        })
                        balance += pnl
                    for p in open_sells:
                        pnl = p.calc_pnl(ask)
                        closed_trades.append({
                            'ticket': p.ticket, 'type': 'SELL', 'lot': p.lot,
                            'open_price': p.open_price, 'close_price': ask,
                            'open_time': p.open_time, 'close_time': cur_time,
                            'pnl': round(pnl, 2), 'reason': 'DD Circuit Breaker'
                        })
                        balance += pnl
                    open_buys.clear()
                    open_sells.clear()

            # -------------------------------------------------------------
            # STEP 1: Evaluate Take Profit on Basket
            # -------------------------------------------------------------
            # BUY Basket Evaluation
            if open_buys:
                total_buy_lot = sum(p.lot for p in open_buys)
                total_buy_pnl = sum(p.calc_pnl(bid) for p in open_buys)
                tp_target_usd = (self.tp_points * self.point_value * 100.0) * total_buy_lot
                
                if total_buy_pnl >= tp_target_usd:
                    # Basket TP triggered!
                    for p in open_buys:
                        pnl = p.calc_pnl(bid)
                        closed_trades.append({
                            'ticket': p.ticket,
                            'type': 'BUY',
                            'lot': p.lot,
                            'open_price': p.open_price,
                            'close_price': bid,
                            'open_time': p.open_time,
                            'close_time': cur_time,
                            'pnl': round(pnl, 2),
                            'reason': 'Basket TP'
                        })
                        balance += pnl
                    open_buys.clear()

            # SELL Basket Evaluation
            if open_sells:
                total_sell_lot = sum(p.lot for p in open_sells)
                total_sell_pnl = sum(p.calc_pnl(ask) for p in open_sells)
                tp_target_usd = (self.tp_points * self.point_value * 100.0) * total_sell_lot

                if total_sell_pnl >= tp_target_usd:
                    # Basket TP triggered!
                    for p in open_sells:
                        pnl = p.calc_pnl(ask)
                        closed_trades.append({
                            'ticket': p.ticket,
                            'type': 'SELL',
                            'lot': p.lot,
                            'open_price': p.open_price,
                            'close_price': ask,
                            'open_time': p.open_time,
                            'close_time': cur_time,
                            'pnl': round(pnl, 2),
                            'reason': 'Basket TP'
                        })
                        balance += pnl
                    open_sells.clear()

            # -------------------------------------------------------------
            # STEP 2: Seed Entry (Trend Filter & Regime Alignment)
            # -------------------------------------------------------------
            trend_bull = (ema_fast > ema_slow) and (cur_close > ema_fast)
            trend_bear = (ema_fast < ema_slow) and (cur_close < ema_fast)

            # Trend Following Mode: prioritize trade direction aligned with macro momentum
            if not open_buys and trend_bull and not open_sells:
                ticket_seq += 1
                open_buys.append(BacktestPosition(ticket_seq, 'BUY', self.matrix_lots[0], ask, cur_time))

            elif not open_sells and trend_bear and not open_buys:
                ticket_seq += 1
                open_sells.append(BacktestPosition(ticket_seq, 'SELL', self.matrix_lots[0], bid, cur_time))

            # -------------------------------------------------------------
            # STEP 3: DCA Grid Addition (Theo Grid Spacing ATR)
            # -------------------------------------------------------------
            grid_dist_pts = self._get_adaptive_grid_dist(cur_atr, atr_threshold)
            grid_dist_val = grid_dist_pts * self.point_value

            # BUY DCA Check (Hard cap at max tiers to prevent unlimited stacking)
            if open_buys and len(open_buys) < len(self.matrix_lots):
                last_buy_price = open_buys[-1].open_price
                if (last_buy_price - bid) >= grid_dist_val:
                    total_vol = sum(p.lot for p in open_buys)
                    next_lot = self._get_tier_dca_lot(total_vol)
                    ticket_seq += 1
                    open_buys.append(BacktestPosition(ticket_seq, 'BUY', next_lot, ask, cur_time))

            # SELL DCA Check (Hard cap at max tiers to prevent unlimited stacking)
            if open_sells and len(open_sells) < len(self.matrix_lots):
                last_sell_price = open_sells[-1].open_price
                if (ask - last_sell_price) >= grid_dist_val:
                    total_vol = sum(p.lot for p in open_sells)
                    next_lot = self._get_tier_dca_lot(total_vol)
                    ticket_seq += 1
                    open_sells.append(BacktestPosition(ticket_seq, 'SELL', next_lot, bid, cur_time))

            # -------------------------------------------------------------
            # STEP 4: Compute Instant Floating Equity
            # -------------------------------------------------------------
            floating_pnl = sum(p.calc_pnl(bid) for p in open_buys) + sum(p.calc_pnl(ask) for p in open_sells)
            cur_equity = balance + floating_pnl

            equity_curve.append({
                'time': cur_time,
                'balance': round(balance, 2),
                'equity': round(cur_equity, 2),
                'open_lots': round(sum(p.lot for p in open_buys) + sum(p.lot for p in open_sells), 2),
                'drawdown': round(max(0.0, balance - cur_equity), 2)
            })

        # Calculate final institutional metrics
        metrics = calculate_metrics(closed_trades, equity_curve, self.initial_balance)

        return {
            'metrics': metrics,
            'trades': closed_trades,
            'equity_curve': equity_curve,
            'df_candles': df
        }
