# -*- coding: utf-8 -*-
"""
Module: HFT News Streamer — Real-time Multi-Source Sentiment Engine
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    High-Frequency Trading grade news sentiment engine. Runs a dedicated
    background thread that continuously polls multiple financial news APIs,
    scores each headline through FinBERT/VADER NLP, and maintains a
    thread-safe rolling sentiment cache with exponential time-decay.

    The AI Engine reads the aggregated sentiment in ~0μs (zero network I/O),
    enabling microsecond-latency signal generation even during news storms.

Architecture:
    ┌──────────────────────────────────────────────────────┐
    │  HFTNewsStreamer (daemon thread)                     │
    │  ├─ Source 1: ForexFactory Calendar API              │
    │  ├─ Source 2: FinnHub Real-time News                 │
    │  ├─ Source 3: NewsAPI.org Financial Headlines        │
    │  └─ Aggregated → NLP Score → Cache (deque + Lock)   │
    └──────────────────────────────────────────────────────┘
              ↓  Zero-latency read (no I/O)
    ┌──────────────────────────────────────────────────────┐
    │  AIEngine.predict()  →  IPC Bridge  →  MT5 EA       │
    └──────────────────────────────────────────────────────┘
"""

import os
import sys
import time
import math
import hashlib
import logging
import threading
from datetime import datetime, timezone, timedelta
from collections import deque
from typing import Dict, Any, List, Optional, Tuple

# UTF-8 console protection
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import requests
except ImportError:
    requests = None  # type: ignore

# ─────────────────────────────────────────────────────────────
# CONFIGURATION CONSTANTS
# ─────────────────────────────────────────────────────────────

# Polling intervals (seconds) — adaptive based on market proximity
POLL_INTERVAL_NORMAL = 15.0       # Thị trường bình yên
POLL_INTERVAL_PRE_NEWS = 5.0      # 30 phút trước tin quan trọng
POLL_INTERVAL_DURING_NEWS = 2.0   # Đang trong vùng bão tin tức
POLL_INTERVAL_BURST = 1.0         # Phát hiện Burst (nhiều tin cùng lúc)

# Sentiment cache
CACHE_MAX_SIZE = 500              # Tối đa 500 tin tức gần nhất trong bộ nhớ
SENTIMENT_HALF_LIFE_SECONDS = 300 # Sentiment giảm 50% sau 5 phút
BURST_THRESHOLD = 3               # >= 3 tin trong 60s = Burst Mode
BURST_WINDOW_SECONDS = 60.0

# API endpoints
FOREXFACTORY_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# Free-tier API keys (user should replace with their own for production)
# These are optional — system works without them using ForexFactory only
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
NEWSAPI_API_KEY = os.environ.get("NEWSAPI_API_KEY", "")


class SentimentEntry:
    """Một mục tin tức đã được chấm điểm sentiment, kèm timestamp."""

    __slots__ = ('headline', 'source', 'sentiment_value', 'label',
                 'confidence', 'timestamp', 'hash_id', 'impact', 'currency')

    def __init__(self, headline: str, source: str, sentiment_value: float,
                 label: str, confidence: float, timestamp: float,
                 impact: str = "Medium", currency: str = "USD"):
        self.headline = headline
        self.source = source
        self.sentiment_value = sentiment_value
        self.label = label
        self.confidence = confidence
        self.timestamp = timestamp
        self.hash_id = hashlib.md5(headline.encode('utf-8', errors='replace')).hexdigest()[:12]
        self.impact = impact
        self.currency = currency

    def age_seconds(self) -> float:
        """Tuổi của tin tức tính bằng giây."""
        return time.time() - self.timestamp

    def decayed_sentiment(self, half_life: float = SENTIMENT_HALF_LIFE_SECONDS) -> float:
        """
        Sentiment với hàm suy giảm theo thời gian (Exponential Decay).
        Tin cũ 5 phút → chỉ còn 50% trọng số.
        Tin cũ 10 phút → chỉ còn 25%.
        Tin cũ 20 phút → chỉ còn 6.25%.
        """
        age = self.age_seconds()
        decay_factor = math.exp(-0.693147 * age / half_life)  # ln(2) ≈ 0.693147
        return self.sentiment_value * decay_factor

    def to_dict(self) -> Dict[str, Any]:
        return {
            'headline': self.headline,
            'source': self.source,
            'sentiment_value': self.sentiment_value,
            'label': self.label,
            'confidence': self.confidence,
            'age_seconds': round(self.age_seconds(), 1),
            'decayed_value': round(self.decayed_sentiment(), 4),
            'impact': self.impact,
            'currency': self.currency,
        }


class HFTNewsStreamer:
    """
    High-Frequency Trading News Sentiment Streamer.

    Chạy một daemon thread liên tục thu thập tin tức từ nhiều nguồn,
    chấm điểm NLP, và lưu vào cache thread-safe. AI Engine đọc cache
    với độ trễ ~0 microsecond (không có network I/O).

    Usage:
        streamer = HFTNewsStreamer(nlp_analyzer)
        streamer.start()
        # ... trong vòng lặp trading ...
        sentiment = streamer.get_aggregated_sentiment()
        streamer.stop()
    """

    def __init__(self, nlp_analyzer=None, currency: str = "USD"):
        """
        Args:
            nlp_analyzer: Instance của FinBERT_Analyzer (đã khởi tạo).
            currency: Đồng tiền cần lọc tin (mặc định "USD" cho vàng XAUUSD).
        """
        self.nlp_analyzer = nlp_analyzer
        self.currency = currency

        # Thread-safe cache
        self._cache: deque = deque(maxlen=CACHE_MAX_SIZE)
        self._lock = threading.Lock()
        self._seen_hashes: set = set()  # Deduplicate headlines

        # Thread control
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False

        # Adaptive polling state
        self._current_interval = POLL_INTERVAL_NORMAL
        self._is_burst_mode = False
        self._is_pre_news = False
        self._news_block_active = False
        self._news_block_reason = ""

        # Statistics
        self._stats = {
            'total_headlines_processed': 0,
            'total_poll_cycles': 0,
            'sources_active': [],
            'last_poll_time': 0.0,
            'last_poll_duration_ms': 0.0,
            'burst_events': 0,
        }

        # ForexFactory calendar cache (refresh mỗi 5 phút)
        self._ff_cache = []
        self._ff_last_fetch = 0.0
        self._FF_CACHE_TTL = 300.0  # 5 phút

    # ─────────────────────────────────────────────────────
    # PUBLIC API — Zero-latency reads (no I/O)
    # ─────────────────────────────────────────────────────

    def get_aggregated_sentiment(self) -> Dict[str, Any]:
        """
        Trả về tổng hợp sentiment hiện tại với Exponential Decay.
        Gọi hàm này trong vòng lặp predict() — KHÔNG CÓ NETWORK I/O.

        Returns:
            {
                'composite_score': float (-1.0 → +1.0),
                'num_active_news': int,
                'is_burst': bool,
                'is_news_blocked': bool,
                'news_block_reason': str,
                'dominant_label': str,
                'latest_headlines': List[dict],
                'polling_interval_ms': float,
            }
        """
        with self._lock:
            if not self._cache:
                return {
                    'composite_score': 0.0,
                    'num_active_news': 0,
                    'is_burst': False,
                    'is_news_blocked': self._news_block_active,
                    'news_block_reason': self._news_block_reason,
                    'dominant_label': 'neutral',
                    'latest_headlines': [],
                    'polling_interval_ms': self._current_interval * 1000,
                }

            now = time.time()
            active_entries = []
            weighted_sum = 0.0
            weight_total = 0.0

            for entry in self._cache:
                age = now - entry.timestamp
                if age > 1800:  # Bỏ qua tin > 30 phút
                    continue

                decayed = entry.decayed_sentiment()
                # Trọng số theo impact level
                impact_weight = {'High': 3.0, 'Medium': 1.5, 'Low': 0.5}.get(entry.impact, 1.0)

                weighted_sum += decayed * impact_weight
                weight_total += impact_weight
                active_entries.append(entry)

            if weight_total > 0:
                composite = max(-1.0, min(1.0, weighted_sum / weight_total))
            else:
                composite = 0.0

            # Dominant label
            if composite >= 0.15:
                dominant = 'positive'
            elif composite <= -0.15:
                dominant = 'negative'
            else:
                dominant = 'neutral'

            # Latest headlines (top 5)
            latest = sorted(active_entries, key=lambda e: e.timestamp, reverse=True)[:5]

            return {
                'composite_score': round(composite, 4),
                'num_active_news': len(active_entries),
                'is_burst': self._is_burst_mode,
                'is_news_blocked': self._news_block_active,
                'news_block_reason': self._news_block_reason,
                'dominant_label': dominant,
                'latest_headlines': [e.to_dict() for e in latest],
                'polling_interval_ms': self._current_interval * 1000,
            }

    def get_live_sentiment_value(self) -> float:
        """
        Shortcut: Trả về chỉ số composite_score duy nhất.
        Dùng để inject trực tiếp vào feature vector của AI.
        """
        return self.get_aggregated_sentiment()['composite_score']

    def is_news_blocked(self) -> Tuple[bool, str]:
        """Kiểm tra nhanh xem có đang trong vùng bão tin tức không."""
        with self._lock:
            return self._news_block_active, self._news_block_reason

    def get_active_events(self) -> List[Dict[str, Any]]:
        """Lay danh sach cac su kien kinh te tu cache ForexFactory."""
        with self._lock:
            if self._ff_cache:
                return list(self._ff_cache)
        return []

    def get_stats(self) -> Dict[str, Any]:
        """Thong ke hoat dong cua Streamer."""
        with self._lock:
            return dict(self._stats)

    # ─────────────────────────────────────────────────────
    # THREAD LIFECYCLE
    # ─────────────────────────────────────────────────────

    def start(self) -> None:
        """Khởi động daemon thread cho HFT News Streaming."""
        if self._is_running:
            print("[HFT-News] Streamer dang chay roi!")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._polling_loop,
            name="HFT-NewsStreamer",
            daemon=True
        )
        self._thread.start()
        self._is_running = True
        print("[HFT-News] ✓ Da khoi dong HFT News Streamer (daemon thread).")
        print(f"[HFT-News]   Polling interval: {self._current_interval}s | "
              f"Cache size: {CACHE_MAX_SIZE} | Decay half-life: {SENTIMENT_HALF_LIFE_SECONDS}s")

    def stop(self) -> None:
        """Dừng daemon thread."""
        if not self._is_running:
            return
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._is_running = False
        print("[HFT-News] Da dung HFT News Streamer.")

    @property
    def running(self) -> bool:
        return self._is_running

    # ─────────────────────────────────────────────────────
    # CORE POLLING LOOP (runs in background thread)
    # ─────────────────────────────────────────────────────

    def _polling_loop(self) -> None:
        """
        Vòng lặp chính chạy trong background thread.
        Liên tục poll tin tức → NLP score → cập nhật cache.
        """
        print("[HFT-News] Background thread started. Polling news sources...")

        while not self._stop_event.is_set():
            cycle_start = time.time()

            try:
                new_headlines = []

                # Source 1: ForexFactory Economic Calendar (luôn hoạt động, free)
                ff_headlines = self._fetch_forexfactory()
                new_headlines.extend(ff_headlines)

                # Source 2: FinnHub News API (nếu có key)
                if FINNHUB_API_KEY:
                    fh_headlines = self._fetch_finnhub()
                    new_headlines.extend(fh_headlines)

                # Source 3: NewsAPI Headlines (nếu có key)
                if NEWSAPI_API_KEY:
                    na_headlines = self._fetch_newsapi()
                    new_headlines.extend(na_headlines)

                # NLP Score & Cache Update
                added_count = 0
                for item in new_headlines:
                    h_hash = hashlib.md5(
                        item['headline'].encode('utf-8', errors='replace')
                    ).hexdigest()[:12]

                    if h_hash in self._seen_hashes:
                        continue  # Skip duplicates

                    # Score via NLP
                    if self.nlp_analyzer:
                        nlp_result = self.nlp_analyzer.analyze_headline(item['headline'])
                        sentiment_val = nlp_result['sentiment_value']
                        label = nlp_result['label']
                        confidence = nlp_result['confidence']
                    else:
                        sentiment_val = 0.0
                        label = 'neutral'
                        confidence = 0.0

                    entry = SentimentEntry(
                        headline=item['headline'],
                        source=item.get('source', 'unknown'),
                        sentiment_value=sentiment_val,
                        label=label,
                        confidence=confidence,
                        timestamp=item.get('timestamp', time.time()),
                        impact=item.get('impact', 'Medium'),
                        currency=item.get('currency', self.currency),
                    )

                    with self._lock:
                        self._cache.append(entry)
                        self._seen_hashes.add(h_hash)
                        # Giới hạn seen_hashes để không bị memory leak
                        if len(self._seen_hashes) > CACHE_MAX_SIZE * 2:
                            self._seen_hashes = set(
                                e.hash_id for e in self._cache
                            )
                    added_count += 1

                # Update adaptive polling interval
                self._update_polling_interval()

                # Update stats
                cycle_dur = (time.time() - cycle_start) * 1000.0
                with self._lock:
                    self._stats['total_headlines_processed'] += added_count
                    self._stats['total_poll_cycles'] += 1
                    self._stats['last_poll_time'] = time.time()
                    self._stats['last_poll_duration_ms'] = round(cycle_dur, 2)
                    active_sources = ['ForexFactory']
                    if FINNHUB_API_KEY:
                        active_sources.append('FinnHub')
                    if NEWSAPI_API_KEY:
                        active_sources.append('NewsAPI')
                    self._stats['sources_active'] = active_sources

                if added_count > 0:
                    agg = self.get_aggregated_sentiment()
                    print(f"[HFT-News] +{added_count} tin moi | "
                          f"Composite: {agg['composite_score']:+.4f} ({agg['dominant_label']}) | "
                          f"Active: {agg['num_active_news']} | "
                          f"Cycle: {cycle_dur:.1f}ms")

            except Exception as e:
                logging.warning(f"[HFT-News] Polling error: {e}")

            # Adaptive sleep
            self._stop_event.wait(timeout=self._current_interval)

    # ─────────────────────────────────────────────────────
    # SOURCE FETCHERS
    # ─────────────────────────────────────────────────────

    def _fetch_forexfactory(self) -> List[Dict[str, Any]]:
        """
        Nguồn 1: ForexFactory Economic Calendar.
        Lấy các sự kiện kinh tế USD impact High/Medium trong tuần.
        Cache kết quả 5 phút để tránh spam API.
        """
        results = []
        now = time.time()

        # Check cache TTL
        if (now - self._ff_last_fetch) < self._FF_CACHE_TTL and self._ff_cache:
            raw_events = self._ff_cache
        else:
            try:
                if requests is None:
                    return results
                resp = requests.get(FOREXFACTORY_URL, timeout=8)
                if resp.status_code == 200:
                    raw_events = resp.json()
                    self._ff_cache = raw_events
                    self._ff_last_fetch = now
                else:
                    raw_events = self._ff_cache or []
            except Exception as e:
                logging.debug(f"[HFT-News/FF] Fetch error: {e}")
                raw_events = self._ff_cache or []

        now_dt = datetime.now().astimezone()

        for item in raw_events:
            country = item.get("country", "")
            impact = item.get("impact", "")
            title = item.get("title", "")

            if country != self.currency:
                continue
            if impact not in ["High", "Medium"]:
                continue
            if not title:
                continue

            # Parse event time
            date_str = item.get("date", "")
            event_ts = now
            is_near = False
            try:
                if date_str:
                    event_dt = datetime.fromisoformat(date_str).astimezone()
                    event_ts = event_dt.timestamp()
                    time_diff_min = (event_dt - now_dt).total_seconds() / 60.0

                    # Phát hiện tin sắp ra / đang ra
                    if -30 <= time_diff_min <= 30:
                        is_near = True
                        with self._lock:
                            self._news_block_active = True
                            self._news_block_reason = (
                                f"[NEWS STORM] {title} "
                                f"({'+' if time_diff_min > 0 else ''}{int(time_diff_min)}min)"
                            )
                    elif -60 <= time_diff_min <= 60:
                        is_near = True
            except Exception:
                pass

            # Tạo headline dạng chuẩn NLP
            actual = item.get("actual", "")
            forecast = item.get("forecast", "")
            previous = item.get("previous", "")

            if actual and forecast:
                try:
                    a_val = float(str(actual).replace('%', '').replace('K', ''))
                    f_val = float(str(forecast).replace('%', '').replace('K', ''))
                    if a_val > f_val:
                        headline = f"{title}: Actual {actual} beats forecast {forecast} (prev: {previous})"
                    elif a_val < f_val:
                        headline = f"{title}: Actual {actual} misses forecast {forecast} (prev: {previous})"
                    else:
                        headline = f"{title}: Actual {actual} meets forecast {forecast} (prev: {previous})"
                except (ValueError, TypeError):
                    headline = f"{title}: {actual} vs forecast {forecast}"
            else:
                headline = f"Upcoming: {title} ({impact} impact USD event)"

            results.append({
                'headline': headline,
                'source': 'ForexFactory',
                'timestamp': event_ts if is_near else now,
                'impact': impact,
                'currency': self.currency,
            })

        # Reset news block if no near events found
        if not any(r.get('_is_near') for r in results):
            near_found = False
            for item in raw_events:
                if item.get("country") == self.currency and item.get("impact") in ["High"]:
                    try:
                        ds = item.get("date", "")
                        if ds:
                            edt = datetime.fromisoformat(ds).astimezone()
                            diff = abs((edt - now_dt).total_seconds() / 60.0)
                            if diff <= 30:
                                near_found = True
                                break
                    except Exception:
                        pass
            if not near_found:
                with self._lock:
                    self._news_block_active = False
                    self._news_block_reason = ""

        return results

    def _fetch_finnhub(self) -> List[Dict[str, Any]]:
        """
        Nguồn 2: FinnHub Real-time Market News.
        Lấy tin tức thị trường forex/commodities real-time.
        """
        results = []
        if not FINNHUB_API_KEY or requests is None:
            return results

        try:
            url = f"{FINNHUB_BASE_URL}/news"
            params = {
                'category': 'forex',
                'token': FINNHUB_API_KEY
            }
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                articles = resp.json()
                # Lọc chỉ tin liên quan đến Gold/XAUUSD/USD
                gold_keywords = [
                    'gold', 'xauusd', 'xau', 'precious metal',
                    'federal reserve', 'fed ', 'interest rate',
                    'inflation', 'cpi', 'nonfarm', 'non-farm',
                    'treasury', 'dollar', 'usd', 'fomc',
                    'geopolitical', 'safe haven', 'war', 'conflict'
                ]
                for article in articles[:50]:  # Top 50 latest
                    title = article.get('headline', '') or article.get('title', '')
                    if not title:
                        continue
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in gold_keywords):
                        ts = article.get('datetime', time.time())
                        results.append({
                            'headline': title,
                            'source': 'FinnHub',
                            'timestamp': float(ts),
                            'impact': 'Medium',
                            'currency': self.currency,
                        })
        except Exception as e:
            logging.debug(f"[HFT-News/FinnHub] Fetch error: {e}")

        return results

    def _fetch_newsapi(self) -> List[Dict[str, Any]]:
        """
        Nguồn 3: NewsAPI.org — Global Financial Headlines.
        Lấy tin tức tổng hợp từ hàng trăm tờ báo tài chính.
        """
        results = []
        if not NEWSAPI_API_KEY or requests is None:
            return results

        try:
            url = f"{NEWSAPI_BASE_URL}/everything"
            params = {
                'q': '(gold OR XAUUSD OR "federal reserve" OR "interest rate" OR inflation) AND (USD OR dollar)',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'apiKey': NEWSAPI_API_KEY,
            }
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for article in data.get('articles', []):
                    title = article.get('title', '')
                    if not title or title == '[Removed]':
                        continue
                    # Parse published time
                    pub_str = article.get('publishedAt', '')
                    try:
                        pub_dt = datetime.fromisoformat(pub_str.replace('Z', '+00:00'))
                        ts = pub_dt.timestamp()
                    except Exception:
                        ts = time.time()

                    results.append({
                        'headline': title,
                        'source': 'NewsAPI',
                        'timestamp': ts,
                        'impact': 'Medium',
                        'currency': self.currency,
                    })
        except Exception as e:
            logging.debug(f"[HFT-News/NewsAPI] Fetch error: {e}")

        return results

    # ─────────────────────────────────────────────────────
    # ADAPTIVE POLLING ENGINE
    # ─────────────────────────────────────────────────────

    def _update_polling_interval(self) -> None:
        """
        Tự động điều chỉnh tần suất poll dựa trên trạng thái thị trường:
        - Bình thường: 15s
        - Gần tin quan trọng: 5s
        - Đang trong bão tin: 2s
        - Burst detected: 1s
        """
        with self._lock:
            # Burst detection: >= 3 tin mới trong 60s gần nhất
            now = time.time()
            recent_count = sum(
                1 for e in self._cache
                if (now - e.timestamp) < BURST_WINDOW_SECONDS
            )

            if recent_count >= BURST_THRESHOLD:
                self._is_burst_mode = True
                self._current_interval = POLL_INTERVAL_BURST
                self._stats['burst_events'] += 1
            elif self._news_block_active:
                self._is_burst_mode = False
                self._current_interval = POLL_INTERVAL_DURING_NEWS
            elif self._is_pre_news:
                self._is_burst_mode = False
                self._current_interval = POLL_INTERVAL_PRE_NEWS
            else:
                self._is_burst_mode = False
                self._current_interval = POLL_INTERVAL_NORMAL

    # ─────────────────────────────────────────────────────
    # MANUAL INJECTION (for testing / telegram commands)
    # ─────────────────────────────────────────────────────

    def inject_headline(self, headline: str, impact: str = "High",
                        source: str = "Manual") -> Dict[str, Any]:
        """
        Inject thủ công một tin tức vào cache (dùng để test hoặc từ Telegram).
        Tin sẽ được NLP score ngay lập tức.
        """
        if self.nlp_analyzer:
            result = self.nlp_analyzer.analyze_headline(headline)
            sentiment_val = result['sentiment_value']
            label = result['label']
            confidence = result['confidence']
        else:
            sentiment_val = 0.0
            label = 'neutral'
            confidence = 0.0

        entry = SentimentEntry(
            headline=headline,
            source=source,
            sentiment_value=sentiment_val,
            label=label,
            confidence=confidence,
            timestamp=time.time(),
            impact=impact,
            currency=self.currency,
        )

        with self._lock:
            self._cache.append(entry)
            self._seen_hashes.add(entry.hash_id)
            self._stats['total_headlines_processed'] += 1

        print(f"[HFT-News] Injected: '{headline}' → {label} ({sentiment_val:+.3f})")
        return entry.to_dict()


# ─────────────────────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Auto-inject path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from src.data.nlp_finbert import FinBERT_Analyzer

    print("=" * 70)
    print("  HFT NEWS STREAMER — REAL-TIME SENTIMENT ENGINE TEST")
    print("=" * 70)

    # Init NLP
    nlp = FinBERT_Analyzer()

    # Init Streamer
    streamer = HFTNewsStreamer(nlp_analyzer=nlp, currency="USD")
    streamer.start()

    print("\n[Test] Streamer dang chay. Theo doi 30 giay...\n")

    try:
        for i in range(6):
            time.sleep(5)
            agg = streamer.get_aggregated_sentiment()
            print(f"  [{i*5}s] Composite: {agg['composite_score']:+.4f} | "
                  f"Active: {agg['num_active_news']} | "
                  f"Label: {agg['dominant_label']} | "
                  f"Burst: {agg['is_burst']} | "
                  f"Blocked: {agg['is_news_blocked']}")

            if agg['latest_headlines']:
                for h in agg['latest_headlines'][:2]:
                    print(f"    → [{h['source']}] {h['headline'][:80]}...")

        # Test manual injection
        print("\n[Test] Inject tin thu cong:")
        streamer.inject_headline(
            "Fed announces emergency 50bp rate cut amid recession fears",
            impact="High"
        )
        streamer.inject_headline(
            "Gold surges to $3000 all-time high as geopolitical tensions escalate",
            impact="High"
        )

        time.sleep(2)
        final = streamer.get_aggregated_sentiment()
        print(f"\n[Final] Composite: {final['composite_score']:+.4f} | "
              f"Active: {final['num_active_news']} | "
              f"Burst: {final['is_burst']}")

    except KeyboardInterrupt:
        pass
    finally:
        streamer.stop()
        stats = streamer.get_stats()
        print(f"\n[Stats] Cycles: {stats['total_poll_cycles']} | "
              f"Headlines: {stats['total_headlines_processed']} | "
              f"Bursts: {stats['burst_events']}")
    print("\nDone.")
