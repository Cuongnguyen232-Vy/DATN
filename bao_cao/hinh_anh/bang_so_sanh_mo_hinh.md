# BẢNG SO SÁNH HIỆU NĂNG CÁC MÔ HÌNH DỰ ĐOÁN XU HƯỚNG XAU/USD

| Model                      |   Accuracy |   Precision |   Recall |   F1-Score |   Train Time (s) |   Inference (ms) |
|:---------------------------|-----------:|------------:|---------:|-----------:|-----------------:|-----------------:|
| Random Forest (Baseline 1) |    39.9171 |     39.3285 |  39.2472 |    39.2599 |            14.24 |             0.08 |
| Standard LSTM (Baseline 2) |    35.9116 |     36.2521 |  36.5216 |    35.7021 |            50.89 |             0.87 |
| Standard GRU (Baseline 3)  |    35.6354 |     36.2412 |  35.9678 |    35.6435 |            59.82 |             0.94 |
| Proposed Compact CNN-BiGRU |    35.4972 |     35.6054 |  35.3726 |    35.168  |            84.86 |             1.79 |

*Ghi chú: Đánh giá độc lập trên cùng tập Test (20% dữ liệu nến H4, Stratified Split).*
