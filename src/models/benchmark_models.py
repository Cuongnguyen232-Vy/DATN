# -*- coding: utf-8 -*-
"""
Module: Academic Benchmark & Time-Series Cross-Validation Suite
Đồ án Tốt nghiệp: Nghiên cứu mô hình học máy trong dự đoán xu hướng thị trường tài chính
Sinh viên thực hiện: Nguyễn Mạnh Cường _ B22DCCN099 (Khoa CNTT 1 - PTIT)

Chức năng:
  1. Tải và tiền xử lý chuỗi nến H4 lịch sử XAU/USD (không có Data Leakage).
  2. Gán nhãn động thích nghi theo biến động ATR (Adaptive ATR Labeling).
  3. Huấn luyện và kiểm định đối chiếu 4 mô hình:
     - Baseline 1: Random Forest (Mô hình học máy truyền thống kinh điển)
     - Baseline 2: Standard LSTM (Mạng nơ-ron hồi quy chuỗi thời gian)
     - Baseline 3: Standard GRU (Gated Recurrent Unit tiêu chuẩn)
     - Proposed   : CNN-BiGRU-Attention (Tích chập 1D + BiGRU + Multi-Head Self-Attention)
  4. Kiểm định chéo chuỗi thời gian (5-Fold Walk-Forward TimeSeriesSplit) tính Mean ± Std.
  5. Đánh giá kiểm thử Out-of-Sample (Test set 20%).
  6. Tự động xuất biểu đồ phân giải cao và bảng Markdown phục vụ Báo cáo Khóa luận.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.utils.class_weight import compute_class_weight

from src.config import DATA_DIR, TIME_STEPS
from src.data.features import FeatureEngine
from src.models.trainer import ModelTrainer

# Thiết lập thư mục lưu ảnh báo cáo
REPORT_IMG_DIR = os.path.join(PROJECT_ROOT, "bao_cao", "hinh_anh")
os.makedirs(REPORT_IMG_DIR, exist_ok=True)


def build_standard_lstm(input_shape):
    """Mô hình Baseline 2: Standard Single-Layer LSTM."""
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.LSTM(32)(inputs)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(16, activation='relu')(x)
    outputs = tf.keras.layers.Dense(3, activation='softmax')(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="Standard_LSTM")
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def build_standard_gru(input_shape):
    """Mô hình Baseline 3: Standard Single-Layer GRU."""
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.GRU(32)(inputs)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(16, activation='relu')(x)
    outputs = tf.keras.layers.Dense(3, activation='softmax')(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="Standard_GRU")
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def build_proposed_cnn_bigru_attention(input_shape):
    """
    Mô hình Đề xuất: Compact CNN-BiGRU với Multi-Head Self-Attention.
    """
    inputs = tf.keras.Input(shape=input_shape, name="sequence_input")
    # Khối Conv1D
    x = tf.keras.layers.Conv1D(filters=48, kernel_size=3, padding='same', activation='relu')(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv1D(filters=32, kernel_size=3, padding='same', activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling1D(pool_size=2)(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    # Khối BiGRU 2 chiều
    gru_seq = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(32, return_sequences=True))(x)
    gru_seq = tf.keras.layers.Dropout(0.2)(gru_seq)

    # Khối Chú ý Đa đầu (Self-Attention)
    attn_out = tf.keras.layers.MultiHeadAttention(num_heads=4, key_dim=16)(
        query=gru_seq, value=gru_seq, key=gru_seq
    )
    attn_res = tf.keras.layers.Add()([gru_seq, attn_out])
    attn_norm = tf.keras.layers.LayerNormalization()(attn_res)

    # Tổng hợp đặc trưng thời gian
    pooled = tf.keras.layers.GlobalAveragePooling1D()(attn_norm)

    # MLP Head
    d = tf.keras.layers.Dense(32, activation='relu')(pooled)
    d = tf.keras.layers.Dropout(0.2)(d)
    outputs = tf.keras.layers.Dense(3, activation='softmax')(d)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="Proposed_CNN_BiGRU_Attention")
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0008),
                  loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def run_benchmark():
    print("=" * 78)
    print("   VQUANT ACADEMIC BENCHMARK SUITE - TIME-SERIES CROSS-VALIDATION")
    print("   Đề tài: Nghiên cứu mô hình học máy trong dự đoán xu hướng tài chính")
    print("   Tác giả: Nguyễn Mạnh Cường _ B22DCCN099 (Khoa CNTT 1 - PTIT)")
    print("=" * 78)

    # 1. Tải và xử lý dữ liệu
    csv_path = os.path.join(DATA_DIR, "XAUUSD_H4.csv")
    if not os.path.exists(csv_path):
        print(f"[Lỗi] Không tìm thấy file dữ liệu: {csv_path}")
        return

    print(f"\n[1/6] Tải dữ liệu lịch sử nến H4 từ {csv_path}...")
    df_raw = pd.read_csv(csv_path)
    print(f" -> Dữ liệu thô: {len(df_raw)} dòng nến.")

    print("\n[2/6] Trích xuất đặc trưng kỹ thuật Causal (Không rò rỉ dữ liệu)...")
    df_feat = FeatureEngine.add_features(df_raw)
    print(f" -> Kích thước ma trận đặc trưng: {df_feat.shape[0]} dòng, {df_feat.shape[1]} cột.")

    print("\n[3/6] Gán nhãn động thích nghi (Adaptive ATR Labeling) và phân rã chuỗi...")
    trainer = ModelTrainer(time_steps=TIME_STEPS)
    X, y, scaler = trainer.prepare_sequences(df_feat)

    unique, counts = np.unique(y, return_counts=True)
    class_names = ['HOLD (Đi ngang)', 'BUY (Tăng)', 'SELL (Giảm)']
    print(" -> Phân bố các lớp mẫu:")
    for u, c in zip(unique, counts):
        print(f"    • Lớp {u} ({class_names[u]}): {c} mẫu ({c/len(y)*100:.1f}%)")

    # Phân tách tập Huấn luyện (Train) và tập Kiểm thử độc lập (Test) theo trục thời gian (Không xáo trộn)
    split_idx = int(len(X) * 0.80)
    X_train_val, X_test = X[:split_idx], X[split_idx:]
    y_train_val, y_test = y[:split_idx], y[split_idx:]

    y_train_cat = tf.keras.utils.to_categorical(y_train_val, num_classes=3)
    y_test_cat = tf.keras.utils.to_categorical(y_test, num_classes=3)

    classes = np.unique(y_train_val)
    weights = compute_class_weight('balanced', classes=classes, y=y_train_val)
    class_weight_dict = dict(zip(classes, weights))

    print(f"\n -> Phân chia Time-Series: Train/Val = {len(X_train_val)} mẫu | Test Out-of-Sample = {len(X_test)} mẫu")

    # 4. Kiểm định chéo chuỗi thời gian (Walk-Forward TimeSeriesSplit)
    print("\n[4/6] Thực hiện 5-Fold Walk-Forward Cross-Validation trên tập Train/Val...")
    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = {
        'Random Forest': {'acc': [], 'f1': []},
        'Standard LSTM': {'acc': [], 'f1': []},
        'Standard GRU': {'acc': [], 'f1': []},
        'Proposed CNN-BiGRU-Attention': {'acc': [], 'f1': []}
    }

    fold_idx = 1
    input_shape = (X.shape[1], X.shape[2])

    for tr_idx, val_idx in tscv.split(X_train_val):
        print(f"  --- Fold {fold_idx}/5 (Train: {len(tr_idx)} mẫu | Val: {len(val_idx)} mẫu) ---")
        X_f_tr, X_f_val = X_train_val[tr_idx], X_train_val[val_idx]
        y_f_tr, y_f_val = y_train_val[tr_idx], y_train_val[val_idx]
        y_f_tr_cat = tf.keras.utils.to_categorical(y_f_tr, num_classes=3)

        # 1. RF Fold
        rf_fold = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
        rf_fold.fit(X_f_tr.reshape(X_f_tr.shape[0], -1), y_f_tr)
        p_rf = rf_fold.predict(X_f_val.reshape(X_f_val.shape[0], -1))
        cv_scores['Random Forest']['acc'].append(accuracy_score(y_f_val, p_rf) * 100)
        cv_scores['Random Forest']['f1'].append(f1_score(y_f_val, p_rf, average='macro', zero_division=0) * 100)

        # 2. LSTM Fold
        lstm_f = build_standard_lstm(input_shape)
        lstm_f.fit(X_f_tr, y_f_tr_cat, epochs=15, batch_size=32, verbose=0, class_weight=class_weight_dict)
        p_lstm = np.argmax(lstm_f.predict(X_f_val, verbose=0), axis=1)
        cv_scores['Standard LSTM']['acc'].append(accuracy_score(y_f_val, p_lstm) * 100)
        cv_scores['Standard LSTM']['f1'].append(f1_score(y_f_val, p_lstm, average='macro', zero_division=0) * 100)

        # 3. GRU Fold
        gru_f = build_standard_gru(input_shape)
        gru_f.fit(X_f_tr, y_f_tr_cat, epochs=15, batch_size=32, verbose=0, class_weight=class_weight_dict)
        p_gru = np.argmax(gru_f.predict(X_f_val, verbose=0), axis=1)
        cv_scores['Standard GRU']['acc'].append(accuracy_score(y_f_val, p_gru) * 100)
        cv_scores['Standard GRU']['f1'].append(f1_score(y_f_val, p_gru, average='macro', zero_division=0) * 100)

        # 4. Proposed CNN-BiGRU-Attention Fold
        prop_f = build_proposed_cnn_bigru_attention(input_shape)
        prop_f.fit(X_f_tr, y_f_tr_cat, epochs=15, batch_size=32, verbose=0, class_weight=class_weight_dict)
        p_prop = np.argmax(prop_f.predict(X_f_val, verbose=0), axis=1)
        cv_scores['Proposed CNN-BiGRU-Attention']['acc'].append(accuracy_score(y_f_val, p_prop) * 100)
        cv_scores['Proposed CNN-BiGRU-Attention']['f1'].append(f1_score(y_f_val, p_prop, average='macro', zero_division=0) * 100)

        fold_idx += 1

    print("\n -> KẾT QUẢ TIME-SERIES CROSS-VALIDATION (5-FOLD MEAN ± STD):")
    for m_name, s in cv_scores.items():
        acc_m, acc_std = np.mean(s['acc']), np.std(s['acc'])
        f1_m, f1_std = np.mean(s['f1']), np.std(s['f1'])
        print(f"    • {m_name:<30}: Accuracy = {acc_m:.2f} ± {acc_std:.2f}% | F1-Score = {f1_m:.2f} ± {f1_std:.2f}%")

    # 5. Huấn luyện Full Train/Val và Đánh giá Out-of-Sample trên Test Set
    print("\n[5/6] Huấn luyện toàn diện và Đánh giá Out-of-Sample trên tập Test độc lập...")
    results = []
    histories = {}
    y_preds = {}

    X_train_flat = X_train_val.reshape(X_train_val.shape[0], -1)
    X_test_flat = X_test.reshape(X_test.shape[0], -1)

    # MÔ HÌNH 1: RANDOM FOREST
    print("\n -> [1/4] Final Test: Random Forest...")
    t0 = time.time()
    rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, class_weight='balanced')
    rf.fit(X_train_flat, y_train_val)
    t_train_rf = time.time() - t0
    t_inf = time.time()
    p_rf = rf.predict(X_test_flat)
    t_inf_rf = (time.time() - t_inf) / len(X_test) * 1000
    y_preds['Random Forest'] = p_rf

    results.append({
        'Model': 'Random Forest (Baseline 1)',
        'CV Accuracy (%)': f"{np.mean(cv_scores['Random Forest']['acc']):.2f} ± {np.std(cv_scores['Random Forest']['acc']):.2f}",
        'CV F1 (%)': f"{np.mean(cv_scores['Random Forest']['f1']):.2f} ± {np.std(cv_scores['Random Forest']['f1']):.2f}",
        'Test Accuracy (%)': round(accuracy_score(y_test, p_rf) * 100, 2),
        'Test Precision (%)': round(precision_score(y_test, p_rf, average='macro', zero_division=0) * 100, 2),
        'Test Recall (%)': round(recall_score(y_test, p_rf, average='macro', zero_division=0) * 100, 2),
        'Test F1 (%)': round(f1_score(y_test, p_rf, average='macro', zero_division=0) * 100, 2),
        'Train Time (s)': round(t_train_rf, 2),
        'Inference (ms)': round(t_inf_rf, 2)
    })

    # MÔ HÌNH 2: STANDARD LSTM
    print(" -> [2/4] Final Test: Standard LSTM...")
    lstm_model = build_standard_lstm(input_shape)
    t0 = time.time()
    h_lstm = lstm_model.fit(X_train_val, y_train_cat, validation_split=0.15, epochs=35, batch_size=32, verbose=0, class_weight=class_weight_dict)
    t_train_lstm = time.time() - t0
    t_inf = time.time()
    p_lstm = np.argmax(lstm_model.predict(X_test, verbose=0), axis=1)
    t_inf_lstm = (time.time() - t_inf) / len(X_test) * 1000
    y_preds['Standard LSTM'] = p_lstm
    histories['Standard LSTM'] = h_lstm

    results.append({
        'Model': 'Standard LSTM (Baseline 2)',
        'CV Accuracy (%)': f"{np.mean(cv_scores['Standard LSTM']['acc']):.2f} ± {np.std(cv_scores['Standard LSTM']['acc']):.2f}",
        'CV F1 (%)': f"{np.mean(cv_scores['Standard LSTM']['f1']):.2f} ± {np.std(cv_scores['Standard LSTM']['f1']):.2f}",
        'Test Accuracy (%)': round(accuracy_score(y_test, p_lstm) * 100, 2),
        'Test Precision (%)': round(precision_score(y_test, p_lstm, average='macro', zero_division=0) * 100, 2),
        'Test Recall (%)': round(recall_score(y_test, p_lstm, average='macro', zero_division=0) * 100, 2),
        'Test F1 (%)': round(f1_score(y_test, p_lstm, average='macro', zero_division=0) * 100, 2),
        'Train Time (s)': round(t_train_lstm, 2),
        'Inference (ms)': round(t_inf_lstm, 2)
    })

    # MÔ HÌNH 3: STANDARD GRU
    print(" -> [3/4] Final Test: Standard GRU...")
    gru_model = build_standard_gru(input_shape)
    t0 = time.time()
    h_gru = gru_model.fit(X_train_val, y_train_cat, validation_split=0.15, epochs=35, batch_size=32, verbose=0, class_weight=class_weight_dict)
    t_train_gru = time.time() - t0
    t_inf = time.time()
    p_gru = np.argmax(gru_model.predict(X_test, verbose=0), axis=1)
    t_inf_gru = (time.time() - t_inf) / len(X_test) * 1000
    y_preds['Standard GRU'] = p_gru
    histories['Standard GRU'] = h_gru

    results.append({
        'Model': 'Standard GRU (Baseline 3)',
        'CV Accuracy (%)': f"{np.mean(cv_scores['Standard GRU']['acc']):.2f} ± {np.std(cv_scores['Standard GRU']['acc']):.2f}",
        'CV F1 (%)': f"{np.mean(cv_scores['Standard GRU']['f1']):.2f} ± {np.std(cv_scores['Standard GRU']['f1']):.2f}",
        'Test Accuracy (%)': round(accuracy_score(y_test, p_gru) * 100, 2),
        'Test Precision (%)': round(precision_score(y_test, p_gru, average='macro', zero_division=0) * 100, 2),
        'Test Recall (%)': round(recall_score(y_test, p_gru, average='macro', zero_division=0) * 100, 2),
        'Test F1 (%)': round(f1_score(y_test, p_gru, average='macro', zero_division=0) * 100, 2),
        'Train Time (s)': round(t_train_gru, 2),
        'Inference (ms)': round(t_inf_gru, 2)
    })

    # MÔ HÌNH 4: PROPOSED CNN-BiGRU-ATTENTION
    print(" -> [4/4] Final Test: Proposed CNN-BiGRU-Attention...")
    prop_model = build_proposed_cnn_bigru_attention(input_shape)
    t0 = time.time()
    h_prop = prop_model.fit(X_train_val, y_train_cat, validation_split=0.15, epochs=35, batch_size=32, verbose=0, class_weight=class_weight_dict)
    t_train_prop = time.time() - t0
    t_inf = time.time()
    p_prop = np.argmax(prop_model.predict(X_test, verbose=0), axis=1)
    t_inf_prop = (time.time() - t_inf) / len(X_test) * 1000
    y_preds['Proposed CNN-BiGRU-Attention'] = p_prop
    histories['Proposed CNN-BiGRU-Attention'] = h_prop

    results.append({
        'Model': 'Proposed CNN-BiGRU-Attention',
        'CV Accuracy (%)': f"{np.mean(cv_scores['Proposed CNN-BiGRU-Attention']['acc']):.2f} ± {np.std(cv_scores['Proposed CNN-BiGRU-Attention']['acc']):.2f}",
        'CV F1 (%)': f"{np.mean(cv_scores['Proposed CNN-BiGRU-Attention']['f1']):.2f} ± {np.std(cv_scores['Proposed CNN-BiGRU-Attention']['f1']):.2f}",
        'Test Accuracy (%)': round(accuracy_score(y_test, p_prop) * 100, 2),
        'Test Precision (%)': round(precision_score(y_test, p_prop, average='macro', zero_division=0) * 100, 2),
        'Test Recall (%)': round(recall_score(y_test, p_prop, average='macro', zero_division=0) * 100, 2),
        'Test F1 (%)': round(f1_score(y_test, p_prop, average='macro', zero_division=0) * 100, 2),
        'Train Time (s)': round(t_train_prop, 2),
        'Inference (ms)': round(t_inf_prop, 2)
    })

    # Xuất bảng Markdown và CSV
    df_res = pd.DataFrame(results)
    csv_out = os.path.join(DATA_DIR, "model_benchmark_results.csv")
    df_res.to_csv(csv_out, index=False)

    md_table_path = os.path.join(REPORT_IMG_DIR, "bang_so_sanh_mo_hinh.md")
    with open(md_table_path, "w", encoding="utf-8") as f:
        f.write("# BẢNG TỔNG HỢP SO SÁNH HIỆU NĂNG CÁC MÔ HÌNH HỌC MÁY\n\n")
        f.write(df_res.to_markdown(index=False))
        f.write("\n\n*Phương pháp kiểm định: 5-Fold Walk-Forward TimeSeriesSplit + Out-of-Sample Test Set (20%).*\n")

    print("\n" + "=" * 78)
    print("   BẢNG TỔNG HỢP ĐỐI CHIẾU CÁC MÔ HÌNH HỌC MÁY (KHOA HỌC CHUẨN MỰC)")
    print("=" * 78)
    print(df_res.to_string(index=False))
    print("=" * 78)

    # 6. Vẽ các biểu đồ khoa học
    print("\n[6/6] Đang vẽ và lưu các biểu đồ báo cáo khoa học vào thư mục bao_cao/hinh_anh/...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    # Biểu đồ 1: So sánh Test Accuracy & F1-Score kèm Walk-Forward CV
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    models = df_res['Model'].tolist()
    x = np.arange(len(models))
    width = 0.35

    ax.bar(x - width/2, df_res['Test Accuracy (%)'], width, label='Test Accuracy (%)', color='#2563EB', edgecolor='black')
    ax.bar(x + width/2, df_res['Test F1 (%)'], width, label='Test F1-Score (%)', color='#059669', edgecolor='black')

    ax.set_ylabel('Tỷ lệ (%)', fontsize=11, fontweight='bold')
    ax.set_title('So sánh Hiệu năng Dự đoán Xu hướng XAU/USD (Out-of-Sample Test Set)', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=9, fontweight='bold')
    ax.set_ylim(0, 75)
    ax.axhline(33.33, color='crimson', linestyle='--', linewidth=1.2, label='Xác suất Ngẫu nhiên (33.33%)')
    ax.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    bar_chart_path = os.path.join(REPORT_IMG_DIR, "model_comparison_bar.png")
    plt.savefig(bar_chart_path, dpi=300)
    plt.close()
    print(f" -> [Đã lưu]: {bar_chart_path}")

    # Biểu đồ 2: Đường cong học tập Loss & Accuracy của mô hình đề xuất
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), dpi=300)
    epochs_range = range(1, len(h_prop.history['loss']) + 1)

    ax1.plot(epochs_range, h_prop.history['loss'], 'b-', label='Train Loss', linewidth=2)
    ax1.plot(epochs_range, h_prop.history['val_loss'], 'r--', label='Val Loss', linewidth=2)
    ax1.set_title('Đường cong Loss (Proposed CNN-BiGRU-Attention)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Epoch', fontsize=10)
    ax1.set_ylabel('Categorical Cross-Entropy', fontsize=10)
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.6)

    ax2.plot(epochs_range, [acc * 100 for acc in h_prop.history['accuracy']], 'b-', label='Train Accuracy', linewidth=2)
    ax2.plot(epochs_range, [acc * 100 for acc in h_prop.history['val_accuracy']], 'r--', label='Val Accuracy', linewidth=2)
    ax2.set_title('Đường cong Độ chính xác (Proposed CNN-BiGRU-Attention)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Epoch', fontsize=10)
    ax2.set_ylabel('Accuracy (%)', fontsize=10)
    ax2.legend()
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    curve_chart_path = os.path.join(REPORT_IMG_DIR, "proposed_model_loss_accuracy.png")
    plt.savefig(curve_chart_path, dpi=300)
    plt.close()
    print(f" -> [Đã lưu]: {curve_chart_path}")

    # Biểu đồ 3: Ma trận nhầm lẫn (Confusion Matrix)
    cm = confusion_matrix(y_test, p_prop, normalize='true') * 100
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    sns.heatmap(cm, annot=True, fmt='.1f', cmap='Blues',
                xticklabels=['HOLD', 'BUY', 'SELL'],
                yticklabels=['HOLD', 'BUY', 'SELL'],
                cbar_kws={'label': 'Tỷ lệ dự đoán đúng (%)'}, ax=ax)
    ax.set_title('Ma trận nhầm lẫn (Confusion Matrix) - Proposed Model', fontsize=11, fontweight='bold')
    ax.set_xlabel('Nhãn Dự Đoán (Predicted)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Nhãn Thực Tế (Actual)', fontsize=10, fontweight='bold')
    plt.tight_layout()
    cm_chart_path = os.path.join(REPORT_IMG_DIR, "confusion_matrix_cnn_bigru.png")
    plt.savefig(cm_chart_path, dpi=300)
    plt.close()
    print(f" -> [Đã lưu]: {cm_chart_path}")

    # Biểu đồ 4: Phân tích Tầm quan trọng Đặc trưng (Feature Importance)
    feat_cols = [c for c in df_feat.columns if c not in ['time', 'real_volume']]
    importances = rf.feature_importances_
    n_features = len(feat_cols)
    avg_importances = np.zeros(n_features)
    for step in range(TIME_STEPS):
        avg_importances += importances[step * n_features : (step + 1) * n_features]
    avg_importances /= TIME_STEPS

    feat_df = pd.DataFrame({'Feature': feat_cols, 'Importance': avg_importances * 100})
    feat_df = feat_df.sort_values(by='Importance', ascending=True)

    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    ax.barh(feat_df['Feature'], feat_df['Importance'], color='#1D4ED8', edgecolor='black')
    ax.set_xlabel('Mức độ Đóng góp Quan trọng (%)', fontsize=10, fontweight='bold')
    ax.set_title('Đánh giá Mức độ Đóng góp của các Chỉ báo Kỹ thuật đối với Dự đoán Giá Vàng', fontsize=11, fontweight='bold')
    plt.tight_layout()
    feat_chart_path = os.path.join(REPORT_IMG_DIR, "feature_importance_analysis.png")
    plt.savefig(feat_chart_path, dpi=300)
    plt.close()
    print(f" -> [Đã lưu]: {feat_chart_path}")

    print("\n" + "=" * 78)
    print(">> TOÀN BỘ THỰC NGHIỆM ĐÃ HOÀN TẤT VÀ LƯU THÀNH CÔNG!")
    print(f">> Đường dẫn ảnh và bảng số liệu: {REPORT_IMG_DIR}")
    print("=" * 78)


if __name__ == "__main__":
    run_benchmark()
