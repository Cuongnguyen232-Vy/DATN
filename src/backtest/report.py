# -*- coding: utf-8 -*-
"""
Module: Institutional HTML Tear-Sheet & Visual Reporting Engine
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    Generates interactive Plotly-based financial tear-sheets featuring:
    - High-contrast Wall-Street Dark UI / Glassmorphism KPI Dashboard
    - Interactive Dual-pane Equity & Underwater Drawdown Curves
    - Audited Trade Execution Log Table
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.config import DATA_DIR


def generate_html_report(backtest_results: dict, output_filename: str = "backtest_report_XAUUSD.html") -> str:
    """
    Renders an interactive HTML tear-sheet with Plotly charts and financial summary cards.
    """
    metrics = backtest_results['metrics']
    equity_data = backtest_results['equity_curve']
    trades_data = backtest_results['trades']

    df_equity = pd.DataFrame(equity_data)
    df_trades = pd.DataFrame(trades_data)

    output_path = os.path.join(DATA_DIR, output_filename)

    # 1. Build Subplot Figure (Top: Equity/Balance, Bottom: Underwater Drawdown)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Cumulative Equity & Balance Trajectory ($ USD)", "Underwater Drawdown Exposure (%)"),
        row_heights=[0.70, 0.30]
    )

    # Balance line
    fig.add_trace(
        go.Scatter(
            x=df_equity['time'],
            y=df_equity['balance'],
            mode='lines',
            name='Realized Balance',
            line=dict(color='#3B82F6', width=2)
        ),
        row=1, col=1
    )

    # Floating Equity line
    fig.add_trace(
        go.Scatter(
            x=df_equity['time'],
            y=df_equity['equity'],
            mode='lines',
            name='Mark-to-Market Equity',
            line=dict(color='#10B981', width=1.5),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.05)'
        ),
        row=1, col=1
    )

    # Underwater Drawdown (%)
    peak_equity = df_equity['equity'].cummax()
    dd_pct = ((df_equity['equity'] - peak_equity) / peak_equity) * 100.0

    fig.add_trace(
        go.Scatter(
            x=df_equity['time'],
            y=dd_pct,
            mode='lines',
            name='Drawdown Depth %',
            line=dict(color='#F43F5E', width=1.5),
            fill='tozeroy',
            fillcolor='rgba(244, 63, 94, 0.15)'
        ),
        row=2, col=1
    )

    # Styling Dark Theme Plotly
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#111625',
        plot_bgcolor='#0B0E17',
        font=dict(family="Inter, -apple-system, sans-serif", color='#94A3B8'),
        hovermode='x unified',
        height=640,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(17, 22, 37, 0.85)',
            bordercolor='#1E2738',
            borderwidth=1,
            font=dict(size=11)
        )
    )
    fig.update_yaxes(title_text="Capital ($ USD)", row=1, col=1, gridcolor='#1E2738', zerolinecolor='#1E2738', title_font=dict(size=11, color='#64748B'))
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1, gridcolor='#1E2738', zerolinecolor='#1E2738', title_font=dict(size=11, color='#64748B'))
    fig.update_xaxes(gridcolor='#1E2738')

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # 2. Build Trade Table HTML Rows with BUY/SELL Filtering
    buy_count = int((df_trades['type'] == 'BUY').sum()) if not df_trades.empty else 0
    sell_count = int((df_trades['type'] == 'SELL').sum()) if not df_trades.empty else 0
    total_trades_count = len(df_trades) if not df_trades.empty else 0

    table_rows = ""
    if not df_trades.empty:
        for _, tr in df_trades.iterrows():
            pnl_val = tr['pnl']
            pnl_color = "#10B981" if pnl_val >= 0 else "#F43F5E"
            tr_type = str(tr['type']).upper()
            is_buy = tr_type == 'BUY'
            badge_bg = "rgba(16, 185, 129, 0.12)" if is_buy else "rgba(244, 63, 94, 0.12)"
            badge_color = "#34D399" if is_buy else "#FB7185"
            badge_border = "rgba(16, 185, 129, 0.25)" if is_buy else "rgba(244, 63, 94, 0.25)"
            
            table_rows += f"""
            <tr class="trade-item" data-type="{tr_type}">
                <td class="font-mono text-muted">#{tr['ticket']}</td>
                <td class="text-muted">{str(tr['open_time'])[:19]}</td>
                <td><span class="badge" style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border};">{tr['type']}</span></td>
                <td class="font-mono">{tr['lot']:.2f}</td>
                <td class="font-mono">${tr['open_price']:.2f}</td>
                <td class="font-mono">${tr['close_price']:.2f}</td>
                <td class="font-mono" style="color: {pnl_color}; font-weight: 600;">{pnl_val:+,.2f} USD</td>
                <td class="text-muted">{tr['reason']}</td>
            </tr>
            """
    else:
        table_rows = "<tr><td colspan='8' style='text-align: center; color: #64748B; padding: 32px;'>Chưa có lệnh chốt trong kỳ kiểm thử.</td></tr>"

    # 3. HTML Assembly with Institutional Design
    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VQuant Portfolio Performance Tear-Sheet</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-page: #0B0E17;
            --bg-surface: #111625;
            --bg-subtle: #171E31;
            --border: #1E2738;
            --border-hover: #2E3B52;
            --text-primary: #F1F5F9;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --accent-blue: #3B82F6;
            --accent-emerald: #10B981;
            --accent-rose: #F43F5E;
            --accent-amber: #F59E0B;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background-color: var(--bg-page);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 36px 40px;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}
        .font-mono {{
            font-family: 'JetBrains Mono', monospace;
            font-feature-settings: 'tnum' 1;
        }}
        .text-muted {{ color: var(--text-muted); }}

        /* Masthead Header */
        .masthead {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 28px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .masthead-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 6px;
        }}
        .masthead-title h1 {{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.01em;
            color: var(--text-primary);
        }}
        .tag-version {{
            background: rgba(59, 130, 246, 0.12);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.25);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}
        .masthead-sub {{
            color: var(--text-secondary);
            font-size: 13px;
        }}
        .masthead-pills {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .pill {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
        }}
        .pill strong {{
            color: var(--text-primary);
        }}

        /* Metrics KPI Grid */
        .grid-kpi {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-bottom: 28px;
        }}
        .kpi-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px 18px;
            transition: border-color 0.15s ease;
        }}
        .kpi-card:hover {{
            border-color: var(--border-hover);
        }}
        .kpi-label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 8px;
        }}
        .kpi-value {{
            font-size: 22px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            font-feature-settings: 'tnum' 1;
            line-height: 1.2;
            margin-bottom: 6px;
        }}
        .kpi-meta {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        /* Panel Containers */
        .panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 28px;
        }}
        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
            background: rgba(17, 22, 37, 0.6);
        }}
        .panel-title {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }}
        .panel-desc {{
            font-size: 12px;
            color: var(--text-muted);
            margin-left: 8px;
            font-weight: 400;
        }}

        /* Filter Switcher */
        .segmented-control {{
            display: flex;
            background: var(--bg-page);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 2px;
            gap: 2px;
        }}
        .seg-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.15s ease;
        }}
        .seg-btn:hover {{
            color: var(--text-primary);
        }}
        .seg-btn.active {{
            background: var(--bg-surface);
            color: var(--text-primary);
            font-weight: 600;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }}

        /* Table Styling */
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            background: var(--bg-surface);
            color: var(--text-muted);
            text-align: left;
            padding: 10px 18px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            border-bottom: 1px solid var(--border);
        }}
        td {{
            padding: 11px 18px;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }}
        tr.trade-item:hover td {{
            background: var(--bg-subtle);
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Footer */
        .footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 36px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            flex-wrap: wrap;
            gap: 12px;
        }}
    </style>
</head>
<body>
    <!-- Masthead -->
    <div class="masthead">
        <div>
            <div class="masthead-title">
                <h1>VQUANT ANALYTICS</h1>
                <span class="tag-version">TEAR-SHEET v2.4</span>
            </div>
            <div class="masthead-sub">Institutional Quantitative Performance Report • Hybrid DCA Grid & AI Volatility Shield</div>
        </div>
        <div class="masthead-pills">
            <div class="pill">Asset: <strong>XAUUSD (Spot Gold)</strong></div>
            <div class="pill">Resolution: <strong>M1 Execution / H1 Macro</strong></div>
            <div class="pill">Researcher: <strong>Nguyễn Mạnh Cường (B22DCCN099)</strong></div>
        </div>
    </div>

    <!-- KPI Metrics Cards -->
    <div class="grid-kpi">
        <div class="kpi-card">
            <div class="kpi-label">Net Realized Profit</div>
            <div class="kpi-value" style="color: {'#10B981' if metrics['net_profit'] >= 0 else '#F43F5E'};">${metrics['net_profit']:+,.2f}</div>
            <div class="kpi-meta">Return on Capital: <span style="font-weight: 600; color: #10B981;">{metrics['return_pct']:+.2f}%</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Win Rate</div>
            <div class="kpi-value" style="color: #38BDF8;">{metrics['win_rate_pct']:.1f}%</div>
            <div class="kpi-meta">{metrics['winning_trades']} Won / {metrics['total_trades']} Total closed</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Profit Factor</div>
            <div class="kpi-value" style="color: #F59E0B;">{metrics['profit_factor']:.2f}</div>
            <div class="kpi-meta">Gross: ${metrics['gross_profit']:,.2f} / Loss: ${metrics['gross_loss']:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Risk-Adjusted Return</div>
            <div class="kpi-value" style="color: #A855F7;">{metrics['sharpe_ratio']:.2f} <span style="font-size: 13px; color: var(--text-muted); font-weight: 400;">Sharpe</span></div>
            <div class="kpi-meta">Sortino: {metrics['sortino_ratio']:.2f} | Calmar: {metrics['calmar_ratio']:.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Max Drawdown</div>
            <div class="kpi-value" style="color: #F43F5E;">{metrics['max_drawdown_pct']:.2f}%</div>
            <div class="kpi-meta">Peak-to-Trough: -${metrics['max_drawdown_usd']:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Final Equity</div>
            <div class="kpi-value">${metrics['final_equity']:,.2f}</div>
            <div class="kpi-meta">Initial Capital: ${metrics['initial_capital']:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Position Balance</div>
            <div class="kpi-value" style="font-size: 18px; color: #38BDF8;">{buy_count} Long / {sell_count} Short</div>
            <div class="kpi-meta">{buy_count*100/max(total_trades_count,1):.1f}% Long • {sell_count*100/max(total_trades_count,1):.1f}% Short</div>
        </div>
    </div>

    <!-- Equity Curve Chart Panel -->
    <div class="panel">
        <div class="panel-header">
            <div>
                <span class="panel-title">Portfolio Trajectory & Underwater Drawdown</span>
                <span class="panel-desc">Realized balance vs. mark-to-market equity with drawdown exposure</span>
            </div>
        </div>
        <div style="padding: 12px 14px;">
            {chart_html}
        </div>
    </div>

    <!-- Audited Execution Log Table Panel -->
    <div class="panel">
        <div class="panel-header">
            <div>
                <span class="panel-title">Audited Order Executions</span>
                <span class="panel-desc">Complete order ledger ({total_trades_count} total positions)</span>
            </div>
            <div class="segmented-control">
                <button onclick="filterTrades('ALL')" id="btn-ALL" class="seg-btn active">All ({total_trades_count})</button>
                <button onclick="filterTrades('BUY')" id="btn-BUY" class="seg-btn">Long ({buy_count})</button>
                <button onclick="filterTrades('SELL')" id="btn-SELL" class="seg-btn">Short ({sell_count})</button>
            </div>
        </div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Ticket</th>
                        <th>Timestamp (UTC)</th>
                        <th>Direction</th>
                        <th>Volume (Lot)</th>
                        <th>Entry Price</th>
                        <th>Exit Price</th>
                        <th>PnL (USD)</th>
                        <th>Closure Reason</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function filterTrades(type) {{
            document.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById('btn-' + type);
            if (activeBtn) activeBtn.classList.add('active');
            
            const rows = document.querySelectorAll('.trade-item');
            rows.forEach(r => {{
                if (type === 'ALL' || r.getAttribute('data-type') === type) {{
                    r.style.display = '';
                }} else {{
                    r.style.display = 'none';
                }}
            }});
        }}
    </script>

    <div class="footer">
        <div>VQuant Algorithmic Trading Architecture • Graduation Thesis PTIT 2026</div>
        <div>Author: Nguyễn Mạnh Cường • Student ID: B22DCCN099</div>
    </div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f">> [Tear-Sheet Generated]: Da xuat thanh cong bao cao HTML tuong tac tai: {output_path}")
    return output_path
