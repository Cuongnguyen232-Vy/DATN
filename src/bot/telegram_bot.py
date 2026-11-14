#!/usr/bin/env python3
"""
V Capital Telegram Remote Control Bot v3
HFT-SAFE: Giao tiep qua file, khong anh huong EA.

Cap nhat:
- Menu "Report" hien thi cac khoang thoi gian cu the (Hom nay, Tuan, Thang...)
- Phan quyen nghiem ngat: Member chi duoc xem Status va Report
- Bieu do Win Rate cho tung bao cao
"""

import os
import re
import asyncio
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, COMMON_FILES_PATH

# ========== CAU HINH ==========
BOT_TOKEN = TELEGRAM_BOT_TOKEN
try:
    OWNER_ID = int(TELEGRAM_CHAT_ID)
except (ValueError, TypeError):
    OWNER_ID = 5831996854      # Fallback Owner ID

CMD_FILE = os.path.join(COMMON_FILES_PATH, "VQUANT.txt")
RESPONSE_FILE = os.path.join(COMMON_FILES_PATH, "VQUANT_RESPONSE.txt")

OWNER_COMMANDS = {"START", "STOP", "PAUSE", "RESUME", "CLOSE_ALL", "CLOSE_BUY", "CLOSE_SELL", "MODE_BUY", "MODE_SELL", "MODE_BOTH"}
PUBLIC_COMMANDS = {"STATUS", "REPORT_MENU", "REPORT_TODAY", "REPORT_WEEK", "REPORT_MONTH", "REPORT_QUARTER", "REPORT_YEAR"}
# ================================

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def send_command(cmd: str) -> bool:
    try:
        with open(CMD_FILE, "w", encoding="utf-16") as f:
            f.write(cmd)
        return True
    except Exception as e:
        print(f"Error writing command: {e}")
        return False

async def wait_for_response(timeout: float = 5.0) -> str:
    elapsed = 0.0
    interval = 0.3
    while elapsed < timeout:
        try:
            if os.path.exists(RESPONSE_FILE):
                with open(RESPONSE_FILE, "r", encoding="utf-16") as f:
                    content = f.read().strip()
                if content:
                    os.remove(RESPONSE_FILE)
                    return content
        except Exception:
            pass
        await asyncio.sleep(interval)
        elapsed += interval
    return ""

def generate_chart(report_text: str) -> io.BytesIO | None:
    """Tao bieu do Dashboard chuyen nghiep tu bao cao"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        
        # Parse data
        wins, losses = 0, 0
        match = re.search(r'\((\d+)W / (\d+)L\)', report_text)
        if match:
            wins = int(match.group(1))
            losses = int(match.group(2))
        
        profit_factor = 0.0
        pf_match = re.search(r'Profit Factor:\s*([\d.]+)', report_text)
        if pf_match: profit_factor = float(pf_match.group(1))
        
        avg_win, avg_loss = 0.0, 0.0
        aw_match = re.search(r'Avg Win:\s*([\d.]+)', report_text)
        if aw_match: avg_win = float(aw_match.group(1))
        al_match = re.search(r'Avg Loss:\s*([\d.]+)', report_text)
        if al_match: avg_loss = float(al_match.group(1))
            
        if wins == 0 and losses == 0:
            return None
            
        title_match = re.search(r'BAO CAO:\s*(.+)', report_text)
        period = title_match.group(1) if title_match else "Performance"

        # Create dual-panel chart
        fig = plt.figure(figsize=(10, 5))
        fig.patch.set_facecolor('#131722')
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
        
        # Panel 1: Win Rate Donut
        ax1 = plt.subplot(gs[0])
        labels = [f'Win\n({wins})', f'Loss\n({losses})']
        sizes = [max(wins, 0.1), max(losses, 0.1)]
        colors = ['#00E676', '#FF1744']
        
        wedges, texts, autotexts = ax1.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            colors=colors, startangle=90, explode=(0.05, 0),
            textprops={'color': 'white', 'fontsize': 11, 'fontweight': 'bold'},
            shadow=True
        )
        
        centre_circle = plt.Circle((0, 0), 0.65, fc='#131722')
        ax1.add_artist(centre_circle)
        
        # Center text
        wr = (wins/(wins+losses)*100) if (wins+losses)>0 else 0
        ax1.text(0, 0, f"{wr:.1f}%\nWin Rate", ha='center', va='center', color='white', fontsize=16, fontweight='bold')
        ax1.set_title(f'V Capital: {period}', color='#b2b5be', fontsize=14, fontweight='bold', pad=20)
        
        # Panel 2: Avg Win vs Loss Bar
        ax2 = plt.subplot(gs[1])
        ax2.set_facecolor('#131722')
        bar_labels = ['Avg Win', 'Avg Loss']
        bar_values = [avg_win, avg_loss]
        bar_colors = ['#00E676', '#FF1744']
        
        bars = ax2.bar(bar_labels, bar_values, color=bar_colors, width=0.5, edgecolor='white', linewidth=0.5)
        
        # Styling ax2
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#2A2E39')
        ax2.spines['bottom'].set_color('#2A2E39')
        ax2.tick_params(colors='#b2b5be')
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (max(bar_values)*0.02),
                    f"{height:.2f}", ha='center', va='bottom', color='white', fontweight='bold')
                    
        # Add Profit Factor text
        ax2.set_title(f'Profit Factor: {profit_factor:.2f}', color='#b2b5be', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf
    except ImportError:
        return None
    except Exception as e:
        print(f"Chart error: {e}")
        return None

# ========== COMMAND HANDLERS ==========

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_owner(user_id):
        keyboard = [
            [InlineKeyboardButton(" START Bot", callback_data="START"),
             InlineKeyboardButton(" STOP Bot", callback_data="STOP")],
            [InlineKeyboardButton(" Pause", callback_data="PAUSE"),
             InlineKeyboardButton(" Resume", callback_data="RESUME")],
            [InlineKeyboardButton(" Chi BUY", callback_data="MODE_BUY"),
             InlineKeyboardButton(" Chi SELL", callback_data="MODE_SELL"),
             InlineKeyboardButton(" BUY & SELL", callback_data="MODE_BOTH")],
            [InlineKeyboardButton(" Status", callback_data="STATUS"),
             InlineKeyboardButton(" Report", callback_data="REPORT_MENU")],
            [InlineKeyboardButton(" Close ALL", callback_data="CLOSE_ALL")],
            [InlineKeyboardButton("Close BUY", callback_data="CLOSE_BUY"),
             InlineKeyboardButton("Close SELL", callback_data="CLOSE_SELL")],
        ]
        title = " <b>V Capital Remote Control</b> \n\nOwner Mode  Full Access"
    else:
        keyboard = [
            [InlineKeyboardButton(" Status", callback_data="STATUS"),
             InlineKeyboardButton(" Report", callback_data="REPORT_MENU")],
        ]
        title = " <b>V Capital Viewer</b> \n\nRead-Only  Chi xem bao cao"
    
    await update.message.reply_text(title, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def show_report_menu(query):
    """Hien thi menu chon thoi gian report"""
    keyboard = [
        [InlineKeyboardButton(" Hom nay", callback_data="REPORT_TODAY"),
         InlineKeyboardButton(" 7 Ngay", callback_data="REPORT_WEEK")],
        [InlineKeyboardButton(" Thang nay", callback_data="REPORT_MONTH"),
         InlineKeyboardButton(" 3 Thang", callback_data="REPORT_QUARTER")],
        [InlineKeyboardButton(" Nam nay", callback_data="REPORT_YEAR")]
    ]
    await query.edit_message_text(
        " <b>Chon khoang thoi gian bao cao:</b>", 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="HTML"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cmd = query.data
    user_id = query.from_user.id
    
    # Kiem tra quyen
    if cmd in OWNER_COMMANDS and not is_owner(user_id):
        await query.answer(" BAN KHONG CO QUYEN!\nChi Chu Bot (Owner) moi duoc phep dung nut nay.", show_alert=True)
        return
        
    if cmd == "REPORT_MENU":
        await show_report_menu(query)
        return
    
    if send_command(cmd):
        await query.edit_message_text(f" Dang lay du lieu tu MT5...")
        response = await wait_for_response(timeout=5.0)
        if response:
            footer = "\n\n<i> 2026 Copyright by <a href='https://t.me/nguyenmanhcuong'>@nguyenmanhcuong</a></i>"
            await query.edit_message_text(response + footer, parse_mode="HTML")
            if cmd.startswith("REPORT_"):
                chart = generate_chart(response)
                if chart:
                    await query.message.reply_photo(photo=chart)
        else:
            await query.edit_message_text(f" EA chua phan hoi lenh {cmd}.")
    else:
        await query.edit_message_text(" Loi ghi file VQUANT.txt!")

# Shortcut commands
async def _send_and_wait(update: Update, cmd: str, owner_only: bool = False):
    user_id = update.effective_user.id
    if owner_only and not is_owner(user_id):
        await update.message.reply_text(" Ban khong co quyen thuc hien lenh nay.")
        return
    
    if send_command(cmd):
        msg = await update.message.reply_text(" Dang xu ly...")
        response = await wait_for_response(timeout=5.0)
        if response:
            footer = "\n\n<i> 2026 Copyright by <a href='https://t.me/nguyenmanhcuong'>@nguyenmanhcuong</a></i>"
            await msg.edit_text(response + footer, parse_mode="HTML")
            if cmd.startswith("REPORT_"):
                chart = generate_chart(response)
                if chart:
                    await update.message.reply_photo(photo=chart)
        else:
            await msg.edit_text(" EA chua phan hoi.")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_and_wait(update, "STATUS")

async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(" Hom nay", callback_data="REPORT_TODAY"),
         InlineKeyboardButton(" 7 Ngay", callback_data="REPORT_WEEK")],
        [InlineKeyboardButton(" Thang nay", callback_data="REPORT_MONTH"),
         InlineKeyboardButton(" 3 Thang", callback_data="REPORT_QUARTER")],
        [InlineKeyboardButton(" Nam nay", callback_data="REPORT_YEAR")]
    ]
    await update.message.reply_text(
        " <b>Chon khoang thoi gian bao cao:</b>", 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="HTML"
    )

async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_and_wait(update, "STOP", owner_only=True)

async def cmd_go(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_and_wait(update, "START", owner_only=True)

async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_and_wait(update, "PAUSE", owner_only=True)

async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_and_wait(update, "RESUME", owner_only=True)

async def cmd_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_and_wait(update, "CLOSE_ALL", owner_only=True)

async def post_init(application: Application):
    commands = [
        BotCommand("menu", "Mo bang dieu khien (Menu chinh)"),
        BotCommand("status", "Xem trang thai lenh va tai khoan"),
        BotCommand("report", "Xem bao cao hieu suat (Win Rate)"),
        BotCommand("go", " Tiep tuc mo lenh moi (Start)"),
        BotCommand("pause", " Tam dung mo lenh (Pause)"),
        BotCommand("stop", " Dung va dong moi lenh (Stop)"),
        BotCommand("close", " Dong toan bo lenh (Close All)")
    ]
    await application.bot.set_my_commands(commands)

# ========== MAIN ==========
def main():
    print("V Capital Telegram Bot v3 (HFT-SAFE)")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("go", cmd_go))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("close", cmd_close))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
