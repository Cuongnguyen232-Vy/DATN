# -*- coding: utf-8 -*-
import os
import json
import time
from src.config import SIGNAL_FILE, LOG_FILE, DATA_DIR


class IPCBridge:
    @staticmethod
    def send_signal(signal_string: str, confidence: float):
        """Xuất Data Predict ra file TXT cho MQL5 đọc (CSV format: SIGNAL,CONFIDENCE,TIMESTAMP)"""
        data = {
            "signal": signal_string,
            "confidence": round(confidence, 4),
            "timestamp": int(time.time())
        }
        content = f"{signal_string},{confidence:.4f},{int(time.time())}"
        symbols = ["XAUUSD", "XAUUSDm", "GOLD"]

        # 1. Thử ghi vào thư mục chung của MetaQuotes Terminal
        written_primary = False
        try:
            target_dir = os.path.dirname(SIGNAL_FILE)
            os.makedirs(target_dir, exist_ok=True)
            for s in symbols:
                fpath = os.path.join(target_dir, f"vc_signal_{s}.txt")
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
            written_primary = True
        except Exception as e:
            # Ghi nhận cảnh báo và chuyển fallback sang local signals
            pass

        # 2. Luôn ghi bản sao vào thư mục local data/signals để lưu trữ và kiểm thử
        try:
            local_sig_dir = os.path.join(DATA_DIR, "signals")
            os.makedirs(local_sig_dir, exist_ok=True)
            for s in symbols:
                fpath = os.path.join(local_sig_dir, f"vc_signal_{s}.txt")
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
        except Exception as e:
            print(f"[IPC Bridge] Loi ghi local signal: {e}")

        # 3. Ghi log lịch sử hệ thống
        try:
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print(f"[IPC Bridge] Loi ghi Log: {e}")
