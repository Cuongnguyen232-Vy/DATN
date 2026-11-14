# -*- coding: utf-8 -*-
"""
VQuant 24/7 Autonomous Sentinel — Tự động lọc tin tức & bắn tín hiệu giao dịch 24/7.
Author: Nguyễn Mạnh Cường_B22DCCN099
Institution: PTIT

Chức năng chính:
  1. Lọc tin tức kinh tế vĩ mô liên tục 24/7 (ForexFactory, FinnHub, NewsAPI).
  2. Bắn cảnh báo tin tức khẩn cấp (Proximity & Breaking News) về Telegram.
  3. Dự báo AI đa tầng (CNN-BiGRU + Pattern Matching + FinBERT Sentiment).
  4. Đưa tín hiệu giao dịch về 24/7 qua:
       - Telegram (Thông báo trực tiếp vào điện thoại người dùng)
       - MetaTrader 5 EA (IPC Bridge file vc_signal_XAUUSD.txt)
       - Web Dashboard (Telemetry API)
  5. Chống crash, tự động phục hồi khi mất mạng (Fault-tolerant 24/7 Loop).
"""

import os
import sys
import time
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import SYMBOL, DATA_DIR
from src.engine.ai_engine import AIEngine
from src.bot.notifier import TelegramNotifier
from src.data.nlp_finbert import FinBERT_Analyzer


class Sentinel247:
    """Hệ thống tự động giám sát tin tức và phát tín hiệu 24/7 độc lập."""

    def __init__(self, cycle_seconds: int = 20):
        self.cycle_seconds = cycle_seconds
        self.start_time = datetime.now()
        self.notifier = TelegramNotifier()
        self.ai_engine = AIEngine()
        
        # State tracking (Deduplication & Anti-spam)
        self.notified_news_events = set()
        self.last_sent_signal = "NEUTRAL"
        self.last_signal_time = 0
        self.last_heartbeat_time = time.time()
        self.last_burst_notified = 0
        self.total_cycles = 0
        self.total_signals_sent = 0
        self.total_news_alerted = 0
        self.running = False

    def initialize(self) -> bool:
        """Khởi động toàn bộ các tầng AI, News Streamer và Telegram Bridge."""
        print("=" * 70)
        print("  VQUANT 24/7 AUTONOMOUS SENTINEL — KHỞI TẠO HỆ THỐNG")
        print("=" * 70)

        # 1. Khởi tạo AI Engine
        print("[1/3] Khởi động AI Engine (Model weights & NLP)...")
        if not self.ai_engine.initialize():
            print("[LỖI] Không thể khởi tạo AI Engine!")
            return False

        if not self.ai_engine.load_model():
            print("[LỖI] Chưa nạp được Deep Learning Model. Vui lòng train model trước!")
            return False

        # 2. Khởi động HFT News Streamer (Daemon background thread)
        print("[2/3] Kích hoạt HFT News Streamer (ForexFactory / FinnHub / NewsAPI)...")
        self.ai_engine._start_hft_streamer()
        time.sleep(2)  # Warm-up

        # 3. Kiểm tra kênh Telegram
        print("[3/3] Kiểm tra kết nối Telegram Bot...")
        welcome_msg = (
            f"🛡️ <b>[VQUANT 24/7] KHỞI ĐỘNG HỆ THỐNG GIÁM SÁT THÀNH CÔNG</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <b>Tài sản giám sát:</b> <code>{SYMBOL}</code>\n"
            f"🧠 <b>Mô hình:</b> CNN-Bidirectional GRU + FinBERT NLP\n"
            f"📡 <b>Chu kỳ quét:</b> Mỗi <code>{self.cycle_seconds}s</code>\n"
            f"🌐 <b>Kênh nhận tín hiệu:</b> Telegram + MT5 IPC Bridge\n"
            f"🕒 <i>Thời gian bắt đầu: {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}</i>"
        )
        self.notifier.send_message(welcome_msg)
        print("  >> Đã gửi thông báo khởi động tới Telegram!\n")
        return True

    def process_news_alerts(self, hft_data: dict):
        """Quét và gửi cảnh báo tin tức sắp tới hoặc vừa công bố."""
        if not hft_data:
            return

        now_local = datetime.now().astimezone()

        # Kiểm tra ForexFactory Calendar events từ streamer
        if self.ai_engine.hft_streamer:
            events = self.ai_engine.hft_streamer.get_active_events()
            for item in events:
                title = item.get("title", "")
                impact = item.get("impact", "")
                date_str = item.get("date", "")
                actual = item.get("actual", "")
                forecast = item.get("forecast", "")
                previous = item.get("previous", "")
                
                if not title or impact not in ["High", "Medium"]:
                    continue

                event_id = f"{title}_{date_str}_{actual}"
                if event_id in self.notified_news_events:
                    continue

                # Phân tích độ gần về mặt thời gian
                try:
                    event_dt = datetime.fromisoformat(date_str).astimezone()
                    time_diff_min = (event_dt - now_local).total_seconds() / 60.0
                    time_str = event_dt.strftime("%H:%M - %d/%m")

                    # 1. Cảnh báo sắp có tin đỏ trong vòng 30 phút
                    if 0 < time_diff_min <= 30:
                        prox_text = f"CÒN {int(time_diff_min)} PHÚT NỮA SẼ CÔNG BỐ!"
                        # NLP score dự đoán
                        headline = f"Upcoming {title}: Forecast {forecast} (Previous: {previous})"
                        nlp_res = self.ai_engine.nlp_analyzer.analyze_headline(headline)

                        self.notifier.notify_economic_news(
                            title=title, impact=impact, time_str=time_str,
                            score=nlp_res['sentiment_value'], label=nlp_res['label'],
                            actual="", forecast=forecast, previous=previous,
                            proximity_text=prox_text
                        )
                        self.notified_news_events.add(event_id)
                        self.total_news_alerted += 1
                        print(f"[News Watchdog] Đã bắn cảnh báo tin đỏ sắp tới: {title} ({prox_text})")

                    # 2. Cảnh báo khi tin vừa có số liệu Actual
                    elif -30 <= time_diff_min <= 0 and actual:
                        prox_text = "SỐ LIỆU THỰC TẾ VỪA ĐƯỢC CÔNG BỐ!"
                        headline = f"{title}: Actual {actual} vs Forecast {forecast} (Previous: {previous})"
                        nlp_res = self.ai_engine.nlp_analyzer.analyze_headline(headline)

                        self.notifier.notify_economic_news(
                            title=title, impact=impact, time_str=time_str,
                            score=nlp_res['sentiment_value'], label=nlp_res['label'],
                            actual=actual, forecast=forecast, previous=previous,
                            proximity_text=prox_text
                        )
                        self.notified_news_events.add(event_id)
                        self.total_news_alerted += 1
                        print(f"[News Watchdog] Đã bắn cảnh báo số liệu thực tế: {title} (Actual: {actual})")

                except Exception as e:
                    pass

    def check_burst_mode(self, hft_data: dict):
        """Giám sát và cảnh báo bão tin tức."""
        if not hft_data:
            return

        is_burst = hft_data.get("is_burst", False)
        now_ts = time.time()

        if is_burst and (now_ts - self.last_burst_notified > 300):  # Cooldown 5 phút
            self.last_burst_notified = now_ts
            self.notifier.notify_burst_alert(
                active_count=hft_data.get("num_active_news", 0),
                composite_score=hft_data.get("composite_score", 0.0),
                news_blocked=hft_data.get("is_news_blocked", False)
            )
            print("[Burst Alert] Đã gửi thông báo bão tin tức về Telegram!")

    def dispatch_trading_signal(self, pred_result: dict):
        """Đưa tín hiệu giao dịch về Telegram và MT5 với cơ chế chống spam."""
        if not pred_result:
            return

        sig = pred_result.get("signal", "NEUTRAL")
        display_sig = pred_result.get("display_signal", "NEUTRAL")
        conf = pred_result.get("confidence", 0.0)
        sentiment = pred_result.get("sentiment", 0.0)
        prob_buy = pred_result.get("prob_buy", 0.0)
        prob_sell = pred_result.get("prob_sell", 0.0)
        prob_hold = pred_result.get("prob_hold", 0.0)
        is_blocked = pred_result.get("is_blocked", False)

        now_ts = time.time()

        # Điều kiện gửi thông báo Telegram:
        # 1. Có tín hiệu MUA hoặc BÁN mạnh (BUY_STRONG / SELL_STRONG)
        # 2. Hoặc tín hiệu thay đổi so với lần gửi trước
        # 3. Hoặc đã qua 30 phút kể từ lần gửi tín hiệu trước
        should_send_telegram = False
        reason = ""

        if is_blocked:
            reason = "Bão tin tức vĩ mô — Tạm ngừng vào lệnh mới để bảo vệ vị thế"
        elif display_sig in ["BUY_STRONG", "SELL_STRONG"]:
            if sig != self.last_sent_signal or (now_ts - self.last_signal_time > 1800):
                should_send_telegram = True
                reason = "AI Deep Learning + Sentiment hội tụ tín hiệu xác suất cao (>80%)"
        elif sig != self.last_sent_signal and self.last_sent_signal in ["BUY_STRONG", "SELL_STRONG"]:
            # Đảo chiều về NEUTRAL -> Báo đóng vị thế
            should_send_telegram = True
            reason = "Thị trường chuyển sang trạng thái đi ngang/trung tính"

        if should_send_telegram:
            self.last_sent_signal = sig
            self.last_signal_time = now_ts
            self.total_signals_sent += 1
            
            self.notifier.notify_trading_signal(
                symbol=SYMBOL,
                signal_str=display_sig,
                confidence=conf,
                sentiment_score=sentiment,
                prob_buy=prob_buy,
                prob_sell=prob_sell,
                prob_hold=prob_hold,
                reason=reason
            )
            print(f"🚀 [Signal Dispatch] Đã bắn tín hiệu '{display_sig}' về Telegram & MT5!")

    def check_heartbeat(self, hft_data: dict):
        """Gửi heartbeat định kỳ 6 tiếng 1 lần để báo cáo hệ thống sống tốt."""
        now_ts = time.time()
        # 6 giờ = 21600s (đổi thành 4 giờ = 14400s)
        if now_ts - self.last_heartbeat_time >= 14400:
            self.last_heartbeat_time = now_ts
            uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            uptime_str = f"{hours}h {minutes}p"

            active_news = hft_data.get("num_active_news", 0) if hft_data else 0
            sentiment = hft_data.get("composite_score", 0.0) if hft_data else 0.0

            self.notifier.notify_heartbeat(
                uptime_str=uptime_str,
                active_news=active_news,
                last_signal=self.last_sent_signal,
                sentiment=sentiment
            )
            print("[Heartbeat] Đã gửi báo cáo sức khỏe định kỳ tới Telegram.")

    def run_247(self):
        """Vòng lặp chính 24/7 — Tự động bắt lỗi và chạy vĩnh viễn."""
        if not self.initialize():
            return

        self.running = True
        print("\n" + "=" * 70)
        print("  VQUANT 24/7 SENTINEL ĐANG HOẠT ĐỘNG...")
        print(f"  Bắt đầu lúc: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("  Nhấn Ctrl+C để dừng an toàn.")
        print("=" * 70 + "\n")

        while self.running:
            try:
                self.total_cycles += 1
                cycle_time_str = datetime.now().strftime("%H:%M:%S")

                # ─── 1. AI Predict & Signal Generation ───
                pred_result = self.ai_engine.predict()
                hft_data = pred_result.get("hft_data") if pred_result else None

                # ─── 2. News Alert Watchdog ───
                if hft_data:
                    self.process_news_alerts(hft_data)
                    self.check_burst_mode(hft_data)

                # ─── 3. Signal Dispatch to Telegram & MT5 ───
                if pred_result:
                    self.dispatch_trading_signal(pred_result)

                # ─── 4. Periodic Heartbeat ───
                self.check_heartbeat(hft_data)

                # ─── Console Status Line ───
                comp_score = hft_data.get("composite_score", 0.0) if hft_data else 0.0
                active_n = hft_data.get("num_active_news", 0) if hft_data else 0
                sig_display = pred_result.get("display_signal", "NEUTRAL") if pred_result else "N/A"
                print(f"[{cycle_time_str}] Cycle #{self.total_cycles} | "
                      f"Sig: {sig_display:<11} | "
                      f"Sentiment: {comp_score:+.3f} | "
                      f"News: {active_n} | "
                      f"Alerts: {self.total_news_alerted} | "
                      f"Signals: {self.total_signals_sent}")

                # Chờ chu kỳ tiếp theo
                time.sleep(self.cycle_seconds)

            except KeyboardInterrupt:
                print("\n[Sentinel 24/7] Người dùng gửi lệnh dừng...")
                self.stop()
                break

            except Exception as e:
                # Bắt mọi lỗi mạng, lỗi MT5, lỗi parser để vòng lặp 24/7 KHÔNG BAO GIỜ CRASH
                print(f"[Sentinel 24/7 Cảnh báo] Gặp lỗi tạm thời: {e}. Tự động khôi phục sau 5s...")
                time.sleep(5)

    def stop(self):
        """Dừng an toàn toàn bộ hệ thống."""
        self.running = False
        print("[Sentinel 24/7] Đang tắt HFT News Streamer...")
        self.ai_engine._stop_hft_streamer()
        self.ai_engine.shutdown()

        stop_msg = (
            f"⏹️ <b>[VQUANT 24/7] HỆ THỐNG ĐÃ TẠM DỪNG</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ Tổng chu kỳ quét: <code>{self.total_cycles}</code>\n"
            f"📰 Cảnh báo tin tức đã gửi: <code>{self.total_news_alerted}</code>\n"
            f"🚀 Tín hiệu giao dịch đã gửi: <code>{self.total_signals_sent}</code>\n"
            f"🕒 <i>Thời gian dừng: {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}</i>"
        )
        self.notifier.send_message(stop_msg)
        print("[Sentinel 24/7] Đã dừng hoàn toàn. Trở về menu chính.\n")


def run_standalone():
    sentinel = Sentinel247(cycle_seconds=20)
    sentinel.run_247()


if __name__ == "__main__":
    run_standalone()
