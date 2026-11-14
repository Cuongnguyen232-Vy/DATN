# -*- coding: utf-8 -*-
"""
VQuant Manual Test Suite — Công cụ kiểm chứng thủ công thực tế
Dành cho tác giả/người dùng tự tay đối chiếu từng thành phần của bộ não AI.
"""

import os
import sys
import time
import random
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import SYMBOL, TIME_STEPS
from src.data.historical_loader import load_cached_data
from src.data.features import FeatureEngine
from src.engine.ai_engine import AIEngine
from src.models.pattern_matcher import PatternMatcher
from src.engine.ipc_bridge import IPCBridge
from src.data.nlp_finbert import FinBERT_Analyzer
from src.bot.notifier import TelegramNotifier


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def test_walk_forward_accuracy():
    """Test 1: Đối chiếu dự báo AI với diễn biến thực tế của nến tương lai."""
    print("\n" + "=" * 70)
    print("  TEST 1: ĐỐI CHIẾU DỰ BÁO AI VỚI DIỄN BIẾN THỰC TẾ LỊCH SỬ (OUT-OF-SAMPLE)")
    print("=" * 70)
    print(">> Đang nạp mô hình AI và dữ liệu 3,700 nến H4...")

    engine = AIEngine()
    if not engine.load_model():
        print("[LỖI] Không thể nạp model! Vui lòng train model trước.")
        return

    df = load_cached_data('H4')
    df_feat = FeatureEngine.add_features(df)
    feature_cols = [c for c in df_feat.columns if c not in ['time', 'real_volume']]

    total_candles = len(df_feat)
    print(f">> Tổng số nến khả dụng: {total_candles}")
    print(">> Hệ thống sẽ chọn ngẫu nhiên 5 thời điểm trong quá khứ.")
    print("   AI chỉ nhìn 50 nến trước đó (KHÔNG BIẾT TƯƠNG LAI) để dự báo.")
    print("   Sau đó mở nến tiếp theo ra đối chiếu xem giá chạy đúng không!\n")

    # Chọn 5 điểm ngẫu nhiên ở 20% dữ liệu cuối (Out-of-sample)
    test_indices = random.sample(range(int(total_candles * 0.8), total_candles - 2), 5)
    
    correct_count = 0
    neutral_count = 0

    print(f"{'Thời điểm':<18} | {'Dự báo AI':<12} | {'Độ tin':<8} | {'Giá hiện tại':<12} | {'Giá nến sau':<12} | {'Biến động':<10} | {'Kết quả'}")
    print("-" * 95)

    for idx in test_indices:
        window = df_feat.iloc[idx - TIME_STEPS:idx]
        current_time = str(window['time'].iloc[-1])[:16] if 'time' in window.columns else f"Bar #{idx}"
        current_price = window['close'].iloc[-1]
        next_price = df_feat['close'].iloc[idx]
        price_diff = next_price - current_price

        # Chuẩn bị input cho model
        raw_feat = window[feature_cols].values
        scaled_feat = engine.scaler.transform(raw_feat)
        X_in = np.array([scaled_feat])

        # Dự báo
        preds = engine.model.predict(X_in, verbose=0)[0]
        prob_hold, prob_buy, prob_sell = preds[0], preds[1], preds[2]

        pred_label = "HOLD"
        conf = prob_hold
        if prob_buy >= 0.40 and prob_buy > prob_sell:
            pred_label = "BUY"
            conf = prob_buy / (prob_buy + prob_sell)
        elif prob_sell >= 0.40 and prob_sell > prob_buy:
            pred_label = "SELL"
            conf = prob_sell / (prob_buy + prob_sell)

        # Đánh giá thực tế
        actual_move = "UP" if price_diff > 3.0 else ("DOWN" if price_diff < -3.0 else "FLAT")
        
        status = "CHỜ"
        if pred_label == "BUY" and actual_move == "UP":
            status = "✅ CHÍNH XÁC"
            correct_count += 1
        elif pred_label == "SELL" and actual_move == "DOWN":
            status = "✅ CHÍNH XÁC"
            correct_count += 1
        elif pred_label == "HOLD" and actual_move == "FLAT":
            status = "✅ CHÍNH XÁC (Lọc nhiễu)"
            correct_count += 1
            neutral_count += 1
        elif pred_label == "HOLD":
            status = "⚪ NEUTRAL (Bỏ qua)"
            neutral_count += 1
        else:
            status = "❌ SAI LỆCH"

        print(f"{current_time:<18} | {pred_label:<12} | {conf*100:>5.1f}%  | ${current_price:>10.2f} | ${next_price:>10.2f} | {price_diff:>+9.2f}$ | {status}")

    print("-" * 95)
    print(f">> Tổng kết 5 lần test ngẫu nhiên: {correct_count}/5 trường hợp hợp lý ({neutral_count} lần giữ trạng thái quan sát).")


def test_custom_news():
    """Test 2: Thử nghiệm tiêu đề tin tức bất kỳ."""
    print("\n" + "=" * 70)
    print("  TEST 2: KIỂM CHỨNG BỘ PHÂN TÍCH TIN TỨC NLP FINBERT / FINANCIAL VADER")
    print("=" * 70)
    analyzer = FinBERT_Analyzer()

    sample_news = [
        ("US Federal Reserve cuts benchmark interest rate by 50 bps", 
         "Fed hạ 50 điểm lãi suất -> Đô la yếu, cực kỳ tốt cho Vàng (BUY)"),
        ("US Non-Farm Payrolls surge past expectations, dollar strengthens sharply", 
         "Việc làm phi nông nghiệp vượt xa kỳ vọng, USD tăng mạnh -> Rất xấu cho Vàng (SELL)"),
        ("Middle East tensions escalate, investors rush to safe-haven gold", 
         "Căng thẳng địa chính trị leo thang, dòng tiền trú ẩn vào Vàng -> Tốt cho Vàng (BUY)"),
        ("Treasury yields surge to multi-month highs as Fed signals hawkish stance", 
         "Lợi suất trái phiếu Mỹ tăng vọt vì Fed giữ lập trường diều hâu -> Xấu cho Vàng (SELL)"),
        ("Central banks report record gold purchases amid global reserve diversification", 
         "Các Ngân hàng Trung ương gom mua lượng Vàng kỷ lục -> Tốt cho Vàng (BUY)"),
        ("US CPI inflation cools more than expected, dollar plunges", 
         "Lạm phát CPI hạ nhiệt sâu hơn dự báo, USD lao dốc -> Tốt cho Vàng (BUY)"),
        ("Federal Reserve signals aggressive rate hike cycle to combat inflation", 
         "Fed phát tín hiệu tăng lãi suất quyết liệt để dập lạm phát -> Xấu cho Vàng (SELL)"),
        ("Banking crisis fears re-emerge as major regional lender fails", 
         "Nỗi lo khủng hoảng ngân hàng tái diễn -> Nhu cầu trú ẩn đẩy giá Vàng lên (BUY)"),
        ("US Dollar index breaks out to fresh highs on robust economic resilience", 
         "Chỉ số DXY bứt phá đỉnh mới nhờ kinh tế Mỹ quá vững -> Xấu cho Vàng (SELL)"),
        ("US unemployment rate jumps to 4.3%, triggering recession warning indicator", 
         "Tỷ lệ thất nghiệp Mỹ tăng vọt lên 4.3%, kích hoạt cảnh báo suy thoái -> Tốt cho Vàng (BUY)")
    ]

    print("\n[DANH SÁCH 10 TIN TỨC VĨ MÔ THỰC TẾ ĐỂ TEST]:")
    for i, (headline, note) in enumerate(sample_news, 1):
        print(f"  {i:2d}. {headline}")
        print(f"      ↳ Ý nghĩa: {note}")
    print("  11. [Tự nhập] Gõ một tiêu đề tin tức tiếng Anh bất kỳ của bạn...")

    choice = input("\nChọn số tin tức muốn test (1-11): ").strip()
    headline = ""
    try:
        idx = int(choice)
        if 1 <= idx <= len(sample_news):
            headline = sample_news[idx - 1][0]
        elif idx == 11:
            headline = input("\nNhập tiêu đề tin tức tiếng Anh: ").strip()
        else:
            headline = sample_news[0][0]
    except Exception:
        headline = sample_news[0][0]

    print(f"\n>> Đang phân tích: \"{headline}\"...")
    t0 = time.time()
    res = analyzer.analyze_headline(headline)
    elapsed = (time.time() - t0) * 1000.0

    print("\n" + "-" * 50)
    print(f"  Engine sử dụng:    {res['engine']}")
    print(f"  Thời gian xử lý:   {elapsed:.2f} ms")
    print(f"  Đánh giá nhãn:     {res['label'].upper()}")
    print(f"  Điểm tác động:     {res['sentiment_value']:+.4f} (Thang -1.0 đến +1.0)")
    
    if res['sentiment_value'] > 0.2:
        print("  -> Tác động lên Vàng: 🟢 TÍCH CỰC (Ủng hộ mở lệnh BUY)")
    elif res['sentiment_value'] < -0.2:
        print("  -> Tác động lên Vàng: 🔴 TIÊU CỰC (Ủng hộ mở lệnh SELL)")
    else:
        print("  -> Tác động lên Vàng: ⚪ TRUNG TÍNH (Không ảnh hưởng lớn)")
    print("-" * 50)


def test_ipc_signal_injection():
    """Test 3: Bắn trực tiếp tín hiệu sang MT5 để kiểm tra EA."""
    print("\n" + "=" * 70)
    print("  TEST 3: BẮN TÍN HIỆU THỦ CÔNG SANG METATRADER 5 (IPC BRIDGE CHECK)")
    print("=" * 70)
    print("Bạn có thể tự chọn bắn lệnh nào sang MetaTrader 5 ngay bây giờ:")
    print("  1. Bắn lệnh BUY  (LONG_POSITION_ON, Độ tự tin: 85%)")
    print("  2. Bắn lệnh SELL (SHORT_POSITION_ON, Độ tự tin: 80%)")
    print("  3. Bắn lệnh NEUTRAL (Hủy trạng thái, Đứng ngoài)")

    choice = input("\nChọn lệnh muốn bắn (1-3): ").strip()
    sig = "NEUTRAL"
    conf = 0.50

    if choice == '1':
        sig = "LONG_POSITION_ON"
        conf = 0.85
    elif choice == '2':
        sig = "SHORT_POSITION_ON"
        conf = 0.80
    elif choice == '3':
        sig = "NEUTRAL"
        conf = 0.30

    IPCBridge.send_signal(sig, conf)
    
    # Bắn thông báo về Telegram cá nhân
    notifier = TelegramNotifier()
    tg_display = "BUY_STRONG" if sig == "LONG_POSITION_ON" else ("SELL_STRONG" if sig == "SHORT_POSITION_ON" else "NEUTRAL")
    p_buy = conf if "LONG" in sig else (0.10 if "SHORT" in sig else 0.33)
    p_sell = conf if "SHORT" in sig else (0.10 if "LONG" in sig else 0.33)
    p_hold = 0.10 if sig != "NEUTRAL" else 0.34
    sent_score = +0.75 if "LONG" in sig else (-0.75 if "SHORT" in sig else 0.0)
    
    print(">> Đang bắn thông báo đồng thời tới Telegram cá nhân...")
    tg_ok = notifier.notify_trading_signal(
        symbol=SYMBOL,
        signal_str=tg_display,
        confidence=conf,
        sentiment_score=sent_score,
        prob_buy=p_buy,
        prob_sell=p_sell,
        prob_hold=p_hold,
        reason="Kích hoạt kiểm thử thủ công trực tiếp từ Manual Test Suite"
    )
    
    # Kiểm tra file đã được ghi
    appdata = os.getenv('APPDATA')
    target_path = os.path.join(appdata, "MetaQuotes", "Terminal", "Common", "Files", f"vc_signal_{SYMBOL}.txt")
    print("\n" + "-" * 60)
    print(f"✅ Đã ghi thành công tín hiệu '{sig}' (Confidence: {conf:.2f})!")
    print(f"📂 Vị trí file MT5 nhận: {target_path}")
    if os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            print(f"📄 Nội dung file thực tế hiện tại: \"{f.read().strip()}\"")
    print(f"📱 Trạng thái gửi Telegram Bot: {'✅ THÀNH CÔNG (Kiểm tra điện thoại)' if tg_ok else '❌ CHƯA GỬI ĐƯỢC'}")
    print("-" * 60)
    print(">> Bạn hãy mở màn hình MT5 và Telegram để xem tín hiệu nhảy đồng thời!")


def test_live_engine_cycle():
    """Test 4: Chạy 1 chu kỳ suy luận thực tế với đầy đủ 3 tầng AI."""
    print("\n" + "=" * 70)
    print("  TEST 4: CHẠY 1 CHU KỲ SUY LUẬN AI ĐẦY ĐỦ 3 TẦNG TRÊN DỮ LIỆU HIỆN TẠI")
    print("=" * 70)
    
    engine = AIEngine()
    engine.initialize()
    engine.load_model()
    
    # Nạp pattern matcher
    df = load_cached_data('H4')
    engine.pattern_matcher = PatternMatcher(df, window_size=TIME_STEPS)

    print("\n>> Bắt đầu quét và suy luận...")
    res = engine.predict()
    
    print("\n" + "=" * 60)
    print("         BẢNG ĐIỀU KHIỂN QUYẾT ĐỊNH AI THỰC TẾ")
    print("=" * 60)
    print(f"  Tín hiệu đưa ra:         {res['display_signal']}")
    print(f"  Độ tự tin định hướng:    {res['confidence']*100:.1f}%")
    print(f"  Xác suất BUY:            {res['prob_buy']*100:.1f}%")
    print(f"  Xác suất SELL:           {res['prob_sell']*100:.1f}%")
    print(f"  Xác suất HOLD:           {res['prob_hold']*100:.1f}%")
    print(f"  Điểm số HFT Sentiment:   {res['sentiment']:+.4f}")
    print(f"  Trạng thái chặn tin đỏ:  {'CÓ (KHÓA LỆNH)' if res['is_blocked'] else 'KHÔNG (CHO PHÉP GIAO DỊCH)'}")
    print("=" * 60)


def main():
    while True:
        clear()
        print("==================================================================")
        print("       VQUANT - BỘ KIỂM TRA & ĐỐI CHIẾU THỰC TẾ THỦ CÔNG          ")
        print("   Tác giả: Nguyễn Mạnh Cường _ B22DCCN099 (Khoa CNTT 1 - PTIT)  ")
        print("==================================================================")
        print("  1. [Test 1] Đối chiếu dự báo AI với diễn biến giá thực tế lịch sử")
        print("  2. [Test 2] Thử nghiệm bộ phân tích tin tức NLP với tin bất kỳ   ")
        print("  3. [Test 3] Tự tay bắn tín hiệu BUY / SELL / NEUTRAL sang MT5   ")
        print("  4. [Test 4] Chạy 1 chu kỳ AI Inference toàn diện trên thị trường ")
        print("  5. Thoát                                                        ")
        print("==================================================================")
        
        c = input("\nChọn bài test thủ công muốn thực hiện (1-5): ").strip()
        if c == '1':
            test_walk_forward_accuracy()
            input("\nNhấn Enter để quay lại menu...")
        elif c == '2':
            test_custom_news()
            input("\nNhấn Enter để quay lại menu...")
        elif c == '3':
            test_ipc_signal_injection()
            input("\nNhấn Enter để quay lại menu...")
        elif c == '4':
            test_live_engine_cycle()
            input("\nNhấn Enter để quay lại menu...")
        elif c == '5':
            print("\nĐã thoát bộ kiểm tra.")
            break


if __name__ == "__main__":
    main()
