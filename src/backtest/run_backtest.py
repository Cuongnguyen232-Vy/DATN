# -*- coding: utf-8 -*-
"""
Script: Execute Full Backtest & Generate Quant Tear-Sheet
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import time
from src.backtest.engine import QuantBacktester
from src.backtest.report import generate_html_report


def main():
    print("=" * 70)
    print("   VQUANT ALGORITHMIC TRADING SUITE - BACKTESTING EXECUTION")
    print("   Tac gia: Nguyen Manh Cuong _ B22DCCN099")
    print("=" * 70)

    print("\n[Backtest] Dang khoi tao mo phong chien luoc DCA Grid + ATR Shield tren XAUUSD...")
    t0 = time.time()
    
    backtester = QuantBacktester(
        initial_balance=10000.0,
        tp_points=800,
        base_grid_points=1500,
        enable_atr_shield=True,
        atr_multiplier=1.8,
        dd_cutoff_percent=30.0
    )

    results = backtester.run(timeframe="M15")
    elapsed = time.time() - t0
    m = results['metrics']

    print(f"\n>> [Hoan tat Mo phong] Thoi gian chay: {elapsed:.2f} giay.")
    print("-" * 70)
    print(f" • Von ban dau (Initial Capital)   : ${m['initial_capital']:,.2f}")
    print(f" • Von cuoi ky (Final Equity)       : ${m['final_equity']:,.2f}")
    print(f" • Loi nhuan rong (Net Profit)      : ${m['net_profit']:+,.2f} ({m['return_pct']:+.2f}%)")
    print(f" • Tong so lenh (Total Trades)      : {m['total_trades']} lenh")
    print(f" • Ty le thang (Win Rate)           : {m['win_rate_pct']:.2f}% ({m['winning_trades']} Thang / {m['losing_trades']} Lo)")
    print(f" • Profit Factor (PF)               : {m['profit_factor']:.2f}")
    print(f" • Max Drawdown (%)                 : {m['max_drawdown_pct']:.2f}% (-${m['max_drawdown_usd']:,.2f})")
    print(f" • Sharpe Ratio (Annualized)        : {m['sharpe_ratio']:.2f}")
    print(f" • Sortino Ratio                    : {m['sortino_ratio']:.2f}")
    print(f" • Calmar Ratio                     : {m['calmar_ratio']:.2f}")
    print("-" * 70)

    print("\n[Report] Dang bien dich bao cao HTML tuong tac...")
    report_file = generate_html_report(results, "backtest_report_XAUUSD.html")
    print(f">> File bao cao HTML: file:///{report_file.replace(os.sep, '/')}")
    print("=" * 70)
    
    try:
        import webbrowser
        webbrowser.open(f"file:///{report_file.replace(os.sep, '/')}")
        print(">> Da tu dong mo bao cao Tear-Sheet tren trinh duyet!")
    except Exception:
        pass
        
    return report_file


if __name__ == "__main__":
    main()

