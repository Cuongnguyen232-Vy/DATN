//+------------------------------------------------------------------+
//| Inputs.mqh                                                       |
//+------------------------------------------------------------------+
#include "Enums.mqh"

//============================= 1. CÀI ĐẶT CHÍNH ===============================
input ENUM_LANG    Interface_Language       = LANG_VI;           // Ngôn ngữ giao diện
input bool         Show_Dashboard           = true;              // Hiển thị bảng điều khiển
input ENUM_FONT_SZ Dashboard_FontSize       = CO_VUA;            // Cỡ chữ bảng điều khiển
input ENUM_LOG_LVL Log_Level                = LOG_CO_BAN;        // Mức độ ghi log
input ENUM_VC_MODE Trading_Mode_Input       = CHE_DO_BUY_VA_SELL; // Chế độ giao dịch
input int          Take_Profit_Points       = 1000;              // Chốt lời rổ (points)
input long         MagicNumber              = 20241868;          // Số magic
input double       DD_Cutoff_Percent        = 35.0;              // Cắt lỗ khi DD đạt (%)
input bool         Limit_Trading_Hours      = false;             // Giới hạn giờ giao dịch
input int          Start_Hour_GMT7          = 7;                 // Giờ bắt đầu (GMT+7)
input int          End_Hour_GMT7            = 17;                // Giờ kết thúc (GMT+7)
input ENUM_TIMEFRAMES Entry_Timeframe       = PERIOD_M15;        // Khung thời gian vào lệnh
input bool         Entry_Every_Second       = true;              // Chế độ vào lệnh mỗi 1 giây

//============================= 2. CẤU HÌNH MA TRẬN (; CHIA CHU KỲ, , CHIA TẦNG) ============================
input string   Matrix_Volume_Caps    = "0.40, 0.60, 0.60, 0.60, 0.50, 0.35";
input string   Matrix_Start_Lots     = "0.01, 0.02, 0.03, 0.04, 0.05, 0.07"; 
input string   Matrix_Grid_Distances = "1000, 1000, 1000, 1000, 1000, 1000";

//============================= 3. TÁI VÀO LỆNH SAU CHỐT LỜI =====================
input string   _sep_reentry_        = "==== TÁI VÀO LỆNH SAU CHỐT LỜI =====";
input bool     Reentry_After_TP     = true;              // Tự mở lệnh mới sau TP

//============================= 4. BỘ LỌC BIẾN ĐỘNG (ATR SHIELD) =================
input string   _sep_atr_            = "==== BỘ LỌC BIẾN ĐỘNG (ATR) =====";
input bool     Enable_ATR_Grid      = true;          // Bật giãn lưới theo biến động
input ENUM_TIMEFRAMES ATR_Timeframe = PERIOD_M15;    // Khung thời gian đo ATR
input int      ATR_Period           = 14;            // Chu kỳ ATR
input int      ATR_Threshold_Points = 15000;         // Ngưỡng bão (VD: ATR > 4000)
input double   ATR_Grid_Multiplier  = 2.0;           // Hệ số giãn lưới khi có bão (VD: x2)

//============================= 5. BỘ LỌC XU HƯỚNG (EMA) =================
input string   _sep_ema_            = "==== BỘ LỌC XU HƯỚNG (EMA) =====";
input int      EMA_Fast             = 21;           // EMA nhanh
input int      EMA_Slow             = 89;           // EMA chậm
input ENUM_TIMEFRAMES Trend_Timeframe = PERIOD_H4;  // Khung xu hướng chính
input ENUM_TIMEFRAMES EMA_Confirm_Timeframe = PERIOD_H1; // Khung xác nhận EMA
input int      Confirm_Candles      = 2;            // Số nến xác nhận

//============================= 6. TỰ ĐỘNG BẬT/TẮT THEO LÃI/LỖ =========
input string   _sep_auto_pl_        = "==== TỰ ĐỘNG BẬT/TẮT THEO LÃI/LỖ =====";
input bool     AutoOFF_On_Profit    = false;         // Tắt khi có lãi
input double   Profit_To_AutoOFF    = 0.0;           // Ngưỡng lãi để tắt ($)
input bool     AutoOFF_On_Loss      = false;         // Tắt khi lỗ
input double   Loss_To_AutoOFF      = 0.0;           // Ngưỡng lỗ để tắt ($)
input bool     AutoON_After_OFF     = false;         // Tự bật lại sau khi tắt
input int      Wait_Minutes_Before_ON = 60;          // Chờ bao lâu trước khi bật (phút)

//============================= 7. TỰ ĐỘNG BẬT/TẮT THEO GIÁ =================
input string   _sep_auto_price_     = "==== TỰ ĐỘNG BẬT/TẮT THEO GIÁ =====";
input bool     AutoOFF_By_Price     = false;         // Tắt theo mức giá
input double   Upper_Price_OFF      = 0.0;           // Giá trên để tắt
input double   Lower_Price_OFF      = 0.0;           // Giá dưới để tắt
input bool     Close_On_Price_Hit   = true;          // Đóng lệnh khi chạm giá
input bool     AutoON_Price_Return  = false;         // Bật lại khi giá quay về
input double   Upper_Price_ON       = 0.0;           // Giá trên để bật lại
input double   Lower_Price_ON       = 0.0;           // Giá dưới để bật lại

//============================= 8. TELEGRAM REMOTE =================
input string   _sep_tg_             = "==== TELEGRAM REMOTE =====";
input bool     Enable_Telegram      = true;         // Bật đọc/ghi file điều khiển từ xa

//============================= 9. BỘ ĐIỀU KHIỂN AI & SENTINEL =================
input string   _sep_ai_             = "==== BỘ ĐIỀU KHIỂN AI & SENTINEL =====";
input bool     Enable_AI_Bridge     = true;         // Bật nhận tín hiệu AI Deep Learning từ Python
input double   AI_Min_Confidence    = 0.55;         // Ngưỡng độ tự tin tối thiểu (0.55 = 55% cho mô hình 3 class)

//============================= GLOBALS ==============================
string   Sym;
double   PointV, MinLot, MaxLot, LotStep;
int      DigitsValue;
datetime g_startTime;
bool     g_paused = false;
datetime g_lastM15CheckTime = 0;
datetime g_lastSecondCheck  = 0;
ulong    g_seedBuyTicketAfterTP  = 0;
ulong    g_seedSellTicketAfterTP = 0;
double   g_seedBuyLotAfterTP     = 0.0;
double   g_seedSellLotAfterTP    = 0.0;
ENUM_LANG   g_runtimeLang;
ENUM_VC_MODE Trading_Mode = CHE_DO_BUY_VA_SELL;
bool     g_runtime_AI_Bridge = true; // Runtime toggle via chart button
// Auto ON/OFF globals
bool     g_autoOFF_active   = false;
datetime g_autoOFF_time     = 0;

// ATR Caching globals
int      g_hATR             = INVALID_HANDLE;
double   g_current_atr_val  = 0.0;
datetime g_last_atr_time    = 0;
string   g_autoOFF_reason   = "";

// EMA handles
int      g_hEmaFastH4 = INVALID_HANDLE;
int      g_hEmaSlowH4 = INVALID_HANDLE;
int      g_hEmaFastH1 = INVALID_HANDLE;
int      g_hEmaSlowH1 = INVALID_HANDLE;

// Tier system globals
struct TierConfig {
   double volume_cap;
   double start_lot;
   int    grid_distance;
};
struct CycleConfig {
   TierConfig tiers[];
   int        tier_count;
};
CycleConfig g_cycles[];
int         g_cycleCount = 0;

//============================= POSITION CACHE (HFT) ==================
struct PosCache {
   int    cnt_buy,  cnt_sell;
   double lot_buy,  lot_sell;
   double pnl_buy,  pnl_sell;
   double lastPrice_buy, lastPrice_sell;
   datetime lastTime_buy, lastTime_sell;
   double lastLot_buy,  lastLot_sell;
   double wcost_buy, wcost_sell;   // weighted cost = Σ(lot*price)
   // Account cache
   double balance, equity;
};
PosCache g_cache;
//============================= HFT VIRTUAL CACHE ==============================
ulong g_closing_tickets[500];
uint g_closing_times[500];

