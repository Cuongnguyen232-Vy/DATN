# -*- coding: utf-8 -*-
"""
Module: Economic Calendar News Filter & Event Detector
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    Monitors ForexFactory economic calendar for high-impact USD events.
    Used as fallback filter when HFT News Streamer is not active,
    and as the news-blocking circuit breaker to prevent trading during
    volatile macro announcements (NFP, FOMC, CPI, etc.).
"""

import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Tuple, List, Dict, Any


class NewsFilter:
    """
    Bộ lọc tin tức kinh tế vĩ mô — Circuit Breaker cho giao dịch.
    
    Tự động khóa giao dịch khi phát hiện sự kiện kinh tế impact cao
    trong khoảng ±before_mins/after_mins phút.
    """

    def __init__(self, currency="USD", impact_levels=None,
                 before_mins=30, after_mins=30):
        self.currency = currency
        self.impact_levels = impact_levels or ["High"]
        self.before_mins = before_mins
        self.after_mins = after_mins
        self.news_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

        # Internal cache to reduce API calls
        self._cached_events = None
        self._cache_timestamp = 0.0
        self._CACHE_TTL = 120.0  # Cache 2 phút

    def fetch_news(self) -> List[Dict[str, Any]]:
        """Lấy lịch kinh tế từ ForexFactory API với caching."""
        import time
        now = time.time()

        # Return cache if still fresh
        if self._cached_events and (now - self._cache_timestamp) < self._CACHE_TTL:
            return self._cached_events

        try:
            response = requests.get(self.news_url, timeout=10)
            if response.status_code == 200:
                self._cached_events = response.json()
                self._cache_timestamp = now
                return self._cached_events
        except Exception as e:
            logging.debug(f"[NewsFilter] Loi lay tin tuc: {e}")

        return self._cached_events or []

    def get_live_sentiment(self) -> float:
        """
        NLP Sentiment Proxy nhanh (dùng khi không có HFT Streamer).
        Trả về -1.0, 0.0, hoặc +1.0 dựa trên sự kiện kinh tế gần nhất.
        """
        news_data = self.fetch_news()
        if not news_data:
            return 0.0

        now_local = datetime.now().astimezone()
        for item in news_data:
            if item.get("country") == self.currency and item.get("impact") in self.impact_levels:
                try:
                    date_str = item.get("date")
                    if not date_str:
                        continue
                    event_time = datetime.fromisoformat(date_str).astimezone()
                    time_diff = (event_time - now_local).total_seconds() / 60.0
                    if -60 <= time_diff <= 60:
                        title = item.get("title", "").lower()
                        # Tin liên quan đến thất nghiệp hoặc CPI → negatice cho gold
                        if "unemployment" in title or "cpi" in title:
                            return -1.0
                        return 1.0
                except Exception:
                    pass
        return 0.0

    def check_news_block(self) -> Tuple[bool, str]:
        """
        Kiểm tra xem hiện tại có nằm trong vùng bão tin tức hay không.
        
        Returns:
            (is_blocked: bool, message: str)
            - is_blocked=True: Tạm ngưng giao dịch
            - message: Mô tả sự kiện / tin tức liên quan
        """
        news_data = self.fetch_news()
        if not news_data:
            return False, "Khong the lay tin tuc"
            
        now_local = datetime.now().astimezone()
        
        upcoming_news = []
        for item in news_data:
            if item.get("country") == self.currency and item.get("impact") in self.impact_levels:
                try:
                    date_str = item.get("date")
                    if not date_str:
                        continue
                    # Parse ISO format with timezone and convert to local time
                    event_time = datetime.fromisoformat(date_str).astimezone()
                    
                    # Calculate time difference
                    time_diff = (event_time - now_local).total_seconds() / 60.0
                    
                    if -self.after_mins <= time_diff <= self.before_mins:
                        return True, f"Tin do: {item.get('title')} vao luc {event_time.strftime('%H:%M')}"
                        
                    if 0 < time_diff <= 120:  # Hiển thị log tin sắp ra trong 2h
                        upcoming_news.append(f"{item.get('title')} ({int(time_diff)}p nua)")
                except Exception:
                    pass
                    
        if upcoming_news:
            return False, "Tin sap ra: " + ", ".join(upcoming_news)
            
        return False, "Thi truong binh yen"

    def get_upcoming_events(self, hours_ahead: int = 4) -> List[Dict[str, Any]]:
        """
        Lấy danh sách sự kiện kinh tế sắp diễn ra trong N giờ tới.
        Dùng cho dashboard hoặc Telegram bot hiển thị lịch.
        """
        news_data = self.fetch_news()
        if not news_data:
            return []

        now_local = datetime.now().astimezone()
        cutoff = now_local + timedelta(hours=hours_ahead)
        events = []

        for item in news_data:
            if item.get("country") != self.currency:
                continue
            try:
                date_str = item.get("date")
                if not date_str:
                    continue
                event_time = datetime.fromisoformat(date_str).astimezone()
                if now_local <= event_time <= cutoff:
                    events.append({
                        'title': item.get('title', ''),
                        'time': event_time.strftime('%H:%M'),
                        'impact': item.get('impact', ''),
                        'forecast': item.get('forecast', ''),
                        'previous': item.get('previous', ''),
                        'minutes_until': int((event_time - now_local).total_seconds() / 60),
                    })
            except Exception:
                pass

        return sorted(events, key=lambda x: x.get('minutes_until', 999))


if __name__ == "__main__":
    nf = NewsFilter(currency="USD")
    is_block, msg = nf.check_news_block()
    print(f"Khoa giao dich: {is_block}")
    print(f"Tin nhan: {msg}")

    print("\nSu kien sap toi (4h):")
    events = nf.get_upcoming_events(hours_ahead=4)
    for evt in events:
        print(f"  [{evt['impact']}] {evt['title']} luc {evt['time']} "
              f"(con {evt['minutes_until']} phut)")
