# -*- coding: utf-8 -*-
"""
Module: Institutional Quantitative Performance Metrics
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    Computes rigorous Wall-Street quantitative metrics for algorithmic trading
    evaluation (Sharpe, Sortino, Calmar, Max Drawdown, Profit Factor, Win Rate).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def calculate_metrics(
    trades: list,
    equity_history: list,
    initial_capital: float = 10000.0,
    risk_free_rate: float = 0.04
) -> Dict[str, Any]:
    """
    Computes comprehensive quant metrics for a backtest execution.
    """
    # 1. Equity Series Analytics
    if not equity_history:
        equity_df = pd.DataFrame([{'time': pd.Timestamp.now(), 'equity': initial_capital, 'balance': initial_capital}])
    else:
        equity_df = pd.DataFrame(equity_history)
        
    equity_series = equity_df['equity'].values
    final_equity = equity_series[-1] if len(equity_series) > 0 else initial_capital
    net_profit = final_equity - initial_capital
    return_pct = (net_profit / initial_capital) * 100.0

    # Drawdown calculation
    peak = np.maximum.accumulate(equity_series)
    drawdowns = (peak - equity_series)
    drawdown_pcts = np.where(peak > 0, (drawdowns / peak) * 100.0, 0.0)
    
    max_dd_usd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0
    max_dd_pct = float(np.max(drawdown_pcts)) if len(drawdown_pcts) > 0 else 0.0

    # 2. Trade Log Analytics
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    total_trades = len(trades_df)
    
    if total_trades > 0 and 'pnl' in trades_df.columns:
        pnl_series = trades_df['pnl'].values
        wins = pnl_series[pnl_series > 0]
        losses = pnl_series[pnl_series <= 0]
        
        n_wins = len(wins)
        n_losses = len(losses)
        win_rate = (n_wins / total_trades) * 100.0
        
        gross_profit = float(np.sum(wins)) if n_wins > 0 else 0.0
        gross_loss = float(abs(np.sum(losses))) if n_losses > 0 else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.0 if gross_profit > 0 else 1.0)
        
        avg_trade = float(np.mean(pnl_series))
        avg_win = float(np.mean(wins)) if n_wins > 0 else 0.0
        avg_loss = float(np.mean(losses)) if n_losses > 0 else 0.0
        payoff_ratio = (abs(avg_win / avg_loss)) if avg_loss != 0 else 1.0
        max_win = float(np.max(wins)) if n_wins > 0 else 0.0
        max_loss = float(np.min(losses)) if n_losses > 0 else 0.0
    else:
        n_wins = n_losses = 0
        win_rate = 0.0
        gross_profit = gross_loss = 0.0
        profit_factor = 1.0
        avg_trade = avg_win = avg_loss = max_win = max_loss = 0.0
        payoff_ratio = 1.0

    # 3. Time Series Risk-Adjusted Returns (Sharpe, Sortino, Calmar)
    if len(equity_series) > 1:
        # Step returns
        returns = np.diff(equity_series) / equity_series[:-1]
        mean_ret = np.mean(returns)
        std_ret = np.std(returns)
        
        # Annualization factor: assuming M15 data (approx 24 * 4 * 252 steps/year)
        annual_factor = np.sqrt(24 * 4 * 252)
        rf_per_step = (risk_free_rate) / (24 * 4 * 252)
        
        # Sharpe Ratio
        if std_ret > 1e-9:
            sharpe_ratio = float(((mean_ret - rf_per_step) / std_ret) * annual_factor)
        else:
            sharpe_ratio = 0.0
            
        # Sortino Ratio (Downside deviation only)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_std = np.std(downside_returns)
            if downside_std > 1e-9:
                sortino_ratio = float(((mean_ret - rf_per_step) / downside_std) * annual_factor)
            else:
                sortino_ratio = sharpe_ratio
        else:
            sortino_ratio = sharpe_ratio * 1.5

        # Calmar Ratio
        if max_dd_pct > 0:
            calmar_ratio = float(return_pct / max_dd_pct)
        else:
            calmar_ratio = return_pct
    else:
        sharpe_ratio = sortino_ratio = calmar_ratio = 0.0

    return {
        'initial_capital': round(initial_capital, 2),
        'final_equity': round(final_equity, 2),
        'net_profit': round(net_profit, 2),
        'return_pct': round(return_pct, 2),
        'total_trades': total_trades,
        'winning_trades': n_wins,
        'losing_trades': n_losses,
        'win_rate_pct': round(win_rate, 2),
        'profit_factor': round(profit_factor, 2),
        'gross_profit': round(gross_profit, 2),
        'gross_loss': round(gross_loss, 2),
        'max_drawdown_usd': round(max_dd_usd, 2),
        'max_drawdown_pct': round(max_dd_pct, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'sortino_ratio': round(sortino_ratio, 2),
        'calmar_ratio': round(calmar_ratio, 2),
        'avg_trade_pnl': round(avg_trade, 2),
        'payoff_ratio': round(payoff_ratio, 2),
        'max_win': round(max_win, 2),
        'max_loss': round(max_loss, 2)
    }
