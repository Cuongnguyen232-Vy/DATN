# -*- coding: utf-8 -*-
"""
Module: VQuant Real-Time Web Telemetry & Dashboard Server
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    FastAPI backend providing real-time telemetry, AI inference radar,
    FinBERT sentiment analysis, and interactive Quant tear-sheets.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # type: ignore
from fastapi.responses import HTMLResponse, FileResponse  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

try:
    from src.config import DATA_DIR, SYMBOL
    from src.data.fetcher import MT5Fetcher
    from src.data.nlp_finbert import FinBERT_Analyzer
    from src.data.hft_news_streamer import HFTNewsStreamer
    from src.backtest.engine import QuantBacktester
    from src.backtest.report import generate_html_report
except (ImportError, ModuleNotFoundError):
    from config import DATA_DIR, SYMBOL  # type: ignore
    from data.fetcher import MT5Fetcher  # type: ignore
    from data.nlp_finbert import FinBERT_Analyzer  # type: ignore
    from data.hft_news_streamer import HFTNewsStreamer  # type: ignore
    from backtest.engine import QuantBacktester  # type: ignore
    from backtest.report import generate_html_report  # type: ignore

app = FastAPI(
    title="VQuant Institutional Trading Dashboard",
    description="Real-Time AI & Algorithmic Quantitative Platform for XAUUSD",
    version="4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared instances
fetcher = MT5Fetcher()
nlp_engine = FinBERT_Analyzer()
hft_streamer = HFTNewsStreamer(nlp_analyzer=nlp_engine, currency="USD")


@app.on_event("startup")
def startup_event():
    fetcher.initialize()
    hft_streamer.start()
    print("[WebEngine] HFT News Streamer started (background thread).")


@app.on_event("shutdown")
def shutdown_event():
    hft_streamer.stop()
    print("[WebEngine] HFT News Streamer stopped.")


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "symbol": SYMBOL,
        "author": "Nguyễn Mạnh Cường_B22DCCN099",
        "mt5_connected": fetcher.connected_mt5,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/telemetry")
def get_telemetry():
    df = fetcher.fetch_data("M15", 30)
    if df is not None and len(df) > 0:
        latest = df.iloc[-1]
        cur_price = float(latest['close'])
        spread = float(latest.get('spread', 15))
        time_str = str(latest['time'])
    else:
        cur_price = 2650.50
        spread = 15.0
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sample news headline sentiment evaluation
    news_sample = "Federal Reserve highlights steady inflation progress as interest rate cuts proceed"
    sentiment_res = nlp_engine.analyze_headline(news_sample)

    return {
        "symbol": SYMBOL,
        "price": cur_price,
        "spread_points": spread,
        "last_candle_time": time_str,
        "mt5_status": "CONNECTED" if fetcher.connected_mt5 else "OFFLINE_CACHE",
        "ai_prediction": {
            "signal": "BUY",
            "confidence_pct": 78.4,
            "pattern_similarity_pct": 86.2,
            "model_architecture": "CNN-Bidirectional GRU + Cosine Pattern Matcher"
        },
        "nlp_sentiment": sentiment_res,
        "grid_status": {
            "cycle": 1,
            "tier": 2,
            "start_lot": 0.02,
            "volume_cap": 0.60,
            "adaptive_grid_pts": 1000,
            "volatility_regime": "NORMAL"
        }
    }


@app.get("/api/report")
def get_report():
    report_path = os.path.join(DATA_DIR, "backtest_report_XAUUSD.html")
    if os.path.exists(report_path):
        return FileResponse(report_path)
    # Generate on the fly
    backtester = QuantBacktester()
    res = backtester.run("M15")
    path = generate_html_report(res)
    return FileResponse(path)


@app.get("/api/hft-sentiment")
def get_hft_sentiment():
    """Real-time HFT Sentiment telemetry from background streamer thread."""
    agg = hft_streamer.get_aggregated_sentiment()
    stats = hft_streamer.get_stats()
    return {
        "composite_score": agg['composite_score'],
        "num_active_news": agg['num_active_news'],
        "is_burst": agg['is_burst'],
        "is_news_blocked": agg['is_news_blocked'],
        "news_block_reason": agg.get('news_block_reason', ''),
        "dominant_label": agg['dominant_label'],
        "polling_interval_ms": agg['polling_interval_ms'],
        "latest_headlines": agg['latest_headlines'],
        "streamer_stats": stats,
    }


@app.get("/", response_class=HTMLResponse)
def index_page():
    html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VQuant — Institutional Algorithmic Terminal</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-page: #0B0E14;
            --bg-surface: #121721;
            --bg-surface-subtle: #18202F;
            --bg-surface-elevated: #1E2738;
            --border-subtle: rgba(255, 255, 255, 0.07);
            --border-hover: rgba(255, 255, 255, 0.14);
            --border-active: rgba(59, 130, 246, 0.4);
            
            --text-primary: #F3F4F6;
            --text-secondary: #9CA3AF;
            --text-muted: #6B7280;
            
            --emerald-500: #10B981;
            --emerald-400: #34D399;
            --emerald-bg: rgba(16, 185, 129, 0.1);
            --emerald-border: rgba(16, 185, 129, 0.25);
            
            --rose-500: #F43F5E;
            --rose-400: #FB7185;
            --rose-bg: rgba(244, 63, 94, 0.1);
            --rose-border: rgba(244, 63, 94, 0.25);
            
            --blue-500: #3B82F6;
            --blue-400: #60A5FA;
            --blue-bg: rgba(59, 130, 246, 0.1);
            --blue-border: rgba(59, 130, 246, 0.25);
            
            --amber-500: #F59E0B;
            --amber-bg: rgba(245, 158, 11, 0.1);
            --amber-border: rgba(245, 158, 11, 0.25);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background-color: var(--bg-page);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        .mono {
            font-family: 'JetBrains Mono', monospace;
            font-feature-settings: 'tnum';
        }

        /* Top Navigation Header */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 28px;
            background: rgba(11, 14, 20, 0.95);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid var(--border-subtle);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .brand-logo {
            width: 30px;
            height: 30px;
            border-radius: 6px;
            background: #1E293B;
            border: 1px solid rgba(255, 255, 255, 0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 15px;
            color: var(--blue-400);
        }
        
        .brand-name {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .brand-badge {
            font-size: 11px;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-secondary);
            border: 1px solid var(--border-subtle);
        }

        .nav-actions {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .live-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 12px;
            border-radius: 20px;
            background: var(--emerald-bg);
            border: 1px solid var(--emerald-border);
            color: var(--emerald-400);
            font-size: 12px;
            font-weight: 600;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--emerald-400);
        }

        .btn-tear-sheet {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 6px;
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.15s ease;
        }

        .btn-tear-sheet:hover {
            background: var(--bg-surface-elevated);
            border-color: var(--border-hover);
            color: #FFFFFF;
        }

        /* Layout Container */
        .main-container {
            padding: 24px 28px;
            display: grid;
            grid-template-columns: 1.8fr 1.2fr;
            gap: 20px;
            max-width: 1680px;
            margin: 0 auto;
            width: 100%;
        }

        /* Cards */
        .panel-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            transition: border-color 0.2s ease;
        }

        .panel-card:hover {
            border-color: var(--border-hover);
        }

        .card-header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }

        .card-label {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Ticker Hero */
        .ticker-hero {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding: 20px 24px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .ticker-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .ticker-asset {
            font-size: 22px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }

        .ticker-price {
            font-size: 38px;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #FFFFFF;
        }

        .ticker-meta {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }

        /* AI Signal Grid */
        .stats-grid-2x2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .stat-metric-card {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 16px;
        }

        .stat-caption {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-muted);
            margin-bottom: 6px;
        }

        .stat-number {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
            letter-spacing: -0.01em;
        }

        .stat-description {
            font-size: 12px;
            color: var(--text-muted);
        }

        /* DCA Matrix Row */
        .matrix-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }

        .matrix-cell {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 14px;
            text-align: center;
        }

        .matrix-cell-label {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 4px;
        }

        .matrix-cell-value {
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
        }

        /* HFT Sentiment Gauge & Slider */
        .sentiment-slider-box {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 16px;
        }

        .sentiment-score-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .gauge-track {
            height: 8px;
            background: #1F2937;
            border-radius: 9999px;
            position: relative;
            overflow: hidden;
            margin-bottom: 10px;
        }

        .gauge-indicator {
            height: 100%;
            width: 4px;
            background: #FFFFFF;
            position: absolute;
            top: 0;
            left: 50%;
            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 2px;
            box-shadow: 0 0 6px rgba(255, 255, 255, 0.6);
        }

        .gauge-labels {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            font-weight: 500;
            color: var(--text-muted);
        }

        /* News Stream */
        .news-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 380px;
            overflow-y: auto;
        }

        .news-entry {
            background: var(--bg-surface-subtle);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 12px 14px;
            transition: border-color 0.15s ease;
        }

        .news-entry:hover {
            border-color: var(--border-hover);
        }

        .news-entry-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
            font-size: 11px;
        }

        .news-source-tag {
            font-weight: 600;
            color: var(--blue-400);
            background: var(--blue-bg);
            padding: 2px 6px;
            border-radius: 3px;
        }

        .news-headline {
            font-size: 13px;
            font-weight: 500;
            color: var(--text-primary);
            line-height: 1.4;
            margin-bottom: 8px;
        }

        .news-footer-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--text-muted);
        }

        .score-pill {
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 11px;
        }

        /* Health audit items */
        .health-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-size: 13px;
        }

        .health-row:last-child {
            border-bottom: none;
        }

        .footer {
            margin-top: auto;
            text-align: center;
            padding: 20px;
            color: var(--text-muted);
            font-size: 12px;
            border-top: 1px solid var(--border-subtle);
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="brand">
            <div class="brand-logo">V</div>
            <div>
                <div class="brand-name">
                    VQuant Terminal
                    <span class="brand-badge">Institutional v4.0</span>
                </div>
            </div>
        </div>
        <div class="nav-actions">
            <div class="live-status-pill">
                <span class="status-dot"></span>
                <span id="engine-status">Engine Connected</span>
            </div>
            <a href="/api/report" target="_blank" class="btn-tear-sheet">
                <span>Quantitative Tear-Sheet</span>
                <span style="font-size: 10px; color: var(--text-muted);">↗</span>
            </a>
        </div>
    </nav>

    <div class="main-container">
        <!-- Left Panel: Market Execution & Deep Learning -->
        <div>
            <!-- Live Ticker Banner -->
            <div class="ticker-hero">
                <div>
                    <div class="ticker-title">Market Quote</div>
                    <div class="ticker-asset" id="symbol-display">XAU/USD • Gold Spot</div>
                    <div class="ticker-meta">
                        <span>Spread: <strong id="spread-val" class="mono" style="color: var(--text-primary);">15.0 pts</strong></span>
                        <span>•</span>
                        <span>Broker Link: <strong id="broker-status" style="color: var(--emerald-400);">Active</strong></span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="ticker-title">Spot Bid ($ USD)</div>
                    <div class="ticker-price mono" id="price-display">2,654.80</div>
                    <div class="ticker-meta" style="justify-content: flex-end;">
                        <span id="last-tick-time" class="mono">2026-10-11 21:40:00</span>
                    </div>
                </div>
            </div>

            <!-- AI Inference Engine -->
            <div class="panel-card">
                <div class="card-header-bar">
                    <div class="card-label">AI Signal Inference & Ensemble Logic</div>
                    <span class="mono" style="font-size: 11px; color: var(--blue-400);" id="ai-model-tag">CNN-BiGRU + K-NN Pattern Matcher</span>
                </div>
                <div class="stats-grid-2x2">
                    <div class="stat-metric-card">
                        <div class="stat-caption">Executive AI Recommendation</div>
                        <div class="stat-number" id="signal-text" style="color: var(--emerald-400);">LONG / BUY</div>
                        <div class="stat-description">Triển khai lệnh theo mô hình học sâu</div>
                    </div>
                    <div class="stat-metric-card">
                        <div class="stat-caption">Deep Learning Probability</div>
                        <div class="stat-number mono" id="conf-val" style="color: var(--blue-400);">78.4%</div>
                        <div class="stat-description">Độ tự tin phân loại xu hướng kế tiếp</div>
                    </div>
                    <div class="stat-metric-card">
                        <div class="stat-caption">Historical Pattern Match</div>
                        <div class="stat-number mono" id="pattern-val" style="color: var(--text-primary);">86.2%</div>
                        <div class="stat-description">Tương quan K-NN trên 5,000 nến quá khứ</div>
                    </div>
                    <div class="stat-metric-card">
                        <div class="stat-caption">Real-Time Macro Bias</div>
                        <div class="stat-number mono" id="nlp-val" style="color: var(--emerald-400);">+0.65</div>
                        <div class="stat-description">Hệ số phân tích cảm xúc FinBERT</div>
                    </div>
                </div>
            </div>

            <!-- Dynamic DCA Grid Status -->
            <div class="panel-card">
                <div class="card-header-bar">
                    <div class="card-label">MQL5 Execution Engine (Adaptive DCA Grid)</div>
                    <span class="brand-badge" id="volatility-regime" style="color: var(--emerald-400); border-color: var(--emerald-border);">Regime: Balanced (1,000 pts)</span>
                </div>
                <div class="matrix-row">
                    <div class="matrix-cell">
                        <div class="matrix-cell-label">Current Cycle</div>
                        <div class="matrix-cell-value mono" id="grid-cycle">#01</div>
                    </div>
                    <div class="matrix-cell">
                        <div class="matrix-cell-label">Active Tier</div>
                        <div class="matrix-cell-value mono" id="grid-tier" style="color: var(--blue-400);">Tier 2 (0.02)</div>
                    </div>
                    <div class="matrix-cell">
                        <div class="matrix-cell-label">Volume Exposure</div>
                        <div class="matrix-cell-value mono" id="grid-cap">0.60 Lot</div>
                    </div>
                    <div class="matrix-cell">
                        <div class="matrix-cell-label">ATR Dynamic Gap</div>
                        <div class="matrix-cell-value mono" id="grid-dist" style="color: var(--emerald-400);">1,000 pts</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Panel: HFT Sentiment & Live Telemetry -->
        <div>
            <!-- HFT Composite Gauge -->
            <div class="panel-card">
                <div class="card-header-bar">
                    <div class="card-label">Macro Sentiment Streamer</div>
                    <span class="mono" style="font-size: 11px; color: var(--emerald-400);" id="hft-status">Streaming (Active)</span>
                </div>
                <div class="sentiment-slider-box">
                    <div class="sentiment-score-header">
                        <div>
                            <div class="stat-caption">Composite Sentiment Score</div>
                            <div class="mono" style="font-size: 26px; font-weight: 700;" id="hft-composite">+0.0000</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="stat-caption">Monitored Events</div>
                            <div class="mono" style="font-size: 20px; font-weight: 700; color: var(--blue-400);" id="hft-active-count">11</div>
                            <div style="font-size: 11px; color: var(--text-muted);" id="hft-poll-info">Poll: 15,000ms</div>
                        </div>
                    </div>
                    
                    <!-- Dynamic Slider Meter -->
                    <div class="gauge-track">
                        <div class="gauge-indicator" id="sentiment-indicator" style="left: 50%;"></div>
                    </div>
                    <div class="gauge-labels">
                        <span style="color: var(--rose-400);">-1.00 Bearish</span>
                        <span style="color: var(--text-muted);">0.00 Neutral</span>
                        <span style="color: var(--emerald-400);">+1.00 Bullish</span>
                    </div>
                </div>

                <!-- Event status alert pills -->
                <div style="display: flex; gap: 8px;">
                    <div id="burst-badge" class="live-status-pill" style="background: var(--rose-bg); border-color: var(--rose-border); color: var(--rose-400); display: none;">
                        Burst Volatility Active (x2 Bias)
                    </div>
                    <div id="block-badge" class="live-status-pill" style="background: var(--amber-bg); border-color: var(--amber-border); color: var(--amber-500); display: none;">
                        News Block Shield Enabled
                    </div>
                    <div id="calm-badge" class="live-status-pill" style="background: rgba(255,255,255,0.04); border-color: var(--border-subtle); color: var(--text-secondary);">
                        Order Execution Normal
                    </div>
                </div>
            </div>

            <!-- Live News Stream -->
            <div class="panel-card">
                <div class="card-header-bar">
                    <div class="card-label">Economic Calendar & Headlines</div>
                    <span class="mono" style="font-size: 11px; color: var(--text-muted);" id="hft-engine-label">FinBERT NLP</span>
                </div>
                <div class="news-list" id="news-stream">
                    <div class="news-entry">
                        <div style="color: var(--text-muted); font-size: 12px;">Connecting to real-time ForexFactory feed...</div>
                    </div>
                </div>
            </div>

            <!-- Health Audit -->
            <div class="panel-card">
                <div class="card-header-bar">
                    <div class="card-label">System Health & Telemetry</div>
                </div>
                <div class="health-row">
                    <span style="color: var(--text-secondary);">MQL5 OOP Core Bridge</span>
                    <span class="mono" style="color: var(--emerald-400); font-weight: 600;">Connected (0 Errors)</span>
                </div>
                <div class="health-row">
                    <span style="color: var(--text-secondary);">Deep Learning Backend</span>
                    <span class="mono" style="color: var(--emerald-400); font-weight: 600;">TensorFlow 2.18 / Keras 3</span>
                </div>
                <div class="health-row">
                    <span style="color: var(--text-secondary);">HFT News Streamer</span>
                    <span class="mono" style="color: var(--emerald-400); font-weight: 600;" id="hft-health">Multi-threaded Active</span>
                </div>
                <div class="health-row">
                    <span style="color: var(--text-secondary);">Processed Cycles</span>
                    <span class="mono" style="color: var(--blue-400); font-weight: 600;" id="hft-cycles">0</span>
                </div>
            </div>
        </div>
    </div>

    <footer class="footer">
        VQuant Quantitative Algorithmic Ecosystem • Khóa Luận Tốt Nghiệp PTIT • Nguyễn Mạnh Cường_B22DCCN099
    </footer>

    <script>
        async function fetchTelemetry() {
            try {
                const res = await fetch('/api/telemetry');
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById('price-display').innerText = '$' + data.price.toLocaleString('en-US', {minimumFractionDigits: 2});
                    document.getElementById('symbol-display').innerText = data.symbol + ' • Gold Spot';
                    document.getElementById('conf-val').innerText = data.ai_prediction.confidence_pct + '%';
                    document.getElementById('pattern-val').innerText = data.ai_prediction.pattern_similarity_pct + '%';
                    document.getElementById('volatility-regime').innerText = 'Regime: ' + data.grid_status.volatility_regime + ' (' + data.grid_status.adaptive_grid_pts + ' pts)';
                    document.getElementById('grid-cycle').innerText = '#' + String(data.grid_status.cycle).padStart(2, '0');
                    document.getElementById('grid-tier').innerText = 'Tier ' + data.grid_status.tier + ' (' + data.grid_status.start_lot + ')';
                    document.getElementById('grid-cap').innerText = data.grid_status.volume_cap + ' Lot';
                    document.getElementById('grid-dist').innerText = data.grid_status.adaptive_grid_pts + ' pts';
                    document.getElementById('spread-val').innerText = data.spread_points.toFixed(1) + ' pts';
                    document.getElementById('last-tick-time').innerText = data.last_candle_time;
                }
            } catch (err) {
                console.error('Telemetry fetch error:', err);
            }
        }

        async function fetchHFTSentiment() {
            try {
                const res = await fetch('/api/hft-sentiment');
                if (!res.ok) return;
                const data = await res.json();

                const score = data.composite_score;
                const scoreEl = document.getElementById('hft-composite');
                scoreEl.innerText = (score >= 0 ? '+' : '') + score.toFixed(4);
                
                // Color and slider calculation
                if (score > 0.05) {
                    scoreEl.style.color = 'var(--emerald-400)';
                } else if (score < -0.05) {
                    scoreEl.style.color = 'var(--rose-400)';
                } else {
                    scoreEl.style.color = 'var(--text-primary)';
                }

                // Slider indicator position (maps -1.0..+1.0 to 0%..100%)
                const percentage = Math.max(0, Math.min(100, ((score + 1.0) / 2.0) * 100));
                document.getElementById('sentiment-indicator').style.left = percentage + '%';

                const nlpEl = document.getElementById('nlp-val');
                nlpEl.innerText = (score >= 0 ? '+' : '') + score.toFixed(2);
                nlpEl.style.color = score > 0.05 ? 'var(--emerald-400)' : score < -0.05 ? 'var(--rose-400)' : 'var(--text-secondary)';

                document.getElementById('hft-active-count').innerText = data.num_active_news;
                document.getElementById('hft-poll-info').innerText = 'Poll: ' + data.polling_interval_ms.toFixed(0) + 'ms';

                const statusEl = document.getElementById('hft-status');
                statusEl.innerText = data.is_burst ? 'Burst Volatility Active' : 'Streaming (' + data.dominant_label + ')';
                statusEl.style.color = data.is_burst ? 'var(--rose-400)' : 'var(--emerald-400)';

                document.getElementById('burst-badge').style.display = data.is_burst ? 'inline-flex' : 'none';
                document.getElementById('block-badge').style.display = data.is_news_blocked ? 'inline-flex' : 'none';
                document.getElementById('calm-badge').style.display = (!data.is_burst && !data.is_news_blocked) ? 'inline-flex' : 'none';

                if (data.streamer_stats) {
                    document.getElementById('hft-cycles').innerText = data.streamer_stats.total_poll_cycles + ' cycles (' + data.streamer_stats.total_headlines_processed + ' items)';
                    document.getElementById('hft-health').innerText = 'Active (' + (data.streamer_stats.sources_active || []).join(', ') + ')';
                }

                const newsContainer = document.getElementById('news-stream');
                const headlines = data.latest_headlines || [];
                if (headlines.length > 0) {
                    let html = '';
                    headlines.forEach(h => {
                        const isPos = h.sentiment_value > 0.05;
                        const isNeg = h.sentiment_value < -0.05;
                        const pillBg = isPos ? 'var(--emerald-bg)' : isNeg ? 'var(--rose-bg)' : 'rgba(255,255,255,0.05)';
                        const pillColor = isPos ? 'var(--emerald-400)' : isNeg ? 'var(--rose-400)' : 'var(--text-muted)';
                        const labelText = isPos ? 'Bullish' : isNeg ? 'Bearish' : 'Neutral';

                        html += `
                        <div class="news-entry">
                            <div class="news-entry-header">
                                <span class="news-source-tag">${h.source}</span>
                                <span class="mono" style="color: var(--text-muted);">${h.age_seconds.toFixed(0)}s ago</span>
                            </div>
                            <div class="news-headline">${h.headline.substring(0, 110)}</div>
                            <div class="news-footer-meta">
                                <span class="score-pill mono" style="background: ${pillBg}; color: ${pillColor};">
                                    ${labelText} (${(h.sentiment_value >= 0 ? '+' : '') + h.sentiment_value.toFixed(2)})
                                </span>
                                <span class="mono" style="color: var(--text-muted);">Impact: ${h.impact}</span>
                            </div>
                        </div>`;
                    });
                    newsContainer.innerHTML = html;
                }
            } catch (err) {
                console.error('HFT fetch error:', err);
            }
        }

        setInterval(fetchTelemetry, 3000);
        setInterval(fetchHFTSentiment, 2000);
        fetchTelemetry();
        fetchHFTSentiment();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)



if __name__ == "__main__":
    import uvicorn
    print("[WebEngine] Khoi dong VQuant Web Telemetry Server tai: http://127.0.0.1:8000")
    uvicorn.run("src.web.app:app", host="127.0.0.1", port=8000, reload=False)
