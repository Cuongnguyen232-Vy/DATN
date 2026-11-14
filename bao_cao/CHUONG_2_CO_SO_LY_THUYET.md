# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ÁP DỤNG

*Trong chương này, đồ án trình bày chi tiết nền tảng lý thuyết và các công nghệ cốt lõi được ứng dụng trong hệ sinh thái VQuant. Nội dung bao gồm: đặc tính thị trường kim loại quý XAU/USD và các chỉ báo kỹ thuật định lượng; nguyên lý hoạt động của mạng học sâu CNN-BiGRU và thuật toán so khớp mẫu hình chuỗi thời gian; phương pháp phân tích cảm xúc tin tức kinh tế vĩ mô qua FinBERT và VADER; nguyên lý chiến lược giao dịch lưới ma trận co giãn động (Adaptive Grid DCA); cùng các độ đo khoa học dùng trong đánh giá mô hình học máy và chiến lược đầu tư tài chính.*

---

## 2.1 Tổng quan về thị trường tài chính và phân tích kỹ thuật

### 2.1.1 Đặc tính thị trường Vàng giao ngay (XAU/USD)

Thị trường kim loại quý — tiêu biểu là cặp tỷ giá Vàng giao ngay so với Đô la Mỹ (**XAU/USD**) — là một trong những thị trường tài chính có tính thanh khoản cao nhất toàn cầu, với khối lượng giao dịch bình quân mỗi ngày ước tính vượt 150 tỷ USD. Khác với thị trường chứng khoán cơ sở chịu giới hạn về biên độ dao động và thời gian mở cửa theo giờ hành chính, thị trường XAU/USD vận hành liên tục 24 giờ mỗi ngày (từ rạng sáng thứ Hai đến đêm muộn thứ Sáu theo giờ Việt Nam).

Đặc trưng động học của cặp tỷ giá XAU/USD bao gồm:
1. **Độ biến động mạnh (High Volatility):** Vàng vừa là hàng hóa giao dịch, vừa là tài sản trú ẩn an toàn (safe-haven asset). Biên độ dao động trung bình hàng ngày (Daily ATR) thường dao động từ $15 đến $40/ounce, và có thể lên tới $60 - $100/ounce trong những thời điểm có sự kiện địa chính trị bất ngờ hoặc công bố dữ liệu kinh tế vĩ mô quan trọng.
2. **Mối tương quan nghịch đảo với đồng USD (DXY Correlation):** Vì vàng được định giá bằng đồng Đô la Mỹ, giá vàng có mối tương quan nghịch biến chặt chẽ với chỉ số Dollar Index (DXY) và lợi suất trái phiếu chính phủ Mỹ kỳ hạn 10 năm. Khi đồng USD tăng giá mạnh do chính sách thắt chặt tiền tệ của Cục Dự trữ Liên bang Mỹ (FED), giá vàng chịu áp lực bán tháo; ngược lại, khi lạm phát gia tăng hoặc đồng USD suy yếu, dòng vốn quốc tế chuyển dịch mạnh mẽ vào kim loại quý nhằm phòng hộ giá trị.
3. **Mô hình hành vi phi tuyến (Non-linear Dynamics):** Đường giá XAU/USD chứa đựng tỷ lệ nhiễu cao (High Noise-to-Signal Ratio). Các giai đoạn thị trường tích lũy (Range-bound/Sideway) chiếm tới 65% – 70% tổng thời gian, trong khi các đợt bứt phá xu hướng mạnh mẽ (Trending/Breakout) chỉ diễn ra trong khoảng 30% thời gian còn lại.

```
       ┌────────────────────────────────────────────────────────┐
       │             BIẾN ĐỘNG GIÁ XAU/USD (REAL-TIME)          │
       └───────────────────────────┬────────────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   [65% - 70% Thời gian]                     [30% - 35% Thời gian]
   THỊ TRƯỜNG TÍCH LŨY (SIDEWAY)             THỊ TRƯỜNG CÓ XU HƯỚNG (TRENDING)
   - Dao động trong biên độ hẹp              - Bứt phá mạnh mẽ (Breakout)
   - Tối ưu cho chiến lược Grid DCA          - Dễ gây cháy tài khoản nếu DCA ngược xu hướng
   - Tần suất nổ lệnh cao, rủi ro thấp       - Yêu cầu AI nhận diện xu hướng sớm để Hedge
```

---

### 2.1.2 Các chỉ báo phân tích kỹ thuật định lượng

Nhằm chuyển đổi chuỗi giá thô (Raw OHLCV: Open, High, Low, Close, Volume) thành các đặc trưng toán học có ý nghĩa thống kê cho mô hình học máy, đồ án áp dụng bộ 5 nhóm chỉ báo kỹ thuật kinh điển:

#### 1. Đường trung bình động hàm mũ (Exponential Moving Average - EMA)
Đường EMA gán trọng số suy giảm theo hàm mũ cho các mức giá gần nhất, giúp phản ứng nhanh hơn so với đường trung bình động đơn giản (SMA):

$$EMA_t = P_t \times \alpha + EMA_{t-1} \times (1 - \alpha)$$

Trong đó:
- $P_t$ là giá đóng cửa của nến tại thời điểm $t$.
- $\alpha = \frac{2}{N + 1}$ là hệ số nhân trọng số (Smoothing Factor), với $N$ là chu kỳ nến (hệ thống sử dụng $N = 20$ và $N = 50$).

Độ lệch tương đối giữa hai đường $EMA_{20}$ và $EMA_{50}$ cung cấp thông tin về gia tốc xu hướng trong ngắn hạn và trung hạn:

$$\Delta EMA_t = \frac{EMA_{20, t} - EMA_{50, t}}{EMA_{50, t}} \times 100\%$$

#### 2. Chỉ số sức mạnh tương đối (Relative Strength Index - RSI)
RSI đo lường tốc độ và sự thay đổi của biến động giá nhằm định lượng trạng thái quá mua (Overbought) hoặc quá bán (Oversold) trên miền giá trị $[0, 100]$:

$$RSI = 100 - \left( \frac{100}{1 + RS} \right)$$

$$RS = \frac{\text{Average Gain}_n}{\text{Average Loss}_n}$$

Trong hệ thống VQuant, RSI chu kỳ 14 nến ($RSI_{14}$) được chuẩn hóa về đoạn $[0, 1]$ qua phép biến đổi:

$$RSI_{\text{norm}} = \frac{RSI_{14}}{100}$$

#### 3. Đường trung bình động hội tụ phân kỳ (MACD)
MACD phản ánh sự tương tác động lượng giữa xu hướng ngắn hạn và dài hạn:

$$\text{MACD Line} = EMA_{12}(P) - EMA_{26}(P)$$

$$\text{Signal Line} = EMA_{9}(\text{MACD Line})$$

$$\text{MACD Histogram} = \text{MACD Line} - \text{Signal Line}$$

Giá trị của MACD Histogram phản ánh trực tiếp xung lực thị trường. Khi Histogram đảo chiều từ âm sang dương, xung lực mua bắt đầu chiếm ưu thế.

#### 4. Dải băng Bollinger (Bollinger Bands)
Bollinger Bands xác định dải biên dao động chuẩn tắc xung quanh đường trung bình động $SMA_{20}$:

$$\text{Middle Band} = SMA_{20}(P)$$

$$\text{Upper Band} = SMA_{20}(P) + 2 \times \sigma_{20}$$

$$\text{Lower Band} = SMA_{20}(P) - 2 \times \sigma_{20}$$

Trong đó $\sigma_{20}$ là độ lệch chuẩn của giá đóng cửa trong 20 chu kỳ. Tỷ lệ phần trăm vị trí giá trong dải (%B) được tính theo công thức:

$$\%B = \frac{P_t - \text{Lower Band}}{\text{Upper Band} - \text{Lower Band}}$$

Chỉ số $\%B$ phản ánh chính xác vị thế tương quan của giá hiện tại so với ngưỡng dao động thống kê chuẩn.

#### 5. Chỉ báo dao động ngẫu nhiên (Stochastic Oscillator)
Stochastic đo lường vị trí tương đối của giá đóng cửa so với biên độ giá (High - Low) trong một khoảng thời gian  = 14$ nến:

\%K = \frac{Close_t - \min_{14}(Low)}{\max_{14}(High) - \min_{14}(Low)} \times 100

\%D = SMA_3(\%K)

Chỉ báo giúp xác định các điểm đảo chiều xung lượng cực ngắn hạn khi $\%K$ cắt qua đường tín hiệu $\%D$ ở các vùng quá mua ($>80$) hoặc quá bán ($<20$).

#### 6. Tốc độ thay đổi giá (Rate of Change - ROC)
ROC đo lường tỷ lệ thay đổi phần trăm giữa giá đóng cửa hiện tại so với giá đóng cửa cách đó  = 10$ nến:

ROC_t = \frac{Close_t - Close_{t-10}}{Close_{t-10}} \times 100\%

Chỉ số phản ánh trực tiếp gia tốc tăng hoặc giảm của xu hướng giá.

#### 7. Độ biến động thực tế trung bình (Average True Range - ATR)
ATR đo lường độ phân tán và biến động thị trường thực tế mà không phụ thuộc vào hướng đi của giá. Phạm vi thực tế (True Range - TR) tại nến $t$ được xác định bởi:

$$TR_t = \max \left( High_t - Low_t, \, |High_t - Close_{t-1}|, \, |Low_t - Close_{t-1}| \right)$$

Chỉ số ATR chu kỳ 14 nến được tính theo phương pháp trung bình làm mượt của Wilder:

$$ATR_{14, t} = \frac{ATR_{14, t-1} \times 13 + TR_t}{14}$$

> **Ý nghĩa then chốt trong hệ thống VQuant:** Chỉ số ATR đóng vai trò "thước đo nhịp đập thị trường". Nó không chỉ được cấp làm đặc trưng đầu vào cho mô hình AI, mà còn là tham số cơ sở để thuật toán Robot MQL5 tự động co giãn bước giá nhồi lệnh (Grid Spacing) và khoảng cách chốt lời (Take Profit).

---

## 2.2 Kiến trúc Học sâu và Học máy trên chuỗi thời gian

### 2.2.1 Mạng nơ-ron tích chập một chiều (1D-CNN)

Mạng tích chập một chiều (1D Convolutional Neural Network) là công cụ trích xuất đặc trưng cực kỳ hiệu quả đối với dữ liệu chuỗi thời gian nhiều biến số (Multivariate Time Series). 

Khác với tích chập 2D trên hình ảnh, phép tích chập 1D thực hiện trượt kernel có kích thước $(k, d)$ dọc theo trục thời gian (Time Dimension):

$$y_t = f \left( \sum_{i=0}^{k-1} W_i \cdot x_{t+i} + b \right)$$

Trong đó:
- $x_{t} \in \mathbb{R}^d$ là vector đặc trưng tại bước thời gian $t$ (với $d = 17$ đặc trưng).
- $W \in \mathbb{R}^{k \times d}$ là ma trận trọng số của bộ lọc (Kernel filter).
- $b$ là bias và $f(\cdot)$ là hàm kích hoạt phi tuyến (ReLU hoặc LeakyReLU).

```
   Chuỗi nến thời gian (T=50, D=17)
   ┌────────────────────────────────┐
   │ t=1  [ o, h, l, c, rsi, ... ]  │
   │ t=2  [ o, h, l, c, rsi, ... ]  │
   │ t=3  [ o, h, l, c, rsi, ... ]  │ ──┐ 1D Kernel (k=3)
   │ ...                            │   ├───────────────► Bản đồ đặc trưng cục bộ
   │ t=50 [ o, h, l, c, rsi, ... ]  │ ──┘                 (Local Invariant Features)
   └────────────────────────────────┘
```

**Ưu điểm của tầng 1D-CNN trong bài toán tài chính:**
- Khả năng bất biến tịnh tiến cục bộ (Local Translation Invariance): Giúp nhận diện các cấu trúc hình nến đặc thù (Pinbar, Engulfing, Morning Star, nến rút râu) mà không bị phụ thuộc vào mức giá tuyệt đối.
- Giảm thiểu đáng kể số lượng tham số cần huấn luyện so với tầng Fully-Connected, từ đó hạn chế hiện tượng quá khớp (Overfitting).

---

### 2.2.2 Mạng nơ-ron hồi quy (LSTM và GRU)

#### 1. Mạng bộ nhớ dài-ngắn hạn (Long Short-Term Memory - LSTM)
Mạng hồi quy truyền thống (RNN) gặp phải rào cản nghiêm trọng về hiện tượng triệt tiêu hoặc bùng nổ đạo hàm (Vanishing / Exploding Gradients) khi học các chuỗi dài. Mô hình LSTM (Hochreiter & Schmidhuber, 1997) giải quyết vấn đề này bằng cách bổ sung đường truyền trạng thái ô nhớ (Cell State $) cùng 3 cổng điều khiển: Cổng quên (Forget Gate $), Cổng vào (Input Gate $) và Cổng ra (Output Gate $):

f_t = \sigma(W_f x_t + U_f h_{t-1} + b_f)
i_t = \sigma(W_i x_t + U_i h_{t-1} + b_i)
\tilde{C}_t = \tanh(W_c x_t + U_c h_{t-1} + b_c)
C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t
o_t = \sigma(W_o x_t + U_o h_{t-1} + b_o)
h_t = o_t \odot \tanh(C_t)

#### 2. Đơn vị hồi quy có cổng (Gated Recurrent Unit - GRU)
Mô hình GRU (Cho et al., 2014) được thiết kế nhằm tinh gọn hóa kiến trúc của LSTM bằng cách gộp Cell State và Hidden State, đồng thời giảm số lượng cổng từ 3 xuống 2 (Cổng cập nhật $ và Cổng đặt lại $):

\text{Cổng cập nhật (Update Gate):} \quad z_t = \sigma \left( W_z x_t + U_z h_{t-1} + b_z 
ight)
\text{Cổng đặt lại (Reset Gate):} \quad r_t = \sigma \left( W_r x_t + U_r h_{t-1} + b_r 
ight)
\text{Trạng thái ẩn ứng viên (Candidate State):} \quad \tilde{h}_t = \tanh \left( W_h x_t + U_h (r_t \odot h_{t-1}) + b_h 
ight)
\text{Trạng thái ẩn cuối cùng (Final Hidden State):} \quad h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t

So với LSTM, GRU có số lượng tham số ít hơn khoảng \%$, tốc độ huấn luyện và suy luận nhanh hơn, đồng thời giảm đáng kể rủi ro quá khớp trên tập dữ liệu chuỗi tài chính có độ dài vừa phải.

#### 3. Kiến trúc hai chiều (Bidirectional GRU - BiGRU)
Trong một cửa sổ trượt quá khứ cố định (Sliding Window độ dài =50$ nến H4), việc xem xét chuỗi theo cả hai chiều thuận (từ nến  
ightarrow 50$) và nghịch (từ nến  
ightarrow 1$) cho phép mạng nắm bắt trọn vẹn ngữ cảnh của cấu trúc sóng giá:

\vec{h}_t = \overrightarrow{\text{GRU}}(x_t, \vec{h}_{t-1})
\overleftarrow{h}_t = \overleftarrow{\text{GRU}}(x_t, \overleftarrow{h}_{t+1})
H_t = [\vec{h}_t \,\|\, \overleftarrow{h}_t]

Trạng thái tổng hợp $ chứa đựng cả xu hướng tích lũy từ quá khứ lẫn sự phản ứng tức thời tại các điểm uốn của chu kỳ nến.

---

### 2.2.3 Cơ chế Chú ý Đa đầu (Multi-Head Self-Attention)

Mặc dù BiGRU giải quyết tốt việc nén thông tin chuỗi, nhưng trong một chuỗi 50 nến, không phải cây nến nào cũng có tầm quan trọng như nhau đối với quyết định bùng nổ xu hướng. Cơ chế Chú ý (Attention Mechanism - Vaswani et al., 2017) cho phép mô hình tự động phân bổ trọng số tập trung vào những nến biến động bước ngoặt (như nến Breakout, nến Pinbar rút chân, nến bão tin tức vĩ mô).

#### 1. Cơ chế Chú ý Tích vô hướng chuẩn hóa (Scaled Dot-Product Attention)
Đầu ra chuỗi nơ-ron từ tầng BiGRU được chiếu tuyến tính thành 3 không gian biểu diễn: Truy vấn (Query $), Khóa (Key $) và Giá trị (Value $):

Q = H W^Q, \quad K = H W^K, \quad V = H W^V

Ma trận trọng số chú ý được tính thông qua tích vô hướng chuẩn hóa:

\text{Attention}(Q, K, V) = \text{softmax}\left( \frac{Q K^T}{\sqrt{d_k}} 
ight) V

Trong đó $\sqrt{d_k}$ là hệ số tỷ lệ nhằm ngăn chặn tích vô hướng trở nên quá lớn khiến hàm softmax rơi vào vùng có đạo hàm cực nhỏ.

#### 2. Cơ chế Chú ý Đa đầu (Multi-Head Attention)
Thay vì chỉ tính một ma trận chú ý duy nhất, mô hình phân chia thành  = 4$ đầu chú ý song song (Heads), mỗi đầu có chiều không gian  = 16$. Điều này cho phép mô hình đồng thời quan sát và liên kết các đặc trưng tại nhiều khía cạnh khác nhau (ví dụ: một đầu chú ý theo dõi xung lượng RSI, một đầu chú ý theo dõi độ nén Bollinger Bands):

\text{head}_i = \text{Attention}(Q W_i^Q, K W_i^K, V W_i^V)
\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \text{head}_2, \dots, \text{head}_h) W^O

#### 3. Kết nối tắt phần dư và Chuẩn hóa tầng (Residual Connection & LayerNorm)
Nhằm duy trì dòng gradient xuyên suốt và tránh hiện tượng bão hòa tín hiệu, đầu ra chú ý được cộng trực tiếp với đầu vào của tầng BiGRU (Skip Connection) kết hợp với tầng chuẩn hóa Layer Normalization:

$$\text{Output}_{\text{Attention}} = \text{LayerNorm}\left( H + \text{MultiHead}(H, H, H) \right)$$

---

### 2.2.4 Mô hình lai đề xuất CNN-BiGRU-Attention

Đồ án đề xuất kiến trúc học sâu tiên tiến **CNN-BiGRU-Attention** kết hợp sức mạnh trích xuất đặc trưng hình thái cục bộ của khối Dual 1D-CNN, khả năng mô hình hóa sự phụ thuộc thời gian 2 chiều của BiGRU, và cơ chế định vị bước ngoặt bằng Multi-Head Self-Attention.

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │         ĐẦU VÀO: Tensor Cửa sổ trượt Đa biến (Batch, 50, 24)            │
  └────────────────────────────────────┬────────────────────────────────────┘
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  KHỐI 1D-CNN KÉP: Conv1D (48 filters, k=3) ──► BatchNorm ──►            │
  │                   Conv1D (32 filters, k=3) ──► BatchNorm ──► MaxPool(2) │
  │  Tự động trích xuất các mẫu hình giá và dao động cục bộ đa quy mô       │
  └────────────────────────────────────┬────────────────────────────────────┘
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  KHỐI BiGRU: Bidirectional GRU (Units=32, return_sequences=True)        │
  │  Nắm bắt động lực xu hướng cả quá khứ và tiến trình thời gian 2 chiều   │
  └────────────────────────────────────┬────────────────────────────────────┘
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  KHỐI CHÚ Ý ĐA ĐẦU: MultiHeadAttention (4 heads, key_dim=16)            │
  │  Tập trung trọng số vào các nến biến động bước ngoặt quan trọng         │
  └────────────────────────────────────┬────────────────────────────────────┘
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  KẾT NỐI TẮT & CHUẨN HÓA: Add() [Residual] ──► LayerNormalization()     │
  │  Chống tiêu biến gradient và duy trì thông tin nền tảng                 │
  └────────────────────────────────────┬────────────────────────────────────┘
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  TỔNG HỢP THỜI GIAN: GlobalAveragePooling1D()                           │
  │  Nén chuỗi thời gian thành vector biểu diễn tổng hợp đặc trưng           │
  └────────────────────────────────────┬────────────────────────────────────┘
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  HEAD PHÂN LOẠI: Dense(32, ReLU) ──► Dropout(0.2) ──► Dense(16, ReLU)   │
  │                  ──► Dense(3, Softmax)                                  │
  │  Đầu ra vector xác suất 3 lớp: [ P(HOLD), P(BUY), P(SELL) ]             │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### Hàm mất mát Focal Loss và Class Weights
Trong thị trường tài chính, phân bố nhãn nến thường bị mất cân bằng nghiêm trọng (lớp HOLD thường chiếm tỷ lệ áp đảo so với các điểm bùng nổ BUY hoặc SELL). Nhằm ngăn chặn hiện tượng mô hình thiên vị dự đoán lớp đa số, đồ án sử dụng ma trận trọng số lớp (Class Weights) và hàm mất mát Categorical Cross-Entropy có hiệu chỉnh:

$$\mathcal{L} = - \sum_{c=1}^{3} w_c \cdot y_c \cdot \log(\hat{y}_c)$$

Trong đó $w_c = \frac{N}{3 \times N_c}$ là trọng số phạt tỷ lệ nghịch với tần suất xuất hiện của nhãn $c$ trong tập huấn luyện.

---

### 2.2.5 Thuật toán so khớp mẫu hình chuỗi thời gian (KNN Pattern Matcher)

Bên cạnh mạng học sâu nơ-ron, đồ án tích hợp phương pháp tiếp cận dựa trên thực nghiệm lịch sử: **So khớp mẫu hình chuỗi thời gian bằng khoảng cách Cosine**.

Nguyên lý: "Lịch sử thị trường có xu hướng tự lặp lại". Nếu chuỗi giá của 20 nến gần nhất có hình thái biến động giống hệt một kịch bản đã từng xảy ra trong quá khứ, thì hành vi giá tiếp theo của kịch bản quá khứ đó sẽ mang lại gợi ý xác suất có giá trị.

Thuật toán thực hiện các bước sau:
1. Trích xuất vector giá đóng cửa $P = [p_1, p_2, \dots, p_K]$ của $K=20$ nến hiện tại.
2. Chuẩn hóa hình dáng đường giá theo phương pháp Min-Max cục bộ nhằm loại bỏ yếu tố mức giá tuyệt đối, chỉ giữ lại hình thái tương đối:

$$\bar{p}_i = \frac{p_i - \min(P)}{\max(P) - \min(P)}$$

3. Duyệt trên toàn bộ kho dữ liệu lịch sử $N$ nến ($N = 3,719$ nến H4), trích xuất từng cửa sổ trượt $Q_j$ độ dài $K$, chuẩn hóa tương tự thành $\bar{Q}_j$.
4. Tính độ tương đồng Cosine (Cosine Similarity) giữa vector hiện tại $\bar{P}$ và từng vector quá khứ $\bar{Q}_j$:

$$\text{Sim}(\bar{P}, \bar{Q}_j) = \frac{\bar{P} \cdot \bar{Q}_j}{\|\bar{P}\|_2 \cdot \|\bar{Q}_j\|_2} = \frac{\sum_{i=1}^{K} \bar{p}_i \bar{q}_{j,i}}{\sqrt{\sum_{i=1}^{K} \bar{p}_i^2} \sqrt{\sum_{i=1}^{K} \bar{q}_{j,i}^2}}$$

5. Chọn ra Top $M$ ($M=5$) kịch bản lịch sử có độ tương đồng cao nhất ($\text{Sim} \ge 0.90$).
6. Quan sát biến động của nến ngay sau $M$ kịch bản đó ($p_{K+1} - p_K$):
   - Nếu đa số nến quá khứ tăng điểm $\rightarrow$ Cộng điểm thiên hướng (Bias) cho xác suất BUY.
   - Nếu đa số nến quá khứ giảm điểm $\rightarrow$ Cộng điểm thiên hướng (Bias) cho xác suất SELL.

---

## 2.3 Xử lý ngôn ngữ tự nhiên trong phân tích cảm xúc tin tức tài chính

### 2.3.1 Kiến trúc mô hình FinBERT

**FinBERT** (Araci, 2019) là mô hình xử lý ngôn ngữ tự nhiên được xây dựng dựa trên kiến trúc Transformer hai chiều (BERT - Bidirectional Encoder Representations from Transformers), được huấn luyện tiếp tục (Continued Pre-training) trên tập dữ liệu tài chính khổng lồ bao gồm: Financial PhraseBank, tài liệu báo cáo tài chính thường niên 10-K, 10-Q của các công ty niêm yết trên sàn chứng khoán Mỹ, và hàng triệu tin tức thị trường từ Reuters, Bloomberg.

Khác với các mô hình ngôn ngữ thông thường vốn hiểu các từ ngữ theo ngữ nghĩa đời thường (ví dụ: từ "share" trong văn bản thông thường nghĩa là chia sẻ, nhưng trong tài chính nghĩa là cổ phần; từ "liability" thông thường nghĩa là gánh nặng, nhưng trong tài chính là khoản nợ phải trả), FinBERT có khả năng phân định sắc thái ngữ nghĩa chuyên ngành tài chính với độ chính xác vượt trội.

```
                  Tiêu đề tin tức:
  "US Core CPI rises 0.4% MoM, beating Fed expectations"
                           │
                           ▼
                 [Tokenization & WordPiece]
                           │
                           ▼
          [12 Tầng Transformer Encoders với Multi-Head Self-Attention]
                           │
                           ▼
                 [Classification Head]
                           │
                           ▼
   Xác suất sắc thái: [ Negative: 0.12, Neutral: 0.08, Positive: 0.80 ]
                           │
                           ▼
             Tâm lý thị trường đối với USD: CỰC KỲ TÍCH CỰC
```

---

### 2.3.2 Phân tích cảm xúc dựa trên từ điển tài chính kết hợp VADER

Do mô hình FinBERT yêu cầu tài nguyên tính toán đáng kể và có thể gặp độ trễ khi xử lý hàng trăm tin tức tức thời trên máy trạm không có GPU chuyên dụng, đồ án tích hợp giải pháp kép kết hợp giữa **FinBERT** và **Bộ phân tích cảm xúc dựa trên từ điển VADER Financial Lexicon**:

Bộ từ điển tài chính chuyên biệt được mở rộng với các thuật ngữ đặc thù của Wall Street và thị trường Ngoại hối/Vàng:

| Từ khóa vĩ mô | Nhóm sắc thái | Điểm số tác động (Valence) | Ý nghĩa kinh tế |
|:---|:---:|:---:|:---|
| `hawkish` / `rate hike` / `tightening` | Bullish USD / Bearish XAU | $+3.5$ (USD) | Lãi suất tăng $\rightarrow$ Vàng giảm |
| `dovish` / `rate cut` / `easing` | Bearish USD / Bullish XAU | $-3.5$ (USD) | Cắt giảm lãi suất $\rightarrow$ Vàng tăng |
| `inflation surge` / `sticky cpi` | Bullish USD / Bearish XAU | $+2.8$ (USD) | Lạm phát dai dẳng $\rightarrow$ FED giữ lãi suất cao |
| `geopolitical tension` / `war crisis` | Safe-Haven Bullish XAU | $+4.0$ (XAU) | Chiến tranh, khủng hoảng $\rightarrow$ Mua vàng trú ẩn |
| `recession fears` / `banking crisis` | Safe-Haven Bullish XAU | $+3.2$ (XAU) | Rủi ro sụp đổ hệ thống $\rightarrow$ Mua vàng |

---

### 2.3.3 Thuật toán ánh xạ cảm xúc vĩ mô vào biến động giá Vàng (XAU/USD Sentiment Inversion)

Một trong những đóng góp học thuật quan trọng của hệ thống VQuant là **Thuật toán đảo chiều cảm xúc đối với tài sản phòng hộ**:

Phần lớn các tin tức kinh tế quốc tế phản ánh sức khỏe của nền kinh tế Mỹ và đồng USD. Nếu một tin tức mang sắc thái "Tích cực" (ví dụ: số liệu việc làm Non-Farm Payrolls tăng vọt), điều này làm đồng USD tăng giá mạnh, nhưng lại gây áp lực bán tháo cực lớn lên kim loại quý Vàng.

Thuật toán xử lý ánh xạ:

$$\text{Sentiment}_{\text{Final}}(XAU) = 
\begin{cases} 
- \text{Score}_{USD} & \text{nếu tin tức thuộc nhóm Kinh tế Mỹ (Fed, CPI, NFP, GDP, Jobs)} \\
+ \text{Score}_{Geopolitics} & \text{nếu tin tức thuộc nhóm Địa chính trị hoặc Khủng hoảng (War, Crisis, Gold Demand)} \\
0 & \text{nếu tin tức trung tính hoặc không liên quan}
\end{cases}$$

Điểm số cảm xúc tổng hợp $\text{Sentiment}_{\text{Final}} \in [-1.0, +1.0]$ sau đó được đưa vào cơ chế bù trừ xác suất (Probability Bias Injection) của Lõi AI Engine để điều chỉnh quyết định vào lệnh cuối cùng.

---

## 2.4 Nền tảng giao dịch MetaTrader 5 và cơ chế giao tiếp liên tiến trình (IPC)

### 2.4.1 MetaTrader 5 và ngôn ngữ MQL5 hướng đối tượng

**MetaTrader 5 (MT5)** là nền tảng giao dịch tài chính chuyên nghiệp tiêu chuẩn thế giới, cung cấp khả năng khớp lệnh tốc độ cao, độ trễ thấp và tích hợp môi trường lập trình **MQL5 (MetaQuotes Language 5)**.

MQL5 là ngôn ngữ lập trình bậc cao có cú pháp tương đồng với C++, hỗ trợ đầy đủ các nguyên lý Lập trình hướng đối tượng (OOP: Kế thừa, Đóng gói, Đa hình). Hệ thống Robot VQuant được thiết kế hoàn toàn theo mô hình OOP kiến trúc Module:
- `CInputs`: Đóng gói và chuẩn hóa toàn bộ tham số người dùng nhập vào.
- `CFileBridge`: Đảm nhận việc đọc/ghi dữ liệu liên tiến trình, xử lý kiểm tra tính toàn vẹn (CRC) và cơ chế quá hạn (Timeout Failsafe).
- `CFilters`: Tính toán các chỉ báo kỹ thuật trực tiếp trên đồ thị nến MT5.
- `CGridManager`: Quản lý logic tính toán ma trận lưới lệnh, xác định bước giá và điểm hòa vốn.
- `COrderManager`: Tương tác trực tiếp với máy chủ giao dịch của sàn (Trade Server), thực thi các cấu trúc `MqlTradeRequest` và xử lý mã lỗi giao dịch (`TRADE_RETCODE`).
- `CDashboard`: Giao diện đồ họa người dùng trực tiếp trên Chart nến, cho phép theo dõi tín hiệu AI và bấm nút can thiệp khẩn cấp.

---

### 2.4.2 Cơ chế giao tiếp liên tiến trình (IPC) qua Shared File Bridge

Để kết nối giữa **Python** (môi trường học máy, phân tích dữ liệu vĩ mô phong phú với TensorFlow/PyTorch) và **MetaTrader 5** (nền tảng thực thi lệnh bằng MQL5 tốc độ cao), hệ thống áp dụng cơ chế **Inter-Process Communication (IPC)** dựa trên tệp chia sẻ tốc độ cao (High-Speed Shared File Protocol).

```
   ┌────────────────────────────────┐
   │       PYTHON AI BACKEND        │
   │  - CNN-BiGRU-Attention Engine            │
   │  - FinBERT NLP Engine          │
   │  - Sentinel Service Monitor    │
   └───────────────┬────────────────┘
                   │ Ghi định kỳ mỗi chu kỳ nến H4
                   ▼
   ┌─────────────────────────────────────────────────────────┐
   │       BỘ NHỚ CHIA SẺ FILE HỆ THỐNG (MT5 COMMON FILES)   │
   │       Tệp: vc_signal_XAUUSDm.txt                        │
   │       Định dạng: TIMESTAMP,SIGNAL,CONFIDENCE            │
   │       Ví dụ: 2026-10-25 14:00:00,BUY_STRONG,0.68       │
   └─────────────────────────────────────────────────────────┘
                   │
                   │ Đọc mỗi Tick (~50 - 100 ms)
                   ▼
   ┌────────────────────────────────┐
   │        MQL5 EXPERT ADVISOR     │
   │  - FileBridge.mqh              │
   │  - Failsafe Watchdog (4h)      │
   │  - Grid Execution Engine       │
   └────────────────────────────────┘
```

**Cơ chế an toàn phòng thủ (Failsafe Timeout Mechanism):**
Một lỗ hổng chết người của các bot giao dịch tự động kết nối qua mạng là hiện tượng "mất kết nối ngầm": Nếu tiến trình Python gặp sự cố crash hoặc đứt mạng, Robot MT5 có thể tiếp tục giữ và thực thi theo một tín hiệu cũ đã lỗi thời nhiều ngày.

Hệ thống VQuant giải quyết triệt để rủi ro này bằng thuật toán Failsafe Watchdog:
- File tín hiệu luôn mang dấu thời gian (Timestamp) theo chuẩn ISO.
- Robot MQL5 mỗi khi đọc file sẽ so sánh:

$$\Delta T = T_{\text{current}} - T_{\text{signal}}$$

- Nếu $\Delta T \le 4\text{ giờ}$: Tín hiệu hợp lệ $\rightarrow$ Robot áp dụng định hướng của AI.
- Nếu $\Delta T > 4\text{ giờ}$ hoặc file không tồn tại: Robot tự động ngắt liên kết AI, kích hoạt trạng thái `AI_OFFLINE / FAILSAFE`, hiển thị cảnh báo `WAITING PYTHON` trên màn hình Dashboard và chuyển sang chế độ tự hành bảo vệ vốn độc lập.

---

---

## 2.5 Thuật toán quản lý vốn lưới ma trận (Matrix DCA) và chiến lược phòng ngừa rủi ro (Hedge)

### 2.5.1 Hạn chế của mô hình AI đơn lẻ và sự cần thiết của thuật toán quản lý vốn

Trong lĩnh vực tài chính định lượng, một ngộ nhận phổ biến là cố gắng tối ưu hóa mô hình AI để đạt độ chính xác dự đoán 70% – 80%. Thực tế nghiên cứu trên toàn thế giới chứng minh rằng: **Thị trường tài chính là một hệ thống ngẫu nhiên bán hiệu quả (Semi-strong form Efficient Market), chứa đầy sự kiện "Thiên nga đen" (Black Swan events). Không có bất kỳ mô hình học máy nào có thể dự đoán đúng hướng đi của từng cây nến với xác suất cao.**

Ngay cả khi mô hình AI đạt độ chính xác 55% – 60%, nếu hệ thống giao dịch áp dụng tỷ lệ Risk/Reward không hợp lý hoặc phương pháp quản lý vốn yếu kém, một chuỗi lệnh thua lỗ liên tiếp vẫn có thể dẫn đến việc phá sản tài khoản (Risk of Ruin).

Do đó, đồ án xây dựng chiến lược theo triết lý: **AI định hướng xu hướng vĩ mô — Thuật toán quản lý vốn lưới ma trận bảo vệ tài khoản và khai thác lợi nhuận vi mô**.

---

### 2.5.2 Nguyên lý thuật toán lưới ma trận co giãn theo ATR (ATR-Adaptive Grid DCA)

Thuật toán Dollar-Cost Averaging (DCA) truyền thống thường nhồi lệnh tại các bước giá cố định (ví dụ: cách nhau 20 pips). Nhược điểm chí tử của phương pháp bước giá cố định là: khi thị trường rơi vào cơn bão giá (biến động 200 - 300 pips do tin tức vĩ mô), bot sẽ nhồi lệnh quá dày đặc, làm cạn kiệt tiền ký quỹ (Margin Call) dẫn đến cháy tài khoản.

Hệ thống VQuant giải quyết triệt để vấn đề này bằng cách thiết kế **Cơ chế lưới co giãn động theo biến động ATR**:

#### 1. Bước giá nhồi lệnh động (Dynamic Grid Spacing)
Khoảng cách giá để mở lệnh nhồi thứ $k$ ($k \ge 1$) được xác định theo công thức:

$$\text{Spacing}_k = \text{BaseSpacing} \times \left( \frac{ATR_{14, \text{current}}}{ATR_{14, \text{baseline}}} \right) \times \gamma^{(k-1)}$$

Trong đó:
- $\text{BaseSpacing}$ là khoảng cách lưới cơ bản (mặc định: $20$ pips).
- $ATR_{14, \text{current}}$ là biên độ biến động thực tế đo được tại thời điểm đặt lệnh.
- $\gamma \ge 1.0$ là hệ số giãn nở bước giá lũy tiến (ví dụ: $\gamma = 1.15$).

Khi thị trường biến động mạnh (ATR tăng vọt), các tầng lưới tự động dãn rộng ra gấp 2 đến 3 lần, giúp tài khoản hấp thụ được các cú sốc giá mà không bị quá tải khối lượng ký quỹ.

#### 2. Quản lý khối lượng lũy tiến kiểm soát (Controlled Lot Multiplier)
Khối lượng lệnh thứ $k$ tuân theo nguyên lý:

$$\text{Lot}_k = \min \left( \text{BaseLot} \times \beta^{(k-1)}, \, \text{MaxLotLimit} \right)$$

Hệ số nhân $\beta$ được cấu hình ở mức thận trọng ($1.2 \le \beta \le 1.4$) thay vì nhân đôi kiểu Martingale kinh điển ($\beta = 2.0$), giúp giữ mức sụt giảm tài khoản (Drawdown) luôn nằm trong giới hạn kiểm soát an toàn.

#### 3. Điểm hòa vốn tổng hòa (Consolidated Break-Even Target)
Thay vì chốt lời từng lệnh lẻ tẻ, thuật toán giám sát giá hòa vốn bình quân trọng số của toàn bộ rổ lệnh (Basket of Orders):

$$P_{\text{BreakEven}} = \frac{\sum_{i=1}^{m} \text{Lot}_i \times \text{OpenPrice}_i}{\sum_{i=1}^{m} \text{Lot}_i}$$

Mức chốt lời tổng thể được dời về:

$$P_{\text{TakeProfit, Basket}} = P_{\text{BreakEven}} \pm \Delta_{\text{Target}}$$

Chỉ cần thị trường có một nhịp hồi kỹ thuật nhỏ (Pullback chiếm 25% – 35% biên độ sóng giảm), toàn bộ rổ lệnh sẽ đóng đồng loạt với tổng lợi nhuận dương.

```
       BÁN KHỐI LƯỢNG LỚN (SELL BIAS)
   ─── Lệnh 3: 0.03 Lot (Giá 2730) ───
         │ (Spacing dãn nở theo ATR)
   ─── Lệnh 2: 0.02 Lot (Giá 2720) ───
         │
   ─── Lệnh 1: 0.01 Lot (Giá 2715) ───
   ───────────────────────────────────► Giá bình quân hòa vốn dời lên cao (2724.1)
                                        Chỉ cần giá hồi về 2722 -> ĐÓNG TOÀN BỘ RỔ CÓ LÃI
```

---

### 2.5.3 Chiến lược phòng ngừa rủi ro hai chiều (Bi-Directional Hedging)

Bên cạnh thuật toán co giãn bước giá theo ATR, hệ thống VQuant tích hợp lớp phòng vệ tối hậu: **Chiến lược phòng hộ hai chiều (Hedging Mode)** nhằm triệt tiêu rủi ro tài khoản khi thị trường xuất hiện xu hướng đơn cực cực đoan (Unilateral Strong Trend):

1. **Khóa rủi ro thả nổi (Floating Drawdown Lock):**
   Khi mức sụt giảm tài khoản thả nổi (Floating DD) của rổ lệnh hiện tại chạm ngưỡng cảnh báo cấu hình (ví dụ:  \ge 25\%$), Robot tự động kích hoạt vị thế đối ứng (Hedge Order) với tổng khối lượng tương đương theo chiều ngược lại:
   \text{Lot}_{\text{Hedge}} = \left| \sum \text{Lot}_{\text{BUY}} - \sum \text{Lot}_{\text{SELL}} 
ight|
   Khi vị thế phòng hộ được xác lập, tổng mức lỗ của tài khoản sẽ bị đóng băng hoàn toàn bất kể giá tiếp tục biến động theo hướng nào.

2. **Cơ chế tháo gỡ vị thế từng phần (Gradual Unwind Mechanism):**
   Sau khi cơn bão giá đi qua và mô hình AI phát hiện tín hiệu suy kiệt xu hướng (Trend Exhaustion / Mean Reversion) trên khung H4, Robot sẽ kích hoạt quy trình tháo gỡ (Unwind) từng cặp lệnh đối nghịch có lãi, đưa trạng thái tài khoản dần trở lại vùng an toàn mà không phải chịu tổn thất cắt lỗ toàn bộ rổ lệnh.

---

## 2.6 Các chỉ số khoa học đánh giá mô hình và hiệu quả đầu tư

Nhằm đánh giá hệ thống một cách khách quan, khoa học và đáp ứng chuẩn mực nghiên cứu định lượng, đồ án sử dụng hai hệ thống chỉ số đo lường riêng biệt:

### 2.6.1 Chỉ số đánh giá mô hình học máy phân loại 3 lớp

Cho bài toán phân loại đa lớp (BUY, HOLD, SELL), từ ma trận nhầm lẫn (Confusion Matrix), các chỉ số được định nghĩa:

#### 1. Độ chính xác tổng thể (Accuracy)
Tỷ lệ số mẫu được dự đoán chính xác trên tổng số mẫu kiểm thử:

$$\text{Accuracy} = \frac{\sum_{c=1}^{3} TP_c}{N_{\text{total}}}$$

*Lưu ý học thuật:* Với bài toán 3 lớp có xác suất ngẫu nhiên là $33.33\%$, mức độ chính xác từ $36\% - 40\%$ trên chuỗi thời gian tài chính đã đại diện cho một lợi thế thống kê thực tế (Statistical Edge).

#### 2. Độ chuẩn xác (Precision)
Tỷ lệ số lần dự đoán đúng nhãn $c$ trên tổng số lần mô hình đưa ra dự đoán nhãn $c$:

$$\text{Precision}_c = \frac{TP_c}{TP_c + FP_c}$$

#### 3. Độ thu hồi (Recall)
Tỷ lệ số mẫu nhãn $c$ được mô hình tìm thấy trên tổng số mẫu thực tế thuộc nhãn $c$:

$$\text{Recall}_c = \frac{TP_c}{TP_c + FN_c}$$

#### 4. Điểm F1 trung bình điều hòa (Macro F1-Score)
Đảm bảo đánh giá công bằng giữa các lớp dữ liệu:

$$F1_c = 2 \times \frac{\text{Precision}_c \times \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

$$\text{Macro } F1 = \frac{1}{3} \sum_{c=1}^{3} F1_c$$

---

### 2.6.2 Chỉ số định lượng tài chính đánh giá hiệu quả đầu tư

Đánh giá một hệ thống giao dịch tự động không chỉ dựa vào tổng số tiền kiếm được, mà quan trọng hơn là **mức độ rủi ro phải đánh đổi để đạt được lợi nhuận đó**:

#### 1. Mức sụt giảm tài khoản tối đa (Maximum Drawdown - MDD)
Đo lường mức sụt giảm giá trị tài khoản lớn nhất từ một đỉnh cao kỷ lục (Peak) đến đáy sâu nhất (Trough) trước khi lập đỉnh mới:

$$\text{Drawdown}_t = \frac{\max_{0 \le \tau \le t}(Equity_\tau) - Equity_t}{\max_{0 \le \tau \le t}(Equity_\tau)}$$

$$MDD = \max_{t} (\text{Drawdown}_t) \times 100\%$$

Chỉ số MDD phản ánh mức độ chịu đựng rủi ro cao nhất của tài khoản. Trong hệ thống VQuant, MDD được giới hạn nghiêm ngặt dưới ngưỡng $35\%$.

#### 2. Tỷ số Sharpe (Sharpe Ratio)
Đo lường mức lợi nhuận vượt trội (Excess Return) trên một đơn vị rủi ro tổng thể:

$$\text{Sharpe Ratio} = \frac{\mathbb{E}[R_p - R_f]}{\sigma_p}$$

Trong đó:
- $R_p$ là tỷ suất sinh lời của chiến lược.
- $R_f$ là tỷ suất sinh lời phi rủi ro (Risk-free Rate, thường lấy theo lãi suất trái phiếu chính phủ Mỹ kỳ hạn ngắn).
- $\sigma_p$ là độ lệch chuẩn (Standard Deviation) của tỷ suất sinh lời chiến lược.
- Tỷ số Sharpe $> 2.0$ được coi là xuất sắc trong quản lý quỹ đầu tư định lượng.

#### 3. Tỷ số Sortino (Sortino Ratio)
Khác với Sharpe Ratio (phạt cả biến động tăng lẫn biến động giảm), Sortino Ratio chỉ đo lường rủi ro đối với biến động tiêu cực (Downside Deviation):

$$\text{Sortino Ratio} = \frac{\mathbb{E}[R_p - R_f]}{\sigma_{\text{downside}}}$$

$$\sigma_{\text{downside}} = \sqrt{\frac{1}{T} \sum_{t=1}^{T} \min(0, R_{p,t} - R_f)^2}$$

Chỉ số này phản ánh chính xác hơn hiệu quả của chiến lược vì nhà đầu tư không coi lợi nhuận tăng đột biến là một rủi ro.

#### 4. Tỷ số Calmar (Calmar Ratio)
Đo lường mối tương quan giữa lợi nhuận kép hàng năm và mức sụt giảm tối đa:

$$\text{Calmar Ratio} = \frac{\text{Annualized Compound Return}}{MDD}$$

#### 5. Hệ số sinh lời (Profit Factor - PF)
Tỷ số giữa tổng số tiền thắng và tổng số tiền thua của toàn bộ các giao dịch:

$$\text{Profit Factor} = \frac{\sum \text{Gross Profits}}{\sum |\text{Gross Losses}|}$$

Chiến lược được coi là có lãi bền vững khi $\text{Profit Factor} > 1.5$. Trong kết quả backtest của VQuant, hệ số này đạt **$2.34$**, khẳng định tính hiệu quả vượt bậc của thuật toán quản lý vốn kết hợp AI.

---

## 2.7 Kết luận chương 2

Trong chương 2, đồ án đã hệ thống hóa toàn bộ cơ sở lý thuyết và nền tảng công nghệ làm nền tảng cho việc thiết kế và hiện thực hóa hệ sinh thái VQuant:
1. Phân tích chi tiết đặc thù động học của thị trường Vàng giao ngay (XAU/USD) và phương pháp tính toán, chuẩn hóa 5 nhóm chỉ báo kỹ thuật cốt lõi (EMA, RSI, MACD, Bollinger Bands, ATR).
2. Xây dựng nền tảng toán học của mô hình học sâu đề xuất **CNN-BiGRU**, giải thích cơ chế trích xuất đặc trưng cục bộ bằng 1D-CNN và mô hình hóa chuỗi thời gian 2 chiều bằng BiGRU, kết hợp thuật toán so khớp mẫu hình chuỗi thời gian **KNN Cosine Similarity**.
3. Thiết lập phương pháp phân tích cảm xúc tin tức vĩ mô dựa trên kiến trúc Transformer **FinBERT** và từ điển **VADER**, cùng thuật toán đảo chiều cảm xúc đối với tài sản phòng hộ XAU/USD.
4. Trình bày nguyên lý thuật toán giao dịch lưới ma trận co giãn động (**Adaptive Grid DCA**) dựa trên ATR và cơ chế quản lý vốn kiểm soát rủi ro.
5. Làm rõ cơ chế giao tiếp liên tiến trình (**IPC Shared File Bridge**) với thuật toán Failsafe Timeout giữa Python và MetaTrader 5.
6. Xác lập đầy đủ hệ thống các chỉ số đánh giá khoa học cả về mặt Học máy (Accuracy, Precision, Recall, Macro F1) và Tài chính định lượng (Max Drawdown, Sharpe, Sortino, Calmar, Profit Factor).

Toàn bộ các cơ sở lý thuyết và công nghệ trên sẽ là căn cứ trực tiếp để thiết kế kiến trúc chi tiết của hệ thống trong **Chương 3**.
