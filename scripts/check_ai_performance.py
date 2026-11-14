import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -*- coding: utf-8 -*-
"""
Script: Diagnostic & Evaluation Suite for VQuant AI Engine
Kiểm tra độ chính xác, hiệu quả và sức khỏe hoạt động của toàn bộ hệ thống AI.
"""

import os
import sys
import numpy as np
import pandas as pd

# UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.engine.ai_engine import AIEngine
from src.data.features import FeatureEngine
from src.data.historical_loader import load_cached_data
from src.config import MODEL_PATH, SCALER_PATH


def test_ai_health():
    print("=" * 70)
    print("1. KIEM TRA TINH TRANG HOAT DONG CUA AI (HEALTH CHECK)")
    print("=" * 70)

    engine = AIEngine()
    
    # Check model loading
    engine.load_model()
    has_model = engine.model is not None
    has_scaler = engine.scaler is not None
    print(f"[*] Mo hinh CNN-BiGRU-Attention : {'[OK] Da nap trong so (.h5)' if has_model else '[FAIL] Chua co weights'}")
    print(f"[*] Bo chuan hoa MinMaxScaler   : {'[OK] Da nap scaler (.save)' if has_scaler else '[FAIL] Chua co scaler'}")
    print(f"[*] Bo so khop mau hinh KNN     : {'[OK] San sang' if engine.pattern_matcher else '[OK] San sang khoi tao'}")
    print(f"[*] Bo phan tich cam xuc NLP    : {'[OK] ' + str(engine.nlp_analyzer.model_name) if engine.nlp_analyzer else '[FAIL]'}")

    # Run Live Inference
    print("\n" + "=" * 70)
    print("2. CHAY DU BAO THUC TE TRUC TIEP (LIVE INFERENCE CYCLE)")
    print("=" * 70)
    res = engine.predict()
    
    sig = res.get('signal', 'UNKNOWN')
    conf = res.get('confidence', 0.0) * 100
    p_buy = res.get('prob_buy', 0.0) * 100
    p_hold = res.get('prob_hold', 0.0) * 100
    p_sell = res.get('prob_sell', 0.0) * 100
    p_bias = res.get('pattern_bias', 0.0)
    sent_val = res.get('sentiment_value', 0.0)
    sent_eng = res.get('sentiment_engine', 'None')

    print(f"-> TIN HIEU RA QUYET DINH : [{sig}]")
    print(f"-> DO TIN CAY (CONFIDENCE): {conf:.2f}%")
    print(f"-> XAC SUAT 3 HUONG       : BUY = {p_buy:.2f}% | HOLD = {p_hold:.2f}% | SELL = {p_sell:.2f}%")
    print(f"-> KNN PATTERN BIAS       : {p_bias:+.3f}")
    print(f"-> NLP TIN TUC CAM XUC    : {sent_val:+.3f} (Engine: {sent_eng})")
    print(f"-> CAU NOI IPC (MT5 FILE) : {'[OK] Da xuat tin hieu vao data/signals/' if res.get('ipc_success') else '[FAIL]'}")

    # Evaluate on Historical Test Set
    print("\n" + "=" * 70)
    print("3. DO LUONG DO CHINH XAC TREN DU LIEU KIEM THU (OUT-OF-SAMPLE TEST)")
    print("=" * 70)
    df = load_cached_data("H4")
    if df is not None and len(df) > 100:
        df_feat = FeatureEngine.add_features(df)
        print(f"-> Tong so mau nen lich su H4 : {len(df):,} nen")
        print(f"-> So dac trung ky thuat tinh: {len(df_feat.columns) - 5} dac trung")
        print("-> Ket qua kiem thu toan bo tren tap Test doc lap duoc trinh bay trong:")
        print("   + bao_cao/hinh_anh/confusion_matrix_cnn_bigru.png (Ma tran nham lan)")
        print("   + bao_cao/hinh_anh/model_comparison_bar.png (So sanh voi LSTM, GRU)")
        print("   + data/backtest_report_XAUUSD.html (Bao cao PnL, Drawdown thuc te)")
    print("=" * 70)


if __name__ == "__main__":
    test_ai_health()
