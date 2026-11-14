HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG
KHOA CÔNG NGHỆ THÔNG TIN 1
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập – Tự do – Hạnh phúc
Hà Nội, ngày 12 tháng 4 năm 2026

ĐỀ CƯƠNG KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC
Tên đề tài: Nghiên cứu mô hình học máy trong dự đoán xu hướng thị trường tài chính và phát triển hệ thống giao dịch tự động
Sinh viên thực hiện: Nguyễn Mạnh Cường
Mã Sinh viên: B22DCCN099
Lớp: D22CNPM02
Ngành/Chuyên nghành: Công nghệ thông tin
Khoa: Công nghệ thông tin 1

1. Lý do lựa chọn đề tài
Sự bùng nổ của cuộc Cách mạng công nghiệp 4.0 trong thập niên vừa qua đã thúc đẩy mạnh mẽ quá trình chuyển đổi số trong lĩnh vực tài chính (Fintech) trên toàn cầu. Các thị trường tài chính, đặc biệt là ngoại hối và tài sản số, đang tạo ra một khối lượng dữ liệu khổng lồ theo thời gian thực (Big Data), yêu cầu tốc độ xử lý và ra quyết định tính bằng mili-giây. Tại Việt Nam, xu hướng này đang diễn ra mạnh mẽ với sự tham gia ngày càng lớn của các nhà đầu tư cá nhân và sự hiện diện của các nền tảng giao dịch quốc tế. Đặc biệt, môi trường pháp lý trong nước đang có những bước chuyển dịch mang tính lịch sử nhằm chính quy hóa thị trường tài chính công nghệ. Với việc Chính phủ ban hành Chiến lược quốc gia về Blockchain đến năm 2030 và dự thảo Luật Công nghiệp công nghệ số dự kiến có hiệu lực khoảng năm 2026, thị trường đang chuyển mình từ trạng thái tự phát sang được quản lý chặt chẽ [1]. Bối cảnh mới này đặt ra yêu cầu cấp thiết về sự chuyên nghiệp hóa trong hoạt động đầu tư, nơi các phương thức giao dịch thủ công, cảm tính sẽ dần bị thay thế bởi các công cụ dựa trên dữ liệu và công nghệ [2].

Tuy nhiên, thực tế cho thấy nhà đầu tư cá nhân vẫn đang đối mặt với những thách thức rất lớn khi tham gia thị trường. Dưới góc độ tài chính hành vi, các quyết định giao dịch của con người thường xuyên bị chi phối bởi các yếu tố tâm lý như sợ hãi, tham lam hoặc tâm lý đám đông, dẫn đến những sai lệch nghiêm trọng trong quản lý vốn [3]. Hơn nữa, với sự biến động phức tạp và phi tuyến tính của thị trường tài chính hiện đại, các công cụ phân tích kỹ thuật truyền thống hay khả năng xử lý của não bộ con người thường có độ trễ, không thể nhận diện kịp thời các mẫu hình giá ẩn sâu trong dữ liệu lịch sử khổng lồ. Điều này dẫn đến hiệu suất đầu tư thấp và rủi ro thua lỗ cao trước sự cạnh tranh của các tổ chức tài chính chuyên nghiệp.

Để giải quyết bài toán trên, việc ứng dụng Trí tuệ nhân tạo (AI) và Học máy (Machine Learning) vào giao dịch tự động đã trở thành xu hướng tất yếu. Các thuật toán học máy hiện đại có khả năng xử lý dữ liệu chuỗi thời gian vượt trội, tự động "học" các quy luật biến động từ quá khứ để đưa ra dự báo xu hướng với độ chính xác cao [4]. Bên cạnh đó, thị trường tài chính cực kỳ nhạy cảm với các biến động vĩ mô (tin tức kinh tế). Một hệ thống tự động hoàn chỉnh không chỉ cần dự đoán đường giá mà còn phải có khả năng đọc hiểu tin tức (Sentiment Analysis/News Filter) để né tránh các rủi ro "bão giá" bất ngờ. Mặc dù tiềm năng là rất lớn, nhưng việc nghiên cứu và triển khai một hệ thống tích hợp trọn vẹn giữa khả năng phân tích của mô hình học máy, màng lọc tin tức NLP, và khả năng thực thi lệnh của nền tảng giao dịch phổ biến như MetaTrader 5 vẫn còn nhiều hạn chế tại Việt Nam. Xuất phát từ nhu cầu thực tiễn đó, đề tài “Nghiên cứu mô hình học máy trong dự đoán xu hướng thị trường tài chính và phát triển hệ thống giao dịch tự động” được lựa chọn thực hiện. Đề tài không chỉ mang ý nghĩa khoa học trong việc kiểm chứng hiệu quả dự báo của AI, mà còn đóng góp một giải pháp công nghệ thực tiễn, giúp tự động hóa quy trình giao dịch, quản trị rủi ro toàn diện và nâng cao hiệu quả đầu tư trong kỷ nguyên kinh tế số.

2. Mục tiêu của đề tài
Mục tiêu tổng quát
Nghiên cứu cơ sở lý thuyết về các mô hình học máy (Machine Learning) trong phân tích dữ liệu chuỗi thời gian. Thiết kế và xây dựng một hệ thống giao dịch tự động tích hợp trí tuệ nhân tạo, có khả năng dự đoán xu hướng thị trường tài chính, tích hợp màng lọc tin tức tự động (News Filter) và tự động thực thi lệnh giao dịch trên nền tảng MetaTrader 5, đồng thời quản lý từ xa qua Telegram nhằm tối ưu hóa lợi nhuận và giảm thiểu rủi ro tâm lý.

Mục tiêu cụ thể
- Tìm hiểu về các chỉ báo kỹ thuật tài chính và các thuật toán học máy chuyên xử lý chuỗi thời gian như LSTM, GRU.
- Phân tích quy trình xử lý dữ liệu tài chính: thu thập dữ liệu lịch sử, làm sạch, chuẩn hóa và gán nhãn xu hướng (Data Preprocessing).
- Thiết kế mô hình hệ thống giao dịch lai (Hybrid System): kết nối luồng dữ liệu và tín hiệu giữa môi trường phân tích (Python) và môi trường giao dịch (MetaTrader 5) thông qua cơ chế IPC (Inter-Process Communication).
- Xây dựng module Lọc tin tức (News Filter): Ứng dụng xử lý ngôn ngữ tự nhiên (NLP) và cào dữ liệu lịch kinh tế (ForexFactory API) để nhận diện "Tin đỏ", làm bộ lọc rủi ro dừng giao dịch khi có biến động vĩ mô.
- Xây dựng chương trình thực nghiệm gồm các module chính: Module Python dự đoán xu hướng & lọc tin tức, Robot (Expert Advisor) trên MQL5 thực hiện chiến thuật DCA Grid (trung bình giá theo lưới), và Telegram Bot để giám sát hệ thống từ xa.
- Lựa chọn công nghệ triển khai: Ngôn ngữ Python (TensorFlow, Keras, BeautifulSoup); nền tảng giao dịch MetaTrader 5 (ngôn ngữ MQL5).

3. Nội dung nghiên cứu
- Nghiên cứu cơ sở lý thuyết: Tìm hiểu về cấu trúc dữ liệu thị trường tài chính, các chỉ báo phân tích kỹ thuật (Technical Indicators) và cơ chế hoạt động của các thuật toán học máy (Machine Learning) trong bài toán phân loại và dự báo chuỗi thời gian. Tìm hiểu phương pháp phân tích cảm xúc (Sentiment Analysis) áp dụng trong tài chính.
- Khảo sát và xử lý dữ liệu: Nghiên cứu các phương pháp thu thập dữ liệu lịch sử từ các sàn giao dịch, quy trình làm sạch dữ liệu (Data Cleaning), chuẩn hóa và trích xuất đặc trưng (Feature Engineering) để xây dựng bộ dữ liệu huấn luyện tối ưu cho mô hình.
- Phân tích và thiết kế hệ thống: Xây dựng kiến trúc tổng thể của hệ thống giao dịch tự động, xác định cơ chế giao tiếp và đồng bộ tín hiệu IPC giữa môi trường phân tích dữ liệu (Python) và môi trường thực thi giao dịch (MetaTrader 5). Tích hợp module lọc tin tức API làm lớp bảo vệ (Risk Shield).
- Xây dựng ứng dụng thực nghiệm: Huấn luyện và tinh chỉnh mô hình học máy (LSTM/GRU) trên Python để nhận diện xu hướng thị trường. Phát triển Robot giao dịch (Expert Advisor) trên ngôn ngữ MQL5 sử dụng thuật toán lưới ma trận (Matrix DCA) để tự động nhận tín hiệu và thực hiện lệnh mua/bán. Xây dựng Bot Telegram để báo cáo PnL và thông báo tín hiệu.
- Thử nghiệm và đánh giá: Thực hiện kiểm thử lại trên dữ liệu quá khứ (Backtesting) và chạy thử nghiệm trên môi trường giả lập (Demo), đánh giá hiệu năng hệ thống dựa trên các chỉ số lợi nhuận, tỷ lệ thắng (Win-rate) và độ sụt giảm tài khoản (Drawdown).

4. Phương pháp nghiên cứu
Phương pháp lý thuyết
- Nghiên cứu các tài liệu, giáo trình và công trình khoa học trong và ngoài nước về phân tích kỹ thuật tài chính (Technical Analysis) và các chỉ báo xu hướng (Trend Indicators).
- Tìm hiểu cơ sở toán học của các thuật toán Deep Learning (Học sâu) áp dụng cho dữ liệu chuỗi thời gian, tập trung vào các mô hình LSTM, GRU.
- Tìm hiểu các công nghệ Crawl dữ liệu và các kỹ thuật Xử lý ngôn ngữ tự nhiên cơ bản (NLP) để thu thập tin tức lịch kinh tế toàn cầu.
- Tổng hợp các phương pháp xử lý dữ liệu tài chính (Data Preprocessing), lý thuyết về gán nhãn dữ liệu và các tiêu chuẩn đánh giá độ chính xác của mô hình dự báo.

Phương pháp thực nghiệm
- Xây dựng quy trình thu thập và xử lý dữ liệu bằng ngôn ngữ Python: lấy dữ liệu lịch sử giá từ API của nền tảng, làm sạch nhiễu và chuẩn hóa dữ liệu đầu vào.
- Cài đặt và huấn luyện các mô hình học máy (TensorFlow/Keras) để nhận diện xu hướng thị trường dựa trên bộ dữ liệu đã xử lý.
- Xây dựng hệ thống quét tin tức ForexFactory qua API để chặn đứng Robot khi sắp có tin tức "High Impact".
- Phát triển hệ thống giao dịch tự động (Robot) trên nền tảng MetaTrader 5 (ngôn ngữ MQL5) theo chiến thuật Hedge DCA (Giao dịch 2 chiều), có khả năng kết nối và nhận tín hiệu từ mô hình Python thông qua IPC file-based.
- Thực hiện kiểm thử lại trên dữ liệu quá khứ (Backtesting) và chạy giả lập trên thị trường thực (Demo) để đánh giá hiệu quả hệ thống qua các chỉ số: lợi nhuận ròng, tỷ lệ thắng và độ sụt giảm tài khoản (Drawdown).

5. Kết quả đạt được (dự kiến)
- Báo cáo khóa luận và mã nguồn phần mềm hoàn chỉnh theo đề cương được duyệt.
- Hệ thống giao dịch tự động (Trading Bot) hoạt động trên nền tảng MetaTrader 5, có khả năng nhận tín hiệu từ mô hình học máy và tự động quản trị rủi ro bằng chiến thuật lưới DCA.
- Mô hình thuật toán (AI Model) đã được huấn luyện và tối ưu hóa để dự đoán xu hướng thị trường XAUUSD.
- Module Lọc tin tức (News Filter) và Telegram Bot hoạt động theo thời gian thực để cảnh báo rủi ro vĩ mô và hỗ trợ điều khiển hệ thống.
- Bộ dữ liệu tài chính lịch sử đã được thu thập, làm sạch và chuẩn hóa phục vụ cho việc huấn luyện.
- Kết quả kiểm thử (Backtest) đánh giá hiệu năng hệ thống về lợi nhuận, tỷ lệ thắng và quản trị rủi ro trên dữ liệu thực tế.

6. Bố cục của khóa luận (dự kiến)
Chương 1: Tổng quan về bài toán dự đoán xu hướng và giao dịch tự động
1.1. Giới thiệu bài toán: Giao dịch tự động trên thị trường tài chính (XAUUSD) là gì?
1.2. Các phương pháp để giải quyết bài toán:
- Phương pháp truyền thống: Giao dịch thủ công dựa trên phân tích kỹ thuật (Cảm tính, dễ bị tâm lý chi phối).
- Phương pháp hiện đại: Ứng dụng Học máy/Học sâu (Deep Learning như LSTM, GRU) kết hợp phân tích dữ liệu lớn.
=> Từ các phương pháp xem xét, nhận thấy phương pháp hiện đại (Deep Learning kết hợp Lọc tin tức vĩ mô) là phương pháp tốt nhất và sẽ được áp dụng trong đồ án, trình bày cụ thể ở Chương 2 và Chương 3.
1.3. Thách thức (hạn chế) gặp phải khi giải quyết bài toán: Nhiễu dữ liệu chuỗi thời gian, độ trễ thực thi lệnh, rủi ro cháy tài khoản do tin tức kinh tế (Bão giá).
1.4. Mục tiêu đồ án.
1.5. Kết luận chương 1.

Chương 2: Cơ sở kiến thức
2.1. Tổng quan về thị trường ngoại hối và các chỉ báo phân tích kỹ thuật (Technical Indicators).
2.2. Cơ sở toán học của mạng nơ-ron hồi quy (RNN, LSTM, GRU) trong dự báo chuỗi thời gian.
2.3. Xử lý ngôn ngữ tự nhiên (NLP) và ứng dụng API (ForexFactory) trong màng lọc tin tức (News Filter).
2.4. Nền tảng giao dịch MetaTrader 5 và cơ chế giao tiếp liên tiến trình (IPC).
2.5. Thuật toán quản lý vốn lưới ma trận (Matrix DCA) và chiến lược phòng ngừa rủi ro (Hedge).
2.6. Kết luận chương 2.

Chương 3: Phân tích và thiết kế hệ thống giao dịch tự động
3.1. Phân tích yêu cầu bài toán và đặc tả luồng dữ liệu (Data Pipeline).
3.2. Kiến trúc tổng thể của hệ thống lai (Hybrid System: Python ↔ MQL5).
3.3. Thiết kế Module AI (dự báo xu hướng) và Module Lọc tin tức (News Filter).
3.4. Thiết kế Expert Advisor (Bot MT5) quản lý lệnh và Bot Telegram giám sát từ xa.
3.5. Kết luận chương 3.

Chương 4: Xây dựng ứng dụng thực nghiệm và đánh giá kết quả
4.1. Môi trường cài đặt và công nghệ triển khai.
4.2. Xây dựng và tích hợp các Module (Python, MQL5).
4.3. Kết quả thực nghiệm (Backtest) và đánh giá hiệu năng (Lợi nhuận, Drawdown, Win-rate).
4.4. Kết luận chương 4.

7. Tài liệu tham khảo
[1] Thủ tướng Chính phủ, “Quyết định số 1236/QĐ-TTg về Chiến lược quốc gia về ứng dụng và phát triển công nghệ chuỗi khối (blockchain) đến năm 2025, định hướng đến năm 2030,” Hà Nội, 2024.
[2] Bộ Thông tin và Truyền thông, “Dự thảo Luật Công nghiệp công nghệ số (Trình Quốc hội khóa XV),” Hà Nội, 2025.
[3] Hiệp hội Blockchain và Tài sản số Việt Nam (VBA), “Báo cáo thị trường tài sản số Việt Nam và xu hướng tuân thủ pháp lý năm 2025,” 2025.
[4] Nguyễn Nhật Quang, “Giáo trình Trí tuệ nhân tạo và Học máy ứng dụng,” NXB Đại học Quốc gia Hà Nội, 2021.
[5] Marcos Lopez de Prado, Advances in Financial Machine Learning, John Wiley & Sons, 2018.
[6] Yves Hilpisch, Python for Finance: Mastering Data-Driven Finance, O'Reilly Media, 2nd Edition, 2018.
[7] Ernest P. Chan, Machine Trading: Deploying Computer Algorithms to Conquer the Markets, Wiley, 2017.
[8] Sepp Hochreiter and Jürgen Schmidhuber, “Long Short-Term Memory,” Neural Computation, vol. 9, no. 8, pp. 1735–1780, 1997.
[9] Chainalysis, “The 2024 Global Crypto Adoption Index,” truy cập tại [https://www.chainalysis.com](https://www.chainalysis.com).
[10] MetaQuotes Ltd, “MQL5 Documentation: Algorithmic Trading and Technical Indicators,” truy cập tại [https://www.mql5.com/en/docs](https://www.mql5.com/en/docs).
[11] Scikit-learn Developers, “User Guide: Supervised learning,” truy cập tại [https://scikit-learn.org/stable/user_guide.html](https://scikit-learn.org/stable/user_guide.html). 
