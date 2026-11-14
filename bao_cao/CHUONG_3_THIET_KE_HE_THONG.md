# CHƯƠNG 3. PHÂN TÍCH THIẾT KẾ VÀ KIẾN TRÚC HỆ THỐNG VQUANT

*Trong chương này, đồ án trình bày chi tiết toàn bộ quá trình phân tích yêu cầu, thiết kế kiến trúc tổng thể và hiện thực hóa từng phân hệ thành phần trong hệ sinh thái VQuant. Nội dung bao gồm: đặc tả các yêu cầu chức năng và phi chức năng; sơ đồ kiến trúc 6 tầng đa nền tảng; thiết kế chi tiết luồng tiền xử lý 17 đặc trưng kỹ thuật; cơ chế suy luận Ensemble kết hợp Deep Learning, Pattern Matching và NLP; giao thức IPC Failsafe liên tiến trình; kiến trúc hướng đối tượng của Robot MQL5 trên MetaTrader 5; cùng hệ thống giám sát tự trị Sentinel 24/7 và Telegram Bot.*

---

## 3.1 Phân tích yêu cầu hệ thống

### 3.1.1 Yêu cầu chức năng (Functional Requirements)

Hệ sinh thái giao dịch định lượng VQuant phải đáp ứng đầy đủ các nhóm chức năng cốt lõi sau:

1. **Thu thập và nạp dữ liệu thị trường tự động (Data Ingestion):**
   - Kết nối trực tiếp vào giao thức MetaTrader 5 qua thư viện `MetaTrader5` trên Python để lấy dữ liệu nến thời gian thực (Real-time Bars) và dữ liệu lịch sử của cặp tỷ giá XAU/USD trên các khung thời gian H4, H1, M15.
   - Cào dữ liệu lịch kinh tế thế giới từ ForexFactory và tin tức vĩ mô tài chính từ NewsAPI/RSS định kỳ 24/7.
2. **Kỹ thuật trích xuất đặc trưng (Feature Engineering):**
   - Tự động tính toán 17 đặc trưng kỹ thuật từ dữ liệu nến: OHLC chuẩn hóa, đường EMA(20), EMA(50), MACD Line, MACD Signal, MACD Hist, RSI(14), Bollinger Upper, Bollinger Lower, Bollinger %B, ATR(14), độ dốc xu hướng (Slope), và biến đại diện cảm xúc tin tức vĩ mô.
   - Chuẩn hóa dữ liệu đầu vào thông qua bộ chuẩn hóa `MinMaxScaler` đã được lưu trữ trọng số.
3. **Phân hệ trí tuệ nhân tạo dự báo xu hướng (AI Forecasting Engine):**
   - Mô hình học sâu CNN-BiGRU xuất xác suất phân loại 3 lớp: $P(\text{BUY}), P(\text{HOLD}), P(\text{SELL})$.
   - Module KNN Pattern Matcher quét lịch sử $3,719$ nến H4, tìm Top 5 mẫu hình có độ tương đồng Cosine $\ge 0.90$ để bổ sung bias xác suất $\pm 10\%$.
   - Module FinBERT & VADER phân tích tiêu đề tin tức, phát hiện bão tin (Burst Mode) và áp dụng cơ chế đảo chiều cảm xúc vàng $\pm 15\% - 25\%$.
4. **Cơ chế ra quyết định có điều kiện (Decision Gate):**
   - Chỉ phát lệnh mua/bán mạnh (`BUY_STRONG` / `SELL_STRONG`) khi xác suất vượt ngưỡng $45\%$ và bỏ xa hướng đối nghịch tối thiểu $15\%$. Khi không đủ độ tin cậy, tự động chuyển về `NEUTRAL`.
5. **Giao tiếp liên tiến trình an toàn (IPC Bridge & Failsafe Watchdog):**
   - Ghi thông điệp tín hiệu định dạng CSV có nhãn thời gian (Timestamp) vào thư mục chia sẻ tốc độ cao của MT5.
   - Robot MQL5 quét file mỗi tick và kiểm tra giới hạn thời gian (Timeout 4 giờ). Nếu quá hạn, tự động cô lập tín hiệu AI và chuyển sang chế độ bảo vệ vốn độc lập.
6. **Thực thi giao dịch tự động trên MetaTrader 5 (Automated Execution):**
   - Khởi tạo lưới lệnh ma trận DCA với khối lượng khởi điểm an toàn (0.01 lot).
   - Tự động co giãn bước giá nhồi lệnh theo biên độ ATR thời gian thực.
   - Tự động dời điểm hòa vốn tổng thể (Consolidated Break-Even) và đóng toàn bộ rổ lệnh khi đạt mục tiêu lợi nhuận.
   - Cung cấp giao diện trực quan tương tác (Chart Dashboard) với 3 nút bấm: `Close All`, `Pause EA`, `Force Reset`.
7. **Giám sát tự trị và cảnh báo từ xa (Monitoring & Alerts):**
   - Dịch vụ Sentinel chạy ngầm 24/7, tự động kiểm tra nhịp tim hệ thống (Heartbeat), tự khởi động lại khi phát hiện crash.
   - Bot Telegram gửi thông báo đẩy tức thì khi: có tín hiệu AI mới, mở/đóng rổ lệnh, xuất hiện tin đỏ nguy hiểm, và báo cáo tổng kết PnL mỗi ngày.

---

### 3.1.2 Yêu cầu phi chức năng (Non-Functional Requirements)

1. **Độ trễ xử lý thấp (Low Latency):**
   - Thời gian suy luận của mô hình CNN-BiGRU trên CPU: $< 5$ mili-giây.
   - Độ trễ đọc và xử lý tín hiệu IPC trên MetaTrader 5: $< 100$ mili-giây mỗi tick.
2. **Độ ổn định và tính chịu lỗi cao (Fault Tolerance & High Availability):**
   - Hệ thống có khả năng vận hành liên tục 24/5 trong suốt tuần giao dịch.
   - Khi mất kết nối Internet hoặc sàn giao dịch mất kết nối tạm thời, Robot không được phép mất trạng thái quản lý các lệnh đang treo (State Persistence qua Magic Number).
3. **An toàn quản lý vốn tối đa (Capital Preservation):**
   - Mức sụt giảm tài khoản tối đa (Max Drawdown) trong mọi kịch bản kiểm thử không vượt quá $35\%$.
   - Tự động kích hoạt cơ chế phòng vệ (Hedging hoặc Emergency Stop) khi rủi ro vượt ngưỡng cho phép.
4. **Tính module hóa và khả năng mở rộng (Modularity & Extensibility):**
   - Kiến trúc MQL5 được thiết kế hoàn toàn theo chuẩn Hướng đối tượng (OOP), tách bạch rõ ràng giữa tầng dữ liệu, chỉ báo, quản lý lưới, quản lý lệnh và giao diện.
   - Cho phép dễ dàng thay thế hoặc bổ sung các mô hình AI mới (Transformer, Random Forest, RL) mà không cần viết lại mã nguồn Robot MQL5.

---

## 3.2 Kiến trúc tổng thể hệ thống VQuant

Hệ sinh thái VQuant được tổ chức theo mô hình kiến trúc **6 Tầng Đa Nền Tảng (6-Tier Decoupled Architecture)**. Các phân hệ được phân tách rõ ràng về mặt chức năng nhưng giao tiếp thông suốt qua các giao thức định lượng:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KIẾN TRÚC TỔNG THỂ HỆ THỐNG VQUANT                    │
└─────────────────────────────────────────────────────────────────────────────┘

 [ TẦNG 1: DATA PIPELINE ]
 ├── MetaTrader 5 API ────────► [ fetcher.py ] ──────┐
 ├── ForexFactory Scraping ────► [ news_filter.py ] ─┼──► [ features.py ] (17 Features)
 └── Financial News Feed ──────► [ hft_streamer.py ] ┘
                                                            │ Tensor (Batch, 50, 17)
                                                            ▼
 [ TẦNG 2: AI & DEEP LEARNING ]
 ├── CNN-BiGRU Neural Net ────► P(BUY), P(HOLD), P(SELL) ──┐
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
 └── CDashboard.mqh ─────────► Bảng điều khiển trực quan + 3 nút bấm tương tác
                                        │
                                        ▼
 [ TẦNG 5 & 6: GIÁM SÁT & ĐỊNH LƯỢNG ]
 ├── Telegram Bot (bot/) ────► Cảnh báo tin tức, biến động PnL, lệnh /status
 ├── Sentinel Service ───────► Giám sát tự trị 24/7, tự phục hồi lỗi
 ├── Backtest Engine ────────► Kiểm thử dữ liệu 14,000+ nến M15 (Sharpe, Drawdown)
 └── Web Dashboard (web/) ───► Giao diện FastAPI theo dõi biểu đồ real-time
```

---

## 3.3 Thiết kế chi tiết các phân hệ thành phần

### 3.3.1 Phân hệ Thu thập và Tiền xử lý dữ liệu (Data Ingestion & Feature Engineering)

Phân hệ bao gồm các thành phần:
- [fetcher.py](file:///c:/KLTNN/src/data/fetcher.py): Khởi tạo phiên làm việc với thiết bị đầu cuối MT5 qua hàm `mt5.initialize()`. Lấy nến H4 gần nhất, trích xuất các mảng giá trị `open`, `high`, `low`, `close`, `tick_volume`.
- [features.py](file:///c:/KLTNN/src/data/features.py): Đảm nhận nhiệm vụ chuyển đổi chuỗi giá trị thô thành ma trận 17 đặc trưng kỹ thuật:

| STT | Tên đặc trưng | Công thức / Phương pháp tính | Ý nghĩa định lượng |
|:---:|:---|:---|:---|
| 1 | `open_norm` | $(Open - Close) / ATR$ | Vị thế tương đối của giá mở cửa |
| 2 | `high_norm` | $(High - Close) / ATR$ | Chiều dài bóng nến trên (áp lực bán) |
| 3 | `low_norm` | $(Close - Low) / ATR$ | Chiều dài bóng nến dưới (áp lực mua) |
| 4 | `close` | Giá đóng cửa thực tế (chuẩn hóa MinMax) | Mức giá tham chiếu |
| 5 | `ema20_diff` | $(Close - EMA_{20}) / EMA_{20}$ | Độ lệch xu hướng ngắn hạn |
| 6 | `ema50_diff` | $(Close - EMA_{50}) / EMA_{50}$ | Độ lệch xu hướng trung hạn |
| 7 | `ema_cross` | $EMA_{20} - EMA_{50}$ | Tín hiệu giao cắt trung bình động |
| 8 | `rsi` | $RSI_{14} / 100$ | Động lượng quá mua/quá bán $[0, 1]$ |
| 9 | `macd` | $EMA_{12} - EMA_{26}$ | Đường MACD chính |
| 10 | `macd_signal` | $EMA_{9}(\text{MACD})$ | Đường tín hiệu MACD |
| 11 | `macd_hist` | $\text{MACD} - \text{Signal}$ | Xung lực động lượng thị trường |
| 12 | `bb_upper_diff` | $(UpperBand - Close) / Close$ | Khoảng cách tới biên trên dải Bollinger |
| 13 | `bb_lower_diff` | $(Close - LowerBand) / Close$ | Khoảng cách tới biên dưới dải Bollinger |
| 14 | `bb_width` | $(UpperBand - LowerBand) / Middle$ | Độ co thắt biến động (Bollinger Squeeze) |
| 15 | `atr_norm` | $ATR_{14} / Close$ | Tỷ lệ biến động tương đối |
| 16 | `slope_5` | Hệ số góc hồi quy tuyến tính 5 nến | Gia tốc hướng đi ngắn hạn |
| 17 | `sentiment_score`| Điểm cảm xúc tin tức vĩ mô $[-1, +1]$ | Tác động cơ bản từ tin tức |

Chuỗi dữ liệu 17 đặc trưng được đóng gói thành các khối cửa sổ trượt (Sliding Windows) có kích thước cố định $(50, 17)$, đại diện cho lịch sử 50 cây nến H4 (tương đương hơn 8 ngày giao dịch liên tục).

---

### 3.3.2 Phân hệ Trí tuệ nhân tạo dự báo xu hướng (AI Forecasting Subsystem)

Bộ não phân tích của hệ thống nằm trong [ai_engine.py](file:///c:/KLTNN/src/engine/ai_engine.py), vận hành theo cơ chế tổng hợp đa tầng:

```
          Tensor Đầu vào: 50 nến x 17 đặc trưng
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
  [ MÔ HÌNH HỌC SÂU ]  [ PATTERN MATCHER ]  [ NLP FINBERT/VADER ]
  CNN-BiGRU Net        KNN Cosine Sim        Lịch kinh tế & Tin tức
       │                   │                   │
  P_DL(BUY, HOLD, SELL)   Cosine Bias (±10%)   Macro Bias (±15% - 25%)
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                  [ TỔNG HỢP XÁC SUẤT ]
            P_final(BUY) = P_DL(BUY) + Bias_KNN + Bias_NLP
            P_final(SELL) = P_DL(SELL) - Bias_KNN - Bias_NLP
                           │
                           ▼
                 [ DECISION THRESHOLD GATE ]
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
   Thỏa mãn điều kiện:                Không thỏa mãn:
   P >= 0.45 VÀ P_lead >= 0.15        Chênh lệch thấp / Không rõ ràng
         │                                   │
         ▼                                   ▼
   Tín hiệu: BUY_STRONG hoặc SELL_STRONG     Tín hiệu: NEUTRAL
```

#### 1. Mô hình đề xuất CNN-BiGRU ([gru_model.py](file:///c:/KLTNN/src/models/gru_model.py))
Kiến trúc mô hình được xây dựng trên TensorFlow/Keras gồm các tầng tuần tự:
- `Input(shape=(50, 17))`
- `Conv1D(filters=32, kernel_size=3, padding='same', activation='relu')`
- `BatchNormalization()`: Ổn định gradient, tăng tốc độ hội tụ.
- `MaxPooling1D(pool_size=2)`: Nén dữ liệu thời gian từ 50 xuống 25 bước.
- `SpatialDropout1D(0.2)`: Loại bỏ ngẫu nhiên 20% bản đồ đặc trưng để chống quá khớp.
- `Bidirectional(GRU(units=32, return_sequences=False))`: Quét chuỗi 2 chiều, tổng hợp thành vector trạng thái 64 chiều.
- `Dropout(0.3)`
- `Dense(16, activation='relu')`
- `Dense(3, activation='softmax')`: Xuất 3 xác suất rời rạc có tổng bằng 1.

#### 2. Kỹ thuật gán nhãn thích nghi biến động (Adaptive ATR Labeling)
Trong [trainer.py](file:///c:/KLTNN/src/models/trainer.py), thay vì gán nhãn cố định theo số pip (dễ sai lệch khi thị trường chuyển mùa biến động), đồ án áp dụng phương pháp gán nhãn dựa trên ngưỡng biến động ATR:

$$\text{Label}_t = 
\begin{cases} 
\text{BUY} (0) & \text{khi } Close_{t+k} - Close_t \ge \alpha \times ATR_t \\
\text{SELL} (2) & \text{khi } Close_t - Close_{t+k} \ge \alpha \times ATR_t \\
\text{HOLD} (1) & \text{còn lại}
\end{cases}$$

Với $k=3$ (dự báo trước 3 nến H4, tương đương 12 giờ) và hệ số $\alpha = 0.75$.

---

### 3.3.3 Phân hệ Robot giao dịch MetaTrader 5 (MQL5 OOP Architecture)

Toàn bộ mã nguồn Robot được xây dựng bằng MQL5 theo chuẩn Lập trình hướng đối tượng trong thư mục [mql5/Include/VQuant/](file:///c:/KLTNN/mql5/Include/VQuant/):

```
mql5/
├── V_Capital_OOP.mq5                 (Điểm khởi chạy chính - OnInit, OnTick, OnDeinit)
└── Include/
    └── VQuant/
        ├── Config/
        │   ├── Enums.mqh             (Kiểu dữ liệu: ENUM_AI_SIGNAL, ENUM_SYSTEM_STATE)
        │   └── Inputs.mqh            (Lớp CInputs: Quản lý tham số Lot, TP, ATR, Magic)
        ├── Communication/
        │   └── FileBridge.mqh        (Lớp CFileBridge: Đọc file IPC + Watchdog 4h)
        ├── Indicators/
        │   └── Filters.mqh           (Lớp CFilters: Tính toán ATR, EMA trên MT5)
        ├── Trading/
        │   ├── GridManager.mqh       (Lớp CGridManager: Logic tính ma trận lưới lệnh)
        │   └── OrderManager.mqh      (Lớp COrderManager: Thực thi lệnh, dời TP, bảo vệ vốn)
        └── UI/
            └── Dashboard.mqh         (Lớp CDashboard: Giao diện đồ họa tương tác trên Chart)
```

#### Sơ đồ hoạt động trong sự kiện `OnTick()`:
1. `CFileBridge::ReadSignal()`: Đọc file tín hiệu IPC. Nếu timestamp quá 4h $\rightarrow$ chuyển cờ `is_ai_online = false`.
2. `CFilters::Update()`: Cập nhật giá trị ATR(14) và EMA của cây nến hiện tại.
3. `COrderManager::MonitorPositions()`: Quét toàn bộ danh sách lệnh có `MagicNumber` của bot:
   - Tính toán lãi/lỗ ròng thả nổi (Floating PnL).
   - Kiểm tra điều kiện chốt lời rổ lệnh: Nếu giá chạm ngưỡng $P_{\text{TakeProfit, Basket}}$, kích hoạt đóng toàn bộ rổ lệnh trong 1 chu kỳ tick.
4. `CGridManager::EvaluateNextAction()`:
   - Nếu chưa có lệnh nào đang mở: Nếu AI phát tín hiệu `BUY_STRONG` $\rightarrow$ Mở lệnh Buy cơ sở; nếu phát `SELL_STRONG` $\rightarrow$ Mở lệnh Sell cơ sở; nếu `NEUTRAL` $\rightarrow$ Đứng ngoài quan sát.
   - Nếu đã có rổ lệnh đang chạy: Kiểm tra khoảng cách giá hiện tại so với lệnh gần nhất. Nếu khoảng cách $\ge \text{Spacing}_{\text{dynamic}}$ tính theo ATR $\rightarrow$ Mở lệnh nhồi tiếp theo theo hệ số nhân $\beta$.
5. `CDashboard::Render()`: Cập nhật bảng thông tin trực quan lên Chart: trạng thái kết nối AI (`ONLINE` xanh lá / `WAITING PYTHON` cam), tín hiệu hiện tại, số lượng lệnh, Floating PnL và hiển thị 3 nút bấm khẩn cấp.

---

### 3.3.4 Phân hệ Giám sát tự trị Sentinel 24/7 và Telegram Bot

Nhằm đảm bảo hệ thống có thể vận hành hoàn toàn không cần sự can thiệp của con người trên máy chủ ảo (VPS), đồ án thiết kế hai thành phần tự trị:

#### 1. Dịch vụ Sentinel 24/7 ([sentinel_service.py](file:///c:/KLTNN/src/engine/sentinel_service.py))
Chạy dưới dạng một tiến trình nền độc lập (Daemon Process):
- **Cơ chế nhịp tim (Heartbeat Monitoring):** Cứ mỗi 60 giây, kiểm tra trạng thái hoạt động của tiến trình suy luận AI và tệp chia sẻ IPC.
- **Tự động phục hồi (Auto-Restart):** Nếu phát hiện tiến trình AI bị tắt đột ngột do lỗi ngoại lệ hoặc quá tải bộ nhớ, Sentinel tự động ghi log lỗi vào hệ thống và kích hoạt chạy lại tiến trình trong vòng 5 giây.
- **Chế độ kiểm tra sức khỏe mạng (Connectivity Check):** Liên tục kiểm tra kết nối tới máy chủ MT5 và API ForexFactory.

#### 2. Telegram Bot & Notifier ([telegram_bot.py](file:///c:/KLTNN/src/bot/telegram_bot.py))
Tích hợp API Telegram Bot để cung cấp kênh giao tiếp 2 chiều:
- **Thông báo chủ động (Push Notifications):**
  - Bắn tin nhắn kèm âm thanh cảnh báo ngay khi AI phát hiện điểm đảo chiều xu hướng mạnh.
  - Cảnh báo trước 30 phút khi sắp diễn ra sự kiện kinh tế High Impact (Non-Farm, CPI, FOMC).
  - Báo cáo tài chính cuối ngày: Tổng số lệnh đã khớp, tổng lợi nhuận thu về, mức sụt giảm cao nhất trong ngày.
- **Tương tác lệnh điều khiển từ xa (Pull Commands):**
  - `/status`: Kiểm tra trạng thái toàn hệ sinh thái (CPU, RAM, kết nối MT5, AI Signal hiện tại).
  - `/profit`: Xem báo cáo lãi/lỗ chi tiết trong ngày, tuần, tháng.
  - `/signal`: Buộc AI thực hiện một chu kỳ phân tích nến và trả kết quả tức thì.
  - `/close`: Lệnh khẩn cấp từ xa đóng toàn bộ các lệnh đang mở trên MT5.

---

## 3.4 Thiết kế cấu trúc trao đổi dữ liệu (IPC Data Schema)

Tệp trao đổi tín hiệu giữa Python AI và Robot MetaTrader 5 được lưu tại đường dẫn chuẩn:
`C:\Users\<User>\AppData\Roaming\MetaQuotes\Terminal\Common\Files\vc_signal_XAUUSDm.txt`

### Định dạng cấu trúc bản tin CSV:
```csv
TIMESTAMP,SIGNAL,CONFIDENCE,SOURCE
2026-10-25 14:00:00,BUY_STRONG,0.6852,CNN_BIGRU_ENSEMBLE
```

### Đặc tả các trường dữ liệu:
1. `TIMESTAMP` (chuỗi ISO `YYYY-MM-DD HH:MM:SS`): Dấu thời gian chính xác tại thời điểm AI hoàn tất suy luận. Robot MT5 dùng trường này để tính toán Failsafe Watchdog Timeout ($\Delta T \le 4\text{h}$).
2. `SIGNAL` (chuỗi ký tự chuẩn hóa):
   - `BUY_STRONG`: AI nhận diện xu hướng tăng mạnh mẽ có sự đồng thuận của cả 3 tầng (Học sâu, Pattern, Tin tức). Robot MT5 ưu tiên mở lệnh Buy hoặc kích hoạt bảo vệ cho rổ lệnh Buy.
   - `SELL_STRONG`: AI nhận diện xu hướng giảm sâu. Robot MT5 ưu tiên mở lệnh Sell.
   - `NEUTRAL`: Thị trường đi ngang tích lũy hoặc các chỉ báo triệt tiêu lẫn nhau. Robot MT5 chạy chế độ DCA lưới thuần túy hoặc tạm dừng mở chu kỳ mới.
3. `CONFIDENCE` (số thực trong đoạn $[0.0, 1.0]$): Mức độ tin cậy của tín hiệu. Robot MT5 có thể cấu hình chỉ hành động khi `CONFIDENCE >= InpMinConfidence` (mặc định $0.55$).
4. `SOURCE` (chuỗi ký tự): Ghi nhận xuất xứ thuật toán phục vụ mục đích kiểm toán và Debug hệ thống.

---

## 3.5 Kết luận chương 3

Trong chương 3, đồ án đã hoàn thành toàn bộ thiết kế kiến trúc và hiện thực hóa hệ thống giao dịch tự động VQuant:
1. Xác định đầy đủ các yêu cầu chức năng (7 nhóm) và phi chức năng (độ trễ thấp, chịu lỗi cao, bảo vệ vốn).
2. Xây dựng sơ đồ kiến trúc tổng thể 6 tầng phân tách rõ ràng từ Data Pipeline, AI Engine, IPC Bridge, Robot MQL5, Telegram Bot, đến Web Dashboard.
3. Chi tiết hóa quy trình trích xuất 24 đặc trưng kỹ thuật nhân quả và cơ chế gán nhãn thích nghi theo biên độ biến động ATR.
4. Hiện thực hóa mạng nơ-ron lai CNN-BiGRU-Attention kết hợp cơ chế bù trừ xác suất từ KNN Pattern Matcher và FinBERT NLP.
5. Thiết kế hoàn chỉnh Robot MQL5 theo mô hình Hướng đối tượng OOP với cơ chế lưới co giãn ATR và phòng hộ rủi ro đa tầng.
6. Thiết lập cơ chế giao tiếp liên tiến trình an toàn với Failsafe Watchdog chống rủi ro ngắt kết nối ngầm.

Toàn bộ hệ thống này đã được triển khai, huấn luyện trên $3,719$ nến H4 thực tế và backtest trên $14,000+$ nến M15, kết quả thực nghiệm chi tiết sẽ được trình bày và phân tích trong **Chương 4**.
