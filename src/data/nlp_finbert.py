# -*- coding: utf-8 -*-
"""
Module: FinBERT & Financial NLP Sentiment Engine
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    Analyzes real-time financial headlines, macroeconomic calendar releases,
    and market news to derive quantitative sentiment polarity (-1.0 to +1.0)
    for XAUUSD / Forex market forecasting.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional

# UTF-8 console output protection for Windows environments
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Optional HuggingFace Transformers pipeline
try:
    from transformers import pipeline  # type: ignore[import-untyped, import-not-found]
    HAS_TRANSFORMERS = True
except (ImportError, Exception):
    HAS_TRANSFORMERS = False

# VADER Sentiment fallback
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore[import-untyped, import-not-found]
    HAS_VADER = True
except (ImportError, Exception):
    HAS_VADER = False


class FinBERT_Analyzer:
    """
    High-performance Financial Sentiment Analyzer.
    Combines Transformer-based FinBERT deep learning with an augmented
    Wall-Street domain lexical dictionary for microsecond latency fallback.
    """

    def __init__(self, force_vader: bool = False):
        self.nlp = None
        self.vader = None
        self.model_name = "None"

        # 1. Attempt loading deep learning FinBERT pipeline if transformers available
        if HAS_TRANSFORMERS and not force_vader:
            try:
                print("[NLP] Dang khoi tao Transformers FinBERT pipeline...")
                self.nlp = pipeline("sentiment-analysis", model="ProsusAI/finbert")
                self.model_name = "ProsusAI/finbert"
                print("[NLP] Khoi tao thanh cong mo hinh FinBERT!")
            except Exception as e:
                print(f"[NLP] Khong the tai FinBERT truc tiep ({e}). Chuyen sang VADER Engine du phong.")
                self.nlp = None

        # 2. High-speed Financial Lexicon & Multi-word Phrase Engine
        if self.nlp is None and HAS_VADER:
            try:
                self.vader = SentimentIntensityAnalyzer()
                self.model_name = "VADER_Financial_Lexicon"
                
                # Single-word financial terms for VADER token matching
                finance_words = {
                    'dovish': 2.2, 'hawkish': -2.2, 'easing': 1.8, 'tightening': -1.8,
                    'inflation': 1.2, 'deflation': -1.2, 'unemployment': -1.5,
                    'bullish': 2.0, 'bearish': -2.0,
                    'surge': 2.0, 'surges': 2.0, 'surging': 2.0,
                    'plunge': -2.0, 'plunges': -2.0, 'plunging': -2.0,
                    'rally': 1.8, 'rallies': 1.8, 'rallying': 1.8,
                    'slump': -1.8, 'slumps': -1.8, 'rebound': 1.5, 'rebounds': 1.5,
                    'escalates': 1.8, 'tension': 1.5, 'tensions': 1.5,
                    'crisis': 2.0, 'war': 2.5, 'conflict': 1.8, 'recession': 2.0,
                    'stimulus': 1.8, 'growth': 1.5, 'slowdown': -1.5,
                    'crash': -2.5, 'collapse': -2.5, 'bailout': 1.8,
                    'boom': 1.5, 'bust': -1.8, 'sanctions': 1.2
                }
                self.vader.lexicon.update(finance_words)
                
                # Multi-word financial key phrases
                self.phrase_weights = {
                    'rate cut': 2.5, 'rate cuts': 2.5,
                    'rate hike': -2.5, 'rate hikes': -2.5,
                    'safe haven': 2.2, 'geopolitical tension': 2.2, 'geopolitical risk': 2.2,
                    'non-farm payrolls': -1.8, 'unemployment drops': -1.8, 'unemployment rises': 1.8,
                    'middle east': 1.2, 'debt ceiling': 1.2,
                    'treasury yields rise': -1.7, 'all-time high': 2.0,
                    'quantitative easing': 2.0, 'quantitative tightening': -2.0
                }
                print("[NLP] Da kich hoat VADER Financial Engine voi tu dien Quants chuyen biet.")
            except Exception as e:
                print(f"[NLP] Loi khoi tao VADER: {e}")
                self.vader = None

    @staticmethod
    def _align_sentiment_to_gold(clean_text: str, raw_score: float) -> tuple:
        """Định hướng sắc thái tin tức theo đặc tính tài sản Vàng (XAUUSD Context)."""
        import re
        text_lower = clean_text.lower()
        
        # 1. Các cụm từ đặc tả chiều hướng rõ ràng cho Vàng (Macro Direct Drivers)
        direct_bullish_phrases = [
            'rate cut', 'rate cuts', 'fed cuts', 'cutting rates', 'monetary easing',
            'dovish', 'safe haven', 'safe-haven', 'gold surges', 'gold rallies',
            'gold gains', 'gold jumps', 'gold climbs', 'gold rises', 'record high',
            'all-time high', 'geopolitical tension', 'war escalates', 'crisis',
            'recession risk', 'recession warning', 'inflation rises', 'dollar plunges',
            'dollar drops', 'dollar weakens', 'dollar slides', 'dollar slumps',
            'usd drops', 'usd plunges', 'usd weakens', 'yields drop', 'yields tumble',
            'rate pause', 'rate cut cycle', 'economic slowdown', 'gold purchases',
            'gold purchase', 'gold buying', 'buy gold', 'buys gold', 'central banks report record',
            'unemployment rate jumps', 'unemployment jumps', 'unemployment rises'
        ]
        
        direct_bearish_phrases = [
            'rate hike', 'rate hikes', 'fed hikes', 'hiking rates', 'monetary tightening',
            'hawkish', 'gold drops', 'gold plunges', 'gold slumps', 'gold tumbles',
            'gold falls', 'gold slides', 'dollar rallies', 'dollar surges',
            'dollar strengthens', 'dollar gains', 'dollar jumps', 'dollar climbs',
            'usd rallies', 'usd surges', 'usd strengthens', 'usd gains',
            'yields rise', 'yields surge', 'treasury yields rise', 'higher yields',
            'strong employment', 'strong jobs', 'payrolls surge', 'payrolls beat',
            'non-farm payrolls surge'
        ]
        
        bull_score = sum(0.5 for p in direct_bullish_phrases if p in text_lower)
        bear_score = sum(0.5 for p in direct_bearish_phrases if p in text_lower)

        # 2. Tương quan nghịch giữa USD / Lãi suất và Vàng (Inverse Correlation)
        usd_subject = bool(re.search(r'\b(usd|dollar|greenback|treasury yields?|yields?|dxy)\b', text_lower))
        gold_subject = bool(re.search(r'\b(gold|xau|xauusd)\b', text_lower))

        score = raw_score

        if bull_score > 0 or bear_score > 0:
            phrase_diff = bull_score - bear_score
            score = max(-1.0, min(1.0, phrase_diff * 0.75 + raw_score * 0.25))
        elif usd_subject and not gold_subject:
            # Nếu chủ ngữ là Dollar/Lợi suất mà không nói về Vàng -> Đảo chiều tương quan!
            # Dollar tăng (raw > 0) => Vàng giảm (score < 0)
            score = -raw_score

        score = round(max(-1.0, min(1.0, score)), 3)
        if score >= 0.15:
            label = 'positive'
        elif score <= -0.15:
            label = 'negative'
        else:
            label = 'neutral'
            
        return score, label

    def analyze_headline(self, text: Optional[str]) -> Dict[str, Any]:
        """
        Phân tích sắc thái tài chính của tiêu đề tin tức.
        
        Args:
            text (str): Tiêu đề hoặc nội dung tin tức (ví dụ: 'Fed signals rate pause as CPI cools')
            
        Returns:
            dict: {
                'text': str,
                'label': 'positive' | 'negative' | 'neutral',
                'confidence': float (0.0 -> 1.0),
                'sentiment_value': float (-1.0 -> 1.0),
                'engine': str
            }
        """
        # Guard clause for empty or invalid input
        if not text or not isinstance(text, str) or not text.strip():
            return {
                'text': '',
                'label': 'neutral',
                'confidence': 0.0,
                'sentiment_value': 0.0,
                'engine': self.model_name
            }

        clean_text = text.strip()

        # Path A: Transformer FinBERT Pipeline
        if self.nlp:
            try:
                result = self.nlp(clean_text)[0]
                raw_label = str(result.get('label', 'neutral')).lower()
                confidence = float(result.get('score', 0.0))
                
                raw_val = confidence if raw_label == 'positive' else (-confidence if raw_label == 'negative' else 0.0)
                gold_val, gold_label = self._align_sentiment_to_gold(clean_text, raw_val)

                return {
                    'text': clean_text,
                    'label': gold_label,
                    'confidence': confidence,
                    'sentiment_value': float(gold_val),
                    'engine': 'FinBERT'
                }
            except Exception as e:
                logging.warning(f"[NLP] FinBERT evaluation error: {e}. Fallback to lexical analyzer.")

        # Path B: VADER Financial Lexicon Pipeline
        if self.vader:
            try:
                scores = self.vader.polarity_scores(clean_text)
                compound = float(scores.get('compound', 0.0))
                
                # Check multi-word phrase bonuses
                phrase_bonus = 0.0
                text_lower = clean_text.lower()
                if hasattr(self, 'phrase_weights') and self.phrase_weights:
                    for phrase, weight in self.phrase_weights.items():
                        if phrase in text_lower:
                            phrase_bonus += (weight * 0.25)
                
                combined = max(-1.0, min(1.0, compound + phrase_bonus))
                gold_val, gold_label = self._align_sentiment_to_gold(clean_text, combined)

                return {
                    'text': clean_text,
                    'label': gold_label,
                    'confidence': round(abs(gold_val), 3),
                    'sentiment_value': round(gold_val, 3),
                    'engine': 'VADER_Financial'
                }
            except Exception as e:
                logging.error(f"[NLP] Lexical score error: {e}")

        # Path C: Ultimate Failsafe
        return {
            'text': clean_text,
            'label': 'neutral',
            'confidence': 0.0,
            'sentiment_value': 0.0,
            'engine': 'Failsafe'
        }

    def analyze_batch(self, headlines: List[str]) -> List[Dict[str, Any]]:
        """Phân tích hàng loạt tin tức trong danh sách"""
        if not headlines:
            return []
        return [self.analyze_headline(h) for h in headlines if h]


if __name__ == "__main__":
    analyzer = FinBERT_Analyzer()
    samples = [
        "US Non-Farm Payrolls significantly exceed expectations, unemployment drops to 3.5%",
        "Federal Reserve signals aggressive rate cut cycle amid economic slowdown",
        "Gold surges to fresh all-time high as geopolitical tension escalates in Middle East",
        "US Dollar index rebounds after higher than expected CPI inflation numbers"
    ]

    print("=" * 70)
    print("VQuant Financial NLP - Sentiment Classification Test Suite")
    print("=" * 70)
    for sample in samples:
        res = analyzer.analyze_headline(sample)
        print(f"Tin: {sample}")
        print(f" -> Label: {res['label'].upper()} | Polarity: {res['sentiment_value']:+.2f} | Conf: {res['confidence']:.2f} ({res['engine']})")
        print("-" * 70)
