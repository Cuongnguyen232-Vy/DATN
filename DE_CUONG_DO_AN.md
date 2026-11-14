# ĐỀ CƯƠNG ĐỒ ÁN TỐT NGHIỆP
# Ngành: Công nghệ Thông tin

---

## 1. THÔNG TIN CHUNG

| | |
|---|---|
| **Tên đề tài** | Xây dựng hệ thống giao dịch tự động XAUUSD ứng dụng mạng nơ-ron hồi quy (LSTM, GRU) và Transformer |
| **Số thành viên** | 2 |
| **Thành viên 1** | _(Điền tên - MSSV)_ |
| **Thành viên 2** | _(Điền tên - MSSV)_ |
| **GVHD** | _(Điền tên cô)_ |
| **Thời gian** | 06/2026 – 11/2026 (~5 tháng) |

---

## 2. LÝ DO CHỌN ĐỀ TÀI

Thị trường vàng (XAUUSD) giao dịch trung bình trên **150 tỷ USD/ngày**, mở cửa 24/5. Việc giao dịch thủ công gặp nhiều hạn chế:

- **Tâm lý**: Sợ hãi, tham lam → quyết định sai
- **Tốc độ**: Thị trường biến động nhanh, con người phản ứng chậm
- **Thời gian**: Không thể giám sát 24/5
- **Dữ liệu**: Quá nhiều chỉ báo kỹ thuật để phân tích đồng thời

Deep Learning (LSTM, GRU, Transformer) đã chứng minh hiệu quả trong nhận diện mẫu hình chuỗi thời gian. Đề tài kết hợp AI dự đoán xu hướng với chiến lược quản lý vốn DCA, xây dựng hệ thống hoàn chỉnh từ **thu thập dữ liệu → huấn luyện AI → giao dịch tự động → giám sát web**.

**Tính ứng dụng CNTT:** Đề tài bao phủ nhiều lĩnh vực kỹ thuật phần mềm: kiến trúc Client-Server, IPC (Inter-Process Communication), REST API, Database, AI/ML pipeline, Web Development, và Deployment.

---

## 3. MỤC TIÊU

### 3.1 Mục tiêu chính
Xây dựng hệ thống giao dịch tự động XAUUSD hoàn chỉnh, tích hợp AI dự đoán xu hướng giá, có giao diện web giám sát.

### 3.2 Mục tiêu cụ thể
1. Xây dựng **Data Pipeline** thu thập và tiền xử lý dữ liệu từ MetaTrader 5
2. Xây dựng và huấn luyện **3 mô hình Deep Learning**: LSTM, GRU, Transformer
3. Tích hợp **News Filter & Sentiment Analysis**: Thu thập lịch kinh tế và tin tức tài chính để cảnh báo "Tin đỏ", bảo vệ an toàn cho tài khoản
4. **So sánh hiệu suất** 3 mô hình trên cùng bộ dữ liệu (Accuracy, F1, Confusion Matrix)
5. Phát triển **Expert Advisor (EA)** trên MetaTrader 5 với chiến lược DCA
6. Tích hợp AI ↔ EA qua cơ chế **IPC file-based**
7. Xây dựng **Web Dashboard** (Flask) giám sát hệ thống
8. Tích hợp **Telegram Bot** thông báo real-time
9. **Backtest** so sánh: DCA thuần vs DCA+AI
10. **Forward Test** trên tài khoản Demo

---

## 4. PHẠM VI

### Trong phạm vi
- Tài sản: XAUUSD (Vàng)
- Khung phân tích: H4 | Khung giao dịch: M15
- Nền tảng: MetaTrader 5
- 3 model AI: LSTM, GRU, Transformer
- Tích hợp Phân tích tin tức (News Filter / Sentiment Analysis)
- Tài khoản: Demo (không dùng tiền thật)

### Ngoài phạm vi
- Các cặp tiền khác | Tài khoản thật
- High-Frequency Trading

---

## 5. CÔNG NGHỆ SỬ DỤNG

| Thành phần | Công nghệ | Nhiệm vụ cụ thể trong dự án |
|------------|-----------|------------------------------|
| **AI/ML** | Python 3.10+, TensorFlow/Keras, Scikit-learn | Xây dựng 3 kiến trúc model (LSTM, GRU, Transformer), huấn luyện trên dữ liệu nến H4, đánh giá bằng Confusion Matrix & F1-Score, xuất model `.h5` |
| **News/NLP** | BeautifulSoup, FinBERT, ForexFactory API | Quét lịch kinh tế (ForexFactory) để nhận diện "Tin Đỏ" (tin quan trọng). Phân tích cảm xúc (Sentiment) của bản tin để dừng bot hoặc cảnh báo người dùng |
| **Data Processing** | Pandas, NumPy, TA-Lib | Tải 3,000+ nến lịch sử từ MT5 API, tính 15 Technical Indicators (RSI, MACD, EMA, Bollinger Bands, ATR...), chuẩn hóa MinMaxScaler, tạo sequences [50×15] cho LSTM |
| **Trading Bot** | MQL5 (MetaQuotes Language 5) | Lập trình Expert Advisor: thực thi lệnh BUY/SELL trên sàn, quản lý giỏ DCA (lot multiplier, grid distance), chốt lời basket TP, cắt lỗ DD cutoff, bộ lọc EMA trend, dashboard on-chart |
| **Web Backend** | Flask, SQLAlchemy | Xây dựng 8+ REST API endpoints (xem trạng thái bot, lịch sử GD, PnL, bật/tắt bot), render trang HTML, kết nối database, xử lý authentication |
| **Web Frontend** | HTML5, CSS3, JavaScript, Chart.js | Xây dựng 5 trang web: Dashboard chính (biểu đồ PnL real-time, bảng lệnh), trang Backtest (equity curve, so sánh chiến lược), trang cấu hình bot, responsive design |
| **Database** | SQLite | Thiết kế 4 bảng (predictions, trades, daily_pnl, bot_config), lưu trữ lịch sử dự đoán AI, log giao dịch, PnL hàng ngày, phục vụ web dashboard query |
| **Notification** | Telegram Bot API (python-telegram-bot) | Gửi thông báo khi: mở lệnh mới, chốt lời, cắt lỗ, DD cảnh báo; Báo cáo PnL cuối ngày; Nhận lệnh từ user (/status, /pause, /resume) |
| **Visualization** | Matplotlib, Seaborn, Plotly | Vẽ Confusion Matrix 3 model, Training Loss/Accuracy curves, Equity Curve backtest, Drawdown chart, bảng so sánh DCA vs DCA+AI |
| **Testing** | pytest | Unit test data pipeline (kiểm tra shape, null values), test model (build → predict shape đúng), test backtest logic (PnL calculation) |
| **Deployment** | Docker, docker-compose, VPS Linux | Container hóa Python AI + Flask Web, triển khai trên VPS, chạy 24/5 liên tục |
| **IPC** | File-based CSV/TXT | Cầu nối Python ↔ MQL5: Python ghi tín hiệu AI (signal, confidence, timestamp) vào file TXT, MQL5 đọc file mỗi 15 phút để ra quyết định giao dịch |

---

## 6. KIẾN TRÚC HỆ THỐNG

### 6.1 Sơ đồ tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                    HỆ THỐNG V CAPITAL                           │
│                                                                 │
│  ┌──────────────────┐   File IPC   ┌──────────────────┐        │
│  │  MODULE AI        │────────────→│  MODULE TRADING   │        │
│  │  (Python Server)  │             │  (MQL5 Expert     │        │
│  │                   │             │   Advisor - MT5)  │        │
│  │  • DataPipeline   │             │  • DCA Strategy   │        │
│  │  • FeatureEngine  │             │  • Hedge Mode     │        │
│  │  • News Filter    │             │  • Risk Manager   │        │
│  │  • ModelTrainer   │             │  • Dashboard MT5  │        │
│  │  • AIEngine       │             │                   │        │
│  └────────┬──────────┘             └────────┬──────────┘        │
│           │                                  │                   │
│           ▼                                  ▼                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  MODULE WEB (Flask + SQLite + Telegram)               │       │
│  │  • REST API endpoints    • Biểu đồ real-time         │       │
│  │  • Quản lý bot           • Lịch sử giao dịch         │       │
│  │  • Backtest viewer       • Telegram notifications     │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Deployment Diagram

```
┌─────────────┐     HTTPS      ┌──────────────────────────┐
│  Trình duyệt │◄─────────────►│  VPS Linux               │
│  (User)       │               │  ┌────────────────────┐  │
└─────────────┘               │  │ Flask Web Server   │  │
                                │  │ (port 8000)        │  │
┌─────────────┐               │  └─────────┬──────────┘  │
│  Telegram    │◄──Bot API────►│            │              │
│  App (User)  │               │  ┌─────────▼──────────┐  │
└─────────────┘               │  │ SQLite Database     │  │
                                │  └────────────────────┘  │
                                │  ┌────────────────────┐  │
                                │  │ Python AI Engine   │  │
                                │  │ (Inference Loop)   │──┼──► IPC File
                                │  └────────────────────┘  │
                                └──────────────────────────┘
                                              │
                                         IPC File
                                              │
                                ┌──────────────▼───────────┐
                                │  Windows PC / VPS        │
                                │  ┌────────────────────┐  │
                                │  │ MetaTrader 5       │  │
                                │  │ + V Capital EA     │──┼──► Broker Server
                                │  └────────────────────┘  │    (Exness, etc.)
                                └──────────────────────────┘
```

---

## 7. SƠ ĐỒ UML

### 7.1 Use Case Diagram

```
                        ┌─────────────────────────┐
                        │   HỆ THỐNG V CAPITAL     │
          ┌─────────────┤                          ├─────────────┐
          │             │                          │             │
          │     ┌───────┤  UC1: Huấn luyện model   │             │
          │     │       │  UC2: Xem AI prediction   │             │
  ┌───┐   │     │       │  UC3: Cấu hình bot       │       ┌───┐
  │   │───┼─────┤       │  UC4: Bật/Tạm dừng bot   │       │   │
  │ T │   │     │       │  UC5: Xem lịch sử GD     ├───────│ A │
  │ r │   │     │       │  UC6: Xem backtest        │       │ I │
  │ a │───┼─────┤       │  UC7: Nhận thông báo TG   │       │   │
  │ d │   │     │       │  UC8: Dự đoán xu hướng    ├───────│ S │
  │ e │   │     │       │  UC9: Tự động mở/đóng     │       │ y │
  │ r │   │     └───────┤  UC10: Quản lý rủi ro     │       │ s │
  │   │───┼─────────────┤  UC11: Ghi log giao dịch  ├───────│ t │
  └───┘   │             │                          │       │ e │
          │             └─────────────────────────┘       │ m │
          │                                                └───┘
          │  Trader: UC1-UC7
          │  AI System: UC8-UC11
```

**Chi tiết Use Case chính:**

| UC | Tên | Actor | Mô tả |
|----|------|-------|-------|
| UC1 | Huấn luyện model | Trader | Chạy train.py để huấn luyện 3 model trên data lịch sử |
| UC2 | Xem AI prediction | Trader | Xem tín hiệu BUY/SELL/HOLD + confidence qua web |
| UC3 | Cấu hình bot | Trader | Thay đổi lot, TP, grid distance, max orders qua web/MT5 |
| UC4 | Bật/Tạm dừng bot | Trader | Bật/tắt giao dịch tự động |
| UC5 | Xem lịch sử GD | Trader | Xem bảng lệnh đã đóng, PnL, filter theo ngày |
| UC6 | Xem backtest | Trader | Chạy backtest, xem equity curve, so sánh chiến lược |
| UC7 | Nhận thông báo | Trader | Nhận alert qua Telegram khi mở/đóng lệnh |
| UC8 | Dự đoán xu hướng | AI System | Tự động predict mỗi 4h |
| UC9 | Mở/đóng lệnh | AI System | Tự động thực thi lệnh trên MT5 |
| UC10 | Quản lý rủi ro | AI System | DD cutoff, auto-OFF |
| UC11 | Ghi log | AI System | CSV logging mỗi event |

### 7.2 Class Diagram (Module AI — Python)

```
┌──────────────────────┐     ┌──────────────────────┐
│    DataPipeline       │     │    FeatureEngine      │
├──────────────────────┤     ├──────────────────────┤
│ - symbol: str         │     │ - indicators: list    │
│ - timeframe: int      │     ├──────────────────────┤
│ - n_candles: int      │     │ + calc_ema()          │
├──────────────────────┤     │ + calc_rsi()          │
│ + connect_mt5()       │────►│ + calc_macd()         │
│ + fetch_data(): DataFrame   │ + calc_bollinger()    │
│ + create_labels()     │     │ + calc_atr()          │
│ + create_sequences()  │     │ + add_all(): DataFrame│
│ + split_data()        │     └──────────────────────┘
└──────────┬───────────┘
           │ uses
           ▼
┌──────────────────────┐     ┌──────────────────────┐
│  «abstract»           │     │    ModelTrainer       │
│    BaseModel          │     ├──────────────────────┤
├──────────────────────┤     │ - models: list        │
│ + build(): Model      │     │ - scaler: MinMaxScaler│
│ + get_name(): str     │     ├──────────────────────┤
├──────────────────────┤     │ + train_all()         │
         ▲                    │ + evaluate_all()      │
    ┌────┼────┐               │ + compare(): DataFrame│
    │    │    │               │ + save_best()         │
┌───┴──┐│┌───┴────────┐     │ + plot_results()      │
│ LSTM ││ │ Transformer│     └──────────────────────┘
│Model │││ Model      │              ▲ uses
└──────┘│└────────────┘              │
   ┌────┴──┐               ┌────────┴─────────────┐
   │ GRU   │               │    AIEngine           │
   │ Model │               ├──────────────────────┤
   └───────┘               │ - model: keras.Model  │
                            │ - scaler: Scaler      │
                            ├──────────────────────┤
                            │ + load_model()        │
                            │ + predict(): dict     │
                            │ + send_ipc_signal()   │
                            │ + run_loop()          │
                            └──────────────────────┘
```

### 7.3 Sequence Diagram — Luồng Giao Dịch Chính

```
  Trader      WebApp       AIEngine      IPC File     MT5 EA       Broker
    │            │            │             │           │            │
    │            │     ┌──────┴──────┐      │           │            │
    │            │     │ Mỗi 4h:     │      │           │            │
    │            │     │ fetch 50    │      │           │            │
    │            │     │ nến H4      │      │           │            │
    │            │     │ + predict() │      │           │            │
    │            │     └──────┬──────┘      │           │            │
    │            │            │             │           │            │
    │            │            │──write───►  │           │            │
    │            │            │ "BUY,0.87"  │           │            │
    │            │            │             │           │            │
    │            │            │             │  ┌────────┴────────┐   │
    │            │            │             │  │ Mỗi 15p:       │   │
    │            │            │             │◄─│ đọc file IPC   │   │
    │            │            │             │  │ check BUY>80%  │   │
    │            │            │             │  │ check EMA OK   │   │
    │            │            │             │  │ check session  │   │
    │            │            │             │  └────────┬────────┘   │
    │            │            │             │           │            │
    │            │            │             │           │──Buy 0.15─►│
    │            │            │             │           │◄──OK───────│
    │            │            │             │           │            │
    │            │            │             │     (giá đi ngược)     │
    │            │            │             │           │            │
    │            │            │             │           │──Buy 0.19─►│
    │            │            │             │           │◄──OK───────│
    │            │            │             │           │            │
    │            │            │             │     (giá hồi phục)     │
    │            │            │             │           │            │
    │            │            │             │           │──Close All─►│
    │            │            │             │           │◄──+$1,759──│
    │            │            │             │           │            │
    │◄───Telegram notify──────────────────────────────│            │
    │            │            │             │           │            │
    │──Xem web──►│            │             │           │            │
    │◄──PnL chart│            │             │           │            │
```

### 7.4 Activity Diagram — Quy trình DCA

```
                    ┌─────────┐
                    │  START   │
                    └────┬────┘
                         ▼
                ┌────────────────┐
                │ Đọc tín hiệu   │
                │ AI từ file IPC  │
                └───────┬────────┘
                        ▼
               ┌────────────────┐    KHÔNG
               │ Signal = BUY    ├──────────┐
               │ & Conf > 80%?   │           │
               └───────┬────────┘           │
                   CÓ  │                     │
                       ▼                     │
               ┌────────────────┐           │
               │ EMA trend OK?  ├──KHÔNG───►│
               └───────┬────────┘           │
                   CÓ  │                     │
                       ▼                     │
               ┌────────────────┐           │
               │ Trong session?  ├──KHÔNG───►│
               └───────┬────────┘           │
                   CÓ  │                     │
                       ▼                     │
               ┌────────────────┐           │
               │ Mở lệnh SEED   │           │
               │ BUY 0.15 lot   │           │
               └───────┬────────┘           │
                       ▼                     │
        ┌──────────────────────────┐        │
        │ Giám sát giá liên tục    │◄───────┘
        └──────────┬───────────────┘
                   ▼
          ┌────────────────┐
     ┌────┤ Giá hiện tại?  ├────┐
     │    └────────────────┘    │
     ▼                          ▼
┌─────────┐             ┌────────────┐
│ Giá đi   │             │ Giá hồi    │
│ ngược    │             │ đủ TP?     │
└────┬────┘             └─────┬──────┘
     ▼                        │ CÓ
┌──────────┐                  ▼
│ Grid OK? │          ┌──────────────┐
│ < Max 8? ├──CÓ──►  │ ĐÓNG toàn bộ │
└────┬─────┘          │ giỏ lệnh     │
 KHÔNG│                │ CHỐT LỜI ✅  │
     ▼                └──────┬───────┘
┌──────────┐                 ▼
│ Chờ tiếp │          ┌──────────────┐
└──────────┘          │ Mở seed mới  │
                      │ → Quay lại   │
                      └──────────────┘
```

### 7.5 ERD — Thiết kế Database

```
┌─────────────────────┐    ┌──────────────────────┐
│    predictions       │    │    trades             │
├─────────────────────┤    ├──────────────────────┤
│ PK id: INTEGER       │    │ PK id: INTEGER        │
│    timestamp: DATETIME│    │    ticket: INTEGER     │
│    symbol: TEXT       │    │    symbol: TEXT        │
│    model_name: TEXT   │    │    side: TEXT (BUY/SELL│
│    signal: TEXT       │    │    lot: REAL           │
│    prob_buy: REAL     │    │    open_price: REAL    │
│    prob_sell: REAL    │    │    close_price: REAL   │
│    prob_hold: REAL    │    │    pnl: REAL           │
│    confidence: REAL   │    │    open_time: DATETIME │
│    ipc_sent: BOOLEAN  │    │    close_time: DATETIME│
└─────────────────────┘    │    event: TEXT          │
                            │    note: TEXT           │
┌─────────────────────┐    └──────────────────────┘
│    daily_pnl         │
├─────────────────────┤    ┌──────────────────────┐
│ PK id: INTEGER       │    │    bot_config          │
│    date: DATE         │    ├──────────────────────┤
│    realized_pnl: REAL │    │ PK id: INTEGER        │
│    trades_count: INT  │    │    key: TEXT           │
│    win_count: INT     │    │    value: TEXT         │
│    max_dd: REAL       │    │    updated_at: DATETIME│
└─────────────────────┘    └──────────────────────┘
```

---

## 8. DESIGN PATTERNS SỬ DỤNG

| Pattern | Áp dụng ở đâu | Lý do |
|---------|---------------|-------|
| **Strategy** | 3 model AI (LSTM, GRU, Transformer) kế thừa BaseModel | Dễ thêm model mới, swap model runtime |
| **Observer** | Telegram Bot lắng nghe sự kiện trade | Tách biệt logic giao dịch và thông báo |
| **Factory** | ModelFactory tạo model theo tên | Khởi tạo model linh hoạt từ config |
| **Singleton** | Database connection, MT5 connection | Đảm bảo 1 kết nối duy nhất |
| **Template Method** | BaseModel.build() → LSTM/GRU/Transformer override | Chuẩn hóa pipeline build model |

---

## 9. PHÂN CÔNG

| Thành viên | Module | Nội dung |
|------------|--------|----------|
| **Thành viên A** | AI / Machine Learning (~5,000 dòng) | Data pipeline, Feature engineering, 3 model (LSTM/GRU/Transformer), Training, Evaluation, Inference engine, So sánh model |
| **Thành viên B** | Bot & Hệ thống (~7,000 dòng) | Expert Advisor MQL5, Backtest engine, Web Dashboard (Flask + HTML/CSS/JS), Database, Telegram Bot, Docker deployment |

---

## 10. KẾ HOẠCH THỰC HIỆN

| Giai đoạn | Thời gian | Thành viên A | Thành viên B |
|-----------|-----------|-------------|-------------|
| **1. Nghiên cứu** | T06-T07 | Lý thuyết LSTM, GRU, Transformer | Lý thuyết DCA, MQL5, Flask |
| **2. Data & Model** | T07 | data_pipeline.py, feature_engine.py | Refactor V Capital.mq5 |
| **3. AI Training** | T07-T08 | 3 model + train.py + evaluate.py | database.py + backtest.py |
| **4. Integration** | T08-T09 | ai_engine.py (inference) | web_app.py + templates |
| **5. Web & Bot** | T09-T10 | Tests + tối ưu model | telegram_bot.py + API |
| **6. Testing** | T10 | Forward test AI | Tích hợp toàn bộ + demo |
| **7. Báo cáo** | T10-T11 | Chương 2 + 4 (AI) + 5 (so sánh) | Chương 3 + 4 (Bot/Web) + 5 (backtest) |

---

## 11. CẤU TRÚC BÁO CÁO DỰ KIẾN

| Chương | Nội dung | Người viết |
|--------|----------|------------|
| **1** | Tổng quan: lý do, mục tiêu, phạm vi, phương pháp | Chung |
| **2** | Cơ sở lý thuyết: LSTM, GRU, Transformer, DCA, Indicators | A |
| **3** | Phân tích & Thiết kế: UML, ERD, kiến trúc, wireframe | B |
| **4** | Hiện thực: code AI (A) + code Bot/Web (B) | Chia đôi |
| **5** | Thử nghiệm: so sánh 3 model (A) + backtest/forward test (B) | Chia đôi |
| **6** | Kết luận & Hướng phát triển | Chung |

---

## 12. SẢN PHẨM DỰ KIẾN

| Sản phẩm | Mô tả |
|----------|-------|
| **Source code** | ~12,000 dòng (Python + MQL5 + HTML/CSS/JS) |
| **3 model AI** | LSTM, GRU, Transformer đã huấn luyện (.h5) |
| **Trading Bot** | Expert Advisor chạy trên MetaTrader 5 |
| **Web Dashboard** | Giao diện giám sát + quản lý (Flask) |
| **Telegram Bot** | Thông báo real-time |
| **Báo cáo backtest** | So sánh DCA thuần vs DCA+AI (biểu đồ + số liệu) |
| **Báo cáo đồ án** | ~80-100 trang |
| **6 sơ đồ UML** | Use Case, Class, Sequence, Activity, ERD, Deployment |

---

## 13. TÀI LIỆU THAM KHẢO

1. Hochreiter, S. & Schmidhuber, J. (1997). *Long Short-Term Memory*. Neural Computation, 9(8).
2. Cho, K. et al. (2014). *Learning Phrase Representations using RNN Encoder-Decoder*. arXiv:1406.1078.
3. Vaswani, A. et al. (2017). *Attention Is All You Need*. NeurIPS 2017.
4. Fischer, T. & Krauss, C. (2018). *Deep Learning with LSTM for Financial Market Predictions*. European Journal of OR, 270(2).
5. MetaQuotes (2024). *MQL5 Reference*. https://www.mql5.com/en/docs
6. Murphy, J. (1999). *Technical Analysis of the Financial Markets*. NYIF.
7. Chollet, F. (2021). *Deep Learning with Python, 2nd Edition*. Manning.
8. Grinberg, M. (2018). *Flask Web Development, 2nd Edition*. O'Reilly.

---

*Ngày lập: 05/06/2026*
*Tài liệu này được chuẩn bị để thảo luận với GVHD.*
