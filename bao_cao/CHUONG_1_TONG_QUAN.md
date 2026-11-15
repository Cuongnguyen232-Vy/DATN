# CHƯƠNG 1. TỔNG QUAN VỀ BÀI TOÁN DỰ ĐOÁN XU HƯỚNG VÀ GIAO DỊCH TỰ ĐỘNG TRÊN THỊ TRƯỜNG TÀI CHÍNH

*Chương 1 trình bày bối cảnh thực tiễn của bài toán giao dịch tự động trên thị trường vàng (XAU/USD), giải thích các khái niệm nghiệp vụ tài chính dưới góc nhìn Công nghệ thông tin để người đọc kỹ thuật dễ dàng tiếp cận. Tiếp đó, chương này phân tích so sánh các phương pháp giải quyết, làm rõ 4 thách thức kỹ thuật cốt lõi, xác định mục tiêu nghiên cứu và tóm tắt cấu trúc 3 chương của đồ án.*

---

## 1.1 Giới thiệu bài toán

### 1.1.1 Bối cảnh thực tiễn và tính cấp thiết của đề tài
Sự phát triển mạnh mẽ của cuộc Cách mạng công nghiệp lần thứ tư đã thúc đẩy quá trình chuyển đổi số toàn diện trong lĩnh vực công nghệ tài chính (FinTech). Thị trường ngoại hối (Forex) và kim loại quý quốc tế — đặc biệt là vàng giao ngay (XAU/USD) — hoạt động liên tục 24/5 với thanh khoản hàng nghìn tỷ USD mỗi ngày, sản sinh ra khối lượng dữ liệu chuỗi thời gian khổng lồ theo thời gian thực [1]. Tại Việt Nam, sự tham gia ngày càng lớn của các nhà đầu tư cá nhân cùng các chủ trương chính quy hóa thị trường tài sản số đặt ra yêu cầu cấp thiết về việc áp dụng phân tích định lượng (Quantitative Trading) và tự động hóa thuật toán (Algorithmic Trading) có tính kỷ luật cao [2], [3].

Tuy nhiên, việc giao dịch thủ công của con người luôn gặp phải các rào cản nghiêm trọng:
- **Tâm lý con người:** Hơn 90% thua lỗ bắt nguồn từ sự chi phối của cảm xúc: lòng tham (FOMO), nỗi sợ hãi hoặc thiếu kỷ luật khi cắt lỗ [4].
- **Hạn chế về thể lực và tốc độ:** Thị trường biến động từng mili-giây, con người không thể quan sát biểu đồ liên tục 24/5 để đưa ra quyết định tối ưu mà không bị mệt mỏi hay sai sót.
- **Tính phi tuyến và nhạy cảm vĩ mô:** Giá vàng vừa biến động theo quy luật kỹ thuật, vừa phản ứng dữ dội trước các tin tức kinh tế vĩ mô đột xuất của Mỹ (như lãi suất FED, chỉ số lạm phát CPI, tỷ lệ thất nghiệp).

Do đó, đề tài: **"Nghiên cứu mô hình học máy trong dự đoán xu hướng thị trường tài chính và phát triển hệ thống giao dịch tự động"** được lựa chọn nhằm xây dựng một hệ thống hoàn chỉnh kết hợp Trí tuệ nhân tạo (AI) dự báo xu hướng, màng lọc tin tức (NLP) phòng vệ rủi ro và Robot giao dịch tự động (MQL5) trên nền tảng MetaTrader 5 để loại bỏ cảm tính và tối ưu hóa hiệu quả đầu tư.

### 1.1.2 Giải thích các khái niệm tài chính dưới góc nhìn Công nghệ thông tin
Do đặc thù đề tài thuộc lĩnh vực liên ngành giữa Công nghệ thông tin và Tài chính định lượng, để các thầy cô và hội đồng kỹ thuật phần mềm thuận tiện theo dõi, Bảng 1.1 giải thích rõ ràng bản chất kỹ thuật của các thuật ngữ nghiệp vụ được sử dụng xuyên suốt đồ án:

### Bảng 1.1: Diễn giải các khái niệm nghiệp vụ tài chính dưới góc nhìn kỹ thuật Công nghệ thông tin

| Thuật ngữ nghiệp vụ | Định nghĩa tài chính | Bản chất kỹ thuật trong hệ thống phần mềm |
| :--- | :--- | :--- |
| **XAU/USD** | Cặp tỷ giá Vàng giao ngay (Gold Spot) định giá bằng Đô la Mỹ. | Đối tượng chuỗi thời gian (Time-series) mục tiêu cần thu thập, tiền xử lý và dự báo giá trị. |
| **Nến Nhật (Candlestick / OHLCV)** | Mô hình biểu diễn biến động giá trong một khoảng thời gian cố định. | Bản ghi dữ liệu (Data Record) gồm 5 trường số thực: Mở cửa (Open), Cao nhất (High), Thấp nhất (Low), Đóng cửa (Close) và Khối lượng (Volume). |
| **Khung thời gian H4** | Chu kỳ nén dữ liệu 4 giờ cho một cây nến. | Bước lấy mẫu thời gian (Sampling Rate): Cứ 4 giờ hệ thống tạo một mẫu dữ liệu mới để kích hoạt luồng suy luận của AI. |
| **Pips / Points** | Đơn vị đo lường biến động giá nhỏ nhất của cặp tiền tệ/hàng hóa. | Đơn vị lượng tử hóa độ dịch chuyển số học (với Vàng: 1 USD = 100 points, ví dụ giá tăng từ 2700 lên 2701 là tăng 100 points). |
| **DCA (Dollar Cost Averaging)** | Chiến thuật trung bình giá: mở thêm lệnh với khối lượng tăng dần khi giá tạm thời đi ngược hướng. | Thuật toán tối ưu hóa điểm hòa vốn: Tự động tính trung bình gia quyền giá vốn để rổ lệnh có thể chốt lời ngay khi giá có nhịp hồi ngắn. |
| **Hedging (Phòng hộ hai chiều)** | Kỹ thuật mở vị thế đối ứng có khối lượng tương đương theo chiều ngược lại. | Cơ chế ngắt mạch khẩn cấp (Circuit Breaker): Đóng băng 100% mức lỗ thả nổi, triệt tiêu rủi ro tài khoản khi thị trường xuất hiện bão giá một chiều. |
| **Drawdown (Mức sụt giảm vốn)** | Tỷ lệ phần trăm sụt giảm tài sản từ đỉnh vốn cao nhất gần nhất. | Chỉ số kiểm thử độ tin cậy và an toàn của hệ thống (phần mềm phải giữ Drawdown luôn dưới ngưỡng 25%). |
| **Tin đỏ (High-Impact News)** | Các sự kiện kinh tế vĩ mô cực kỳ quan trọng được công bố theo lịch (Lãi suất FED, CPI, Non-Farm). | Các sự kiện ngoại sinh (External Interrupts) gây đột biến biến động; hệ thống cần lắng nghe qua API để tạm dừng giao dịch tự động. |
| **MetaTrader 5 (MT5) & MQL5** | Nền tảng giao dịch tài chính chuyên nghiệp và ngôn ngữ lập trình hướng đối tượng chuyên dụng. | Môi trường thực thi lệnh thời gian thực có độ trễ cực thấp (Execution Engine), chạy Robot viết bằng MQL5 (hướng đối tượng tương tự C++). |
| **IPC (Inter-Process Communication)** | Cơ chế giao tiếp liên tiến trình. | Cầu nối trao đổi dữ liệu không đồng bộ giữa tiến trình phân tích AI (Python) và tiến trình thực thi giao dịch (MT5) qua tệp trung gian JSON. |

---

## 1.2 Phương pháp giải quyết bài toán

### 1.2.1 Phương pháp truyền thống: Phân tích kỹ thuật cổ điển
Phân tích kỹ thuật (Technical Analysis) sử dụng các công thức thống kê tính trên đường giá quá khứ để xây dựng các quy tắc logic cứng (Rule-based):
- *Chỉ báo động lượng:* RSI xác định vùng quá mua/quá bán; MACD nhận diện điểm giao cắt xung lượng; Stochastic bắt nhịp đảo chiều ngắn hạn.
- *Chỉ báo xu hướng và biến động:* Đường trung bình động hàm mũ (EMA 20, EMA 50) xác định hướng đi của sóng giá; Bollinger Bands và ATR (Average True Range) đo lường biên độ dao động thị trường.

*Hạn chế cốt tử:* Các chỉ báo kỹ thuật bản chất là **chỉ báo trễ (Lagging Indicators)**. Khi thị trường đi ngang (Sideway) hoặc chịu tác động của tin tức, chúng liên tục phát ra tín hiệu giả (Whipsaws), dẫn đến thua lỗ nặng do thiếu khả năng tự thích nghi với sự thay đổi cấu trúc thị trường.

### 1.2.2 Phương pháp phân tích cơ bản và phân tích cảm xúc tin tức
Phân tích cơ bản đánh giá giá trị tài sản dựa trên các báo cáo kinh tế vĩ mô (lãi suất, lạm phát, việc làm). Tuy nhiên, con người đọc và phân tích tin tức thường bị chậm trễ. Ứng dụng Xử lý ngôn ngữ tự nhiên (NLP) với các mô hình tài chính như FinBERT và VADER cho phép tự động định lượng sắc thái tin tức thành điểm số cảm xúc (Sentiment Score $\in [-1.0, +1.0]$) theo thời gian thực [5].

### 1.2.3 Phương pháp hiện đại: Học sâu và Hệ thống lai thông minh đề xuất
Khắc phục nhược điểm của phương pháp truyền thống, đồ án lựa chọn hướng tiếp cận hiện đại ứng dụng Học sâu (Deep Learning) và Kiến trúc lai đa tầng:
- **Mô hình học sâu CNN-BiGRU-Attention:** Khối 1D-CNN trích xuất mẫu hình nến cục bộ; Bidirectional GRU học ngữ cảnh chuỗi thời gian 2 chiều; cơ chế Multi-Head Self-Attention tập trung trọng số vào các nến biến động bước ngoặt.
- **So khớp mẫu hình (Pattern Matcher):** Dùng độ đo Cosine Similarity tìm kiếm các chuỗi nến lịch sử có hình thái tương đồng nhất để bổ trợ xác suất dự đoán.
- **Kiến trúc hệ thống lai phân tầng:** Tầng AI Python chịu trách nhiệm phân tích dự báo và lọc tin tức vĩ mô; tầng MQL5 trên MetaTrader 5 chịu trách nhiệm khớp lệnh vi mô và quản trị vốn lưới DCA co giãn theo ATR.

### Bảng 1.2: So sánh phương pháp giao dịch truyền thống và hệ thống định lượng AI đề xuất

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
  Trình bày bối cảnh, giải thích các thuật ngữ nghiệp vụ dưới góc độ kỹ thuật, phân tích so sánh các phương pháp tiếp cận, nêu rõ 4 thách thức kỹ thuật và xác định mục tiêu nghiên cứu.
- **Chương 2: Cơ sở lý thuyết và Công nghệ áp dụng**
  Trình bày cơ sở toán học của các chỉ báo phân tích kỹ thuật, kiến trúc mô hình học sâu đề xuất (CNN-BiGRU-Attention), thuật toán so khớp mẫu hình Cosine Similarity, mô hình phân tích cảm xúc NLP FinBERT và ngôn ngữ lập trình MQL5 trên MetaTrader 5.
- **Chương 3: Thiết kế, Cài đặt thực nghiệm và Đánh giá hệ thống giao dịch tự động**
  Trình bày kiến trúc hệ thống lai (Hybrid System), thiết kế chi tiết các phân hệ (Lõi AI Python, Robot MT5, Telegram Bot), kết quả thực nghiệm huấn luyện, kết quả kiểm thử định lượng (Backtesting), phân tích hiệu quả quản trị rủi ro và kết luận hướng phát triển đề tài.

---

## 1.6 Kết luận chương 1

Chương 1 đã tổng quan bối cảnh bài toán giao dịch tự động trên thị trường tài chính, giải thích rõ ràng các thuật ngữ nghiệp vụ tài chính dưới góc nhìn Công nghệ thông tin giúp người đọc kỹ thuật nắm bắt mạch lạc bài toán. Chương này cũng phân tích ưu nhược điểm của các phương pháp hiện hữu, khẳng định tính đúng đắn của giải pháp định lượng AI, xác định rõ các thách thức kỹ thuật, mục tiêu nghiên cứu và bố cục 3 chương của đồ án. 

Nội dung tiếp theo của **Chương 2** sẽ đi sâu vào **Cơ sở lý thuyết và Công nghệ áp dụng**, làm nền tảng toán học và kỹ thuật vững chắc cho việc thiết kế, cài đặt hệ thống ở Chương 3.
