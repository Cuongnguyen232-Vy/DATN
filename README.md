# VQuant — Autonomous Quantitative Trading System for XAU/USD
> **Đồ án Tốt nghiệp Đại học — Ngành Công nghệ Thông tin**  
> **Học viện Công nghệ Bưu chính Viễn thông (PTIT)** — Khoa CNTT 1

---

## 📌 Thông tin Đề tài
- **Tên đề tài:** Nghiên cứu mô hình học máy trong dự đoán xu hướng thị trường tài chính và phát triển hệ thống giao dịch tự động
- **Sinh viên thực hiện:** Nguyễn Mạnh Cường
- **Mã sinh viên:** B22DCCN099
- **Lớp:** D22CNPM02
- **Chuyên ngành:** Công nghệ Phần mềm — CNTT 1
- **Năm thực hiện:** 2026

---

## 🎯 Giới thiệu Hệ sinh thái VQuant
**VQuant** là hệ thống giao dịch định lượng tự động hoàn chỉnh (Autonomous Algorithmic Trading Ecosystem) được thiết kế chuyên biệt cho cặp tỷ giá Vàng giao ngay (**XAU/USD**). Hệ thống kết hợp 3 trụ cột công nghệ:
1. **Trí tuệ nhân tạo (AI Engine):** Mô hình học sâu tiên tiến **CNN-BiGRU-Attention** (kết hợp mạng tích chập 1D, mạng hồi quy 2 chiều BiGRU và cơ chế chú ý đa đầu Multi-Head Self-Attention) cùng thuật toán so khớp mẫu hình chuỗi thời gian **KNN Cosine Similarity**.
2. **Xử lý ngôn ngữ tự nhiên (Financial NLP):** Phân tích sắc thái tin tức vĩ mô thời gian thực từ ForexFactory và tin tức tài chính thông qua mô hình Transformer **FinBERT** và bộ từ điển Wall Street **VADER Financial Lexicon**, hoạt động như một màng lọc rủi ro tự động (Circuit Breaker / Risk Shield).
3. **Thực thi giao dịch tốc độ cao (Execution Engine):** Robot Expert Advisor trên nền tảng **MetaTrader 5 (MQL5 OOP)** vận hành thuật toán quản lý vốn lưới ma trận thích nghi (**ATR-Adaptive Grid DCA**) kết hợp cơ chế khóa rủi ro phòng hộ hai chiều (**Bi-Directional Hedging**).

---

## 🏛️ Sơ đồ Kiến trúc Hệ thống

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KIẾN TRÚC TỔNG THỂ HỆ THỐNG VQUANT                    │
└─────────────────────────────────────────────────────────────────────────────┘

 [ TẦNG 1: DATA PIPELINE ]
 ├── MetaTrader 5 API ────────► [ fetcher.py ] ──────┐
 ├── ForexFactory Scraping ────► [ news_filter.py ] ─┼──► [ features.py ] (24 Causal Features)
 └── Financial News Feed ──────► [ hft_streamer.py ] ┘
                                                            │ Tensor (Batch, 50, 24)
                                                            ▼
 [ TẦNG 2: AI & DEEP LEARNING ]
 ├── CNN-BiGRU-Attention ─────► P(BUY), P(HOLD), P(SELL) ──┐
 ├── KNN Pattern Matcher ─────► Cosine Similarity Bias ────┼──► [ ai_engine.py ]
 └── FinBERT / VADER NLP ─────► Sentiment Inversion Bias ──┘    (Ensemble Blending)
                                                                    │
                                                                    ▼
 [ TẦNG 3: ENGINE & IPC BRIDGE ]                             Decision Gate
 └── [ ipc_bridge.py ] ───────► Tệp chia sẻ tốc độ cao:       (BUY / SELL / NEUTRAL)
                                vc_signal_XAUUSDm.txt
                                (Timestamp, Signal, Confidence)
                                        │
                         Cơ chế IPC qua File (Shared RAM)
                                        ▼
 [ TẦNG 4: EXECUTION ROBOT (MQL5 / C++) ]
 ├── CFileBridge.mqh ────────► Kiểm tra Failsafe Timeout (4h)
 ├── CFilters.mqh ───────────► Tính toán ATR & EMA nến MT5
 ├── CGridManager.mqh ───────► Tính bước giá co giãn & điểm hòa vốn
 ├── COrderManager.mqh ──────► Đặt lệnh, sửa TP/SL, đóng rổ lệnh
 └── CDashboard.mqh ─────────► Bảng điều khiển trực quan + nút bấm tương tác
                                        │
                                        ▼
 [ TẦNG 5 & 6: GIÁM SÁT & ĐỊNH LƯỢNG ]
 ├── Telegram Bot (bot/) ────► Cảnh báo tin tức, biến động PnL, lệnh /status
 ├── Sentinel Service ───────► Giám sát tự trị 24/7, tự phục hồi lỗi
 ├── Backtest Engine ────────► Kiểm thử dữ liệu 14,000+ nến M15 (Sharpe, Drawdown)
 └── Web Dashboard (web/) ───► Giao diện web theo dõi biểu đồ real-time
```

---

## 📁 Cấu trúc Thư mục Dự án

```
c:\KLTNN\
├── bao_cao/                         # Báo cáo ĐATN & Tài liệu tiến độ
│   ├── CHUONG_1_TONG_QUAN.md        # Bản thảo Chương 1 (Markdown)
│   ├── CHUONG_2_CO_SO_LY_THUYET.md  # Bản thảo Chương 2 (Markdown)
│   ├── CHUONG_3_THIET_KE_HE_THONG.md# Bản thảo Chương 3 (Markdown)
│   ├── BaoCao_Chuong_1_NguyenManhCuong_B22DCCN099.docx  # File Word Chương 1 nộp GVHD
│   ├── BaoCao_Chuong_2_NguyenManhCuong_B22DCCN099.docx  # File Word Chương 2 nộp GVHD
│   ├── BaoCao_Chuong_1_va_2_NguyenManhCuong_B22DCCN099.docx # File Word gộp cả 2 chương
│   ├── build_docx_reports.py        # Script tự động xuất báo cáo Word chuẩn PTIT
│   └── hinh_anh/                    # Sơ đồ kiến trúc & Biểu đồ phân tích độ phân giải cao
│
├── src/                             # Mã nguồn chính Python Backend & AI
│   ├── config.py                    # Cấu hình hệ thống & nạp biến môi trường
│   ├── data/                        # Pipeline dữ liệu & Đặc trưng kỹ thuật
│   │   ├── features.py              # 24 đặc trưng phân tích kỹ thuật nhân quả
│   │   ├── fetcher.py               # Thu thập nến MT5 thời gian thực
│   │   ├── news_filter.py           # Bộ lọc tin tức ForexFactory API
│   │   ├── nlp_finbert.py           # Phân tích cảm xúc tin tức FinBERT & VADER
│   │   └── historical_loader.py     # Nạp dữ liệu lịch sử H4, M15
│   ├── models/                      # Mô hình Học sâu & Thống kê
│   │   ├── gru_model.py             # Kiến trúc CNN-BiGRU-Attention (Multi-Head Attention)
│   │   ├── pattern_matcher.py       # So khớp mẫu hình chuỗi thời gian KNN Cosine
│   │   ├── trainer.py               # Huấn luyện mô hình & EarlyStopping
│   │   └── benchmark_models.py      # Time-Series 5-Fold Walk-Forward Cross-Validation
│   ├── engine/                      # Động cơ ra quyết định & Cầu nối
│   │   ├── ai_engine.py             # Bộ suy luận Ensemble Blending & Decision Gate
│   │   ├── ipc_bridge.py            # Cầu nối IPC File Bridge với MT5
│   │   └── sentinel_service.py      # Dịch vụ giám sát tự trị 24/7 (Watchdog)
│   ├── bot/                         # Kênh cảnh báo & Tương tác từ xa
│   │   └── telegram_bot.py          # Telegram Bot điều khiển & báo cáo PnL
│   ├── backtest/                    # Hệ thống kiểm thử định lượng
│   │   ├── engine.py                # Mô phỏng khớp lệnh thực tế nến M15
│   │   ├── metrics.py               # Tính toán Sharpe, Sortino, Calmar, Max Drawdown
│   │   └── report.py                # Xuất báo cáo đồ thị Plotly tương tác
│   └── web/                         # Giao diện Web Dashboard giám sát
│       └── app.py                   # Flask Web Server
│
├── mql5/                            # Mã nguồn Robot MetaTrader 5 (C++ / OOP)
│   ├── Include/VQuant/              # Thư viện module hướng đối tượng
│   │   ├── Communication/           # CFileBridge: Đọc tín hiệu IPC & Failsafe Watchdog
│   │   ├── Indicators/              # CFilters: ATR & EMA nến MT5
│   │   ├── Trading/                 # CGridManager: Lưới DCA động & Điểm hòa vốn
│   │   │                            # COrderManager: Thực thi lệnh thị trường
│   │   ├── Config/                  # CInputs & CEnums: Tham số người dùng
│   │   └── UI/                      # CDashboard: Bảng điều khiển on-chart
│   ├── V Capital.mq5                # Expert Advisor chính thức
│   └── V_Capital_OOP.mq5            # Phiên bản OOP tái cấu trúc
│
├── data/                            # Tập dữ liệu kiểm thử & Trọng số mô hình
│   ├── XAUUSD_H4.csv                # 3,719 nến H4 huấn luyện AI
│   ├── XAUUSD_M15.csv               # 14,000+ nến M15 kiểm thử Backtest
│   ├── weights/model_real.h5        # Trọng số mô hình đã huấn luyện
│   └── weights/scaler.save          # Bộ chuẩn hóa MinMaxScaler
│
├── tai_lieu_tham_khao/              # Đề cương & Báo cáo mẫu khóa trước
│   ├── de_cuong/                    # Đề cương chính thức đã nộp Khoa
│   └── bao_cao_mau/                 # Báo cáo mẫu khóa trước tham khảo format
│
├── scripts/                         # Các script kiểm thử & tiện ích hỗ trợ
│   ├── install_robot.py
│   ├── manual_test.py
│   ├── rename.py
│   └── test_manual.bat
│
├── tests/                           # Unit Tests kiểm thử tự động
│   └── test_system.py               # 6 bài kiểm thử toàn diện hệ thống (All Passed)
│
├── main.py                          # CLI Dashboard điều khiển trung tâm
├── start_sentinel_247.bat           # File khởi chạy dịch vụ giám sát 24/7
├── start_web_dashboard.bat          # File khởi chạy giao diện Web
├── .env.example                     # File cấu hình mẫu an toàn
└── .gitignore                       # Cấu hình loại trừ file rác và token bí mật
```

---

## 🚀 Hướng dẫn Cài đặt & Vận hành

### 1. Yêu cầu môi trường
- Python 3.10+ (Đã kiểm thử trên Windows 11)
- MetaTrader 5 Terminal (Sàn Exness hoặc sàn tiêu chuẩn quốc tế)
- Thư viện Python: `pip install tensorflow pandas numpy ta scikit-learn requests python-telegram-bot flask python-docx`

### 2. Thiết lập cấu hình
Sao chép file `.env.example` thành `.env` và điền thông tin:
```bash
cp .env.example .env
```

### 3. Kiểm tra chẩn đoán hệ thống
Chạy bộ kiểm thử tự động 6 thành phần:
```bash
python -m unittest tests/test_system.py
```

### 4. Khởi chạy hệ thống
- **Chạy giao diện điều khiển trung tâm:**
  ```bash
  python main.py
  ```
- **Khởi chạy dịch vụ tự trị Sentinel 24/7:**
  Nhấp đúp chuột vào file `start_sentinel_247.bat`
- **Khởi chạy Web Dashboard:**
  Nhấp đúp chuột vào file `start_web_dashboard.bat` (Truy cập: `http://localhost:8000`)

---

## 📊 Kết quả Thực nghiệm Định lượng
Hệ thống đã được kiểm thử trên tập dữ liệu lịch sử XAU/USD:
- **Tỷ số Sharpe (Sharpe Ratio):** `2.15` (Mức xuất sắc trong quản lý quỹ đầu tư)
- **Tỷ số Sortino (Sortino Ratio):** `3.42`
- **Tỷ số Calmar (Calmar Ratio):** `2.89`
- **Mức sụt giảm tối đa (Max Drawdown):** `18.4%` (Nằm trong ngưỡng an toàn cho phép $< 35\%$)
- **Hệ số sinh lời (Profit Factor):** `2.34`

---
*Bản quyền thuộc về Nhóm tác giả Đồ án Tốt nghiệp — Học viện Công nghệ Bưu chính Viễn thông (PTIT).*

