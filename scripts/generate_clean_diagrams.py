# -*- coding: utf-8 -*-
"""
Script generating clean, highly visual, low-text, professional academic figures for Chapter 2.
Style: IEEE / Nature Scientific Reports clean aesthetic.
300 DPI, modern institutional palette.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUTPUT_DIR = r"c:\KLTNN\bao_cao\hinh_anh"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_clean_neural_architecture():
    """Hình 2.2: Sơ đồ kiến trúc mạng CNN-BiGRU-Attention trực quan, ít chữ, tập trung vào hình khối và luồng tensor"""
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 45)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Color Palette
    C_INPUT = '#E2E8F0'
    C_CONV = '#BFDBFE'
    C_BIGRU = '#DDD6FE'
    C_ATTN = '#FED7AA'
    C_DENSE = '#BBF7D0'
    C_OUT = '#FECDD3'
    BORDER_DARK = '#334155'

    blocks = [
        # (x, y, w, h, name, shape_txt, fill_color, border_color)
        (3, 10, 12, 25, "Input Window", "(50, 20)", C_INPUT, '#64748B'),
        (20, 10, 13, 25, "Dual Conv1D\n+ MaxPool", "(25, 32)", C_CONV, '#2563EB'),
        (38, 10, 13, 25, "Bidirectional\nGRU", "(25, 64)", C_BIGRU, '#7C3AED'),
        (56, 10, 14, 25, "Multi-Head\nAttention", "(25, 64)", C_ATTN, '#EA580C'),
        (75, 12, 10, 21, "Global Pool\n+ Dense", "(32)", C_DENSE, '#16A34A'),
        (89, 14, 8, 17, "Softmax\nOutput", "(3)", C_OUT, '#E11D48')
    ]

    for x, y, w, h, name, shape, fc, ec in blocks:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.5",
                             facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=2)
        ax.add_patch(box)
        # Block title
        ax.text(x + w/2, y + h/2 + 2, name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=BORDER_DARK, zorder=3)
        # Tensor shape badge
        badge = FancyBboxPatch((x + w/2 - 4.5, y + 2), 9, 3.5, boxstyle="round,pad=0,rounding_size=0.8",
                               facecolor='#FFFFFF', edgecolor=ec, linewidth=1.0, zorder=4)
        ax.add_patch(badge)
        ax.text(x + w/2, y + 3.7, shape, ha='center', va='center',
                fontsize=7.5, fontweight='semibold', color=ec, zorder=5)

    # Arrows between blocks
    arrows = [(15, 22.5, 20, 22.5), (33, 22.5, 38, 22.5),
              (51, 22.5, 56, 22.5), (70, 22.5, 75, 22.5), (85, 22.5, 89, 22.5)]
    for x1, y1, x2, y2 in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor='#475569', edgecolor='#475569',
                                    width=1.5, headwidth=6, headlength=6), zorder=6)

    # Residual skip connection arrow (BiGRU -> Attention output)
    arc_x = [44.5, 44.5, 72.5, 72.5]
    arc_y = [35.0, 40.0, 40.0, 33.0]
    ax.plot(arc_x, arc_y, color='#0284C7', linestyle='--', linewidth=1.5, zorder=6)
    ax.annotate('', xy=(72.5, 33.0), xytext=(72.5, 36.0),
                arrowprops=dict(facecolor='#0284C7', edgecolor='#0284C7',
                                width=1.2, headwidth=5, headlength=5), zorder=6)
    ax.text(58.5, 41.5, "Residual Add + LayerNorm", ha='center', va='center',
            fontsize=7.5, fontweight='bold', color='#0284C7', backgroundcolor='#FFFFFF', zorder=7)

    # Labels below input and output
    ax.text(9, 5, "50 nến H4 x 20 đặc trưng", ha='center', va='center', fontsize=7.5, color='#64748B', style='italic')
    ax.text(93, 7, "[BUY, HOLD, SELL]", ha='center', va='center', fontsize=7.5, color='#BE123C', fontweight='bold')

    plt.tight_layout()
    out_p = os.path.join(OUTPUT_DIR, "clean_neural_architecture.png")
    plt.savefig(out_p, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Da tao hinh kien truc mang sach, it chu: {out_p}")


def generate_clean_dca_price_action():
    """Hình 2.3: Mô tả nguyên lý lưới DCA co giãn ATR & điểm hòa vốn trên biểu đồ giá trực quan"""
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')

    # Simulated Price Action curve (downward then rebound)
    x = np.linspace(0, 10, 500)
    # Price drops from 2730 down to 2690, then rebounds to 2708
    y = 2730 - 38 * (1 - np.exp(-0.45 * x)) + 4 * np.sin(2.5 * x)
    # Rebound at the end
    rebound_idx = 350
    y[rebound_idx:] += 18 * np.linspace(0, 1, len(y) - rebound_idx)**1.3

    ax.plot(x, y, color='#1E293B', linewidth=2.0, label='Đường giá Vàng (XAU/USD)', zorder=3)

    # Grid Order Execution Points (BUY DCA basket)
    order_x = [0.8, 2.5, 4.8, 7.2]
    order_y = [y[int(ox / 10 * 500)] for ox in order_x]
    lots = ["0.01 Lot (Lệnh 1)", "0.02 Lot (Lệnh 2)", "0.03 Lot (Lệnh 3)", "0.04 Lot (Lệnh 4)"]

    for i, (ox, oy, lot) in enumerate(zip(order_x, order_y, lots)):
        ax.plot(ox, oy, marker='^', markersize=9, color='#16A34A', zorder=5)
        ax.text(ox + 0.15, oy - 2.2, f"BUY {lot}", fontsize=7.8, fontweight='bold', color='#15803D', zorder=6)
        if i > 0:
            # Show spacing arrow
            prev_y = order_y[i-1]
            dist = prev_y - oy
            ax.annotate('', xy=(ox, oy), xytext=(ox, prev_y),
                        arrowprops=dict(arrowstyle='<->', color='#2563EB', lw=1.2), zorder=4)
            ax.text(ox - 0.2, (oy + prev_y)/2, f"ATR Grid\nSpacing {i}", ha='right', va='center',
                    fontsize=6.8, color='#1D4ED8', fontweight='semibold')

    # Weighted Break-even line
    break_even_price = 2704.5
    ax.axhline(break_even_price, color='#DC2626', linestyle='--', linewidth=1.8,
               label=f'Giá hòa vốn bình quân (Break-even: {break_even_price})', zorder=4)

    # Take profit line
    tp_price = 2707.0
    ax.axhline(tp_price, color='#16A34A', linestyle=':', linewidth=1.8,
               label=f'Mục tiêu chốt lời toàn rổ (+30 pts)', zorder=4)

    # Exit circle at rebound
    exit_x = 9.4
    exit_y = tp_price
    ax.plot(exit_x, exit_y, marker='o', markersize=12, markerfacecolor='#22C55E', markeredgecolor='#15803D', markeredgewidth=2, zorder=7)
    ax.text(exit_x - 0.3, exit_y + 3.0, "ĐÓNG TOÀN BỘ RỔ CÓ LÃI", ha='right', va='center',
            fontsize=8.5, fontweight='bold', color='#166534',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#DCFCE7', edgecolor='#16A34A', lw=1.2))

    ax.set_title("Cơ chế Quản lý vốn Lưới ma trận DCA co giãn theo ATR & Điểm hòa vốn", fontsize=10.5, fontweight='bold', color='#0F172A', pad=12)
    ax.set_xlabel("Thời gian (Nến)", fontsize=8.5, color='#475569')
    ax.set_ylabel("Mức giá (USD/oz)", fontsize=8.5, color='#475569')
    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E1')
    ax.legend(loc='upper right', fontsize=8.0, framealpha=0.95)

    plt.tight_layout()
    out_p = os.path.join(OUTPUT_DIR, "clean_dca_grid_mechanism.png")
    plt.savefig(out_p, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Da tao hinh DCA Price Action truc quan: {out_p}")


def generate_clean_pattern_matching():
    """Hình 2.4: Mô tả trực quan thuật toán so khớp mẫu hình sóng giá (Cosine Similarity)"""
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')

    # Wave 1: Current 20 candles
    t = np.arange(20)
    np.random.seed(42)
    current_wave = np.sin(t * 0.35) + 0.15 * np.cos(t * 0.7) + np.linspace(0, 0.8, 20)
    # Min-max normalized
    current_norm = (current_wave - np.min(current_wave)) / (np.max(current_wave) - np.min(current_wave))

    # Wave 2: Historical matched wave (Similarity = 0.94)
    hist_wave = current_norm + np.random.normal(0, 0.04, 20)
    hist_norm = (hist_wave - np.min(hist_wave)) / (np.max(hist_wave) - np.min(hist_wave))

    # Future movement of historical wave (it rose!)
    t_future = np.arange(19, 26)
    future_hist = np.linspace(hist_norm[-1], hist_norm[-1] + 0.35, 7) + 0.05 * np.sin(np.arange(7))

    ax.plot(t, current_norm, color='#2563EB', linewidth=2.5, marker='o', markersize=5, label='Sóng nến hiện tại (20 nến H4)', zorder=4)
    ax.plot(t, hist_norm, color='#64748B', linewidth=2.0, linestyle='--', marker='s', markersize=4, label='Mẫu hình lịch sử tương đồng nhất (Cosine Sim = 0.94)', zorder=3)
    ax.plot(t_future, future_hist, color='#16A34A', linewidth=2.2, linestyle=':', marker='^', markersize=5, label='Diễn biến giá tiếp theo trong quá khứ (+Tăng điểm)', zorder=3)

    # Highlight bias injection
    ax.axvspan(19, 25, color='#DCFCE7', alpha=0.35, label='Vùng gợi ý xác suất (Bias BUY)', zorder=1)

    ax.set_title("Nguyên lý So khớp mẫu hình chuỗi thời gian (Cosine Similarity Pattern Matching)", fontsize=10.5, fontweight='bold', color='#0F172A', pad=12)
    ax.set_xlabel("Bước thời gian nến (Window K=20)", fontsize=8.5, color='#475569')
    ax.set_ylabel("Biên độ giá chuẩn hóa [0, 1]", fontsize=8.5, color='#475569')
    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E1')
    ax.legend(loc='upper left', fontsize=7.8, framealpha=0.95)

    plt.tight_layout()
    out_p = os.path.join(OUTPUT_DIR, "clean_pattern_matching.png")
    plt.savefig(out_p, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Da tao hinh Pattern Matching truc quan: {out_p}")


if __name__ == '__main__':
    generate_clean_neural_architecture()
    generate_clean_dca_price_action()
    generate_clean_pattern_matching()
