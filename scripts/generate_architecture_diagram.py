# -*- coding: utf-8 -*-
"""
Script to generate the 100% accurate System Architecture Diagram for VQuant DSS Thesis.
Resolution: 2400 x 2400 px, 300 DPI.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, BoxStyle, ArrowStyle
import numpy as np

def create_diagram(output_path):
    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Background
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    # Color Palette
    PRIMARY_NAVY = '#0F2C59'
    HEADER_BLUE = '#1A365D'
    CARD_BG = '#FFFFFF'
    BORDER_COLOR = '#CBD5E1'
    ACCENT_CYAN = '#0284C7'
    ACCENT_GREEN = '#10B981'
    ACCENT_AMBER = '#F59E0B'
    TEXT_DARK = '#0F172A'
    TEXT_MUTED = '#475569'
    ARROW_COLOR = '#334155'
    
    # Helper to draw modern card with header
    def draw_component_card(x, y, w, h, title, subheader=None):
        # Card Body
        body = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0,rounding_size=2.5",
                              facecolor=CARD_BG, edgecolor=BORDER_COLOR,
                              linewidth=1.8, zorder=2)
        ax.add_patch(body)
        
        # Header banner (clip to top of card)
        hh = 11.5
        header = FancyBboxPatch((x, y + h - hh), w, hh,
                                boxstyle="round,pad=0,rounding_size=2.5",
                                facecolor=PRIMARY_NAVY, edgecolor=PRIMARY_NAVY,
                                linewidth=1.5, zorder=3)
        ax.add_patch(header)
        
        # Bottom cover of header to make rectangular connection with body
        rect_cover = patches.Rectangle((x, y + h - hh), w, 4,
                                       facecolor=PRIMARY_NAVY, edgecolor=PRIMARY_NAVY,
                                       linewidth=0, zorder=4)
        ax.add_patch(rect_cover)
        
        # Header Text
        ax.text(x + w/2, y + h - 5.5, title,
                ha='center', va='center', color='#FFFFFF',
                fontsize=13.5, fontweight='bold', family='sans-serif', zorder=5)
        if subheader:
            ax.text(x + w/2, y + h - 9.0, subheader,
                    ha='center', va='center', color='#93C5FD',
                    fontsize=9.5, fontweight='semibold', family='sans-serif', zorder=5)

    # 1. TOP-LEFT: AI ENGINE (PYTHON)
    draw_component_card(4, 52, 42, 44, "AI ENGINE (PYTHON)", "Dự báo Xu hướng & Lượng hóa Rủi ro")
    
    # Sub-badges for AI models inside AI Engine
    models = [
        ("1D-CNN", "Trích xuất mẫu nến", 6, 81.5, 11, 6.2, '#E0F2FE', '#0369A1'),
        ("BiGRU", "Động lượng 2 chiều", 19.5, 81.5, 11, 6.2, '#E0F2FE', '#0369A1'),
        ("Attention", "Tập trung bước ngoặt", 33, 81.5, 11, 6.2, '#E0F2FE', '#0369A1'),
        ("NLP FinBERT", "Lọc tin vĩ mô 24/7", 8.5, 73.5, 15, 6.2, '#FEF3C7', '#B45309'),
        ("KNN Matcher", "So khớp sóng giá", 26.5, 73.5, 15, 6.2, '#DCFCE7', '#15803D')
    ]
    for name, desc, bx, by, bw, bh, bg_c, border_c in models:
        badge = FancyBboxPatch((bx, by), bw, bh,
                               boxstyle="round,pad=0,rounding_size=1.2",
                               facecolor=bg_c, edgecolor=border_c,
                               linewidth=1.2, zorder=4)
        ax.add_patch(badge)
        ax.text(bx + bw/2, by + bh*0.62, name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=border_c, zorder=5)
        ax.text(bx + bw/2, by + bh*0.25, desc, ha='center', va='center',
                fontsize=6.5, fontweight='normal', color=TEXT_MUTED, zorder=5)
        
    # AI Engine Description items
    ai_features = [
        "Thu thập & làm sạch chuỗi nến H4, M15",
        "Trích xuất 20 đặc trưng kỹ thuật & ATR",
        "Sinh tín hiệu (BUY / SELL / HOLD) & Độ tin cậy",
        "Sentinel 24/7: Cào lịch kinh tế ForexFactory"
    ]
    for i, feat in enumerate(ai_features):
        ax.plot(7, 69.5 - i * 4.2, marker='o', markersize=4, color=ACCENT_CYAN, zorder=5)
        ax.text(8.8, 69.5 - i * 4.2, feat, ha='left', va='center',
                fontsize=8.2, color=TEXT_DARK, fontweight='medium', zorder=5)

    # 2. TOP-RIGHT: TRADING BOT (MQL5 / METATRADER 5)
    draw_component_card(54, 52, 42, 44, "TRADING BOT (MQL5)", "Thực thi Lệnh & Quản trị Vốn (MT5)")
    
    # Sub-badges for Trading Bot components
    bot_badges = [
        ("IPC Listener", "Đọc tín hiệu JSON", 56.5, 81.5, 17, 6.2, '#F1F5F9', '#475569'),
        ("ATR Grid DCA", "Lưới co giãn vốn", 76.5, 81.5, 17, 6.2, '#EFF6FF', '#2563EB'),
        ("Hedging Lock", "Khóa rủi ro 2 chiều", 56.5, 73.5, 17, 6.2, '#FEE2E2', '#B91C1C'),
        ("Chart Dashboard", "Bảng nút bấm trực quan", 76.5, 73.5, 17, 6.2, '#ECFDF5', '#047857')
    ]
    for name, desc, bx, by, bw, bh, bg_c, border_c in bot_badges:
        badge = FancyBboxPatch((bx, by), bw, bh,
                               boxstyle="round,pad=0,rounding_size=1.2",
                               facecolor=bg_c, edgecolor=border_c,
                               linewidth=1.2, zorder=4)
        ax.add_patch(badge)
        ax.text(bx + bw/2, by + bh*0.62, name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=border_c, zorder=5)
        ax.text(bx + bw/2, by + bh*0.25, desc, ha='center', va='center',
                fontsize=6.5, fontweight='normal', color=TEXT_MUTED, zorder=5)

    bot_features = [
        "Khớp lệnh tự động độ trễ thấp (Mili-giây)",
        "Tính điểm hòa vốn rổ lệnh (Break-even)",
        "Kiểm soát sụt giảm tài khoản (Max Drawdown < 25%)",
        "Ghi nhật ký lịch sử giao dịch & xuất logs"
    ]
    for i, feat in enumerate(bot_features):
        ax.plot(57, 69.5 - i * 4.2, marker='o', markersize=4, color=ACCENT_GREEN, zorder=5)
        ax.text(58.8, 69.5 - i * 4.2, feat, ha='left', va='center',
                fontsize=8.2, color=TEXT_DARK, fontweight='medium', zorder=5)

    # 3. BOTTOM-LEFT: FASTAPI DASHBOARD & TELEGRAM BOT
    draw_component_card(4, 4, 42, 42, "FASTAPI & TELEGRAM BOT", "Giám sát Thời gian thực & Cảnh báo")
    
    # Sub-badges
    dash_badges = [
        ("FastAPI Server", "WebSocket Telemetry", 6.5, 33.5, 17.5, 6.2, '#F0FDF4', '#16A34A'),
        ("Telegram Bot", "Cảnh báo & Lệnh từ xa", 26, 33.5, 17.5, 6.2, '#F0F9FF', '#0284C7'),
    ]
    for name, desc, bx, by, bw, bh, bg_c, border_c in dash_badges:
        badge = FancyBboxPatch((bx, by), bw, bh,
                               boxstyle="round,pad=0,rounding_size=1.2",
                               facecolor=bg_c, edgecolor=border_c,
                               linewidth=1.2, zorder=4)
        ax.add_patch(badge)
        ax.text(bx + bw/2, by + bh*0.62, name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=border_c, zorder=5)
        ax.text(bx + bw/2, by + bh*0.25, desc, ha='center', va='center',
                fontsize=6.5, fontweight='normal', color=TEXT_MUTED, zorder=5)

    dash_features = [
        "Biểu đồ Radar suy luận AI & Tín hiệu nến",
        "Báo cáo định lượng Quant Tear-Sheet tương tác",
        "Cảnh báo Telegram khi có tín hiệu BUY/SELL",
        "Thông báo tin tức vĩ mô đỏ sắp công bố"
    ]
    for i, feat in enumerate(dash_features):
        ax.plot(7, 28.5 - i * 4.6, marker='o', markersize=4, color=ACCENT_CYAN, zorder=5)
        ax.text(8.8, 28.5 - i * 4.6, feat, ha='left', va='center',
                fontsize=8.2, color=TEXT_DARK, fontweight='medium', zorder=5)

    # 4. BOTTOM-RIGHT: BROKER (SÀN GIAO DỊCH EXNESS / MT5 SERVERS)
    draw_component_card(54, 4, 42, 42, "BROKER (SÀN GIAO DỊCH)", "Thanh khoản & Dữ liệu Thị trường (Exness)")
    
    broker_badges = [
        ("Market Data API", "Giá nến OHLCV thời gian thực", 56.5, 33.5, 17.5, 6.2, '#FEF2F2', '#DC2626'),
        ("Trade Servers", "Khớp lệnh thị trường 24/5", 76, 33.5, 17.5, 6.2, '#F8FAFC', '#334155'),
    ]
    for name, desc, bx, by, bw, bh, bg_c, border_c in broker_badges:
        badge = FancyBboxPatch((bx, by), bw, bh,
                               boxstyle="round,pad=0,rounding_size=1.2",
                               facecolor=bg_c, edgecolor=border_c,
                               linewidth=1.2, zorder=4)
        ax.add_patch(badge)
        ax.text(bx + bw/2, by + bh*0.62, name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=border_c, zorder=5)
        ax.text(bx + bw/2, by + bh*0.25, desc, ha='center', va='center',
                fontsize=6.5, fontweight='normal', color=TEXT_MUTED, zorder=5)

    broker_features = [
        "Cặp giao dịch mục tiêu: XAU/USD (Vàng giao ngay)",
        "Cung cấp bước nhảy giá Tick và Nến H4/M15",
        "Cổng định tuyến lệnh tới trung tâm thanh khoản",
        "Tài khoản thực nghiệm: Exness Demo Pro ECN"
    ]
    for i, feat in enumerate(broker_features):
        ax.plot(57, 28.5 - i * 4.6, marker='o', markersize=4, color=ACCENT_AMBER, zorder=5)
        ax.text(58.8, 28.5 - i * 4.6, feat, ha='left', va='center',
                fontsize=8.2, color=TEXT_DARK, fontweight='medium', zorder=5)

    # ================= ARROWS & FLOWS =================

    # Flow 1: AI ENGINE -> TRADING BOT (Horizontal Top)
    ax.annotate('', xy=(53.5, 75), xytext=(46.5, 75),
                arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=2.5, headwidth=9, headlength=9),
                zorder=6)
    
    # Pill label for IPC
    ipc_pill = FancyBboxPatch((44, 76.8), 12, 5.8,
                              boxstyle="round,pad=0,rounding_size=1.5",
                              facecolor='#FEE2E2', edgecolor='#EF4444', linewidth=1.2, zorder=7)
    ax.add_patch(ipc_pill)
    ax.text(50, 80.5, "IPC (File-based)", ha='center', va='center',
            fontsize=8.2, fontweight='bold', color='#991B1B', zorder=8)
    ax.text(50, 78.2, "Signal JSON / Common Files", ha='center', va='center',
            fontsize=6.5, fontweight='medium', color='#7F1D1D', zorder=8)

    # Flow 2: AI ENGINE <-> FASTAPI DASHBOARD & TELEGRAM (Vertical Left)
    ax.annotate('', xy=(25, 46.5), xytext=(25, 51.5),
                arrowprops=dict(facecolor=ARROW_COLOR, edgecolor=ARROW_COLOR, width=2, headwidth=7, headlength=7),
                zorder=6)
    ax.annotate('', xy=(25, 51.5), xytext=(25, 46.5),
                arrowprops=dict(facecolor=ARROW_COLOR, edgecolor=ARROW_COLOR, width=2, headwidth=7, headlength=7),
                zorder=6)
    
    left_pill = FancyBboxPatch((15.5, 47.2), 19, 4.4,
                               boxstyle="round,pad=0,rounding_size=1.2",
                               facecolor='#F1F5F9', edgecolor='#94A3B8', linewidth=1, zorder=7)
    ax.add_patch(left_pill)
    ax.text(25, 49.4, "Telemetry, Logs & Cảnh báo", ha='center', va='center',
            fontsize=7.5, fontweight='bold', color=TEXT_DARK, zorder=8)

    # Flow 3: TRADING BOT <-> BROKER (Vertical Right)
    ax.annotate('', xy=(75, 46.5), xytext=(75, 51.5),
                arrowprops=dict(facecolor='#0284C7', edgecolor='#0284C7', width=2, headwidth=7, headlength=7),
                zorder=6)
    ax.annotate('', xy=(75, 51.5), xytext=(75, 46.5),
                arrowprops=dict(facecolor='#0284C7', edgecolor='#0284C7', width=2, headwidth=7, headlength=7),
                zorder=6)
    
    right_pill = FancyBboxPatch((64, 47.2), 22, 4.4,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor='#E0F2FE', edgecolor='#0284C7', linewidth=1, zorder=7)
    ax.add_patch(right_pill)
    ax.text(75, 49.4, "Nến OHLCV & Khớp lệnh", ha='center', va='center',
            fontsize=7.5, fontweight='bold', color='#0369A1', zorder=8)

    # Flow 4: TRADING BOT <-> DASHBOARD (Diagonal/Feedback)
    ax.annotate('', xy=(46.5, 38), xytext=(53.5, 54),
                arrowprops=dict(facecolor='#10B981', edgecolor='#10B981', width=1.8, headwidth=6, headlength=6),
                zorder=6)
    diag_pill = FancyBboxPatch((40, 44), 18, 4.0,
                               boxstyle="round,pad=0,rounding_size=1.0",
                               facecolor='#ECFDF5', edgecolor='#10B981', linewidth=1, zorder=7)
    ax.add_patch(diag_pill)
    ax.text(49, 46.0, "PnL, Trạng thái & Lệnh", ha='center', va='center',
            fontsize=7.0, fontweight='bold', color='#047857', zorder=8)

    # Title Banner at Top
    title_box = FancyBboxPatch((15, 96.5), 70, 3.2,
                               boxstyle="round,pad=0,rounding_size=1.0",
                               facecolor='#1E293B', edgecolor='#1E293B', linewidth=1, zorder=7)
    ax.add_patch(title_box)
    ax.text(50, 98.1, "SƠ ĐỒ KIẾN TRÚC TỔNG THỂ HỆ THỐNG VQUANT DSS", ha='center', va='center',
            fontsize=10.5, fontweight='bold', color='#F8FAFC', zorder=8)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Da tao so do kien truc chuan 100%: {output_path}")

if __name__ == '__main__':
    target = r"c:\KLTNN\bao_cao\hinh_anh\system_architecture_diagram.png"
    create_diagram(target)
