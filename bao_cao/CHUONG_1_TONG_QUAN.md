# CHƯƠNG 1. TỔNG QUAN VỀ BÀI TOÁN VÀ HỆ THỐNG HỖ TRỢ RA QUYẾT ĐỊNH GIAO DỊCH TÀI CHÍNH

*Chương 1 trình bày bối cảnh thực tiễn của bài toán giao dịch tài chính tự động trên thị trường vàng (XAU/USD), làm rõ khái niệm Hệ thống hỗ trợ ra quyết định (Decision Support System - DSS) và giải thích các thuật ngữ nghiệp vụ tài chính dưới góc nhìn Công nghệ thông tin để người đọc kỹ thuật dễ dàng tiếp cận. Tiếp đó, chương này phân tích sâu sắc các phương pháp tiếp cận từ phân tích kỹ thuật cổ điển đến các mô hình học sâu hiện đại, nhận diện 4 thách thức kỹ thuật cốt lõi, xác định mục tiêu nghiên cứu và tóm tắt bố cục 3 chương của đồ án.*

---

## 1.1 Giới thiệu bài toán và Tính cấp thiết của đề tài

### 1.1.1 Bối cảnh thực tiễn và làn sóng chuyển đổi số trong tài chính
Sự bùng nổ của cuộc Cách mạng công nghiệp lần thứ tư (Industry 4.0) trong thập kỷ qua đã thúc đẩy quá trình chuyển đổi số toàn diện trong ngành tài chính công nghệ (FinTech) trên phạm vi toàn cầu. Các thị trường tài chính quốc tế — đặc biệt là thị trường ngoại hối (Forex) và thị trường kim loại quý (tiêu biểu là vàng giao ngay XAU/USD) — hoạt động liên tục 24 giờ mỗi ngày với khối lượng thanh khoản khổng lồ lên tới hàng nghìn tỷ USD mỗi phiên giao dịch. 

Đặc thù nổi bật của thị trường tài chính hiện đại là tính chất sản sinh dữ liệu lớn theo chuỗi thời gian thực (Big Data Time-Series). Các bước nhảy giá (tick data) và diễn biến nến diễn ra liên tục từng giây, phản ánh sự tương tác phức tạp giữa cung cầu của các tổ chức tài chính quốc tế, các quỹ phòng hộ (Hedge Funds), ngân hàng trung ương và hàng triệu nhà đầu tư cá nhân trên toàn thế giới [1].

Tại Việt Nam, làn sóng tiếp cận công nghệ tài chính đang phát triển mạnh mẽ. Số lượng nhà đầu tư cá nhân tham gia vào các thị trường phái sinh quốc tế và tài sản số tăng trưởng vượt bậc. Đồng thời, môi trường pháp lý trong nước đang có những bước chuyển mình mang tính lịch sử nhằm chính quy hóa các hoạt động tài chính công nghệ, tiêu biểu như Chiến lược quốc gia về Blockchain đến năm 2030 của Chính phủ và Dự thảo Luật Công nghiệp công nghệ số [2]. Bối cảnh mới này đặt ra một yêu cầu cấp thiết về sự chuyên nghiệp hóa và chuẩn mực hóa công nghệ. Các phương thức giao dịch thủ công, cảm tính và tự phát dần bộc lộ sự lạc hậu, đòi hỏi phải được thay thế bằng các phương pháp phân tích định lượng (Quantitative Trading) và hệ thống giao dịch tự động dựa trên dữ liệu (Algorithmic Trading) có tính kỷ luật cao [3].

### 1.1.2 Những rào cản và nghịch lý cốt tử trong giao dịch tài chính thủ công
Mặc dù tiềm năng sinh lời là rất lớn, thị trường vàng giao ngay (XAU/USD) luôn được đánh giá là một trong những môi trường giao dịch khốc liệt và khó lường nhất đối với các nhà đầu tư cá nhân do ba rào cản mang tính cốt tử:

1. **Rào cản tâm lý con người (Psychological Bias):** 
   Các công trình nghiên cứu kinh điển về tài chính hành vi (Behavioral Finance) đã chỉ ra rằng, hơn 90% tổn thất của các nhà đầu tư cá nhân không xuất phát từ việc thiếu kiến thức phân tích, mà bắt nguồn từ sự chi phối không thể kiểm soát của tâm lý [4]. Lòng tham khi thị trường tăng nóng dẫn đến hội chứng sợ bỏ lỡ cơ hội (FOMO), nỗi sợ hãi tột độ khi tài khoản rơi vào trạng thái sụt giảm thả nổi (Floating Drawdown), hoặc tâm lý cay cú muốn gỡ gạc dẫn đến việc tự ý phá vỡ kỷ luật cắt lỗ và nhồi lệnh vô tội vạ.
2. **Sức ép về tốc độ và giới hạn sinh học của con người:** 
   Thị trường tài chính hiện đại vận hành với tốc độ tính bằng mili-giây. Một con người bình thường không thể duy trì sự tập trung 24/5 để liên tục quan sát đồ thị giá, đồng thời đọc hiểu tức thì hàng chục bản tin kinh tế quốc tế vừa công bố, và đưa ra quyết định đặt lệnh với độ chính xác tuyệt đối mà không gặp phải sai sót do mệt mỏi thể chất hay căng thẳng tinh thần.
3. **Tính chất phi tuyến và độ nhạy cảm vĩ mô cực cao của Vàng (XAU/USD):** 
   Vàng vừa là một loại hàng hóa phái sinh có tính đầu cơ cao, vừa là tài sản trú ẩn an toàn (Safe-Haven Asset) của dòng vốn toàn cầu. Biến động giá vàng là chuỗi dữ liệu phi tuyến tính cao độ, chịu sự chi phối chặt chẽ của các biến số vĩ mô như lãi suất của Cục Dự trữ Liên bang Mỹ (FED), chỉ số Dollar Index (DXY), lạm phát CPI và các xung đột địa chính trị bất ngờ. Các đợt "bão giá" kinh tế có thể quét sạch tài khoản chỉ trong vài phút nếu không có biện pháp phòng hộ kịp thời.

### 1.1.3 Khái niệm Hệ thống hỗ trợ ra quyết định (Decision Support System - DSS) trong tài chính
Dưới góc độ Công nghệ phần mềm, **Hệ thống hỗ trợ ra quyết định (Decision Support System - DSS)** là một hệ thống thông tin tương tác dựa trên máy tính, được thiết kế nhằm trợ giúp con người ra quyết định giải quyết các bài toán bán cấu trúc hoặc phi cấu trúc thông qua việc kết hợp dữ liệu lớn, các mô hình phân tích định lượng và giao diện tương tác trực quan [6]. 

Trong bài toán giao dịch tài chính, việc xây dựng một **Hệ thống hỗ trợ ra quyết định giao dịch tài chính (Financial Trading Decision Support System - FTDSS)** hoàn chỉnh bao gồm 4 phân hệ cốt lõi:
- **Phân hệ quản lý dữ liệu (Data Management Subsystem):** Tự động thu thập dữ liệu giá nến H4 theo thời gian thực từ sàn giao dịch, làm sạch, khử nhiễu và trích xuất các đặc trưng phân tích kỹ thuật.
- **Phân hệ quản lý mô hình (Model Management Subsystem):** Tích hợp các thuật toán học máy, mô hình học sâu (CNN-BiGRU-Attention), bộ so khớp mẫu hình quá khứ (Pattern Matcher) và mô hình ngôn ngữ tự nhiên (NLP FinBERT) nhằm lượng hóa xác suất xu hướng thị trường.
- **Phân hệ cơ sở tri thức và quy tắc an toàn (Knowledge/Rule Base Subsystem):** Chứa các quy tắc quản trị vốn nghiêm ngặt, cơ chế co giãn bước giá theo biến động thực tế (ATR Grid), quy tắc kích hoạt vị thế đối ứng phòng hộ (Hedging) và cơ chế ngắt mạch an toàn khi phát hiện bão tin tức vĩ mô (News Circuit Breaker).
- **Phân hệ giao diện tương tác người dùng (User Interface Subsystem):** Cung cấp bảng điều khiển trực quan (Dashboard) trên đồ thị giao dịch MetaTrader 5 và kênh tương tác cảnh báo từ xa qua Telegram Bot.

Từ các phân tích trên, đề tài tốt nghiệp được xác định chính xác là: **"Xây dựng hệ thống hỗ trợ ra quyết định giao dịch tài chính sử dụng dữ liệu chuỗi thời gian"**.

### 1.1.4 Giải thích các khái niệm tài chính dưới góc nhìn Công nghệ thông tin
Do đặc thù đề tài thuộc lĩnh vực liên ngành giữa Công nghệ phần mềm và Tài chính định lượng, để các thầy cô và hội đồng kỹ thuật thuận tiện theo dõi và đánh giá, Bảng 1.1 giải thích rõ ràng bản chất kỹ thuật của các thuật ngữ nghiệp vụ được sử dụng xuyên suốt đồ án:

### Bảng 1.1: Diễn giải các khái niệm nghiệp vụ tài chính dưới góc nhìn kỹ thuật Công nghệ thông tin

| Thuật ngữ nghiệp vụ | Định nghĩa tài chính | Bản chất kỹ thuật trong hệ thống phần mềm |
| :--- | :--- | :--- |
| **XAU/USD** | Cặp tỷ giá Vàng giao ngay (Gold Spot) định giá bằng Đô la Mỹ. | **Đối tượng chuỗi thời gian (Time-series)** mục tiêu cần thu thập, tiền xử lý và dự báo xu hướng. |
| **Nến Nhật (OHLCV)** | Mô hình biểu diễn biến động giá trong một chu kỳ thời gian cố định. | **Bản ghi dữ liệu (Data Record)** gồm 5 trường số thực: Mở cửa (Open), Cao nhất (High), Thấp nhất (Low), Đóng cửa (Close) và Khối lượng (Volume). |
| **Khung thời gian H4** | Chu kỳ nén dữ liệu 4 giờ cho một cây nến. | **Bước lấy mẫu thời gian (Sampling Rate)**: Cứ mỗi 4 giờ, hệ thống tạo một mẫu dữ liệu mới để kích hoạt luồng suy luận của AI. |
| **Pips / Points** | Đơn vị đo lường biến động giá nhỏ nhất của cặp tiền tệ/hàng hóa. | **Đơn vị lượng tử hóa độ dịch chuyển số học** (với Vàng: \$1 USD = 100 points, ví dụ giá tăng từ 2700 lên 2701 là tăng 100 points). |
| **DCA (Dollar Cost Averaging)** | Chiến thuật trung bình giá: mở thêm lệnh với khối lượng tăng dần khi giá tạm thời đi ngược hướng. | **Thuật toán tối ưu hóa điểm hòa vốn (Break-even)**: Tự động tính trung bình gia quyền giá vốn để rổ lệnh có thể chốt lời ngay khi giá có nhịp hồi ngắn. |
| **Hedging (Phòng hộ hai chiều)** | Kỹ thuật mở vị thế đối ứng có khối lượng tương đương theo chiều ngược lại. | **Cơ chế ngắt mạch khẩn cấp (Circuit Breaker)**: Đóng băng 100% mức lỗ thả nổi, triệt tiêu rủi ro tài khoản khi thị trường xuất hiện bão giá một chiều. |
| **Drawdown (Mức sụt giảm vốn)** | Tỷ lệ phần trăm sụt giảm tài sản từ đỉnh vốn cao nhất gần nhất. | **Chỉ số kiểm thử độ tin cậy và an toàn của hệ thống** (yêu cầu phần mềm phải kiểm soát Drawdown luôn dưới ngưỡng 25%). |
| **Tin đỏ (High-Impact News)** | Các sự kiện kinh tế vĩ mô cực kỳ quan trọng được công bố theo lịch (Lãi suất FED, CPI, Non-Farm). | **Các sự kiện ngoại sinh (External Interrupts)** gây đột biến dữ liệu; hệ thống cần lắng nghe qua API để tạm dừng giao dịch tự động. |
| **MetaTrader 5 (MT5) & MQL5** | Nền tảng giao dịch tài chính chuyên nghiệp và ngôn ngữ lập trình hướng đối tượng chuyên dụng. | **Môi trường thực thi lệnh thời gian thực có độ trễ cực thấp (Execution Engine)**, chạy Robot viết bằng MQL5 (hướng đối tượng tương tự C++). |
| **IPC (Inter-Process Communication)** | Cơ chế giao tiếp liên tiến trình. | **Cầu nối trao đổi dữ liệu không đồng bộ** giữa tiến trình phân tích AI (Python) và tiến trình thực thi giao dịch (MT5) qua tệp trung gian JSON. |

---

## 1.2 Các phương pháp giải quyết bài toán

Để giải quyết bài toán dự báo và hỗ trợ ra quyết định trên thị trường tài chính, trong lịch sử và thực tiễn đã hình thành các trường phái tiếp cận chủ đạo:

### 1.2.1 Phương pháp truyền thống: Phân tích kỹ thuật cổ điển
Phương pháp phân tích kỹ thuật (Technical Analysis) là cách tiếp cận phổ biến nhất, dựa trên giả định nền tảng rằng "mọi thông tin thị trường đều được phản ánh đầy đủ vào đường giá" và "lịch sử biến động giá luôn có xu hướng lặp lại". Các công cụ kỹ thuật cổ điển thường được lập trình thành các robot giao dịch quy tắc cứng (Rule-based Expert Advisors):

- **Các chỉ báo động lượng và đảo chiều (Momentum Indicators):** 
  - *Chỉ số sức mạnh tương đối (RSI):* Đo lường tương quan giữa mức tăng và giảm giá trung bình trong 14 chu kỳ, xác định ngưỡng quá mua ($RSI > 70$) hoặc quá bán ($RSI < 30$).
  - *Đường trung bình động hội tụ phân kỳ (MACD):* Dựa trên độ lệch giữa hai đường trung bình động hàm mũ EMA(12) và EMA(26) cùng đường tín hiệu Signal EMA(9) để phát hiện điểm giao cắt xác nhận xung lượng.
  - *Chỉ báo dao động ngẫu nhiên (Stochastic Oscillator):* So sánh mức giá đóng cửa hiện tại với biên độ dao động đỉnh - đáy trong 14 chu kỳ để bắt các điểm đảo chiều nhịp ngắn.
- **Các chỉ báo xu hướng và biến động (Trend & Volatility Indicators):**
  - *Đường trung bình động hàm mũ (EMA 20, EMA 50):* Làm mượt đường giá và xác định xu hướng trung - ngắn hạn.
  - *Dải Bollinger Bands:* Đo lường độ biến động chuẩn tắc xung quanh đường trung bình động SMA(20).
  - *Độ biến động thực tế trung bình (ATR):* Đo lường biên độ dao động tuyệt đối của nến, đóng vai trò then chốt trong việc tính toán khoảng cách cắt lỗ và co giãn bước giá.

**Hạn chế cố hữu của phương pháp truyền thống:**
Mặc dù trực quan và dễ cài đặt, các chỉ báo kỹ thuật truyền thống về bản chất toán học đều là các **chỉ báo trễ (Lagging Indicators)** — chúng được tính toán dựa trên dữ liệu giá đã xảy ra. Khi thị trường xuất hiện xu hướng đơn cực mạnh mẽ (Trending), các quy tắc kỹ thuật có thể phát huy tác dụng; tuy nhiên trong phần lớn thời gian thị trường tích lũy giằng co (Sideway) hoặc bị bão tin tức, các chỉ báo này liên tục phát ra các tín hiệu giả (Whipsaws), dẫn đến thua lỗ liên tiếp. Hơn nữa, các quy tắc cố định không thể tự học hỏi hay tự thích nghi khi cấu trúc thị trường biến đổi sang một pha mới (Regime Shift).

### 1.2.2 Phương pháp phân tích cơ bản và Khai phá cảm xúc tin tức vĩ mô (NLP)
Trường phái phân tích cơ bản (Fundamental Analysis) đánh giá giá trị nội tại của tài sản dựa trên sức khỏe nền kinh tế. Đối với cặp tỷ giá Vàng/USD (XAU/USD), vàng chịu sự chi phối mạnh mẽ bởi các báo cáo kinh tế Mỹ được công bố theo lịch định kỳ (ForexFactory Calendar):
- Khi nền kinh tế Mỹ công bố các chỉ số vượt kỳ vọng (Báo cáo việc làm Non-Farm Payrolls tăng cao, GDP tăng trưởng mạnh, lạm phát CPI dai dẳng khiến FED duy trì chính sách thắt chặt tiền tệ), đồng USD tăng giá mạnh mẽ, gây áp lực bán tháo nghiêm trọng lên kim loại quý Vàng.
- Ngược lại, khi xuất hiện các sự kiện địa chính trị bất ổn, khủng hoảng ngân hàng hoặc dấu hiệu suy thoái, dòng tiền toàn cầu nhanh chóng chuyển dịch vào vàng nhằm mục đích phòng hộ rủi ro.

Tuy nhiên, việc con người tự đọc và phân tích hàng loạt dòng tin tức quốc tế thường bị chậm trễ và mang tính chủ quan. Sự ra đời của các mô hình Xử lý ngôn ngữ tự nhiên (NLP) hiện đại — tiêu biểu là mô hình Transformers **FinBERT** (Pre-trained trên dữ liệu tài chính tài chính Wall Street) và bộ từ điển phân tích sắc thái cảm xúc **VADER** — đã mở ra khả năng tự động hóa quy trình lượng hóa sắc thái tin tức thành điểm số cảm xúc (Sentiment Score $\in [-1.0, +1.0]$) với độ trễ microsecond [5].

### 1.2.3 Phương pháp hiện đại: Học sâu và Hệ thống lai thông minh đề xuất
Khắc phục triệt để các rào cản của phương pháp truyền thống, hướng tiếp cận tiên tiến hiện nay tập trung vào việc áp dụng Trí tuệ nhân tạo (AI), Học máy (Machine Learning) và Học sâu (Deep Learning) vào phân tích chuỗi thời gian:

- **Mô hình học sâu CNN-BiGRU-Attention:** 
  Sự kết hợp giữa mạng tích chập 1 chiều (Dual 1D-CNN) giúp trích xuất các mẫu hình nến cục bộ đa quy mô, mạng hồi quy có cổng hai chiều (Bidirectional GRU) nắm bắt quy luật biến động theo cả hai chiều quá khứ và tương lai trong chuỗi trượt 50 nến H4, và Cơ chế Chú ý Đa đầu (Multi-Head Self-Attention) giúp mô hình tự động phân bổ trọng số tập trung vào những cây nến mang tính bước ngoặt.
- **Kỹ thuật so khớp mẫu hình chuỗi thời gian (Time-Series Pattern Matcher):** 
  Sử dụng độ đo độ tương đồng Cosine (Cosine Similarity) để quét nhanh hình thái sóng giá 20 nến hiện tại trên toàn bộ kho dữ liệu lịch sử nhiều năm, từ đó tìm kiếm các kịch bản tương đồng nhất để bổ trợ xác suất cho mô hình học sâu.
- **Hệ thống hỗ trợ ra quyết định lai đa tầng (Hybrid DSS Architecture):** 
  Thay vì phó mặc toàn bộ quá trình cho một thuật toán duy nhất, đề tài đề xuất kiến trúc phân tầng chuyên biệt:
  1. *Tầng định hướng AI (Strategic Layer - Python):* Mô hình CNN-BiGRU-Attention kết hợp Pattern Matcher phân tích nến H4, đưa ra xác suất 3 lớp (BUY, HOLD, SELL).
  2. *Tầng màng lọc rủi ro (Risk Shield Layer - Python):* Module NLP kết nối API ForexFactory quét tin đỏ, tự động ngắt mở lệnh khi thị trường sắp có bão giá.
  3. *Tầng thực thi vi mô (Tactical Execution Layer - MQL5 trên MT5):* Robot Expert Advisor thực thi chiến thuật quản lý vốn lưới ma trận DCA co giãn linh hoạt theo ATR và kích hoạt vị thế Hedging khóa rủi ro khi cần thiết.

### Bảng 1.2: So sánh toàn diện giữa Phương pháp Giao dịch Truyền thống và Hệ thống Định lượng AI Đề xuất

| Tiêu chí so sánh | Phương pháp Giao dịch Truyền thống (Rule-based EA) | Hệ thống Định lượng Lai Đề xuất (VQuant AI Ecosystem) |
| :--- | :--- | :--- |
| **Cơ chế ra quyết định** | Dựa trên các ngưỡng cố định cứng nhắc (RSI > 70, MACD cắt qua 0) | Học phi tuyến tính trên không gian đa biến (20 đặc trưng kỹ thuật + Attention) |
| **Khả năng thích ứng** | Cố định, dễ lỗi thời và thua lỗ khi thị trường đổi pha (Regime Shift) | Tự học quy luật từ dữ liệu lớn, liên tục cập nhật theo chuỗi thời gian |
| **Độ trễ tín hiệu** | Chỉ báo trễ (Lagging), phát nhiều tín hiệu giả trong vùng Sideway | Kết hợp 1D-CNN trích xuất hình thái nến và BiGRU bắt động lượng sớm |
| **Phản ứng trước tin tức** | Không có khả năng đọc tin, thường xuyên bị cháy tài khoản do giật giá | Màng lọc tin vĩ mô tự động kích hoạt Circuit Breaker đóng băng lệnh |
| **Quản trị vốn & Rủi ro** | Đặt Stop Loss cố định hoặc nhồi lệnh Martingale nhân đôi lot nguy hiểm | Lưới DCA co giãn theo ATR, giới hạn Drawdown và kích hoạt khóa Hedging |
| **Tính kỷ luật** | Phụ thuộc vào việc bật tắt thủ công của nhà đầu tư | Tự động hóa 100% không cảm tính, có giám sát từ xa qua Telegram |

**Kết luận lựa chọn:** Việc lựa chọn **Mô hình lai thông minh kết hợp Học sâu (CNN-BiGRU-Attention), Màng lọc tin tức NLP và Robot giao dịch tự động MQL5 trên MetaTrader 5** là giải pháp tối ưu và toàn diện nhất, dung hòa được năng lực phân tích thông minh của Trí tuệ nhân tạo với tốc độ khớp lệnh mili-giây của nền tảng tài chính chuyên nghiệp.

---

## 1.3 Thách thức kỹ thuật gặp phải khi giải quyết bài toán

Quá trình nghiên cứu và phát triển một hệ thống giao dịch tự động tích hợp trí tuệ nhân tạo trên thị trường thực tế phải giải quyết 4 bài toán kỹ thuật hóc búa:

1. **Đặc tính dữ liệu chuỗi thời gian tài chính có độ nhiễu cao (High Noise & Non-stationarity):**
   Dữ liệu giá tài chính không tuân theo phân phối chuẩn tĩnh mà biến động liên tục theo thời gian. Tỷ lệ tín hiệu trên nhiễu (Signal-to-Noise Ratio) của dữ liệu giá rất thấp. Nếu sử dụng các mô hình học máy quá cồng kềnh với hàng triệu tham số, mô hình sẽ nhanh chóng rơi vào trạng thái học vẹt (Overfitting) — hoạt động rất tốt trên tập huấn luyện quá khứ nhưng thất bại hoàn toàn khi dự báo thị trường thực tế trong tương lai. Do đó, bài toán đặt ra là phải thiết kế kiến trúc mạng nơ-ron gọn nhẹ (Compact Architecture), sử dụng kỹ thuật điều chuẩn (Dropout, Batch Normalization) và phương pháp gán nhãn thích nghi theo độ biến động thị trường (Adaptive ATR Labeling).

2. **Rủi ro biến động cực đoan do bão tin tức vĩ mô (Flash Crashes & News Shocks):**
   Thị trường Vàng (XAU/USD) thường xuyên xuất hiện các đợt biến động giá đột ngột hàng chục đến hàng trăm USD chỉ trong vài phút khi các báo cáo kinh tế Mỹ được công bố. Trong các thời điểm này, spread (chênh lệch giá mua - bán) của các sàn môi giới bị giãn rộng, xảy ra hiện tượng trượt giá (Slippage) và thanh khoản suy giảm nghiêm trọng. Mọi mô hình thuần kỹ thuật đều trở nên vô hiệu trước các cú sốc tin tức này. Vì vậy, hệ thống bắt buộc phải sở hữu một màng lọc tin tức tự động chạy ngầm 24/7 để cảnh báo và tự động vô hiệu hóa hoạt động mở lệnh trước và sau các thời điểm nhạy cảm.

3. **Thách thức về tích hợp liên nền tảng (Cross-Platform Integration & Low Latency IPC):**
   Hệ sinh thái phân tích dữ liệu và học máy mạnh nhất hiện nay được xây dựng trên ngôn ngữ Python (TensorFlow, PyTorch, Pandas), trong khi nền tảng giao dịch trực tiếp có độ trễ thấp và ổn định nhất thế giới là MetaTrader 5 (hoạt động bằng ngôn ngữ C++ tùy biến — MQL5). Hai môi trường này hoàn toàn độc lập về không gian bộ nhớ. Thách thức lớn là phải thiết kế một cơ chế giao tiếp liên tiến trình (Inter-Process Communication - IPC) nhẹ, ổn định, không xung đột truy cập file, và có cơ chế dự phòng an toàn (Failsafe Mechanism): khi tiến trình Python dừng hoạt động, Robot MT5 phải tự động nhận biết để chuyển về chế độ phòng thủ, tránh treo lệnh hoặc xử lý sai lệch.

4. **Bài toán quản trị vốn và kiểm soát sụt giảm tài khoản (Drawdown Management):**
   Không có bất kỳ mô hình dự đoán AI nào có thể đạt độ chính xác 100% trong thị trường tài chính. Một hệ thống giao dịch muốn tồn tại lâu dài không thể chỉ dựa vào xác suất dự đoán mà phụ thuộc phần lớn vào thuật toán quản trị vốn. Việc áp dụng chiến thuật nhồi lệnh DCA (Dollar Cost Averaging) nếu không kiểm soát tốt sẽ tiềm ẩn nguy cơ "cháy tài khoản". Do đó, thuật toán thực thi cần tích hợp các lớp bảo vệ: bước giá lưới tự thích nghi theo ATR, giới hạn số tầng lệnh tối đa (Order Cap), tỷ lệ rủi ro tối đa trên mỗi chu kỳ, và tính năng can thiệp trực tiếp qua bảng điều khiển biểu đồ cũng như điều khiển từ xa qua Telegram.

---

## 1.4 Mục tiêu và nhiệm vụ của đồ án

### 1.4.1 Mục tiêu tổng quát
Nghiên cứu cơ sở lý thuyết về các mô hình học sâu và xử lý ngôn ngữ tự nhiên trong phân tích chuỗi thời gian tài chính. Thiết kế, xây dựng và triển khai thực nghiệm thành công một **Hệ thống hỗ trợ ra quyết định giao dịch tài chính (Financial Trading Decision Support System - VQuant)** cho cặp tỷ giá XAU/USD; kết hợp mô hình học sâu CNN-BiGRU-Attention dự báo xu hướng, màng lọc tin tức vĩ mô NLP thời gian thực, Robot Expert Advisor thực thi chiến thuật lưới thích nghi trên MetaTrader 5, và kênh giám sát tương tác từ xa qua Telegram nhằm tối ưu hóa lợi nhuận và kiểm soát rủi ro an toàn tuyệt đối.

### 1.4.2 Các nhiệm vụ nghiên cứu cụ thể
Để đạt được mục tiêu tổng quát, đồ án đề ra 6 nhiệm vụ kỹ thuật cụ thể:

1. **Nghiên cứu cơ sở lý thuyết và mô hình toán học:**
   - Khảo sát các chỉ báo kỹ thuật tài chính cốt lõi (EMA, ATR, RSI, Bollinger Bands, Stochastic, ROC).
   - Nghiên cứu cơ sở toán học của mạng nơ-ron tích chập 1D (Conv1D), mạng hồi quy 2 chiều (BiGRU) và Cơ chế Chú ý Đa đầu (Multi-Head Self-Attention).
   - Nghiên cứu các phương pháp Xử lý ngôn ngữ tự nhiên (NLP FinBERT, VADER) và cơ chế cào dữ liệu lịch kinh tế từ ForexFactory.
   - Tìm hiểu kiến trúc MetaTrader 5, ngôn ngữ MQL5 hướng đối tượng và cơ chế giao tiếp liên tiến trình (IPC).

2. **Thu thập, tiền xử lý và chuẩn hóa dữ liệu:**
   - Thu thập tập dữ liệu nến lịch sử đa khung thời gian (H4, H1, M15) của cặp XAU/USD từ sàn giao dịch Exness MT5.
   - Xây dựng quy trình làm sạch dữ liệu, xử lý nhiễu, chuẩn hóa đặc trưng (MinMaxScaler) với 20 đặc trưng kỹ thuật nhân quả, loại bỏ hoàn toàn rò rỉ dữ liệu (Data Leakage).
   - Áp dụng phương pháp gán nhãn thích nghi theo biến động thực tế (Adaptive ATR Labeling) nhằm giải quyết bài toán mất cân bằng nhãn (Class Imbalance).

3. **Xây dựng và tối ưu hóa Lõi AI Engine (Python):**
   - Xây dựng kiến trúc mô hình học sâu lai CNN-BiGRU-Attention kết hợp bộ so khớp mẫu hình KNN Pattern Matcher trên Python.
   - Huấn luyện mô hình với kỹ thuật EarlyStopping, ReduceLROnPlateau và ma trận trọng số lớp (Class Weights).
   - Phát triển Module Sentinel 24/7 tự động cào tin tức kinh tế, phân tích cảm xúc tin tức tài chính và phân loại mức độ rủi ro ("Tin đỏ", "Tin cam", "Tin vàng").
   - Thiết lập kênh cầu nối IPC truyền tải dữ liệu tín hiệu và độ tin cậy thời gian thực sang thư mục dùng chung của MetaTrader 5.

4. **Phát triển Robot giao dịch trên MetaTrader 5 (MQL5):**
   - Lập trình Expert Advisor hướng đối tượng (OOP) theo cấu trúc module rõ ràng (Bridge, Strategy, OrderManager, RiskManager, UI Dashboard).
   - Triển khai chiến lược giao dịch lưới ma trận Hedge DCA kết hợp bộ lọc xu hướng AI.
   - Xây dựng giao diện bảng điều khiển trực quan (Dashboard) hiển thị đầy đủ thông số trạng thái thời gian thực và các nút bấm tương tác trực tiếp trên biểu đồ.

5. **Xây dựng kênh giám sát và cảnh báo từ xa qua Telegram:**
   - Phát triển Telegram Bot tự động gửi thông báo khi có tín hiệu AI mới, cảnh báo tin tức đỏ sắp xuất hiện, và báo cáo tổng kết lãi/lỗ (PnL) định kỳ.

6. **Thử nghiệm, đánh giá hiệu năng và kiểm chứng thực tế:**
   - Thực hiện kiểm thử quá khứ (Backtesting) trên dữ liệu lịch sử nhiều năm để đánh giá các chỉ số định lượng: Lợi nhuận ròng (Net Profit), Tỷ lệ thắng (Win Rate), Tỷ số Sharpe, Tỷ số Sortino, Tỷ số Calmar, Hệ số lợi nhuận (Profit Factor) và Mức sụt giảm tài khoản tối đa (Max Drawdown).
   - Triển khai vận hành thực tế 24/7 trên tài khoản Demo sàn Exness để kiểm chứng độ ổn định, khả năng chịu lỗi và tính tự động hoàn toàn của hệ thống.

### 1.4.3 Sản phẩm bàn giao của đồ án
- Báo cáo khóa luận tốt nghiệp hoàn chỉnh theo đúng quy chuẩn định dạng của Học viện Công nghệ Bưu chính Viễn thông.
- Bộ mã nguồn Lõi AI Engine phân tích dữ liệu và màng lọc tin tức vĩ mô (ngôn ngữ Python).
- Bộ trọng số mô hình đã được huấn luyện tối ưu (`model_real.h5` và `scaler.save`).
- Phần mềm Robot giao dịch tự động hoàn chỉnh (`Matrix_DCA.mq5` và bộ thư viện MQL5 đi kèm) sẵn sàng vận hành trên nền tảng MetaTrader 5.
- Kênh Bot Telegram giám sát và điều khiển từ xa.
- Bộ dữ liệu lịch sử kiểm thử và Báo cáo kiểm định định lượng chi tiết (Backtest HTML Tear-Sheet).

---

## 1.5 Bố cục của khóa luận tốt nghiệp

Cấu trúc nội dung của khóa luận tốt nghiệp được phân chia tinh gọn trong **3 chương** chính:

- **Chương 1: Tổng quan về bài toán và hệ thống hỗ trợ ra quyết định giao dịch tài chính**
  Trình bày bối cảnh thực tiễn, làm rõ khái niệm hệ thống hỗ trợ ra quyết định (DSS), diễn giải các thuật ngữ tài chính dưới góc độ công nghệ thông tin, phân tích so sánh các phương pháp tiếp cận, chỉ ra 4 thách thức kỹ thuật cốt lõi và xác định mục tiêu, nhiệm vụ nghiên cứu cùng cấu trúc tổng thể của đề tài.
- **Chương 2: Cơ sở lý thuyết và Công nghệ áp dụng**
  Trình bày chi tiết cơ sở lý thuyết toán học của các chỉ báo phân tích kỹ thuật, kiến trúc mô hình học sâu đề xuất (CNN-BiGRU-Attention), thuật toán so khớp mẫu hình Cosine Similarity, lý thuyết phân tích cảm xúc NLP FinBERT, nền tảng MetaTrader 5 (MQL5) và nguyên lý quản lý vốn ma trận DCA lưới thích nghi kết hợp chiến lược Hedge.
- **Chương 3: Thiết kế, Cài đặt thực nghiệm và Đánh giá hệ thống giao dịch tự động VQuant**
  Trình bày kiến trúc hệ thống lai (Hybrid System), thiết kế chi tiết các phân hệ (Lõi AI Python, Robot MT5, Telegram Bot), kết quả thực nghiệm huấn luyện, kết quả kiểm thử định lượng (Backtesting), phân tích hiệu quả quản trị rủi ro và kết luận hướng phát triển đề tài.

---

## 1.6 Kết luận chương 1

Trong Chương 1, đồ án đã tổng hợp toàn diện bối cảnh thực tiễn của bài toán giao dịch tài chính tự động trong kỷ nguyên số hóa; giải thích rõ ràng các khái niệm nghiệp vụ dưới góc nhìn Công nghệ thông tin giúp người đọc kỹ thuật nắm bắt mạch lạc bài toán; phân tích ưu nhược điểm của các phương pháp phân tích kỹ thuật truyền thống, phân tích cơ bản và khẳng định tính vượt trội của phương pháp tiếp cận hiện đại kết hợp Trí tuệ nhân tạo. Đồ án cũng đã nhận diện rõ 4 thách thức kỹ thuật cốt lõi cần giải quyết và thiết lập hệ thống mục tiêu, nhiệm vụ chi tiết cùng các sản phẩm bàn giao cụ thể.

Dựa trên các mục tiêu đã đề ra, nội dung của **Chương 2** tiếp theo sẽ đi sâu vào **Cơ sở lý thuyết và Công nghệ áp dụng**, trình bày chi tiết nền tảng lý thuyết toán học của các mô hình học sâu CNN-BiGRU-Attention, thuật toán so khớp mẫu hình KNN, lý thuyết phân tích cảm xúc NLP FinBERT, cấu trúc nền tảng MetaTrader 5 (MQL5) và nguyên lý quản lý vốn ma trận DCA lưới thích nghi kết hợp chiến lược Hedge.
