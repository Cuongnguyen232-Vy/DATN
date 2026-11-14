# -*- coding: utf-8 -*-
"""
Module: Deep Learning Model Trainer
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
"""

import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from src.config import SCALER_PATH, MODEL_PATH, TIME_STEPS, BASE_DIR
from src.models.gru_model import TradingGRU


class ModelTrainer:
    def __init__(self, time_steps=TIME_STEPS):
        self.time_steps = time_steps

    def prepare_sequences(self, df: pd.DataFrame):
        """
        Chuẩn bị chuỗi thời gian (Time-series sequences) và gán nhãn thích nghi (Adaptive ATR Labeling).
        """
        feature_cols = [c for c in df.columns if c not in ['time', 'real_volume']]
        features = df[feature_cols].values
        print(f"[Feature Matrix] Số lượng đặc trưng: {len(feature_cols)} ({', '.join(feature_cols[:8])}...)")

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(features)

        # Tính toán ATR(14) để gán nhãn thích nghi theo biến động thị trường
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - df['close'].shift(1)).abs()
        tr3 = (df['low'] - df['close'].shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr14 = tr.rolling(14).mean().bfill().values

        X, y = [], []
        for i in range(len(scaled_data) - self.time_steps - 1):
            X.append(scaled_data[i:(i + self.time_steps)])
            current_close = df['close'].iloc[i + self.time_steps - 1]
            future_close = df['close'].iloc[i + self.time_steps]
            diff = future_close - current_close

            # Ngưỡng biến động thích ứng: 0.25 * ATR(14), tối thiểu $3.00 để lọc nhiễu sideway
            idx = i + self.time_steps - 1
            threshold = max(3.0, atr14[idx] * 0.25)

            if diff > threshold:
                y.append(1)   # UP / BUY
            elif diff < -threshold:
                y.append(2)   # DOWN / SELL
            else:
                y.append(0)   # HOLD / NEUTRAL

        return np.array(X), np.array(y), scaler

    def train(self, df: pd.DataFrame):
        print("\n[Preprocessing] Scale MinMax (0-1) va phan ra TimeSteps...")
        X, y, scaler = self.prepare_sequences(df)

        os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
        joblib.dump(scaler, SCALER_PATH)
        print(f" -> Da luu bo chuan hoa Scaler tai: {SCALER_PATH}")

        y_cat = tf.keras.utils.to_categorical(y, num_classes=3)

        # Tính toán trọng số lớp để xử lý mất cân bằng dữ liệu
        classes = np.unique(y)
        class_weights = compute_class_weight('balanced', classes=classes, y=y)
        class_weight_dict = dict(zip(classes, class_weights))
        print(f"[*] Class Weights ap dung: {class_weight_dict}")

        X_train, X_val, y_train, y_val = train_test_split(
            X, y_cat, test_size=0.2, random_state=42, stratify=y
        )
        print(f"[*] Dataset: Train={len(X_train)} samples, Validation={len(X_val)} samples (Stratified)")

        # Khởi tạo mô hình CNN-BiGRU-Attention đề xuất
        model = TradingGRU.build_model(input_shape=(X.shape[1], X.shape[2]))

        callbacks = [
            EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-5, verbose=1)
        ]

        print("\n[Training] Bat dau huan luyen CNN-BiGRU-Attention...")
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=50,
            batch_size=32,
            class_weight=class_weight_dict,
            callbacks=callbacks,
            verbose=1
        )

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        model.save(MODEL_PATH)
        print(f"\n[OK] Model da duoc luu tai: '{MODEL_PATH}'")

        # Lưu đồ thị loss & accuracy
        self._plot_history(history)

        # Đánh giá Metrics
        self.evaluate(model, X, y_cat)

    def _plot_history(self, history):
        try:
            report_dir = os.path.join(BASE_DIR, "bao_cao", "hinh_anh")
            os.makedirs(report_dir, exist_ok=True)
            out_img = os.path.join(report_dir, "training_history.png")

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=200)
            epochs = range(1, len(history.history['loss']) + 1)

            ax1.plot(epochs, history.history['loss'], 'b-', label='Train Loss', linewidth=2)
            ax1.plot(epochs, history.history['val_loss'], 'r--', label='Val Loss', linewidth=2)
            ax1.set_title('Loss Curve (Categorical Cross-Entropy)', fontweight='bold')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True, linestyle=':', alpha=0.6)

            ax2.plot(epochs, [a * 100 for a in history.history['accuracy']], 'b-', label='Train Acc', linewidth=2)
            ax2.plot(epochs, [a * 100 for a in history.history['val_accuracy']], 'r--', label='Val Acc', linewidth=2)
            ax2.set_title('Accuracy Curve (%)', fontweight='bold')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Accuracy (%)')
            ax2.legend()
            ax2.grid(True, linestyle=':', alpha=0.6)

            plt.tight_layout()
            plt.savefig(out_img)
            plt.close()
            print(f" -> Da luu bieu do lich su huan luyen tai: {out_img}")
        except Exception as e:
            print(f"[Warning] Khong the ve bieu do history: {e}")

    def evaluate(self, model, X, y_cat):
        print("\n[Evaluation] Dang tinh toan cac chi so bao cao...")
        predictions = model.predict(X, verbose=0)
        y_pred = np.argmax(predictions, axis=1)
        y_true = np.argmax(y_cat, axis=1)

        target_names = ['HOLD (0)', 'BUY (1)', 'SELL (2)']
        report = classification_report(y_true, y_pred, target_names=target_names)
        print("\n============= BAO CAO HOC THUAT =============")
        print(report)
        print("=============================================")
