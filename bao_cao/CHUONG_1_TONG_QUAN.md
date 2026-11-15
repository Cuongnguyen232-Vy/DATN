# CHƯƠNG 1. TỔNG QUAN VỀ BÀI TOÁN DỰ ĐOÁN XU HƯỚNG VÀ GIAO DỊCH TỰ ĐỘNG TRÊN THỊ TRƯỜNG TÀI CHÍNH

*Chương 1 trình bày bối cảnh thực tiễn của bài toán giao dịch tài chính tự động trên thị trường vàng (XAU/USD), phân tích ưu nhược điểm của các phương pháp tiếp cận từ truyền thống đến hiện đại. Tiếp đó, chương này làm rõ các thách thức kỹ thuật cốt lõi, xác định mục tiêu nghiên cứu và tóm tắt bố cục 3 chương của đồ án.*

---

## 1.1 Giới thiệu bài toán

Sự phát triển mạnh mẽ của cuộc Cách mạng công nghiệp lần thứ tư đã thúc đẩy làn sóng chuyển đổi số trong lĩnh vực công nghệ tài chính (FinTech). Thị trường ngoại hối (Forex) và kim loại quý — đặc biệt là vàng giao ngay (XAU/USD) — hoạt động liên tục 24/5 với thanh khoản hàng nghìn tỷ USD mỗi ngày, tạo ra khối lượng dữ liệu chuỗi thời gian khổng lồ theo thời gian thực [1]. Tại Việt Nam, sự tham gia ngày càng lớn của các nhà đầu tư cá nhân cùng các định hướng chính quy hóa thị trường tài chính số đặt ra yêu cầu cấp thiết về việc ứng dụng công nghệ và phân tích định lượng vào hoạt động đầu tư [2], [3].

Tuy nhiên, việc giao dịch thủ công trên thị trường XAU/USD đối mặt với nhiều rào cản nghiêm trọng:
- **Chi phối bởi tâm lý con người:** Hơn 90% tổn thất của nhà đầu tư cá nhân bắt nguồn từ yếu tố tâm lý như sợ hãi, tham lam (FOMO) hoặc thiếu kỷ luật khi cắt lỗ [4].
- **Hạn chế về tốc độ và sức bền:** Thị trường biến động từng mili-giây, con người không thể liên tục theo dõi bảng điện tử 24/5 và phản ứng tức thì trước các biến động giá.
- **Tính phi tuyến và nhạy cảm vĩ mô:** Giá vàng vừa tuân theo các quy luật kỹ thuật, vừa phản ứng dữ dội trước các tin tức kinh tế vĩ mô đột xuất của Mỹ (như lãi suất FED, CPI, Non-Farm Payrolls).

Xuất phát từ thực tiễn trên, đề tài được xác định là: **"Nghiên cứu mô hình học máy trong dự đoán xu hướng thị trường tài chính và phát triển hệ thống giao dịch tự động"**. Đồ án tập trung nghiên cứu giải pháp kết hợp giữa Trí tuệ nhân tạo (AI) dự báo xu hướng, màng lọc tin tức (NLP) phòng ngừa rủi ro và Robot giao dịch tự động (MQL5) trên nền tảng MetaTrader 5 nhằm loại bỏ yếu tố tâm lý và tối ưu hóa hiệu quả đầu tư.

---

## 1.2 Phương pháp giải quyết bài toán

### 1.2.1 Phương pháp truyền thống: Phân tích kỹ thuật cổ điển
Phân tích kỹ thuật (Technical Analysis) dựa trên giả định lịch sử giá có xu hướng lặp lại, sử dụng các chỉ báo toán học để xây dựng quy tắc giao dịch (Rule-based):
- *Chỉ báo động lượng:* RSI xác định vùng quá mua/quá bán; MACD nhận diện xung lượng xu hướng; Stochastic bắt nhịp đảo chiều ngắn hạn.
- *Chỉ báo xu hướng và biến động:* Đường trung bình động hàm mũ (EMA 20, EMA 50) xác định hướng đi của giá; Bollinger Bands và Average True Range (ATR) đo lường biên độ dao động thị trường.

*Hạn chế:* Các chỉ báo kỹ thuật bản chất là chỉ báo trễ (Lagging Indicators). Khi thị trường đi ngang (Sideway) hoặc chịu tác động của tin tức, chúng thường phát tín hiệu giả (Whipsaws), dẫn đến thua lỗ liên tiếp do thiếu khả năng tự thích nghi.

### 1.2.2 Phương pháp phân tích cơ bản và phân tích cảm xúc tin tức
Phân tích cơ bản đánh giá giá trị nội tại dựa trên các chỉ số vĩ mô (lãi suất, lạm phát, việc làm). Tuy nhiên, việc con người tự đọc và phân tích tin tức thường chậm trễ. Ứng dụng Xử lý ngôn ngữ tự nhiên (NLP) với các mô hình chuyên sâu tài chính như FinBERT và VADER cho phép tự động định lượng sắc thái tin tức thành điểm số cảm xúc (Sentiment Score $\in [-1.0, +1.0]$) theo thời gian thực [5].

### 1.2.3 Phương pháp hiện đại: Học sâu và Hệ thống lai thông minh
Khắc phục nhược điểm của phương pháp truyền thống, hướng tiếp cận hiện đại ứng dụng Học sâu (Deep Learning) và Hệ thống lai (Hybrid System):
- **Mô hình học sâu CNN-BiGRU-Attention:** Khối 1D-CNN trích xuất mẫu hình nến cục bộ; Bidirectional GRU nắm bắt ngữ cảnh chuỗi thời gian 2 chiều; cơ chế Multi-Head Self-Attention tập trung trọng số vào các nến biến động bước ngoặt.
- **So khớp mẫu hình (Pattern Matcher):** Dùng độ đo Cosine Similarity tìm kiếm các chuỗi nến lịch sử có hình thái tương đồng nhất để bổ trợ xác suất dự đoán.
- **Kiến trúc hệ thống lai đa tầng:** Tầng AI Python chịu trách nhiệm phân tích dự báo và lọc tin vĩ mô; tầng MQL5 trên MetaTrader 5 chịu trách nhiệm khớp lệnh vi mô và quản trị vốn lưới DCA co giãn theo ATR.

### Bảng 1.1: So sánh phương pháp truyền thống và hệ thống định lượng AI đề xuất

| Tiêu chí | Giao dịch truyền thống (Rule-based EA) | Hệ thống định lượng AI (VQuant đề xuất) |
| :--- | :--- | :--- |
| **Cơ chế ra quyết định** | Dựa trên ngưỡng cố định cứng nhắc (RSI > 70) | Mô hình học sâu phi tuyến tính đa biến (20 đặc trưng + Attention) |
| **Khả năng thích ứng** | Cố định, dễ lỗi thời khi thị trường đổi pha | Tự động học quy luật từ dữ liệu chuỗi thời gian lớn |
| **Độ trễ tín hiệu** | Chỉ báo trễ, nhiều tín hiệu giả khi Sideway | Kết hợp 1D-CNN và BiGRU phát hiện sớm biến động |
| **Phản ứng tin tức** | Không đọc được tin, dễ cháy tài khoản do bão giá | Màng lọc tin tức NLP tự động kích hoạt Circuit Breaker |
| **Quản trị vốn** | Cắt lỗ cố định hoặc Martingale nhân đôi rủi ro | Lưới DCA co giãn theo ATR kết hợp khóa phòng hộ (Hedging) |
| **Tính kỷ luật** | Dễ bị con người can thiệp cảm tính | Tự động hóa 100%, có giám sát cảnh báo từ xa qua Telegram |

**Kết luận:** Đồ án lựa chọn phương pháp **Mô hình lai thông minh kết hợp Học sâu (CNN-BiGRU-Attention), Màng lọc tin tức NLP và Robot giao dịch MQL5 trên MetaTrader 5** làm giải pháp trọng tâm.

---

## 1.3 Thách thức gặp phải khi giải quyết bài toán

Quá trình xây dựng hệ thống phải giải quyết 4 thách thức kỹ thuật cốt lõi:
1. **Nhiễu dữ liệu chuỗi thời gian và hiện tượng quá khớp (Overfitting):** Tỷ lệ tín hiệu trên nhiễu của giá tài chính rất thấp. Mạng nơ-ron cần được thiết kế gọn nhẹ (Compact), sử dụng Dropout, Batch Normalization và cơ chế gán nhãn thích nghi theo biến động (Adaptive ATR Labeling) để tránh học vẹt.
2. **Biến động cực đoan do tin tức vĩ mô (News Shocks & Slippage):** Các thời điểm ra tin đỏ (NFP, CPI, FED) thường làm giãn spread và trượt giá nghiêm trọng. Hệ thống bắt buộc phải có màng lọc tin tức tự động đóng băng giao dịch trước và sau tin tức.
3. **Tích hợp liên nền tảng với độ trễ thấp (Cross-Platform IPC):** Kết nối luồng dữ liệu giữa môi trường phân tích Python và nền tảng thực thi MetaTrader 5 (MQL5) đòi hỏi cơ chế giao tiếp liên tiến trình (IPC) ổn định, nhẹ và có cơ chế dự phòng an toàn (Failsafe).
4. **Quản trị vốn và kiểm soát sụt giảm tài khoản (Drawdown Management):** Chiến lược nhồi lệnh nếu không kiểm soát sẽ gây rủi ro lớn. Thuật toán thực thi cần có bước giá co giãn động theo biến động ATR, giới hạn số tầng lệnh và cơ chế phòng hộ hai chiều (Hedging).

---

## 1.4 Mục tiêu của đồ án

### 1.4.1 Mục tiêu tổng quát
Nghiên cứu, thiết kế và phát triển thành công một **Hệ thống giao dịch tự động định lượng (VQuant)** cho cặp tỷ giá XAU/USD; kết hợp mô hình học sâu CNN-BiGRU-Attention dự báo xu hướng, màng lọc tin tức NLP thời gian thực, Robot Expert Advisor thực thi lưới DCA thích nghi trên MetaTrader 5 và kênh cảnh báo từ xa qua Telegram.

### 1.4.2 Nhiệm vụ nghiên cứu cụ thể
1. **Nghiên cứu cơ sở lý thuyết:** Khảo sát các chỉ báo kỹ thuật, cơ sở toán học của CNN, BiGRU, Multi-Head Attention, NLP FinBERT và ngôn ngữ MQL5.
2. **Thu thập và tiền xử lý dữ liệu:** Thu thập dữ liệu nến lịch sử H4 XAU/USD, trích xuất 20 đặc trưng kỹ thuật và áp dụng gán nhãn thích nghi Adaptive ATR.
3. **Xây dựng Lõi AI Engine (Python):** Huấn luyện mô hình CNN-BiGRU-Attention, tích hợp bộ so khớp mẫu hình KNN và module lọc tin tức ForexFactory.
4. **Phát triển Robot giao dịch trên MetaTrader 5 (MQL5):** Xây dựng Expert Advisor quản trị rổ lệnh DCA thích nghi theo ATR, cơ chế khóa Hedging và giao diện Dashboard trực quan.
5. **Tích hợp Telegram Bot:** Tự động gửi cảnh báo tín hiệu, biến động tin tức và báo cáo lãi/lỗ (PnL) định kỳ.
6. **Kiểm thử và đánh giá hiệu năng:** Thực hiện Backtesting trên dữ liệu lịch sử và chạy thử nghiệm thực tế trên tài khoản Demo sàn Exness để đánh giá Win-rate, Drawdown, Profit Factor.

---

## 1.5 Bố cục của khóa luận tốt nghiệp

Khóa luận được kết cấu tinh gọn trong **3 chương**:

- **Chương 1: Tổng quan về bài toán dự đoán xu hướng và giao dịch tự động trên thị trường tài chính**
  Trình bày bối cảnh, phân tích so sánh các phương pháp tiếp cận, nêu rõ 4 thách thức kỹ thuật và xác định mục tiêu, nhiệm vụ nghiên cứu.
- **Chương 2: Cơ sở lý thuyết và Công nghệ áp dụng**
  Trình bày cơ sở toán học của các chỉ báo phân tích kỹ thuật, kiến trúc mô hình học sâu đề xuất (CNN-BiGRU-Attention), thuật toán so khớp mẫu hình Cosine Similarity, mô hình phân tích cảm xúc NLP FinBERT và ngôn ngữ lập trình MQL5 trên MetaTrader 5.
- **Chương 3: Thiết kế, Cài đặt thực nghiệm và Đánh giá hệ thống giao dịch tự động**
  Trình bày kiến trúc hệ thống lai (Hybrid System), thiết kế chi tiết các phân hệ (Lõi AI Python, Robot MT5, Telegram Bot), kết quả thực nghiệm huấn luyện, kết quả kiểm thử định lượng (Backtesting), phân tích hiệu quả quản trị rủi ro và kết luận hướng phát triển đề tài.

---

## 1.6 Kết luận chương 1

Chương 1 đã tổng quan bối cảnh bài toán giao dịch tự động trên thị trường tài chính, phân tích ưu nhược điểm của các phương pháp hiện hữu và khẳng định tính phù hợp của giải pháp định lượng kết hợp Trí tuệ nhân tạo. Chương này cũng đã xác định rõ các thách thức kỹ thuật, mục tiêu nghiên cứu và bố cục 3 chương của đồ án. 

Nội dung tiếp theo của **Chương 2** sẽ trình bày chi tiết về **Cơ sở lý thuyết và Công nghệ áp dụng**, làm nền tảng cho việc thiết kế và xây dựng hệ thống ở Chương 3.
