# -*- coding: utf-8 -*-
"""
VQuant Automated Unit & Integration Test Suite
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.features import FeatureEngine
from src.models.gru_model import TradingGRU
from src.data.nlp_finbert import FinBERT_Analyzer
from src.models.pattern_matcher import PatternMatcher
from src.engine.ipc_bridge import IPCBridge
from src.backtest.metrics import calculate_metrics
from src.config import DATA_DIR


class TestVQuantSuite(unittest.TestCase):
    def setUp(self):
        # Tạo dữ liệu nến OHLCV giả lập để kiểm thử
        np.random.seed(42)
        n = 100
        closes = 2000.0 + np.cumsum(np.random.randn(n) * 2.0)
        highs = closes + np.random.uniform(0.5, 3.0, n)
        lows = closes - np.random.uniform(0.5, 3.0, n)
        opens = (highs + lows) / 2.0
        volumes = np.random.randint(100, 1000, n)

        self.mock_df = pd.DataFrame({
            'time': pd.date_range("2026-01-01", periods=n, freq="4h"),
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'tick_volume': volumes,
            'spread': [15] * n
        })

    def test_01_feature_engine(self):
        """Kiểm tra Feature Engine tính toán đầy đủ các chỉ báo và không chứa NaN."""
        df_feat = FeatureEngine.add_features(self.mock_df)
        self.assertFalse(df_feat.empty)
        self.assertIn('rsi', df_feat.columns)
        self.assertIn('macd', df_feat.columns)
        self.assertIn('stoch_k', df_feat.columns)
        self.assertIn('atr_norm', df_feat.columns)
        self.assertNotIn('news_sentiment', df_feat.columns, "news_sentiment không được rò rỉ vào feature matrix")
        self.assertEqual(df_feat.isna().sum().sum(), 0, "Không được có giá trị NaN trong features")

    def test_02_model_architecture(self):
        """Kiểm tra mô hình CNN-BiGRU-Attention được xây dựng đúng kích thước input/output."""
        input_shape = (50, 16)
        model = TradingGRU.build_model(input_shape)
        self.assertIsNotNone(model)
        # Output shape phải là (None, 3) tương ứng 3 lớp [HOLD, BUY, SELL]
        self.assertEqual(model.output_shape, (None, 3))
        # Dự đoán thử nghiệm một batch ngẫu nhiên
        dummy_input = np.random.rand(2, 50, 16).astype(np.float32)
        preds = model.predict(dummy_input, verbose=0)
        self.assertEqual(preds.shape, (2, 3))
        # Tổng xác suất mỗi sample phải xấp xỉ 1.0 (Softmax)
        np.testing.assert_almost_equal(np.sum(preds, axis=1), [1.0, 1.0], decimal=5)

    def test_03_nlp_financial_sentiment(self):
        """Kiểm tra phân tích cảm xúc tài chính (Lexical/FinBERT)."""
        nlp = FinBERT_Analyzer()
        res_bull = nlp.analyze_headline("Federal Reserve signals aggressive rate cut cycle")
        self.assertGreater(res_bull['sentiment_value'], 0.0, "Rate cut phải có điểm số tích cực cho Vàng")
        self.assertEqual(res_bull['label'], 'positive')

        res_bear = nlp.analyze_headline("US Non-Farm Payrolls surge and Dollar strengthens sharply")
        self.assertLess(res_bear['sentiment_value'], 0.0, "Dollar strengthens phải có điểm số tiêu cực cho Vàng")

    def test_04_pattern_matcher(self):
        """Kiểm tra thuật toán tìm kiếm chuỗi thời gian tương đồng Cosine Similarity."""
        matcher = PatternMatcher(self.mock_df, window_size=20)
        current_window = self.mock_df['close'].values[-20:]
        matches = matcher.find_similar_patterns(current_window, top_k=3)
        self.assertEqual(len(matches), 3)
        self.assertIn('similarity', matches[0])
        self.assertIn('future_change_usd', matches[0])

    def test_05_ipc_bridge(self):
        """Kiểm tra IPC Bridge ghi tín hiệu giao dịch ra file an toàn."""
        IPCBridge.send_signal("LONG_POSITION_ON", 0.88)
        sig_file = os.path.join(DATA_DIR, "signals", "vc_signal_XAUUSD.txt")
        self.assertTrue(os.path.exists(sig_file), "File tín hiệu local phải được tạo thành công")
        with open(sig_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        self.assertTrue(content.startswith("LONG_POSITION_ON,0.8800,"))

    def test_06_quantitative_metrics(self):
        """Kiểm tra tính toán Sharpe, Sortino, Calmar, Drawdown."""
        trades = [
            {'ticket': 1, 'pnl': 150.0},
            {'ticket': 2, 'pnl': -50.0},
            {'ticket': 3, 'pnl': 200.0}
        ]
        equity_hist = [
            {'time': '2026-01-01', 'equity': 10000.0, 'balance': 10000.0},
            {'time': '2026-01-02', 'equity': 10150.0, 'balance': 10150.0},
            {'time': '2026-01-03', 'equity': 10100.0, 'balance': 10100.0},
            {'time': '2026-01-04', 'equity': 10300.0, 'balance': 10300.0}
        ]
        metrics = calculate_metrics(trades, equity_hist, initial_capital=10000.0)
        self.assertGreater(metrics['net_profit'], 0)
        self.assertEqual(metrics['winning_trades'], 2)
        self.assertEqual(metrics['losing_trades'], 1)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('sortino_ratio', metrics)
        self.assertIn('calmar_ratio', metrics)


if __name__ == '__main__':
    unittest.main()

