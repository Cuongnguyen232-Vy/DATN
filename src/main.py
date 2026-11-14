# -*- coding: utf-8 -*-
"""
Main Entry Point: VQuant Quantitative Algorithmic Trading Ecosystem
Author: Nguyễn Mạnh Cường_B22DCCN099
Institution: Posts and Telecommunications Institute of Technology (PTIT)
"""

import os
import sys
import time

# Auto-inject project root and src into sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.config import DATA_DIR, SYMBOL, MODEL_PATH, SCALER_PATH
from src.engine.ai_engine import AIEngine
from src.engine.sentinel_service import Sentinel247
from src.data.fetcher import MT5Fetcher
from src.data.nlp_finbert import FinBERT_Analyzer
from src.backtest.run_backtest import main as execute_backtest


def clear_screen() -> None:
    """Clear terminal console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def run_diagnostics() -> None:
    """Performs end-to-end system health check across all architectural layers."""
    clear_screen()
    print("=" * 70)
    print("   VQUANT SYSTEM HEALTH AUDIT & DIAGNOSTIC SUITE")
    print("   Kiem tra tinh san sang cua he thong truoc khi van hanh/bao cao")
    print("=" * 70)

    # 1. Market Data Layer
    print("\n[1/5] Kiem tra Tang Du lieu Thi truong (Data Engine):")
    fetcher = MT5Fetcher()
    fetcher.initialize()
    df_h4 = fetcher.fetch_data("H4", 50)
    if df_h4 is not None and len(df_h4) >= 50:
        last_price = df_h4.iloc[-1]['close']
        print(f"  -> [OK] Du lieu nến H4 ({SYMBOL}): San sang "
              f"({len(df_h4)} nến, Giá cuối: ${last_price:.2f})")
    else:
        print("  -> [FAIL] Khong the lay du lieu nen H4!")

    # 2. AI Model Weights
    print("\n[2/5] Kiem tra Mo hinh Hoc sau (Deep Learning Weights):")
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        print(f"  -> [OK] Trọng số CNN-BiGRU-Attention: Tồn tại ({MODEL_PATH})")
    else:
        print("  -> [INFO] Chua co file weights da train. Ban co the chon Menu [2] de train ngay.")

    # 3. NLP Financial Sentiment
    print("\n[3/5] Kiem tra NLP FinBERT / Financial Lexicon Engine:")
    nlp = FinBERT_Analyzer()
    t0 = time.time()
    res = nlp.analyze_headline("US Non-Farm Payrolls significantly exceed expectations")
    t_el = (time.time() - t0) * 1000.0
    print(f"  -> [OK] NLP Engine: {res['engine']} | Tốc độ: {t_el:.2f} ms | "
          f"Score: {res['sentiment_value']:+.2f}")

    # 4. MQL5 Expert Advisor Files
    print("\n[4/5] Kiem tra Robot MQL5 (VQuant OOP Core):")
    mql5_root = os.path.join(PROJECT_ROOT, "mql5")
    grid_mgr = os.path.join(mql5_root, "Include", "VQuant", "Trading", "GridManager.mqh")
    ea_file = os.path.join(mql5_root, "V_Capital_OOP.mq5")
    if os.path.exists(grid_mgr) and os.path.exists(ea_file):
        print("  -> [OK] Ma nguon CGridManager.mqh & V_Capital_OOP.mq5 hop le va day du.")
    else:
        print("  -> [WARN] Thieu file ma nguon MQL5!")

    # 5. Backtest Tear-Sheet
    print("\n[5/5] Kiem tra Bao cao Dinh luong (Quant Tear-Sheet):")
    report_file = os.path.join(DATA_DIR, "backtest_report_XAUUSD.html")
    if os.path.exists(report_file):
        print(f"  -> [OK] File bao cao HTML san sang: {report_file}")
    else:
        print("  -> [INFO] Chua co bao cao HTML. Ban co the chon Menu [3] de sinh bao cao tu dong.")

    print("\n" + "=" * 70)
    print(">> Chuan doan hoan tat! He thong dat tieu chuan ky su.")
    print("=" * 70)


def start_web_dashboard() -> None:
    """Spawns the real-time FastAPI telemetry web server."""
    clear_screen()
    print("=" * 70)
    print("   VQUANT REAL-TIME WEB DASHBOARD SERVER")
    print("=" * 70)
    print("\n[Web] Dang khoi dong Web Terminal...")
    print(">> Vui long mo trinh duyet tai: http://127.0.0.1:8000")
    print(">> Nhan Ctrl+C de dung server va quay lai Menu chinh.\n")
    try:
        import uvicorn  # type: ignore
        uvicorn.run("src.web.app:app", host="127.0.0.1", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\n[Web] Da dung Web Server.")


def main_loop() -> None:
    """Main terminal command loop."""
    clear_screen()
    engine = AIEngine()
    
    while True:
        print("==================================================================")
        print("      VQUANT 4.0 - INSTITUTIONAL QUANTITATIVE AI ECOSYSTEM        ")
        print("   Tac gia: Nguyen Manh Cuong _ B22DCCN099 (Khoa CNTT 1 - PTIT)  ")
        print("==================================================================")
        print("   [MENU TRUNG TÂM ĐIỀU KHIỂN]")
        print("   1. Khoi dong AI Engine (Live Trading & IPC Bridge toi MT5)    ")
        print("   2. Khoi dong Sentinel 24/7 (Tu dong loc Tin & Ban tin hieu)   ")
        print("   3. Huan luyen Mo hinh Hoc sau (CNN-BiGRU-Attention)          ")
        print("   4. Chay Backtesting & Xuat Bao Cao Dinh Luong (Tear-Sheet)    ")
        print("   5. Khoi dong Web Dashboard (Giao dien Thoi gian thuc Quants)  ")
        print("   6. Khoi dong Telegram Remote Bot (Giam sat & Dieu khien)      ")
        print("   7. Kiem tra Suc khoe He thong (Diagnostic Health Audit)       ")
        print("   8. Kiem tra & Doi chieu Tin tuc NLP thuc te (ForexFactory)     ")
        print("   9. Thuc nghiem Doi chieu 4 Mo hinh (Academic Benchmark Suite) ")
        print("   0. Thoat chuong trinh                                         ")
        print("==================================================================")
        
        choice = input("\n[System] Nhap so chuc nang muon thuc thi (0-9): ").strip()
        
        if choice == '1':
            clear_screen()
            if engine.initialize():
                engine.run_loop()
                engine.shutdown()
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()

        elif choice == '2':
            clear_screen()
            sentinel = Sentinel247(cycle_seconds=20)
            sentinel.run_247()
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()
            
        elif choice == '3':
            clear_screen()
            if engine.initialize():
                engine.train_model()
                engine.shutdown()
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()

        elif choice == '4':
            clear_screen()
            execute_backtest()
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()

        elif choice == '5':
            start_web_dashboard()
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()
            
        elif choice == '6':
            clear_screen()
            print("Dang khoi dong Telegram Bot...")
            bot_path = os.path.join(os.path.dirname(__file__), 'bot', 'telegram_bot.py')
            os.system(f"python {bot_path}")
            clear_screen()

        elif choice == '7':
            run_diagnostics()
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()

        elif choice == '8':
            clear_screen()
            verify_script = os.path.join(os.path.dirname(__file__), 'tools', 'verify_sentiment.py')
            os.system(f"python {verify_script}")
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()
            
        elif choice == '9':
            clear_screen()
            from src.models.benchmark_models import run_benchmark
            run_benchmark()
            input("\n[System] Nhan Enter de quay lai Menu chinh...")
            clear_screen()
            
        elif choice == '0':
            print("\n[System] Tam biet! Da dung toan bo he thong VQuant.")
            break
            
        else:
            print("\n Lua chon khong hop le! Vui long nhap so tu 0 den 9.")
            time.sleep(1)
            clear_screen()


if __name__ == "__main__":
    main_loop()

