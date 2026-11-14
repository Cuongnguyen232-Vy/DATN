# CHƯƠNG 1. TỔNG QUAN VỀ BÀI TOÁN DỰ ĐOÁN XU HƯỚNG VÀ GIAO DỊCH TỰ ĐỘNG TRÊN THỊ TRƯỜNG TÀI CHÍNH

*Trong chương đầu tiên, đồ án sẽ trình bày bối cảnh thực tiễn của bài toán giao dịch tài chính tự động, phân tích các phương pháp tiếp cận từ truyền thống đến hiện đại cùng những ưu nhược điểm tương ứng. Tiếp đó, chương này làm rõ các thách thức kỹ thuật cốt lõi cần giải quyết khi xây dựng một hệ thống giao dịch tự động thông minh. Cuối cùng, đồ án xác định rõ ràng mục tiêu tổng quát, các nhiệm vụ cụ thể cần hoàn thành và tóm tắt cấu trúc định hướng cho toàn bộ đồ án.*

---

## 1.1 Giới thiệu bài toán

Sự bùng nổ của cuộc Cách mạng công nghiệp lần thứ tư (Industry 4.0) trong thập kỷ qua đã thúc đẩy quá trình chuyển đổi số toàn diện trong ngành tài chính (FinTech). Các thị trường tài chính toàn cầu — đặc biệt là thị trường ngoại hối (Forex) và thị trường kim loại quý (tiêu biểu là vàng giao ngay XAU/USD) — hoạt động liên tục 24 giờ mỗi ngày với khối lượng thanh khoản lên tới hàng nghìn tỷ USD. Đặc tính của thị trường này là sản sinh ra một lượng dữ liệu giao dịch khổng lồ theo thời gian thực (Big Data), trong đó các biến động giá cả diễn ra liên tục từng giây và chịu tác động đa chiều từ kinh tế vĩ mô, địa chính trị cho đến tâm lý thị trường [1].

Tại Việt Nam, làn sóng chuyển đổi số tài chính đang phát triển mạnh mẽ. Số lượng nhà đầu tư cá nhân tham gia vào các thị trường phái sinh, tài sản số và giao dịch tài chính quốc tế tăng trưởng vượt bậc. Đồng thời, khung pháp lý trong nước đang có những bước chuyển mình mang tính bước ngoặt nhằm chính quy hóa các hoạt động tài chính công nghệ, tiêu biểu như Chiến lược quốc gia về Blockchain đến năm 2030 của Chính phủ và Dự thảo Luật Công nghiệp công nghệ số [2]. Bối cảnh mới này đặt ra một yêu cầu cấp thiết: thị trường tài chính cần sự chuyên nghiệp hóa và chuẩn mực hóa công nghệ, nơi các quyết định giao dịch dựa trên cảm tính cá nhân dần phải nhường chỗ cho các phương pháp phân tích định lượng (Quantitative Trading) và giao dịch tự động dựa trên dữ liệu (Algorithmic Trading) [3].

Tuy nhiên, bài toán đầu tư và giao dịch trên thị trường tài chính nói chung và cặp tỷ giá Vàng/USD (XAU/USD) nói riêng luôn là một trong những bài toán phức tạp bậc nhất đối với các kỹ sư và nhà đầu tư:
- **Rào cản tâm lý con người:** Các nghiên cứu về tài chính hành vi đã chỉ ra rằng, hơn 90% tổn thất của các nhà đầu tư cá nhân xuất phát từ sự chi phối của tâm lý: nỗi sợ hãi khi thị trường sụt giảm, lòng tham khi thị trường tăng nóng (hội chứng FOMO), hoặc sự thiếu kỷ luật trong việc cắt lỗ [4].
- **Sức ép về tốc độ và khả năng xử lý thông tin:** Thị trường tài chính hiện đại biến động tính bằng mili-giây. Bộ não con người không thể theo dõi liên tục hàng nghìn biến động giá, đọc hiểu tức thì các bản tin kinh tế quốc tế vừa được công bố, và đưa ra quyết định đặt lệnh chuẩn xác 24/7 mà không gặp sai sót do mệt mỏi.
- **Tính chất phi tuyến và nhạy cảm vĩ mô:** Biến động của giá Vàng (XAU/USD) là chuỗi dữ liệu thời gian phi tuyến tính cao độ, vừa chịu sự điều tiết của các quy luật kỹ thuật trong ngắn hạn, vừa phản ứng dữ dội trước các tin tức kinh tế vĩ mô đột xuất (như lãi suất của Cục Dự trữ Liên bang Mỹ - FED, số liệu việc làm Non-Farm Payrolls, chỉ số lạm phát CPI).

Xuất phát từ những thực tiễn trên, bài toán trọng tâm được đặt ra cho đồ án là: **Nghiên cứu ứng dụng các mô hình học máy (Machine Learning) và học sâu (Deep Learning) để dự báo xu hướng thị trường tài chính; đồng thời tích hợp màng lọc tin tức kinh tế vĩ mô tự động (News Filter) và phát triển một hệ thống giao dịch tự động hoàn chỉnh trên nền tảng MetaTrader 5 (MT5)**. Hệ thống hướng đến mục tiêu loại bỏ hoàn toàn yếu tố tâm lý con người, tối ưu hóa tỷ suất sinh lời và kiểm soát rủi ro tài khoản một cách nghiêm ngặt.

---

## 1.2 Phương pháp giải quyết bài toán

Để giải quyết bài toán dự báo và giao dịch trên thị trường tài chính, trong lịch sử và thực tiễn đã tồn tại nhiều trường phái và phương pháp tiếp cận khác nhau. Các phương pháp có thể phân chia thành hai nhóm chính: phương pháp truyền thống và phương pháp hiện đại dựa trên trí tuệ nhân tạo.

### 1.2.1 Phương pháp truyền thống: Phân tích kỹ thuật cổ điển

Phương pháp phân tích kỹ thuật (Technical Analysis) là cách tiếp cận phổ biến nhất trong giới giao dịch tài chính cổ điển. Phương pháp này dựa trên giả định rằng mọi thông tin thị trường đều được phản ánh vào đường giá, và lịch sử giá có xu hướng lặp lại. Các công cụ truyền thống thường được áp dụng gồm:
- **Chỉ báo động lượng (Momentum Indicators):** 
  - Chỉ số sức mạnh tương đối (*Relative Strength Index - RSI*): Dùng để xác định trạng thái quá mua (Overbought khi RSI > 70) hoặc quá bán (Oversold khi RSI < 30) nhằm tìm kiếm điểm đảo chiều xu hướng.
  - Đường trung bình động hội tụ phân kỳ (*Moving Average Convergence Divergence - MACD*): Dựa trên độ lệch giữa hai đường trung bình động hàm mũ EMA(12) và EMA(26) cùng đường tín hiệu EMA(9) để xác định xu hướng và động lượng của thị trường.
- **Chỉ báo đo lường biến động (Volatility Indicators):**
  - Dải Bollinger Bands: Đo lường độ co giãn biến động dựa trên độ lệch chuẩn (Standard Deviation) xung quanh đường trung bình động SMA(20).
  - Độ biến động thực tế trung bình (*Average True Range - ATR*): Đo lường biên độ dao động giá trung bình trong n chu kỳ nến, là cơ sở then chốt để xác định khoảng cách đặt cắt lỗ (Stop Loss) hoặc bước giá nhồi lệnh.

**Hạn chế của phương pháp truyền thống:**
Mặc dù trực quan và dễ lập trình thành các quy tắc cứng (rule-based), các chỉ báo kỹ thuật truyền thống là các chỉ báo trễ (lagging indicators). Khi thị trường xuất hiện xu hướng rõ ràng (Trending), các chỉ báo có thể mang lại hiệu quả tốt; tuy nhiên trong các giai đoạn thị trường tích lũy đi ngang (Sideway) hoặc bị nhiễu do tin tức, các chỉ báo này liên tục phát tín hiệu giả (whipsaws), dẫn đến thua lỗ nặng nề. Hơn nữa, các hệ thống quy tắc cố định không có khả năng thích nghi linh hoạt khi cấu trúc thị trường thay đổi.

### 1.2.2 Phương pháp phân tích cơ bản và phân tích cảm xúc tin tức

Trường phái phân tích cơ bản (Fundamental Analysis) tập trung vào giá trị nội tại của tài sản dựa trên các dữ liệu kinh tế vĩ mô. Đối với kim loại quý XAU/USD, giá vàng tỷ lệ nghịch sâu sắc với sức mạnh đồng USD (chỉ số DXY) và lợi suất trái phiếu chính phủ Mỹ. Khi nền kinh tế Mỹ công bố các chỉ số vượt kỳ vọng (việc làm tăng, GDP tăng, lạm phát cao khiến lãi suất duy trì ở mức cao), đồng USD mạnh lên và giá vàng có xu hướng giảm sâu, và ngược lại.

Trong thời đại số, các dữ liệu kinh tế này được theo dõi thông qua lịch kinh tế quốc tế (như ForexFactory, Bloomberg, Reuters). Tuy nhiên, việc con người tự phân tích hàng loạt dòng tin tức và tiêu đề báo chí tốn nhiều thời gian và dễ mang tính định tính. Ứng dụng công nghệ Xử lý ngôn ngữ tự nhiên (NLP) thông qua các mô hình phân tích cảm xúc (Sentiment Analysis) chuyên sâu cho tài chính (như FinBERT, VADER) đã mở ra giải pháp phân tích tự động sắc thái tin tức vĩ mô để hỗ trợ định hướng thị trường theo thời gian thực [5].

### 1.2.3 Phương pháp hiện đại: Học máy và Học sâu kết hợp hệ thống lai

Trước những hạn chế của phương pháp truyền thống, hướng tiếp cận hiện đại tập trung vào việc áp dụng Trí tuệ nhân tạo (AI), Học máy (Machine Learning) và Học sâu (Deep Learning) vào phân tích chuỗi thời gian tài chính:
- **Mạng nơ-ron hồi quy tiên tiến kết hợp Cơ chế chú ý (LSTM, BiGRU, Multi-Head Attention):** Khắc phục triệt để hiện tượng triệt tiêu đạo hàm (vanishing gradient) của RNN truyền thống, có khả năng ghi nhớ thông tin dài hạn và nhận diện các chuỗi phụ thuộc thời gian phức tạp trong dữ liệu nến H4, H1. Đặc biệt, kiến trúc BiGRU (Bidirectional Gated Recurrent Unit) cho phép xử lý dữ liệu theo hai chiều ngữ cảnh quá khứ - tương lai trong chuỗi trượt, kết hợp với mạng tích chập 1D (Conv1D) để trích xuất đặc trưng hình thái giá cục bộ và cơ chế Chú ý Đa đầu (Multi-Head Self-Attention) giúp mô hình tập trung trọng số vào các bước nến mang tính bước ngoặt.
- **Kỹ thuật so khớp mẫu hình chuỗi thời gian (KNN Pattern Matcher):** So sánh hình dạng của chuỗi nến hiện tại với hàng nghìn kịch bản nến trong lịch sử bằng khoảng cách Cosine hoặc Euclidean, nhằm đo lường xác suất lịch sử lặp lại dưới góc nhìn định lượng.
- **Mô hình lai thông minh (Hybrid Intelligence Trading System):** Thay vì phụ thuộc vào một thuật toán đơn lẻ, giải pháp tối ưu là xây dựng một kiến trúc đa tầng:
  1. *Tầng dự báo vĩ mô:* Mô hình Deep Learning (CNN-BiGRU-Attention) kết hợp KNN Pattern Matcher dự đoán xu hướng chủ đạo (Regime) trên khung thời gian lớn (H4).
  2. *Tầng màng lọc rủi ro (Risk Shield):* Module NLP phân tích tin tức thời gian thực và lịch kinh tế ForexFactory, tự động kích hoạt chế độ "đóng băng" hệ thống khi có tin tức High Impact ("Tin đỏ").
  3. *Tầng thực thi vi mô (Execution Engine):* Robot Expert Advisor (EA) viết bằng MQL5 chạy trên MetaTrader 5, áp dụng chiến thuật quản lý vốn lưới ma trận (Matrix DCA) với bước giá co giãn động theo biến động ATR, nhận tín hiệu chỉ đạo từ tầng AI qua cơ chế giao tiếp liên tiến trình (IPC).

**Kết luận lựa chọn:** Từ việc so sánh, phân tích các giải pháp hiện hữu, đồ án lựa chọn phương pháp **Mô hình lai thông minh kết hợp Học sâu (CNN-BiGRU-Attention), Màng lọc tin tức NLP và Robot giao dịch tự động MQL5 trên MetaTrader 5** làm hướng giải quyết trọng tâm. Phương pháp này tận dụng được độ chính xác trong dự báo xu hướng của AI, sự an toàn của màng lọc rủi ro vĩ mô, và tốc độ thực thi lệnh tính bằng mili-giây của nền tảng MetaTrader 5.

---

## 1.3 Thách thức gặp phải khi giải quyết bài toán

Quá trình xây dựng một hệ thống giao dịch tự động tích hợp trí tuệ nhân tạo trên thị trường tài chính thực tế phải đối mặt với nhiều thách thức kỹ thuật mang tính đặc thù:

1. **Đặc tính dữ liệu chuỗi thời gian tài chính có độ nhiễu cao (High Noise & Non-stationarity):**
   Dữ liệu giá tài chính không tuân theo phân phối chuẩn tĩnh mà biến động liên tục theo thời gian (regime changes). Tỷ lệ tín hiệu trên nhiễu (Signal-to-Noise Ratio) của dữ liệu giá rất thấp. Nếu sử dụng các mô hình học máy quá cồng kềnh với nhiều tham số, mô hình sẽ nhanh chóng rơi vào trạng thái học vẹt (overfitting) — hoạt động rất tốt trên tập huấn luyện quá khứ nhưng thất bại hoàn toàn khi dự báo thị trường thực tế trong tương lai. Do đó, bài toán đặt ra là phải thiết kế kiến trúc mạng nơ-ron gọn nhẹ (compact architecture), sử dụng chuẩn hóa Batch Normalization và cơ chế gán nhãn thích nghi theo độ biến động thị trường (Adaptive ATR Labeling).

2. **Rủi ro biến động cực đoan do tin tức kinh tế vĩ mô (Flash Crashes & News Shocks):**
   Thị trường Vàng (XAU/USD) thường xuyên xuất hiện các đợt biến động giá đột ngột hàng chục đến hàng trăm USD chỉ trong vài phút khi các báo cáo kinh tế Mỹ được công bố. Trong các thời điểm này, spread (chênh lệch giá mua - bán) của các sàn môi giới bị giãn rộng, xảy ra hiện tượng trượt giá (slippage) và thanh khoản suy giảm nghiêm trọng. Mọi mô hình thuần kỹ thuật đều trở nên vô hiệu trước các cú sốc tin tức này. Vì vậy, hệ thống bắt buộc phải sở hữu một màng lọc tin tức tự động chạy ngầm 24/7 để cảnh báo và tự động vô hiệu hóa hoạt động mở lệnh trước và sau các thời điểm nhạy cảm.

3. **Thách thức về tích hợp liên nền tảng (Cross-Platform Integration & Low Latency IPC):**
   Hệ sinh thái phân tích dữ liệu và học máy mạnh nhất hiện nay được xây dựng trên ngôn ngữ Python (TensorFlow, PyTorch, Pandas), trong khi nền tảng giao dịch trực tiếp có độ trễ thấp và ổn định nhất thế giới là MetaTrader 5 (hoạt động bằng ngôn ngữ C++ tùy biến — MQL5). Hai môi trường này hoàn toàn độc lập về không gian bộ nhớ. Thách thức lớn là phải thiết kế một cơ chế giao tiếp liên tiến trình (Inter-Process Communication - IPC) nhẹ, ổn định, không xung đột truy cập file, và có cơ chế dự phòng an toàn (Failsafe Mechanism): khi tiến trình Python dừng hoạt động, Robot MT5 phải tự động nhận biết để chuyển về chế độ phòng thủ, tránh treo lệnh hoặc xử lý sai lệch.

4. **Bài toán quản trị vốn và kiểm soát sụt giảm tài khoản (Drawdown Management):**
   Không có bất kỳ mô hình dự đoán AI nào có thể đạt độ chính xác 100% trong thị trường tài chính. Một hệ thống giao dịch muốn tồn tại lâu dài không thể chỉ dựa vào xác suất dự đoán mà phụ thuộc phần lớn vào thuật toán quản trị vốn. Việc áp dụng chiến thuật nhồi lệnh DCA (Dollar Cost Averaging) nếu không kiểm soát tốt sẽ tiềm ẩn nguy cơ "cháy tài khoản". Do đó, thuật toán thực thi cần tích hợp các lớp bảo vệ: bước giá lưới tự thích nghi theo ATR, giới hạn số tầng lệnh tối đa (Order Cap), tỷ lệ rủi ro tối đa trên mỗi chu kỳ, và tính năng can thiệp trực tiếp qua bảng điều khiển biểu đồ cũng như điều khiển từ xa qua Telegram.

---

## 1.4 Mục tiêu đồ án

Mục tiêu chung của đồ án là: **Nghiên cứu, thiết kế và phát triển thành công một hệ sinh thái giao dịch tự động hoàn chỉnh (Autonomous Algorithmic Trading Ecosystem) cho cặp tỷ giá XAU/USD; kết hợp mô hình học sâu CNN-BiGRU-Attention và KNN Pattern Matcher dự báo xu hướng, màng lọc tin tức vĩ mô NLP thời gian thực, Robot Expert Advisor thực thi chiến thuật lưới thích nghi trên MetaTrader 5, và kênh giám sát tương tác từ xa qua Telegram.**

Để hiện thực hóa mục tiêu chung, đồ án đề ra các nhiệm vụ cụ thể cần hoàn thành như sau:

1. **Nghiên cứu cơ sở lý thuyết:**
   - Khảo sát các chỉ báo kỹ thuật tài chính cốt lõi (EMA, ATR, RSI, Bollinger Bands, Stochastic, ROC).
   - Nghiên cứu cơ sở toán học và cơ chế lan truyền ngược của mạng nơ-ron tích chập (CNN), mạng hồi quy (BiGRU) và cơ chế Chú ý Đa đầu (Multi-Head Self-Attention) trong bài toán phân loại xu hướng chuỗi thời gian.
   - Nghiên cứu các phương pháp Xử lý ngôn ngữ tự nhiên (NLP) phân tích sắc thái văn bản tài chính (FinBERT, VADER) và cơ chế cào dữ liệu tin tức vĩ mô từ ForexFactory.
   - Tìm hiểu kiến trúc nền tảng MetaTrader 5, ngôn ngữ lập trình hướng đối tượng MQL5, và các phương thức giao tiếp liên tiến trình (IPC).

2. **Thu thập, xử lý và chuẩn hóa dữ liệu:**
   - Thu thập tập dữ liệu nến lịch sử đa khung thời gian (H4, H1, M15) của cặp XAU/USD từ sàn giao dịch Exness MT5.
   - Xây dựng quy trình làm sạch dữ liệu, xử lý nhiễu, chuẩn hóa đặc trưng (MinMaxScaler) với 24 đặc trưng kỹ thuật nhân quả, loại bỏ hoàn toàn rò rỉ dữ liệu (Data Leakage).
   - Áp dụng phương pháp gán nhãn thích nghi theo biến động thực tế (Adaptive ATR Labeling) nhằm khắc phục hiện tượng mất cân bằng dữ liệu giữa các trạng thái BUY, SELL và HOLD.

3. **Xây dựng và tối ưu hóa các module hệ thống:**
   - Xây dựng mô hình học sâu lai CNN-BiGRU-Attention kết hợp bộ so khớp mẫu hình KNN Pattern Matcher trên Python, huấn luyện và đánh giá trên tập dữ liệu kiểm thử độc lập thông qua kỹ thuật Time-Series Cross-Validation (Walk-Forward Validation).
   - Phát triển Module Sentinel 24/7 tự động cào tin tức kinh tế, phân tích cảm xúc tin tức tài chính và phân loại mức độ rủi ro ("Tin đỏ", "Tin cam", "Tin vàng").
   - Thiết lập kênh cầu nối IPC truyền tải dữ liệu tín hiệu và độ tin cậy thời gian thực từ Python sang thư mục dùng chung của MetaTrader 5.

4. **Phát triển Robot giao dịch trên MetaTrader 5 (MQL5):**
   - Lập trình Expert Advisor hướng đối tượng (OOP) theo cấu trúc module rõ ràng (Bridge, Strategy, OrderManager, RiskManager, UI Dashboard).
   - Triển khai chiến lược giao dịch lưới ma trận Hedge DCA kết hợp bộ lọc xu hướng AI.
   - Xây dựng giao diện bảng điều khiển trực quan (Dashboard) hiển thị đầy đủ thông số trạng thái thời gian thực và các nút bấm tương tác trực tiếp trên biểu đồ (Đổi chế độ giao dịch, Bật/Tắt AI Filter, Đóng toàn bộ lệnh khẩn cấp).

5. **Xây dựng kênh giám sát và cảnh báo từ xa qua Telegram:**
   - Phát triển Telegram Bot tự động gửi thông báo khi có tín hiệu AI mới, cảnh báo tin tức đỏ sắp xuất hiện, và báo cáo tổng kết lãi/lỗ (PnL) định kỳ.

6. **Thử nghiệm, đánh giá hiệu năng và kiểm chứng thực tế:**
   - Thực hiện kiểm thử quá khứ (Backtesting) trên dữ liệu lịch sử nhiều năm để đánh giá các chỉ số định lượng: Lợi nhuận ròng (Net Profit), Tỷ lệ thắng (Win Rate), Tỷ số Sharpe, Tỷ số Sortino, Tỷ số Calmar, Hệ số lợi nhuận (Profit Factor) và Mức sụt giảm tài khoản tối đa (Max Drawdown).
   - Triển khai vận hành thực tế 24/7 trên tài khoản Demo sàn Exness để kiểm chứng độ ổn định, khả năng chịu lỗi và tính tự động hoàn toàn của hệ thống.

---

## 1.5 Kết luận chương 1

Trong Chương 1, đồ án đã tổng hợp toàn diện bối cảnh thực tiễn của bài toán giao dịch tài chính tự động trong kỷ nguyên số hóa; phân tích ưu nhược điểm của các phương pháp phân tích kỹ thuật truyền thống, phân tích cơ bản và khẳng định tính vượt trội của phương pháp tiếp cận hiện đại kết hợp Trí tuệ nhân tạo. Đồ án cũng đã nhận diện rõ 4 thách thức kỹ thuật cốt lõi cần giải quyết và thiết lập hệ thống mục tiêu, nhiệm vụ chi tiết cần đạt được.

Dựa trên các mục tiêu đã đề ra, nội dung của **Chương 2** tiếp theo sẽ đi sâu vào **Cơ sở kiến thức**, trình bày chi tiết nền tảng lý thuyết toán học của các mô hình học sâu CNN-BiGRU-Attention, thuật toán so khớp mẫu hình KNN, lý thuyết phân tích cảm xúc NLP FinBERT, cấu trúc nền tảng MetaTrader 5 (MQL5) và nguyên lý quản lý vốn ma trận DCA lưới thích nghi kết hợp chiến lược Hedge.
