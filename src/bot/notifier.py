# -*- coding: utf-8 -*-
"""
VQuant Telegram Notifier — Real-time Alert & Signal Dispatcher.
Gửi thông báo và tín hiệu 24/7 trực tiếp về Telegram của người dùng.
"""

import os
import sys
import requests
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramNotifier:
    """Module gửi thông báo tự động 24/7 tới Telegram cá nhân/nhóm."""

    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Gửi tin nhắn Telegram qua REST API có xử lý ngoại lệ."""
        if not self.token or not self.chat_id:
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        try:
            resp = requests.post(url, json=payload, timeout=8)
            return resp.status_code == 200
        except Exception as e:
            print(f"[Telegram Notifier] Loi gui tin nhan: {e}")
            return False

    def notify_economic_news(self, title: str, impact: str, time_str: str, 
                             score: float, label: str, actual: str = "", 
                             forecast: str = "", previous: str = "",
                             proximity_text: str = ""):
        """Gửi cảnh báo tin tức kinh tế quan trọng (CPI, FOMC, NFP...)."""
        icon_impact = "🔴 HIGH" if impact == "High" else "🟠 MEDIUM"
        if score > 0.05:
            trend_icon = "📈 <b>TĂNG VÀNG (BULLISH)</b>"
        elif score < -0.05:
            trend_icon = "📉 <b>GIẢM VÀNG (BEARISH)</b>"
        else:
            trend_icon = "⚖️ <b>TRUNG TÍNH (NEUTRAL)</b>"

        time_now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        
        data_line = ""
        if actual:
            data_line = f"\n▫️ <b>Actual:</b> <code>{actual}</code> | <b>Forecast:</b> <code>{forecast}</code> | <b>Previous:</b> <code>{previous}</code>"
        elif forecast:
            data_line = f"\n▫️ <b>Forecast:</b> <code>{forecast}</code> | <b>Previous:</b> <code>{previous}</code>"

        prox_line = f"\n⚠️ <b>Thời điểm:</b> {proximity_text}" if proximity_text else ""

        msg = (
            f"🔔 <b>[VQUANT 24/7] CẢNH BÁO TIN TỨC VĨ MÔ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📰 <b>Sự kiện:</b> <code>{title}</code>\n"
            f"⚡ <b>Mức độ:</b> {icon_impact} (USD)\n"
            f"⏰ <b>Lịch công bố:</b> {time_str}{prox_line}{data_line}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 <b>FinBERT NLP:</b> {score:+.3f} | {label.upper()}\n"
            f"🎯 <b>Xu hướng dự báo:</b> {trend_icon}\n"
            f"🕒 <i>Cập nhật: {time_now}</i>"
        )
        return self.send_message(msg)

    def notify_trading_signal(self, symbol: str, signal_str: str, confidence: float,
                              sentiment_score: float, prob_buy: float, 
                              prob_sell: float, prob_hold: float, reason: str = ""):
        """Gửi tín hiệu vào lệnh giao dịch sinh ra từ AI Engine."""
        if "BUY" in signal_str or "LONG" in signal_str:
            action_badge = "🟢 <b>MUA MẠNH (BUY / LONG)</b>"
        elif "SELL" in signal_str or "SHORT" in signal_str:
            action_badge = "🔴 <b>BÁN MẠNH (SELL / SHORT)</b>"
        else:
            action_badge = "🟡 <b>ĐỨNG NGOÀI (HOLD / NEUTRAL)</b>"

        time_now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        reason_line = f"\n💡 <b>Lý do:</b> {reason}" if reason else ""

        msg = (
            f"🚀 <b>[VQUANT 24/7] TÍN HIỆU GIAO DỊCH MỚI</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <b>Cặp tài sản:</b> <code>{symbol}</code>\n"
            f"🎯 <b>Tín hiệu:</b> {action_badge}\n"
            f"📊 <b>Độ tự tin AI:</b> <code>{confidence*100:.1f}%</code>\n"
            f"🧠 <b>News Sentiment:</b> <code>{sentiment_score:+.3f}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 Xác suất BUY:  <code>{prob_buy*100:.1f}%</code>\n"
            f"📉 Xác suất SELL: <code>{prob_sell*100:.1f}%</code>\n"
            f"⏸️ Xác suất HOLD: <code>{prob_hold*100:.1f}%</code>{reason_line}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <i>Lệnh đã chuyển sang MT5 EA qua IPC Bridge.</i>\n"
            f"🕒 <i>Thời gian: {time_now}</i>"
        )
        return self.send_message(msg)

    def notify_burst_alert(self, active_count: int, composite_score: float, 
                           news_blocked: bool):
        """Cảnh báo bão tin tức vĩ mô (Burst Mode)."""
        time_now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        shield = "🛡️ <b>ĐÃ KÍCH HOẠT SHIELD: TẠM NGỪNG MỞ LỆNH ĐỂ BẢO VỆ VỐN!</b>" if news_blocked else "⚠️ <b>Hệ thống đang nhân đôi (x2) trọng số Sentiment!</b>"

        msg = (
            f"🌪️ <b>[VQUANT 24/7] PHÁT HIỆN BÃO TIN TỨC (BURST MODE)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💥 <b>Số tin dồn dập:</b> <code>{active_count} tin tức / 60 giây</code>\n"
            f"📊 <b>Composite Sentiment:</b> <code>{composite_score:+.4f}</code>\n"
            f"{shield}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 <i>Thời gian: {time_now}</i>"
        )
        return self.send_message(msg)

    def notify_heartbeat(self, uptime_str: str, active_news: int, 
                         last_signal: str, sentiment: float):
        """Báo cáo định kỳ sức khỏe hệ thống 24/7."""
        time_now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        msg = (
            f"💚 <b>[VQUANT 24/7] HEARTBEAT BÁO CÁO ĐỊNH KỲ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ <b>Thời gian hoạt động:</b> {uptime_str}\n"
            f"📰 <b>Tin tức đang theo dõi:</b> {active_news} tin tức\n"
            f"🧠 <b>Tâm lý thị trường:</b> <code>{sentiment:+.3f}</code>\n"
            f"🎯 <b>Tín hiệu gần nhất:</b> <code>{last_signal}</code>\n"
            f"✅ <i>Tất cả luồng Daemon & HFT Streamer hoạt động ổn định.</i>\n"
            f"🕒 <i>Thời gian: {time_now}</i>"
        )
        return self.send_message(msg)
