import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class PatternMatcher:
    def __init__(self, history_df: pd.DataFrame, window_size=20):
        """
        Khởi tạo thuật toán Tìm kiếm Chuỗi Thời gian Tương đồng (Time-Series Similarity).
        Sử dụng Cosine Similarity kết hợp Normalize để rà quét toàn bộ quá khứ.
        """
        self.window_size = window_size
        self.history_df = history_df.copy()
        
        if 'time' in self.history_df.columns:
            self.history_df.set_index('time', inplace=True)
            
        self.patterns, self.outcomes, self.dates = self._build_database()
        
    def _build_database(self):
        print(f"[PatternMatcher] Đang vector hóa toàn bộ dữ liệu lịch sử (Window: {self.window_size} nến)...")
        patterns, outcomes, dates = [], [], []
        
        closes = self.history_df['close'].values
        idx_dates = self.history_df.index.values
        
        for i in range(len(closes) - self.window_size - 1):
            window = closes[i:i+self.window_size]
            # Chuẩn hóa nến (Bắt đầu từ 0) để so sánh hình dáng biểu đồ
            normalized_window = window - window[0] 
            
            # Tính lợi nhuận (PnL) ở nến ngay sau đó để xem thị trường đi hướng nào
            future_change = closes[i+self.window_size] - closes[i+self.window_size-1]
            
            patterns.append(normalized_window)
            outcomes.append(future_change)
            dates.append(idx_dates[i+self.window_size-1])
            
        return np.array(patterns), np.array(outcomes), dates

    def find_similar_patterns(self, current_window, top_k=5):
        """
        Tìm top_k mẫu hình trong quá khứ có đường giá giống hệt hiện tại nhất.
        """
        if len(current_window) != self.window_size:
            return []
            
        # Chuẩn hóa biểu đồ hiện tại
        current_normalized = np.array(current_window) - current_window[0]
        current_normalized = current_normalized.reshape(1, -1)
        
        # So sánh độ tương đồng với HÀNG TRIỆU mẫu hình quá khứ trong vài Mili-giây
        similarities = cosine_similarity(current_normalized, self.patterns)[0]
        
        # Lấy top_k vị trí giống nhất
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'similarity': float(similarities[idx]),
                'future_change_usd': float(self.outcomes[idx]),
                'date': str(self.dates[idx])
            })
            
        return results
