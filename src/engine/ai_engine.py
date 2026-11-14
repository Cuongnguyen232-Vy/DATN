import os
import time
import numpy as np
from datetime import datetime
import joblib
from tensorflow.keras.models import load_model

from src.config import SYMBOL, MODEL_PATH, SCALER_PATH, TIME_STEPS
from src.data.fetcher import MT5Fetcher
from src.data.features import FeatureEngine
from src.models.trainer import ModelTrainer
from src.engine.ipc_bridge import IPCBridge
from src.models.pattern_matcher import PatternMatcher
from src.data.nlp_finbert import FinBERT_Analyzer
from src.data.news_filter import NewsFilter
from src.data.hft_news_streamer import HFTNewsStreamer


class AIEngine:
    """
    VQuant AI Engine — Institutional-grade Trading Signal Generator.

    Tích hợp:
        1. CNN-Bidirectional GRU Deep Learning Model
        2. Time-Series Pattern Matching (K-Nearest Neighbors)
        3. HFT News Sentiment Streamer (Background Thread, Zero-latency)
        4. IPC Bridge → MetaTrader 5 Expert Advisor
    """

    def __init__(self):
        self.fetcher = MT5Fetcher(SYMBOL)
        self.model = None
        self.scaler = None
        self.pattern_matcher = None
        self.nlp_analyzer = FinBERT_Analyzer()
        self.hft_streamer = None  # Khởi tạo khi run_loop()

    def initialize(self):
        return self.fetcher.initialize()

    def load_model(self):
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            return False
        self.model = load_model(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        return True

    def _start_hft_streamer(self) -> None:
        """Khởi động HFT News Streamer daemon thread."""
        if self.hft_streamer is not None and self.hft_streamer.running:
            return
        self.hft_streamer = HFTNewsStreamer(
            nlp_analyzer=self.nlp_analyzer,
            currency="USD"
        )
        self.hft_streamer.start()

    def _stop_hft_streamer(self) -> None:
        """Dừng HFT News Streamer."""
        if self.hft_streamer is not None:
            self.hft_streamer.stop()
            self.hft_streamer = None

    def predict(self):
        print(f"\n[Data Fetch] Dang tai he ma tran nen H4 ({SYMBOL})...")
        df_h4 = self.fetcher.fetch_data(16388, 150) 
        
        if df_h4 is None or len(df_h4) < 150:
            return None

        # Feature Engineering (Bao gom News Sentiment lich su)
        df_h4 = FeatureEngine.add_features(df_h4)

        # ─── HFT SENTIMENT: Zero-latency read từ Background Thread ───
        live_sentiment = 0.0
        is_blocked = False
        news_msg = "Thi truong binh yen"
        hft_data = None

        if self.hft_streamer and self.hft_streamer.running:
            # Đọc aggregated sentiment KHÔNG CÓ NETWORK I/O (~0μs)
            hft_data = self.hft_streamer.get_aggregated_sentiment()
            live_sentiment = hft_data['composite_score']
            is_blocked = hft_data['is_news_blocked']
            news_msg = hft_data.get('news_block_reason', '')

            # In telemetry
            print(f"[HFT-NLP] Composite Sentiment: {live_sentiment:+.4f} "
                  f"({hft_data['dominant_label'].upper()}) | "
                  f"Active News: {hft_data['num_active_news']} | "
                  f"Burst: {'YES' if hft_data['is_burst'] else 'NO'} | "
                  f"Poll: {hft_data['polling_interval_ms']:.0f}ms")

            # Hiển thị top headlines
            for h in hft_data.get('latest_headlines', [])[:3]:
                age_str = f"{h['age_seconds']:.0f}s ago"
                decay_str = f"decay:{h['decayed_value']:+.3f}"
                print(f"  → [{h['source']}] ({age_str}, {decay_str}) "
                      f"{h['headline'][:70]}...")
        else:
            # Fallback: gọi NLP trực tiếp nếu streamer chưa chạy
            nf = NewsFilter(currency="USD")
            is_blocked, news_msg = nf.check_news_block()
            finbert_result = self.nlp_analyzer.analyze_headline(news_msg)
            live_sentiment = finbert_result['sentiment_value']
            print(f"[NLP FinBERT] Fallback mode | Sentiment: {live_sentiment:+.2f}")
            
        # Live sentiment được kết hợp đa tầng ở Ensemble Layer (không làm ô nhiễm không gian đặc trưng chuỗi)
            
        df_recent = df_h4.tail(TIME_STEPS)
        feature_cols = [c for c in df_recent.columns if c not in ['time', 'real_volume']]
        features = df_recent[feature_cols].values
        
        # ─── PATTERN MATCHING: Tìm kiếm quá khứ tương đồng ───
        pattern_bias = 0.0
        if self.pattern_matcher is not None:
            current_close_window = df_recent['close'].values
            similar_patterns = self.pattern_matcher.find_similar_patterns(current_close_window, top_k=5)
            
            up_count = sum(1 for p in similar_patterns if p['future_change_usd'] > 0)
            down_count = sum(1 for p in similar_patterns if p['future_change_usd'] < 0)
            
            print(f"[Pattern Matching] Da tim thay {len(similar_patterns)} mau hinh trong lich su giong het hien tai!")
            print(f" -> Qua khu: {up_count} lan TANG, {down_count} lan GIAM.")
            
            pattern_bias = (up_count - down_count) / 5.0

        # ─── DEEP LEARNING INFERENCE ───
        try:
            scaled = self.scaler.transform(features)
            X_input = np.array([scaled])
            pred = self.model.predict(X_input, verbose=0)[0]
        except Exception as e:
            print("[Loi] Kich thuoc Vector khong khop. Vui long Train lai AI!")
            return None
            
        prob_hold, prob_buy, prob_sell = pred[0], pred[1], pred[2]
        
        # ─── ENSEMBLE: Kết hợp DL + Pattern + HFT Sentiment ───
        # Pattern Matching bias
        prob_buy += pattern_bias * 0.1
        prob_sell -= pattern_bias * 0.1

        # HFT Sentiment bias (trọng số 0.15 — mạnh hơn pattern vì tin tức real-time)
        sentiment_boost = live_sentiment * 0.15
        if live_sentiment > 0.2:  # Tin tốt cho vàng → tăng xác suất BUY
            prob_buy += sentiment_boost
            prob_sell -= sentiment_boost * 0.5
        elif live_sentiment < -0.2:  # Tin xấu cho vàng → tăng xác suất SELL
            prob_sell += abs(sentiment_boost)
            prob_buy -= abs(sentiment_boost) * 0.5

        # Burst mode: tăng gấp đôi trọng số sentiment khi có bão tin tức
        if hft_data and hft_data.get('is_burst'):
            burst_boost = live_sentiment * 0.10
            prob_buy += burst_boost if live_sentiment > 0 else 0
            prob_sell += abs(burst_boost) if live_sentiment < 0 else 0
            print(f"[BURST MODE] Phat hien bao tin tuc! Sentiment boost x2: {burst_boost:+.4f}")

        # Normalize probabilities
        total = prob_hold + prob_buy + prob_sell
        if total > 0:
            prob_hold /= total
            prob_buy /= total
            prob_sell /= total
        
        print(f"[Deep Learning CNN-GRU] BUY ({prob_buy*100:.1f}%) | SELL ({prob_sell*100:.1f}%) | HOLD ({prob_hold*100:.1f}%)")
        
        signal_string = "NEUTRAL"
        display_signal = "NEUTRAL"
        confidence = float(prob_hold)
        
        # ─── NEWS FILTER BLOCKING ───
        if is_blocked:
            print(f"[NEWS ALERT] {news_msg}")
            print(">> AI phat hien bao tin tuc! Tam ngung vao lenh.")
            prob_buy = 0.0; prob_sell = 0.0
        
        # Nguong ra quyet dinh da tang: Voi 3 lop (HOLD/BUY/SELL), xac suat dong deu la 33.3%.
        # Khi mot phe vuot 45% va ap dao phe doi dien (+15%), do la tin hieu xu huong manh.
        if prob_buy >= 0.45 and prob_buy > prob_sell + 0.15:
            dir_conf = float(prob_buy / (prob_buy + prob_sell)) if (prob_buy + prob_sell) > 0 else float(prob_buy)
            signal_string = "LONG_POSITION_ON"; display_signal = "BUY_STRONG"; confidence = dir_conf
        elif prob_sell >= 0.45 and prob_sell > prob_buy + 0.15:
            dir_conf = float(prob_sell / (prob_buy + prob_sell)) if (prob_buy + prob_sell) > 0 else float(prob_sell)
            signal_string = "SHORT_POSITION_ON"; display_signal = "SELL_STRONG"; confidence = dir_conf
        else:
            signal_string = "NEUTRAL"; display_signal = "NEUTRAL"; confidence = float(prob_hold)
            
        print(f"\n--- SIGNAL: {display_signal} (Do tu tin: {confidence:.2f}) ---")
        IPCBridge.send_signal(signal_string, confidence)
        print("-" * 60)
        
        return {
            "signal": signal_string,
            "display_signal": display_signal,
            "confidence": confidence,
            "prob_buy": float(prob_buy),
            "prob_sell": float(prob_sell),
            "prob_hold": float(prob_hold),
            "sentiment": live_sentiment,
            "hft_data": hft_data,
            "is_blocked": is_blocked,
            "news_msg": news_msg if is_blocked else ""
        }


    def run_loop(self):
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("-" * 60)
        print(f"[{now_str}] Kich hoat Inference Engine (REAL AI)...")
        
        if not self.load_model():
            print(" Chua tim thay model. Vui long chay che do Huan luyen (2) truoc!")
            print("-" * 60)
            return

        # ─── KHỞI ĐỘNG HFT NEWS STREAMER ───
        print("\n[System] Dang khoi dong HFT News Sentiment Streamer...")
        self._start_hft_streamer()
        # Chờ 3 giây để streamer thu thập tin tức đầu tiên
        print("[System] Cho streamer warm-up 3 giay...")
        time.sleep(3)

        print("[System] Dang nap co so du lieu Pattern Matching (K-Nearest Neighbors)...")
        hist_df = self.fetcher.fetch_data(16388, 5000)
        if hist_df is not None:
            self.pattern_matcher = PatternMatcher(hist_df, window_size=TIME_STEPS)
            
        print("[Main] Dang lang nghe Streaming Tick va cho dong nen...")
        print("=" * 60)
        print("  VQUANT HFT ENGINE — LIVE MODE")
        print("  AI Model: CNN-Bidirectional GRU")
        print("  News Engine: HFT Multi-Source Streamer (Background Thread)")
        print("  IPC Bridge: File-based → MT5 EA")
        print(f"  Symbol: {SYMBOL}")
        print("=" * 60)

        cycle_count = 0
        while True:
            try:
                time.sleep(10)  # Chu kỳ dự đoán (10s)
                cycle_count += 1
                print(f"\n{'='*60}")
                print(f"[Cycle #{cycle_count}] {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}")
                self.predict()
            except KeyboardInterrupt:
                print("\n[System] Ngat ket noi. Dang dung HFT Streamer...")
                self._stop_hft_streamer()
                print("[System] Tro ve Menu chinh.")
                break

    def train_model(self):
        print("==================================================")
        print("   V CAPITAL 4.0 - REAL NEURAL NETWORK TRAINING   ")
        print("   Huan luyen TensorFlow/Keras Bidirectional GRU  ")
        print("==================================================")
        
        print("[Data Pipeline] Tai 5,000 nen H4 lich su de lam Dataset hoc tap...")
        df = self.fetcher.fetch_data(16388, 5000)
        
        if df is None:
            print(" Loi tai du lieu!")
            return
            
        print("[Feature Engine] Tinh toan RSI, MACD, Bollinger Bands...")
        df = FeatureEngine.add_features(df)
        
        trainer = ModelTrainer(time_steps=TIME_STEPS)
        trainer.train(df)

    def shutdown(self):
        self._stop_hft_streamer()
        self.fetcher.shutdown()
