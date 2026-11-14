# -*- coding: utf-8 -*-
"""
Module: Deep Learning Architecture - CNN-BiGRU-Attention
Author: Nguyễn Mạnh Cường_B22DCCN099
Project: VQuant Quantitative Trading System
Description:
    Mô hình học sâu tiên tiến kết hợp mạng tích chập 1D (Conv1D),
    mạng hồi quy 2 chiều (Bidirectional GRU), và cơ chế chú ý đa đầu
    (Multi-Head Self-Attention Mechanism with Residual Connections & LayerNorm).
"""

import tensorflow as tf
from tensorflow.keras.layers import (
    Input, Conv1D, BatchNormalization, MaxPooling1D, Dropout,
    Bidirectional, GRU, MultiHeadAttention, LayerNormalization,
    GlobalAveragePooling1D, Dense, Add
)
from tensorflow.keras.models import Model


class TradingGRU:
    @staticmethod
    def build_model(input_shape):
        """
        Khởi tạo mô hình học sâu CNN-BiGRU-Attention:
        1. Dual Conv1D + BatchNorm: Tự động trích xuất các mẫu hình giá và dao động cục bộ.
        2. Bidirectional GRU: Nắm bắt động lực xu hướng cả quá khứ và tiến trình thời gian 2 chiều.
        3. Multi-Head Self-Attention (4 heads): Trọng tâm chú ý vào các nến bước ngoặt biến động.
        4. Residual Skip Connection & Layer Normalization: Chống tiêu biến gradient và ổn định gradient descent.
        5. Head phân loại 3 lớp: HOLD (0), BUY (1), SELL (2).
        """
        print(f"[Model] Xay dung kien truc CNN-BiGRU-Attention (Multi-Head Self-Attention) cho input {input_shape}...")

        inputs = Input(shape=input_shape, name="sequence_features_input")

        # Khối 1: Trích xuất đặc trưng hình thái (Conv1D Block)
        x = Conv1D(filters=48, kernel_size=3, padding='same', activation='relu')(inputs)
        x = BatchNormalization()(x)
        x = Conv1D(filters=32, kernel_size=3, padding='same', activation='relu')(x)
        x = BatchNormalization()(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = Dropout(0.2)(x)

        # Khối 2: Trích xuất phụ thuộc chuỗi thời gian (BiGRU Block)
        gru_seq = Bidirectional(GRU(32, return_sequences=True), name="bidirectional_gru")(x)
        gru_seq = Dropout(0.2)(gru_seq)

        # Khối 3: Cơ chế Chú ý Đa đầu (Multi-Head Self-Attention)
        attn_out = MultiHeadAttention(num_heads=4, key_dim=16, name="multi_head_attention")(
            query=gru_seq, value=gru_seq, key=gru_seq
        )

        # Kết nối tắt phần dư (Residual Connection) & Chuẩn hóa LayerNorm
        attn_residual = Add()([gru_seq, attn_out])
        attn_norm = LayerNormalization()(attn_residual)

        # Khối 4: Tổng hợp đặc trưng thời gian (Global Temporal Pooling)
        pooled = GlobalAveragePooling1D(name="global_temporal_pooling")(attn_norm)

        # Khối 5: Head phân loại xác suất (MLP Classifier)
        d = Dense(32, activation='relu')(pooled)
        d = Dropout(0.2)(d)
        d = Dense(16, activation='relu')(d)
        outputs = Dense(3, activation='softmax', name="direction_probabilities")(d)

        model = Model(inputs=inputs, outputs=outputs, name="CNN_BiGRU_MultiHead_Attention")
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.0008)
        model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
        return model
