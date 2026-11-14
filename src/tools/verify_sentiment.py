# -*- coding: utf-8 -*-
"""
HFT Sentiment Verification Tool — Đối chiếu thực tế với nguồn bên ngoài.
Chạy: python src/tools/verify_sentiment.py

Công cụ này sẽ:
  1. Lấy lịch kinh tế THẬT từ ForexFactory API
  2. Chấm điểm NLP mỗi sự kiện
  3. Hiển thị kết quả rõ ràng để bạn mở trình duyệt đối chiếu
  4. Tự mở ForexFactory trên trình duyệt để so sánh trực quan
"""

import os
import sys
import time
import webbrowser
import json
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
from src.data.nlp_finbert import FinBERT_Analyzer
from src.data.hft_news_streamer import HFTNewsStreamer

# ─── Constants ───
FF_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FF_BROWSER_URL = "https://www.forexfactory.com/calendar"
INVESTING_GOLD_URL = "https://www.investing.com/commodities/gold"

SEPARATOR = "=" * 75
THIN_SEP = "-" * 75


def print_header():
    print(f"\n{SEPARATOR}")
    print("  VQUANT HFT SENTIMENT — REAL-WORLD VERIFICATION TOOL")
    print("  Doi chieu du lieu NLP voi nguon tin ben ngoai (ForexFactory)")
    print(f"{SEPARATOR}\n")


def fetch_forexfactory_raw():
    """Lay du lieu tho tu ForexFactory API."""
    try:
        resp = requests.get(FF_URL, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"[ERROR] Khong the ket noi ForexFactory: {e}")
    return []


def run_verification():
    """Chay xac minh doi chieu thuc te."""
    print_header()

    # ─── Step 1: Init NLP Engine ───
    print("[1/4] Khoi tao NLP Engine...")
    nlp = FinBERT_Analyzer()
    print(f"  >> Engine: {nlp.model_name}\n")

    # ─── Step 2: Fetch REAL data from ForexFactory ───
    print("[2/4] Dang lay lich kinh te THAT tu ForexFactory API...")
    print(f"  >> URL: {FF_URL}")
    raw_events = fetch_forexfactory_raw()
    print(f"  >> Tong so su kien trong tuan: {len(raw_events)}\n")

    if not raw_events:
        print("[!] Khong lay duoc du lieu. Kiem tra ket noi internet.")
        return

    # ─── Step 3: Filter USD High-Impact events ───
    print("[3/4] Loc su kien USD (High + Medium Impact)...\n")

    now_local = datetime.now().astimezone()
    usd_events = []

    for item in raw_events:
        if item.get("country") != "USD":
            continue
        impact = item.get("impact", "")
        if impact not in ["High", "Medium"]:
            continue
        usd_events.append(item)

    print(f"  >> Tim thay {len(usd_events)} su kien USD (High/Medium)\n")

    # ─── Step 4: NLP Score each event ───
    print("[4/4] Cham diem NLP cho tung su kien...\n")
    print(THIN_SEP)
    print(f"  {'#':<4} {'THOI GIAN':<18} {'IMPACT':<8} {'TEN SU KIEN':<35} {'NLP SCORE':>10} {'LABEL':>10}")
    print(THIN_SEP)

    scored_events = []
    for i, item in enumerate(usd_events):
        title = item.get("title", "Unknown")
        impact = item.get("impact", "?")
        actual = item.get("actual", "")
        forecast = item.get("forecast", "")
        previous = item.get("previous", "")
        date_str = item.get("date", "")

        # Parse time
        time_display = "N/A"
        time_diff_min = None
        try:
            if date_str:
                event_dt = datetime.fromisoformat(date_str).astimezone()
                time_display = event_dt.strftime("%a %d/%m %H:%M")
                time_diff_min = (event_dt - now_local).total_seconds() / 60.0
        except Exception:
            pass

        # Build headline for NLP
        if actual and forecast:
            headline = f"{title}: Actual {actual} vs Forecast {forecast} (Previous: {previous})"
        elif forecast:
            headline = f"Upcoming {title}: Forecast {forecast} (Previous: {previous})"
        else:
            headline = f"{title} ({impact} impact USD economic event)"

        # NLP Score
        t0 = time.perf_counter_ns()
        result = nlp.analyze_headline(headline)
        latency_us = (time.perf_counter_ns() - t0) / 1000

        score = result['sentiment_value']
        label = result['label']

        # Color indicator
        if score > 0.05:
            indicator = "↑ TANG"
        elif score < -0.05:
            indicator = "↓ GIAM"
        else:
            indicator = "= TRUNG"

        # Time proximity indicator
        proximity = ""
        if time_diff_min is not None:
            if -30 <= time_diff_min <= 0:
                proximity = " [DA XAY RA]"
            elif 0 < time_diff_min <= 60:
                proximity = f" [CON {int(time_diff_min)}p]"
            elif -60 <= time_diff_min < -30:
                proximity = f" [{abs(int(time_diff_min))}p TRUOC]"

        print(f"  {i+1:<4} {time_display:<18} {impact:<8} {title[:35]:<35} {score:>+8.3f}   {indicator}")

        scored_events.append({
            'title': title,
            'time': time_display,
            'impact': impact,
            'actual': actual,
            'forecast': forecast,
            'previous': previous,
            'headline_for_nlp': headline,
            'nlp_score': score,
            'nlp_label': label,
            'nlp_latency_us': latency_us,
            'proximity': proximity,
        })

    print(THIN_SEP)

    # ─── Summary Statistics ───
    if scored_events:
        avg_score = sum(e['nlp_score'] for e in scored_events) / len(scored_events)
        pos_count = sum(1 for e in scored_events if e['nlp_score'] > 0.05)
        neg_count = sum(1 for e in scored_events if e['nlp_score'] < -0.05)
        neu_count = len(scored_events) - pos_count - neg_count
        avg_latency = sum(e['nlp_latency_us'] for e in scored_events) / len(scored_events)

        print(f"\n  THONG KE TONG HOP:")
        print(f"  >> Tong su kien:     {len(scored_events)}")
        print(f"  >> Tich cuc (TANG):  {pos_count}")
        print(f"  >> Tieu cuc (GIAM):  {neg_count}")
        print(f"  >> Trung tinh:       {neu_count}")
        print(f"  >> Diem trung binh:  {avg_score:+.4f}")
        print(f"  >> Toc do NLP TB:    {avg_latency:.1f} microseconds/headline")

    # ─── Detailed breakdown for verification ───
    print(f"\n{SEPARATOR}")
    print("  CHI TIET DE DOI CHIEU (mo ForexFactory de so sanh)")
    print(f"{SEPARATOR}\n")

    for e in scored_events:
        print(f"  * {e['title']}")
        print(f"    Thoi gian:    {e['time']}{e['proximity']}")
        print(f"    Impact:       {e['impact']}")
        if e['actual']:
            print(f"    Actual:       {e['actual']}   (Forecast: {e['forecast']}, Previous: {e['previous']})")
        else:
            print(f"    Forecast:     {e['forecast']}   (Previous: {e['previous']})")
        print(f"    Headline NLP: \"{e['headline_for_nlp']}\"")
        print(f"    NLP Score:    {e['nlp_score']:+.3f} ({e['nlp_label'].upper()}) | Latency: {e['nlp_latency_us']:.0f}us")
        print()

    # ─── Open browser for comparison ───
    print(f"{SEPARATOR}")
    print("  MO TRINH DUYET DE DOI CHIEU")
    print(f"{SEPARATOR}")
    print(f"\n  ForexFactory Calendar: {FF_BROWSER_URL}")
    print(f"  Investing.com Gold:   {INVESTING_GOLD_URL}")

    try:
        choice = input("\n  Ban co muon mo ForexFactory trong trinh duyet? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '']:
            webbrowser.open(FF_BROWSER_URL)
            print("  >> Da mo ForexFactory Calendar trong trinh duyet!")
            time.sleep(1)
            webbrowser.open(INVESTING_GOLD_URL)
            print("  >> Da mo Investing.com Gold Chart!")
    except (KeyboardInterrupt, EOFError):
        pass

    # ─── HFT Streamer quick test ───
    print(f"\n{SEPARATOR}")
    print("  TEST HFT STREAMER REAL-TIME (10 giay)")
    print(f"{SEPARATOR}\n")

    streamer = HFTNewsStreamer(nlp_analyzer=nlp, currency="USD")
    streamer.start()

    try:
        for tick in range(5):
            time.sleep(2)
            agg = streamer.get_aggregated_sentiment()
            burst_tag = " [BURST!]" if agg['is_burst'] else ""
            block_tag = " [BLOCKED!]" if agg['is_news_blocked'] else ""
            print(f"  [{tick*2+2}s] Composite: {agg['composite_score']:+.4f} | "
                  f"Active: {agg['num_active_news']} | "
                  f"{agg['dominant_label'].upper()}{burst_tag}{block_tag} | "
                  f"Poll: {agg['polling_interval_ms']:.0f}ms")
    except KeyboardInterrupt:
        pass
    finally:
        streamer.stop()

    print(f"\n{SEPARATOR}")
    print("  HOAN TAT! So sanh ket qua NLP voi ForexFactory tren trinh duyet.")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    run_verification()
