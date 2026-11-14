//+------------------------------------------------------------------+
//|                                                   VCapital.mq5   |
//| V Capital (XAUUSD) - Hedge DCA Mirror 1–1 TP USD/lot             |
//| (final patched) - CTrade 100%, DCA đúng, Mirror 1–1 chuẩn        |
//+------------------------------------------------------------------+
#property strict
#property description "V Capital - XAUUSD Hedge DCA Mirror 1–1 TP USD/lot"
#property version   "4.0"

#include <Trade/Trade.mqh>   // CTrade

CTrade Trade;

//============================= ENUMS ================================
enum ENUM_LANG    { LANG_VI=0, LANG_EN=1 };
enum ENUM_FONT_SZ { CO_NHO=0, CO_VUA=1, CO_LON=2 };
enum ENUM_LOG_LVL { LOG_CO_BAN=0, LOG_CHI_TIET=1 };
enum ENUM_VC_MODE { CHE_DO_CHI_BUY=0, CHE_DO_CHI_SELL=1, CHE_DO_BUY_VA_SELL=2 };
enum ENUM_LOT_MODE { LOT_MULTIPLIER=0, LOT_STEP=1 };
enum ENUM_TIER_MODE { TIER_BY_COUNT=0, TIER_BY_VOLUME=1 };

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

//============================= HELPERS: UI CLEANUP ===================
void DeleteObjectsByPrefix(const string prefix){
   int total = ObjectsTotal(0);
   for(int i=total-1;i>=0;i--){
      string name = ObjectName(0,i);
      if(StringFind(name,prefix,0)==0) ObjectDelete(0,name);
   }
}

//============================= TIER HELPERS ===========================
int ParseCSVDoubles(const string csv, double &arr[]){
   string parts[];
   int count = StringSplit(csv, ',', parts);
   ArrayResize(arr, count);
   for(int i=0; i<count; i++) arr[i] = StringToDouble(parts[i]);
   return count;
}
int ParseCSVInts(const string csv, int &arr[]){
   string parts[];
   int count = StringSplit(csv, ',', parts);
   ArrayResize(arr, count);
   for(int i=0; i<count; i++) arr[i] = (int)StringToInteger(parts[i]);
   return count;
}
void InitTiers(){
   string cycles_vol[], cycles_lot[], cycles_dist[];
   int nC_vol = StringSplit(Matrix_Volume_Caps, ';', cycles_vol);
   int nC_lot = StringSplit(Matrix_Start_Lots, ';', cycles_lot);
   int nC_dist = StringSplit(Matrix_Grid_Distances, ';', cycles_dist);
   
   g_cycleCount = MathMax(nC_vol, MathMax(nC_lot, nC_dist));
   if(g_cycleCount <= 0) return;
   
   ArrayResize(g_cycles, g_cycleCount);
   
   for(int c=0; c<g_cycleCount; c++){
      string s_vol = (c < nC_vol) ? cycles_vol[c] : (nC_vol > 0 ? cycles_vol[nC_vol-1] : "99.0");
      string s_lot = (c < nC_lot) ? cycles_lot[c] : (nC_lot > 0 ? cycles_lot[nC_lot-1] : "0.01");
      string s_dist = (c < nC_dist) ? cycles_dist[c] : (nC_dist > 0 ? cycles_dist[nC_dist-1] : "2000");
      
      double arr_vol[], arr_lot[];
      int arr_dist[];
      int nT_vol = ParseCSVDoubles(s_vol, arr_vol);
      int nT_lot = ParseCSVDoubles(s_lot, arr_lot);
      int nT_dist = ParseCSVInts(s_dist, arr_dist);
      
      int t_count = MathMax(nT_vol, MathMax(nT_lot, nT_dist));
      if(t_count == 0) t_count = 1; // Failsafe
      g_cycles[c].tier_count = t_count;
      ArrayResize(g_cycles[c].tiers, t_count);
      
      for(int t=0; t<t_count; t++){
         g_cycles[c].tiers[t].volume_cap    = (t < nT_vol)  ? arr_vol[t]  : (nT_vol > 0  ? arr_vol[nT_vol-1]  : 99.0);
         g_cycles[c].tiers[t].start_lot     = (t < nT_lot)  ? arr_lot[t]  : (nT_lot > 0  ? arr_lot[nT_lot-1]  : 0.01);
         g_cycles[c].tiers[t].grid_distance = (t < nT_dist) ? arr_dist[t] : (nT_dist > 0 ? arr_dist[nT_dist-1] : 2000);
      }
   }
   
   Print("V Capital: 2D Matrix Nested Cycles ON — ", g_cycleCount, " Cycles detected.");
   for(int c=0; c<g_cycleCount; c++){
      Print(" Cycle ", c+1, " (", g_cycles[c].tier_count, " tiers):");
      for(int t=0; t<g_cycles[c].tier_count; t++){
         Print("   T", t+1, ": start=", g_cycles[c].tiers[t].start_lot,
               " vol_cap=", g_cycles[c].tiers[t].volume_cap,
               " grid=", g_cycles[c].tiers[t].grid_distance);
      }
   }
}

// === DISPATCHER: Xác định Tầng và Chu kỳ hiện tại ===
void GetTierAndCycleIndex(ENUM_POSITION_TYPE type, int &out_tier, int &out_cycle){
   out_tier = 0;
   out_cycle = 0;
   if(g_cycleCount <= 0) return;
   
   double total_vol = SumLotsByType(type);
   if(total_vol <= 1e-9) return;
   
   double remaining_vol = NormalizeDouble(total_vol, 2);
   int cycle = 0;
   
   while(remaining_vol >= 0.009){ // Handle float precision
      int c_idx = (cycle < g_cycleCount) ? cycle : (g_cycleCount - 1); // Failsafe lặp lại chu kỳ cuối
      int t_count = g_cycles[c_idx].tier_count;
      
      bool cycle_completed = false;
      for(int t=0; t<t_count; t++){
         double tier_cap = g_cycles[c_idx].tiers[t].volume_cap;
         if(remaining_vol >= tier_cap - 0.001){
            remaining_vol -= tier_cap;
            remaining_vol = NormalizeDouble(remaining_vol, 2);
            if(t == t_count - 1){ // Đã lấp đầy tầng cuối của chu kỳ này
               cycle_completed = true;
            }
         } else {
            out_tier = t;
            out_cycle = cycle;
            return;
         }
      }
      
      if(cycle_completed){
         cycle++;
         if(cycle > 100) { // Safety break
            out_tier = g_cycles[c_idx].tier_count - 1; 
            out_cycle = cycle; 
            return; 
         }
      } else {
         break; 
      }
   }
}

// Tổng số lệnh tối đa (Hard Cap)
int TotalMaxOrders(){
   return 999; // Matrix cycle controls max orders
}

// Lấy lot khởi đầu
double GetSeedLot(){
   if(g_cycleCount > 0 && g_cycles[0].tier_count > 0) return NormalizeLot(g_cycles[0].tiers[0].start_lot);
   return NormalizeLot(0.01);
}


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

void RegisterClosingTicket(ulong tk){
   uint now = GetTickCount();
   // Find an empty slot or overwrite an expired slot (>1000ms = 1s)
   for(int i=0; i<500; i++){
      if(g_closing_tickets[i] == 0 || (now - g_closing_times[i] > 1000)){
         g_closing_tickets[i] = tk;
         g_closing_times[i] = now;
         return;
      }
   }
}

bool IsTicketClosing(ulong tk){
   uint now = GetTickCount();
   for(int i=0; i<500; i++){
      if(g_closing_tickets[i] == tk){
         if(now - g_closing_times[i] <= 1000) return true;
         else {
            g_closing_tickets[i] = 0; // Expired
            return false;
         }
      }
   }
   return false;
}

void RefreshPositionCache(){

   g_cache.cnt_buy=0;     g_cache.cnt_sell=0;
   g_cache.lot_buy=0.0;   g_cache.lot_sell=0.0;
   g_cache.pnl_buy=0.0;   g_cache.pnl_sell=0.0;
   g_cache.lastPrice_buy=0.0; g_cache.lastPrice_sell=0.0;
   g_cache.lastTime_buy=0;    g_cache.lastTime_sell=0;
   g_cache.lastLot_buy=0.0;   g_cache.lastLot_sell=0.0;
   g_cache.wcost_buy=0.0;     g_cache.wcost_sell=0.0;
   
   // Account cache (1 lần duy nhất)
   g_cache.balance = AccountInfoDouble(ACCOUNT_BALANCE);
   g_cache.equity  = AccountInfoDouble(ACCOUNT_EQUITY);

   const int total = PositionsTotal();
   for(int i=0; i<total; ++i){
            ulong tk = PositionGetTicket(i);
      if(tk==0 || !PositionSelectByTicket(tk)) continue;
      if(IsTicketClosing(tk)) continue; // HFT: Tàng hình lệnh đang được Async Close

      if(PositionGetString(POSITION_SYMBOL)!=Sym) continue;
      if((long)PositionGetInteger(POSITION_MAGIC)!=MagicNumber) continue;

      double vol   = PositionGetDouble(POSITION_VOLUME);
      double prc   = PositionGetDouble(POSITION_PRICE_OPEN);
      double profit= PositionGetDouble(POSITION_PROFIT);
      double swap  = PositionGetDouble(POSITION_SWAP);
      double comm  = 0.0; // POSITION_COMMISSION is deprecated in newer MT5 builds
      double net_pnl = profit + swap + comm;
      datetime tm  = (datetime)PositionGetInteger(POSITION_TIME);
      int ptype    = (int)PositionGetInteger(POSITION_TYPE);

      if(ptype == POSITION_TYPE_BUY){
         g_cache.cnt_buy++;
         g_cache.lot_buy  += vol;
         g_cache.pnl_buy  += profit;
         g_cache.wcost_buy+= vol * prc;
         if(tm >= g_cache.lastTime_buy){ g_cache.lastTime_buy=tm; g_cache.lastPrice_buy=prc; g_cache.lastLot_buy=vol; }
      } else {
         g_cache.cnt_sell++;
         g_cache.lot_sell  += vol;
         g_cache.pnl_sell  += profit;
         g_cache.wcost_sell+= vol * prc;
         if(tm >= g_cache.lastTime_sell){ g_cache.lastTime_sell=tm; g_cache.lastPrice_sell=prc; g_cache.lastLot_sell=vol; }
      }
   }
}

//============================= I18N =================================
string L(const string key){
  const bool EN=(g_runtimeLang==LANG_EN);
  if(EN){
    if(key=="EA_TITLE")          return "V Capital";
    if(key=="ACC_DATA")          return "--- Account Data ---";
    if(key=="BALANCE")           return "Balance:";
    if(key=="EQUITY")            return "Equity:";
    if(key=="FLOATING_PNL")      return "Profit:";
    if(key=="SYM_INFO")          return "--- Info on " + Sym + " ---";
    if(key=="TOTAL_ORDERS")      return "Orders:";
    if(key=="TOTAL_VOLUME")      return "Volume:";
    if(key=="BUY_PNL")           return "Buy PnL:";
    if(key=="SELL_PNL")          return "Sell PnL:";
    if(key=="CURRENT_DD")        return "Drawdown:";
    if(key=="MODE")              return "Mode:";
    if(key=="STATUS")            return "Status:";
    if(key=="EA_STATUS_RUNNING") return "Trading";
    if(key=="EA_STATUS_PAUSE")   return "Paused";
    if(key=="ONLY_BUY")          return "Only Buy";
    if(key=="ONLY_SELL")         return "Only Sell";
    if(key=="BUY_AND_SELL")      return "Buy & Sell";
    if(key=="AUTO")              return "Auto";
    if(key=="OUT_SESSION")       return "Out of Session";
    if(key=="BTN_PAUSE")         return g_paused?"Resume":"Pause";
    if(key=="BTN_LANG")          return (g_runtimeLang==LANG_EN?"VI":"EN");
    if(key=="BTN_CORNER")        return "Corner";
    return key;
  } else {
    if(key=="EA_TITLE")          return "V Capital";
    if(key=="ACC_DATA")          return "--- Dữ Liệu Tài Khoản ---";
    if(key=="BALANCE")           return "Số dư:";
    if(key=="EQUITY")            return "Tài sản:";
    if(key=="FLOATING_PNL")      return "Lãi/Lỗ:";
    if(key=="SYM_INFO")          return "--- Thông Tin " + Sym + " ---";
    if(key=="TOTAL_ORDERS")      return "Tổng lệnh:";
    if(key=="TOTAL_VOLUME")      return "Tổng KL:";
    if(key=="BUY_PNL")           return "L/L Buy:";
    if(key=="SELL_PNL")          return "L/L Sell:";
    if(key=="CURRENT_DD")        return "Sụt giảm:";
    if(key=="MODE")              return "Chế độ:";
    if(key=="STATUS")            return "Trạng thái:";
    if(key=="EA_STATUS_RUNNING") return "Giao dịch";
    if(key=="EA_STATUS_PAUSE")   return "Tạm dừng";
    if(key=="ONLY_BUY")          return "Chỉ Buy";
    if(key=="ONLY_SELL")         return "Chỉ Sell";
    if(key=="BUY_AND_SELL")      return "Buy và Sell";
    if(key=="AUTO")              return "Tự động";
    if(key=="OUT_SESSION")       return "Ngoài giờ GD";
    if(key=="BTN_PAUSE")         return g_paused?"Mở lại":"Tạm dừng";
    if(key=="BTN_LANG")          return (g_runtimeLang==LANG_EN?"VI":"EN");
    if(key=="BTN_CORNER")        return "Đổi góc";
    return key;
  }
}

//============================= UTILS ================================
int VolumeDigits(){
  if(LotStep<=1e-9) return 2;
  double inv=1.0/LotStep; int d=(int)MathRound(MathLog10(inv));
  if(d<0) d=0; if(d>8) d=8; return d;
}
double NormalizeLot(double lots){
  lots=MathMax(MinLot,MathMin(MaxLot,lots));
  if(LotStep<=1e-9) return NormalizeDouble(lots,2);
  double steps=floor((lots-MinLot)/LotStep+0.5);
  double v=MinLot+steps*LotStep;
  return NormalizeDouble(v,VolumeDigits());
}
bool WithinSession(){
  if(!Limit_Trading_Hours) return true;
  datetime server_time=TimeCurrent();
  long server_gmt_offset_sec=(long)server_time-(long)TimeGMT();
  long adjustment_sec=(7*3600)-server_gmt_offset_sec;
  datetime time_gmt7=(datetime)(server_time+adjustment_sec);
  MqlDateTime dt; TimeToStruct(time_gmt7,dt);
  int hr=dt.hour;
  if(Start_Hour_GMT7<=End_Hour_GMT7) return (hr>=Start_Hour_GMT7 && hr<End_Hour_GMT7);
  return (hr>=Start_Hour_GMT7 || hr<End_Hour_GMT7);
}

//========================= POSITION HELPERS (HFT: đọc từ cache) ======
int CountPositionsByType(ENUM_POSITION_TYPE type){
  return (type==POSITION_TYPE_BUY ? g_cache.cnt_buy : g_cache.cnt_sell);
}
double SumLotsByType(ENUM_POSITION_TYPE type){
  return (type==POSITION_TYPE_BUY ? g_cache.lot_buy : g_cache.lot_sell);
}
double BasketPnLUSD(ENUM_POSITION_TYPE type){
  return (type==POSITION_TYPE_BUY ? g_cache.pnl_buy : g_cache.pnl_sell);
}
double LastOpenPrice(ENUM_POSITION_TYPE type){
  return (type==POSITION_TYPE_BUY ? g_cache.lastPrice_buy : g_cache.lastPrice_sell);
}

// Lấy danh sách lot đã sort tăng dần

//========================== FILE LOGGING ============================
int g_fileHandle = INVALID_HANDLE;
string ModeName(){
  switch(Trading_Mode){
    case CHE_DO_CHI_BUY:     return "ONLY_BUY";
    case CHE_DO_CHI_SELL:    return "ONLY_SELL";
    case CHE_DO_BUY_VA_SELL: return "BUY_AND_SELL";
      }
  return "UNKNOWN";
}
string CurrentLogFile(){
  MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);   // FIX: dùng TimeToStruct
  return StringFormat("VC_%s_%d_%04d-%02d-%02d.csv", Sym, MagicNumber, dt.year, dt.mon, dt.day);
}
void EnsureLogOpened(){
  static string opened_path="";
  string path=CurrentLogFile();
  if(opened_path==path && g_fileHandle!=INVALID_HANDLE) return;
  if(g_fileHandle!=INVALID_HANDLE){ FileClose(g_fileHandle); g_fileHandle=INVALID_HANDLE; }
  g_fileHandle=FileOpen(path, FILE_WRITE|FILE_READ|FILE_CSV|FILE_ANSI|FILE_SHARE_WRITE, ',');
  if(g_fileHandle==INVALID_HANDLE){ Print("LOG: cannot open file: ",path); return; }
  if(FileSize(g_fileHandle)==0){
    FileWrite(g_fileHandle,
      "timestamp_server","symbol","mode","side","event","lot","price_open","price_close","pnl_usd",
      "basket_total_lot_buy","basket_total_lot_sell","dd_percent","note");
    FileFlush(g_fileHandle);
  } else {
    FileSeek(g_fileHandle, 0, SEEK_END);
  }
  opened_path=path;
}
void LogCSV(const string side,const string event,double lot,double price_open,double price_close,double pnl_usd,const string note=""){
  EnsureLogOpened(); if(g_fileHandle==INVALID_HANDLE) return;
  double bal=AccountInfoDouble(ACCOUNT_BALANCE), eq=AccountInfoDouble(ACCOUNT_EQUITY);
  double ddp=(bal>1e-9 ? (bal-eq)/bal*100.0 : 0.0);
  FileWrite(g_fileHandle,
    TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS), Sym, ModeName(), side, event,
    DoubleToString(lot,VolumeDigits()), DoubleToString(price_open,DigitsValue),
    DoubleToString(price_close,DigitsValue), DoubleToString(pnl_usd,2),
    DoubleToString(SumLotsByType(POSITION_TYPE_BUY),VolumeDigits()),
    DoubleToString(SumLotsByType(POSITION_TYPE_SELL),VolumeDigits()),
    DoubleToString(ddp,2), note);
  if(Log_Level==LOG_CHI_TIET) FileFlush(g_fileHandle);
}

//========================== RISK =====================================
bool CheckDDCutoff(){
  double bal=g_cache.balance, eq=g_cache.equity;
  if(bal<=1e-9) return false;
  double ddp=(bal-eq)/bal*100.0;
  if(ddp>=DD_Cutoff_Percent){
    // HFT: async batch close — gửi tất cả lệnh đóng song song
    Trade.SetAsyncMode(true);
    for(int i=PositionsTotal()-1;i>=0;i--){
      ulong tk=PositionGetTicket(i);
      if(tk>0 && PositionSelectByTicket(tk)){
        if(PositionGetString(POSITION_SYMBOL)==Sym && PositionGetInteger(POSITION_MAGIC)==MagicNumber){
          if(Trade.PositionClose(tk)){
             RegisterClosingTicket(tk);
          }
        }
      }
    }
    Trade.SetAsyncMode(false);
    LogCSV("", "DD_CUTOFF_CLOSE_ALL", 0,0,0,0, StringFormat("DD reached %.2f%%",ddp));
    g_seedBuyTicketAfterTP=0; g_seedSellTicketAfterTP=0;
    return true;
  }
  return false;
}

//========================== TP BASKET ===============================
double BasketTPPrice(ENUM_POSITION_TYPE type){
  // HFT: đọc từ cache thay vì scan lại
  double total_lot = (type==POSITION_TYPE_BUY ? g_cache.lot_buy : g_cache.lot_sell);
  double total_cost= (type==POSITION_TYPE_BUY ? g_cache.wcost_buy : g_cache.wcost_sell);
  if(total_lot<=1e-9) return 0.0;
  double avg_price = total_cost / total_lot;
  double tp_distance = Take_Profit_Points * PointV;
  if(type==POSITION_TYPE_BUY) return avg_price + tp_distance;
  else return avg_price - tp_distance;
}
bool CloseBasket(ENUM_POSITION_TYPE type){
  bool ok=true; double pnl=BasketPnLUSD(type);
  Trade.SetAsyncMode(true); // HFT: Gửi lệnh đóng không đồng bộ để không block GUI
  for(int i=PositionsTotal()-1;i>=0;i--){
    ulong tk=PositionGetTicket(i);
    if(tk>0 && PositionSelectByTicket(tk)){
      if(PositionGetString(POSITION_SYMBOL)==Sym &&
         PositionGetInteger(POSITION_MAGIC)==MagicNumber &&
         PositionGetInteger(POSITION_TYPE)==type){
        
        if(Trade.PositionClose(tk)){
           // Đóng thành công → đánh dấu để cache bỏ qua "xác chết" (nếu MT5 chưa xóa kịp)
           RegisterClosingTicket(tk);
        } else {
           ok=false;
           Print("V Capital: LỖI ĐÓNG LỆNH ", tk, " Retcode=", (int)Trade.ResultRetcode());
           // KHÔNG RegisterClosingTicket → lệnh VẪN HIỆN trong cache → Bot KHÔNG bị mù
        }
      }
    }
  }
  Trade.SetAsyncMode(false);
  
  if(ok) {
    if(type==POSITION_TYPE_BUY) g_seedBuyTicketAfterTP = 0;
    else g_seedSellTicketAfterTP = 0;
    LogCSV(type==POSITION_TYPE_BUY?"BUY":"SELL", "TP_CLOSE_BASKET", 0,0,0, pnl, "All closed");
  }
  return ok;
}
bool OpenSeedOrderAfterTP(ENUM_POSITION_TYPE closedType){
  if(!Reentry_After_TP) return false;
  if(g_paused || g_autoOFF_active || !WithinSession()){ Print("Seed after TP skipped."); return false; }

  // Determine direction based on mode
  ENUM_POSITION_TYPE seedType = closedType;

  switch(Trading_Mode){
    case CHE_DO_CHI_BUY:
      seedType = POSITION_TYPE_BUY;
      break;
    case CHE_DO_CHI_SELL:
      seedType = POSITION_TYPE_SELL;
      break;
    case CHE_DO_BUY_VA_SELL:
      // Buy và Sell: vào lại cùng chiều vừa TP
      seedType = closedType;
      break;
    }

  double lot = GetSeedLot();
  if(lot <= 1e-9) return false;

  bool ok = false; double price_open = 0.0; ulong pos_id = 0;
  if(seedType == POSITION_TYPE_BUY) ok = Trade.Buy(lot, Sym, 0.0, 0.0, 0.0, "VQuant0");
  else                               ok = Trade.Sell(lot, Sym, 0.0, 0.0, 0.0, "VQuant0");

  if(ok){
    pos_id     = GetPositionFromLastDeal();
    price_open = Trade.ResultPrice();
    string side = (seedType == POSITION_TYPE_BUY ? "BUY" : "SELL");
    if(seedType == POSITION_TYPE_BUY){ g_seedBuyTicketAfterTP = pos_id; g_seedBuyLotAfterTP = lot; }
    else                             { g_seedSellTicketAfterTP = pos_id; g_seedSellLotAfterTP = lot; }
    LogCSV(side, "SEED_AFTER_TP", lot, price_open, 0, 0, "Re-entry after TP");
    return true;
  } else {
    Print("Open seed after TP failed. Retcode=", (int)Trade.ResultRetcode());
  }
  return false;
}
// Seed micro-scalp uses Take_Profit_Points for TP distance
void CheckBasketTP(){
  MqlTick tick;
  if(!SymbolInfoTick(Sym, tick)) return;
  
  // BUY basket: close when bid >= TP price
  if(SumLotsByType(POSITION_TYPE_BUY)>1e-9){
    double tpPrice=BasketTPPrice(POSITION_TYPE_BUY);
    if(tpPrice>1e-9 && tick.bid>=tpPrice){
      if(CloseBasket(POSITION_TYPE_BUY)){
        RefreshPositionCache();
        OpenSeedOrderAfterTP(POSITION_TYPE_BUY);
        RefreshPositionCache();
      }
    }
  }
  // SELL basket: close when ask <= TP price
  if(SumLotsByType(POSITION_TYPE_SELL)>1e-9){
    double tpPrice=BasketTPPrice(POSITION_TYPE_SELL);
    if(tpPrice>1e-9 && tick.ask<=tpPrice){
      if(CloseBasket(POSITION_TYPE_SELL)){
        RefreshPositionCache();
        OpenSeedOrderAfterTP(POSITION_TYPE_SELL);
        RefreshPositionCache();
      }
    }
  }
}

//===================== SEED MICRO-SCALP (AFTER TP) ===================
void CheckSeedMicroScalp(){
  // BUY seed
  if(g_seedBuyTicketAfterTP>0){
    if(PositionSelectByTicket(g_seedBuyTicketAfterTP)){
      double pnl=PositionGetDouble(POSITION_PROFIT);
      double seedOpen=PositionGetDouble(POSITION_PRICE_OPEN);
      double seedTP=seedOpen+Take_Profit_Points*PointV;
      double curPrice=PositionGetDouble(POSITION_PRICE_CURRENT);
      bool tp_hit=(curPrice>=seedTP);
      if(tp_hit){
        ulong tk_close = g_seedBuyTicketAfterTP;
        g_seedBuyTicketAfterTP = 0; // Reset NGAY LẬP TỨC
        if(Trade.PositionClose(tk_close)){
          RegisterClosingTicket(tk_close);
          LogCSV("BUY","SEED_MICROSCALP_CLOSE",g_seedBuyLotAfterTP,seedOpen,curPrice,pnl,"Seed closed for scalp");
          bool ok=Trade.Buy(g_seedBuyLotAfterTP,Sym,0.0,0.0,0.0,"VQuant0");
          if(ok){
            g_seedBuyTicketAfterTP = GetPositionFromLastDeal();
            double price_open = Trade.ResultPrice();
            LogCSV("BUY","SEED_MICROSCALP_REOPEN",g_seedBuyLotAfterTP,price_open,0,0,"Seed reopened");
          } else { g_seedBuyTicketAfterTP=0; Print("Reopen BUY seed fail. Retcode=", (int)Trade.ResultRetcode()); }
        }
      }
    } else g_seedBuyTicketAfterTP=0;
  }
  // SELL seed
  if(g_seedSellTicketAfterTP>0){
    if(PositionSelectByTicket(g_seedSellTicketAfterTP)){
      double pnl=PositionGetDouble(POSITION_PROFIT);
      double seedOpen=PositionGetDouble(POSITION_PRICE_OPEN);
      double seedTP=seedOpen-Take_Profit_Points*PointV;
      double curPrice=PositionGetDouble(POSITION_PRICE_CURRENT);
      bool tp_hit=(curPrice<=seedTP);
      if(tp_hit){
        ulong tk_close = g_seedSellTicketAfterTP;
        g_seedSellTicketAfterTP = 0; // Reset NGAY LẬP TỨC
        if(Trade.PositionClose(tk_close)){
          RegisterClosingTicket(tk_close);
          LogCSV("SELL","SEED_MICROSCALP_CLOSE",g_seedSellLotAfterTP,seedOpen,curPrice,pnl,"Seed closed for scalp");
          bool ok=Trade.Sell(g_seedSellLotAfterTP,Sym,0.0,0.0,0.0,"VQuant0");
          if(ok){
            g_seedSellTicketAfterTP = GetPositionFromLastDeal();
            double price_open = Trade.ResultPrice();
            LogCSV("SELL","SEED_MICROSCALP_REOPEN",g_seedSellLotAfterTP,price_open,0,0,"Seed reopened");
          } else { g_seedSellTicketAfterTP=0; Print("Reopen SELL seed fail. Retcode=", (int)Trade.ResultRetcode()); }
        }
      }
    } else g_seedSellTicketAfterTP=0;
  }
}

//===================== PARTIAL CLOSE (FIFO) ==========================


//========================== EMA TREND FILTER ========================
bool IsTrendBuy(){
   if(EMA_Fast<=0 || EMA_Slow<=0) return true; // disabled
   double emaFastH4[], emaSlowH4[], emaFastH1[], emaSlowH1[];
   ArraySetAsSeries(emaFastH4,true); ArraySetAsSeries(emaSlowH4,true);
   ArraySetAsSeries(emaFastH1,true); ArraySetAsSeries(emaSlowH1,true);
   
   if(g_hEmaFastH4==INVALID_HANDLE || g_hEmaSlowH4==INVALID_HANDLE ||
      g_hEmaFastH1==INVALID_HANDLE || g_hEmaSlowH1==INVALID_HANDLE) return true;
   
   int need = Confirm_Candles + 1;
   if(CopyBuffer(g_hEmaFastH4,0,0,need,emaFastH4)<need) return true;
   if(CopyBuffer(g_hEmaSlowH4,0,0,need,emaSlowH4)<need) return true;
   if(CopyBuffer(g_hEmaFastH1,0,0,need,emaFastH1)<need) return true;
   if(CopyBuffer(g_hEmaSlowH1,0,0,need,emaSlowH1)<need) return true;
   
   // H4: EMA fast > EMA slow (uptrend)
   if(emaFastH4[0] <= emaSlowH4[0]) return false;
   // H1: confirm consecutive candles
   for(int i=0; i<Confirm_Candles; i++){
      if(emaFastH1[i] <= emaSlowH1[i]) return false;
   }
   return true;
}

bool IsTrendSell(){
   if(EMA_Fast<=0 || EMA_Slow<=0) return true;
   double emaFastH4[], emaSlowH4[], emaFastH1[], emaSlowH1[];
   ArraySetAsSeries(emaFastH4,true); ArraySetAsSeries(emaSlowH4,true);
   ArraySetAsSeries(emaFastH1,true); ArraySetAsSeries(emaSlowH1,true);
   
   if(g_hEmaFastH4==INVALID_HANDLE || g_hEmaSlowH4==INVALID_HANDLE ||
      g_hEmaFastH1==INVALID_HANDLE || g_hEmaSlowH1==INVALID_HANDLE) return true;
   
   int need = Confirm_Candles + 1;
   if(CopyBuffer(g_hEmaFastH4,0,0,need,emaFastH4)<need) return true;
   if(CopyBuffer(g_hEmaSlowH4,0,0,need,emaSlowH4)<need) return true;
   if(CopyBuffer(g_hEmaFastH1,0,0,need,emaFastH1)<need) return true;
   if(CopyBuffer(g_hEmaSlowH1,0,0,need,emaSlowH1)<need) return true;
   
   if(emaFastH4[0] >= emaSlowH4[0]) return false;
   for(int i=0; i<Confirm_Candles; i++){
      if(emaFastH1[i] >= emaSlowH1[i]) return false;
   }
   return true;
}

//========================== AUTO ON/OFF PROFIT/LOSS =================
void CheckAutoOFF_ProfitLoss(){
   if(g_autoOFF_active) return;
   double bal=g_cache.balance, eq=g_cache.equity;
   double floating = eq - bal;
   
   if(AutoOFF_On_Profit && Profit_To_AutoOFF > 0.0 && floating >= Profit_To_AutoOFF){
      g_autoOFF_active = true;
      g_autoOFF_time = TimeCurrent();
      g_autoOFF_reason = StringFormat("Profit %.2f >= %.2f", floating, Profit_To_AutoOFF);
      g_paused = true;
      LogCSV("","AUTO_OFF_PROFIT",0,0,0,floating,g_autoOFF_reason);
      Print("V Capital: AUTO OFF - ", g_autoOFF_reason);
   }
   if(AutoOFF_On_Loss && Loss_To_AutoOFF > 0.0 && floating <= -Loss_To_AutoOFF){
      g_autoOFF_active = true;
      g_autoOFF_time = TimeCurrent();
      g_autoOFF_reason = StringFormat("Loss %.2f >= %.2f", MathAbs(floating), Loss_To_AutoOFF);
      g_paused = true;
      LogCSV("","AUTO_OFF_LOSS",0,0,0,floating,g_autoOFF_reason);
      Print("V Capital: AUTO OFF - ", g_autoOFF_reason);
   }
}

void CheckAutoON_Timer(){
   if(!g_autoOFF_active || !AutoON_After_OFF) return;
   if((TimeCurrent() - g_autoOFF_time) >= Wait_Minutes_Before_ON * 60){
      g_autoOFF_active = false;
      g_paused = false;
      LogCSV("","AUTO_ON_TIMER",0,0,0,0,StringFormat("Re-enabled after %d min", Wait_Minutes_Before_ON));
      Print("V Capital: AUTO ON - Timer expired");
   }
}

//========================== AUTO ON/OFF THEO GIÁ ====================
void CheckAutoOFF_Price(){
   if(g_autoOFF_active) return;
   if(!AutoOFF_By_Price) return;
   
   double price = SymbolInfoDouble(Sym, SYMBOL_BID);
   bool triggered = false;
   string reason = "";
   
   if(Upper_Price_OFF > 0.0 && price >= Upper_Price_OFF){
      triggered = true;
      reason = StringFormat("Price %.5f >= Upper %.5f", price, Upper_Price_OFF);
   }
   if(Lower_Price_OFF > 0.0 && price <= Lower_Price_OFF){
      triggered = true;
      reason = StringFormat("Price %.5f <= Lower %.5f", price, Lower_Price_OFF);
   }
   
   if(triggered){
      g_autoOFF_active = true;
      g_autoOFF_time = TimeCurrent();
      g_autoOFF_reason = reason;
      g_paused = true;
      LogCSV("","AUTO_OFF_PRICE",0,0,0,price,reason);
      Print("V Capital: AUTO OFF PRICE - ", reason);
      
      if(Close_On_Price_Hit){
         // HFT: async batch close
         Trade.SetAsyncMode(true);
         for(int i=PositionsTotal()-1;i>=0;i--){
            ulong tk=PositionGetTicket(i);
            if(tk>0 && PositionSelectByTicket(tk)){
               if(PositionGetString(POSITION_SYMBOL)==Sym && PositionGetInteger(POSITION_MAGIC)==MagicNumber)
                  Trade.PositionClose(tk);
            }
         }
         Trade.SetAsyncMode(false);
         LogCSV("","PRICE_CLOSE_ALL",0,0,0,0,"Closed all on price trigger");
      }
   }
}

void CheckAutoON_Price(){
   if(!g_autoOFF_active || !AutoON_Price_Return) return;
   
   double price = SymbolInfoDouble(Sym, SYMBOL_BID);
   bool back_in_range = true;
   
   if(Upper_Price_ON > 0.0 && price >= Upper_Price_ON) back_in_range = false;
   if(Lower_Price_ON > 0.0 && price <= Lower_Price_ON) back_in_range = false;
   
   // Must have at least one bound set
   if(Upper_Price_ON <= 0.0 && Lower_Price_ON <= 0.0) return;
   
   if(back_in_range){
      g_autoOFF_active = false;
      g_paused = false;
      LogCSV("","AUTO_ON_PRICE",0,0,0,price,"Price back in range");
      Print("V Capital: AUTO ON - Price back in safe range");
   }
}

//========================== ENTRY CONDITIONS ========================
bool StrictGridDistanceOK(ENUM_POSITION_TYPE type){
  double last_price=LastOpenPrice(type);
  if(last_price<=1e-9) return true;
  // Xác định grid distance
  int grid_pts = 2000;
  if(g_cycleCount > 0){
    int tier = 0, cycle = 0;
    GetTierAndCycleIndex(type, tier, cycle);
    int c_idx = (cycle < g_cycleCount) ? cycle : (g_cycleCount - 1);
    grid_pts = g_cycles[c_idx].tiers[tier].grid_distance;
  }
  
  if(Enable_ATR_Grid && g_current_atr_val >= ATR_Threshold_Points){
      grid_pts = (int)(grid_pts * ATR_Grid_Multiplier);
  }
  
  double need = grid_pts * PointV; if(need<=1e-9) return false;
  
  MqlTick tick;
  if(!SymbolInfoTick(Sym, tick)) return false;
  
  if(type==POSITION_TYPE_BUY){ return (last_price - tick.bid >= need); }
  else { return (tick.ask - last_price >= need); }
}

//========================== OPEN HELPERS ============================
bool OpenBuy(double lot, ulong &ticket, string comment="VQuant0"){
  lot=NormalizeLot(lot); ticket=0;
  if(lot<=1e-9 || !WithinSession() || g_paused) return false;
  if(!Trade.Buy(lot,Sym,0.0,0.0,0.0,comment)){
    Print("Open BUY fail. Retcode=", (int)Trade.ResultRetcode()); return false;
  }
  ticket = GetPositionFromLastDeal();
  double price_open = Trade.ResultPrice();
  LogCSV("BUY","OPEN",lot,price_open,0,0,comment);
  return true;
}
bool OpenSell(double lot, ulong &ticket, string comment="VQuant0"){
  lot=NormalizeLot(lot); ticket=0;
  if(lot<=1e-9 || !WithinSession() || g_paused) return false;
  if(!Trade.Sell(lot,Sym,0.0,0.0,0.0,comment)){
    Print("Open SELL fail. Retcode=", (int)Trade.ResultRetcode()); return false;
  }
  ticket = GetPositionFromLastDeal();
  double price_open = Trade.ResultPrice();
  LogCSV("SELL","OPEN",lot,price_open,0,0,comment);
  return true;
}

//=== DCA: 2D Matrix Nested Cycle Lot logic ===
double NextLotDCA(ENUM_POSITION_TYPE type)
{
  if(g_cycleCount > 0){
    int tier = 0, cycle = 0;
    GetTierAndCycleIndex(type, tier, cycle);
    
    if(cycle >= g_cycleCount){
       Print("V Capital: Đã vượt quá giới hạn Chu kỳ (Max ", g_cycleCount, "). NGỪNG NHỒI LỆNH ĐỂ BẢO TOÀN VỐN!");
       return 0.0;
    }
    
    double lot = g_cycles[cycle].tiers[tier].start_lot;
    return NormalizeLot(lot);
  }

  return GetSeedLot();
}

//=================== CORE LOGIC (CALLED ON M15 CLOSE) ================
void TryDCAOrBalance(ENUM_POSITION_TYPE type){
  int cnt=CountPositionsByType(type);
  int maxOrders = TotalMaxOrders();
  if(cnt >= maxOrders) return;
  if(!StrictGridDistanceOK(type)) return;

  double lot=NextLotDCA(type);
  if(lot<=1e-9) return;
  string comment = "VQuant" + IntegerToString(cnt);
  ulong tk=0; bool ok=(type==POSITION_TYPE_BUY? OpenBuy(lot,tk,comment): OpenSell(lot,tk,comment));
  if(ok) LogCSV((type==POSITION_TYPE_BUY?"BUY":"SELL"), "DCA_OPEN", lot, 0,0,0, comment);
}



string g_ai_signal = "NEUTRAL";
double g_ai_confidence = 0.0;
datetime g_ai_signal_time = 0;

void ReadAISignal() {
    int handle = FileOpen("vc_signal_XAUUSD.txt", FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
    if(handle != INVALID_HANDLE) {
        string content = FileReadString(handle);
        FileClose(handle);
        string out[];
        int k = StringSplit(content, ',', out);
        if(k >= 3) {
            g_ai_signal = out[0];
            g_ai_confidence = StringToDouble(out[1]);
            g_ai_signal_time = (datetime)StringToInteger(out[2]);
        }
    }
}

void CheckAllEntryLogic(){
  if(!WithinSession() || g_paused || g_autoOFF_active) return;

  bool can_buy=false, can_sell=false;

  switch(Trading_Mode){
    case CHE_DO_CHI_BUY:
      can_buy=true;
      break;
    case CHE_DO_CHI_SELL:
      can_sell=true;
      break;
    case CHE_DO_BUY_VA_SELL:
      // Buy và Sell: chạy cả 2 chiều đồng thời
      can_buy=true; can_sell=true;
      break;
  }

  // ALLOW DCA if positions exist, regardless of the explicit AI entry condition.
  // The 'can_buy' and 'can_sell' flags strictly control the *FIRST* position of a basket.
    // --- AI LOGIC INJECTION ---
  ReadAISignal();
  bool ai_buy = false, ai_sell = false;
  if(TimeCurrent() - g_ai_signal_time < 4 * 3600) {
      if(g_ai_signal == "LONG_POSITION_ON" && g_ai_confidence >= 0.8) ai_buy = true;
      if(g_ai_signal == "SHORT_POSITION_ON" && g_ai_confidence >= 0.8) ai_sell = true;
  }
  
  if(CountPositionsByType(POSITION_TYPE_BUY) == 0) {
      if(!ai_buy) can_buy = false; 
  }
  if(CountPositionsByType(POSITION_TYPE_SELL) == 0) {
      if(!ai_sell) can_sell = false;
  }
  // --- END AI LOGIC INJECTION ---

  if(can_buy || CountPositionsByType(POSITION_TYPE_BUY) > 0)  TryDCAOrBalance(POSITION_TYPE_BUY);
  if(can_sell || CountPositionsByType(POSITION_TYPE_SELL) > 0) TryDCAOrBalance(POSITION_TYPE_SELL);
}

//========================== PROFIT HISTORY =========================
double g_cached_pToday = 0.0;
double g_cached_pWeek  = 0.0;
double g_cached_pMonth = 0.0;
datetime g_last_profit_calc_time = 0;

void UpdateHistoricalProfits(){
  datetime now = TimeCurrent();
  if(now - g_last_profit_calc_time < 60 && g_last_profit_calc_time != 0) return; // Chỉ cập nhật 60s/lần
  g_last_profit_calc_time = now;

  double pToday=0.0, pWeek=0.0, pMonth=0.0;
  
  MqlDateTime dt; TimeToStruct(now, dt);
  
  // Chỉ lấy lịch sử của NGÀY HÔM NAY để tránh treo máy (HistorySelect quá nặng với HFT)
  dt.hour=0; dt.min=0; dt.sec=0;
  datetime today_start=StructToTime(dt);

  // Lọc lịch sử (Chỉ từ đầu ngày hôm nay)
  if(HistorySelect(today_start, now)){
    int total = HistoryDealsTotal();
    for(int i=total-1; i>=0; i--){
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket>0 && HistoryDealGetString(ticket,DEAL_SYMBOL)==Sym &&
         HistoryDealGetInteger(ticket,DEAL_MAGIC)==MagicNumber &&
         HistoryDealGetInteger(ticket,DEAL_ENTRY)==DEAL_ENTRY_OUT)
      {
         double pnl = HistoryDealGetDouble(ticket,DEAL_PROFIT) + 
                      HistoryDealGetDouble(ticket,DEAL_SWAP) + 
                      HistoryDealGetDouble(ticket,DEAL_COMMISSION);
         pToday += pnl;
      }
    }
  }
  
  // Tạm thời vô hiệu hóa pWeek và pMonth để cứu tốc độ HFT
  pWeek = pToday; 
  pMonth = pToday;
  
  // Cộng thêm floating PnL của basket hiện tại
  double float_pnl = BasketPnLUSD(POSITION_TYPE_BUY) + BasketPnLUSD(POSITION_TYPE_SELL);
  g_cached_pToday = pToday + float_pnl;
  g_cached_pWeek  = pWeek + float_pnl;
  g_cached_pMonth = pMonth + float_pnl;
}

string GetTrendString(){
  if(EMA_Fast<=0 || EMA_Slow<=0) return "OFF";
  bool up=IsTrendBuy(), dn=IsTrendSell();
  if(up && !dn) return "UP";
  if(dn && !up) return "DOWN";
  return "NEUTRAL";
}

//========================== ON-CHART UI =============================
void SetLabel(long chart_id,string name,string text,int x,int y,ENUM_BASE_CORNER corner,color clr,int font_size,string font_name="Tahoma",int x_anchor=0){
  if(ObjectFind(chart_id,name)<0){
    ObjectCreate(chart_id,name,OBJ_LABEL,0,0,0);
    ObjectSetInteger(chart_id,name,OBJPROP_FONTSIZE,font_size);
    ObjectSetString (chart_id,name,OBJPROP_FONT,font_name);
    ObjectSetInteger(chart_id,name,OBJPROP_CORNER,corner);
    ObjectSetInteger(chart_id,name,OBJPROP_ANCHOR,(x_anchor==0? ANCHOR_LEFT_UPPER:ANCHOR_RIGHT_UPPER));
  }
  ObjectSetInteger(chart_id,name,OBJPROP_XDISTANCE,x);
  ObjectSetInteger(chart_id,name,OBJPROP_YDISTANCE,y);
  ObjectSetInteger(chart_id,name,OBJPROP_COLOR,clr);
  ObjectSetString (chart_id,name,OBJPROP_TEXT,text);
}



void DrawDashboard(){
  string status_str="Running";
  color statusClr=clrLime;
  if(!Show_Dashboard){ DeleteObjectsByPrefix("VC_"); return; }

  long chart_id=ChartID();
  int font_size=(Dashboard_FontSize==CO_NHO?8:(Dashboard_FontSize==CO_VUA?10:12));
  int line_h=(int)(font_size * 1.8); color txt=clrBlack, posC=clrForestGreen, negC=clrFireBrick, sep=clrDimGray;

  int panel_w=240, x=20, y=20; int x_val=panel_w-20;

  double bal=AccountInfoDouble(ACCOUNT_BALANCE), eq=AccountInfoDouble(ACCOUNT_EQUITY);
  double total_pnl=eq-bal; int nB=CountPositionsByType(POSITION_TYPE_BUY), nS=CountPositionsByType(POSITION_TYPE_SELL);
  double lotB=SumLotsByType(POSITION_TYPE_BUY), lotS=SumLotsByType(POSITION_TYPE_SELL);
  double ddp=(bal>1e-9? (bal-eq)/bal*100.0 : 0.0);
  string ccy=AccountInfoString(ACCOUNT_CURRENCY);

  int yy=y;

   // --- Full Height Left Sidebar Background ---
   if(ObjectFind(chart_id, "VC_DASH_BG") < 0) {
      ObjectCreate(chart_id, "VC_DASH_BG", OBJ_RECTANGLE_LABEL, 0, 0, 0);
   }
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_XDISTANCE, 0);
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_YDISTANCE, 0);
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_XSIZE, panel_w + 30);
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_YSIZE, ChartGetInteger(chart_id, CHART_HEIGHT_IN_PIXELS));
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_BGCOLOR, clrWhiteSmoke);
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_COLOR, clrSilver); // Border color
   ObjectSetInteger(chart_id, "VC_DASH_BG", OBJPROP_BACK, false); // Nằm đè lên trên nến, không bị trong suốt

   // --- Title ---
  SetLabel(chart_id,"VC_LBL_TITLE",L("EA_TITLE"),x,yy,CORNER_LEFT_UPPER,txt,font_size+1); yy+=line_h+4;
  SetLabel(chart_id,"VC_LBL_EXP","VQuant HFT System",x,yy,CORNER_LEFT_UPPER,clrDimGray,font_size); yy+=line_h+4;

  // --- Account Data ---
  string acc_name = AccountInfoString(ACCOUNT_NAME);
  string acc_server = AccountInfoString(ACCOUNT_SERVER);
  SetLabel(chart_id,"VC_LBL_ACC_SEP","--- "+acc_name+" ---",x,yy,CORNER_LEFT_UPPER,sep,font_size); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_SRV_L","Server:",x,yy,CORNER_LEFT_UPPER,clrDimGray,font_size);
  SetLabel(chart_id,"VC_LBL_SRV_V",acc_server,x+x_val,yy,CORNER_LEFT_UPPER,clrDimGray,font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_BAL_L","Balance:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_BAL_V",DoubleToString(bal,2)+" "+ccy,x+x_val,yy,CORNER_LEFT_UPPER,txt,font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_EQ_L","Equity:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_EQ_V",DoubleToString(eq,2)+" "+ccy,x+x_val,yy,CORNER_LEFT_UPPER,txt,font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_TPNL_L","Profit:",x,yy,CORNER_LEFT_UPPER,(total_pnl>=0?posC:negC),font_size);
  SetLabel(chart_id,"VC_LBL_TPNL_V",DoubleToString(total_pnl,2)+" "+ccy,x+x_val,yy,CORNER_LEFT_UPPER,(total_pnl>=0?posC:negC),font_size,"Tahoma",1); yy+=line_h;
  // Margin Level & Spread
  double margin_used = AccountInfoDouble(ACCOUNT_MARGIN);
  double margin_level = (margin_used > 0.01 ? (eq / margin_used) * 100.0 : 0.0);
  color mlClr = (margin_level > 500 ? posC : (margin_level > 200 ? clrGold : negC));
  SetLabel(chart_id,"VC_LBL_ML_L","Margin Lv:",x,yy,CORNER_LEFT_UPPER,mlClr,font_size);
  SetLabel(chart_id,"VC_LBL_ML_V",(margin_used > 0.01 ? StringFormat("%.0f%%", margin_level) : "Free"),x+x_val,yy,CORNER_LEFT_UPPER,mlClr,font_size,"Tahoma",1); yy+=line_h;
  int spread_pts = (int)SymbolInfoInteger(Sym, SYMBOL_SPREAD);
  SetLabel(chart_id,"VC_LBL_SPREAD_L","Spread:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_SPREAD_V",IntegerToString(spread_pts)+" pts",x+x_val,yy,CORNER_LEFT_UPPER,(spread_pts>50?negC:posC),font_size,"Tahoma",1); yy+=line_h;

  // --- Profit ---
  SetLabel(chart_id,"VC_LBL_PRF_SEP","--- Profit ---",x,yy,CORNER_LEFT_UPPER,sep,font_size); yy+=line_h;
  UpdateHistoricalProfits();
  double pToday=g_cached_pToday, pWeek=g_cached_pWeek, pMonth=g_cached_pMonth;
  SetLabel(chart_id,"VC_LBL_PDAY_L","Today:",x,yy,CORNER_LEFT_UPPER,(pToday>=0?posC:negC),font_size);
  SetLabel(chart_id,"VC_LBL_PDAY_V",DoubleToString(pToday,2)+" "+ccy,x+x_val,yy,CORNER_LEFT_UPPER,(pToday>=0?posC:negC),font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_PWEK_L","Week:",x,yy,CORNER_LEFT_UPPER,(pWeek>=0?posC:negC),font_size);
  SetLabel(chart_id,"VC_LBL_PWEK_V",DoubleToString(pWeek,2)+" "+ccy,x+x_val,yy,CORNER_LEFT_UPPER,(pWeek>=0?posC:negC),font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_PMON_L","Month:",x,yy,CORNER_LEFT_UPPER,(pMonth>=0?posC:negC),font_size);
  SetLabel(chart_id,"VC_LBL_PMON_V",DoubleToString(pMonth,2)+" "+ccy,x+x_val,yy,CORNER_LEFT_UPPER,(pMonth>=0?posC:negC),font_size,"Tahoma",1); yy+=line_h;

  // --- Symbol ---
  SetLabel(chart_id,"VC_LBL_SYM_SEP","--- "+Sym+" ---",x,yy,CORNER_LEFT_UPPER,sep,font_size); yy+=line_h;
  double sym_pnl=BasketPnLUSD(POSITION_TYPE_BUY)+BasketPnLUSD(POSITION_TYPE_SELL);
  SetLabel(chart_id,"VC_LBL_SYMPNL_L","Profit:",x,yy,CORNER_LEFT_UPPER,(sym_pnl>=0?posC:negC),font_size);
  SetLabel(chart_id,"VC_LBL_SYMPNL_V",DoubleToString(sym_pnl,2)+" "+ccy,x+x_val,yy,CORNER_LEFT_UPPER,(sym_pnl>=0?posC:negC),font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_DD_L","Drawdown:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_DD_V",StringFormat("%.1f%%",ddp>0?ddp:0.0),x+x_val,yy,CORNER_LEFT_UPPER,txt,font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_VOL_L","Volume:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_VOL_V",DoubleToString(NormalizeDouble(lotB+lotS,VolumeDigits()),VolumeDigits()),x+x_val,yy,CORNER_LEFT_UPPER,txt,font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_ORDERS_L","Orders:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_ORDERS_V",IntegerToString(nB+nS)+"/"+IntegerToString(TotalMaxOrders()),x+x_val,yy,CORNER_LEFT_UPPER,txt,font_size,"Tahoma",1); yy+=line_h;
  
  SetLabel(chart_id,"VC_LBL_BUYTP_L","Buy TP:",x,yy,CORNER_LEFT_UPPER,posC,font_size);
  SetLabel(chart_id,"VC_LBL_BUYTP_V",DoubleToString(BasketTPPrice(POSITION_TYPE_BUY),3),x+x_val,yy,CORNER_LEFT_UPPER,posC,font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_SELLTP_L","Sell TP:",x,yy,CORNER_LEFT_UPPER,negC,font_size);
  SetLabel(chart_id,"VC_LBL_SELLTP_V",DoubleToString(BasketTPPrice(POSITION_TYPE_SELL),3),x+x_val,yy,CORNER_LEFT_UPPER,negC,font_size,"Tahoma",1); yy+=line_h;

  // --- Tier & Cycle Info ---
  if(g_cycleCount > 0){
    int tierB = 0, cycleB = 0; GetTierAndCycleIndex(POSITION_TYPE_BUY, tierB, cycleB);
    int tierS = 0, cycleS = 0; GetTierAndCycleIndex(POSITION_TYPE_SELL, tierS, cycleS);
    string tierBstr = "C" + IntegerToString(cycleB+1) + "-T" + IntegerToString(tierB+1);
    string tierSstr = "C" + IntegerToString(cycleS+1) + "-T" + IntegerToString(tierS+1);
    SetLabel(chart_id,"VC_LBL_TIER_L","Cycle-Tier:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
    SetLabel(chart_id,"VC_LBL_TIER_V","B:"+tierBstr+"  S:"+tierSstr,x+x_val,yy,CORNER_LEFT_UPPER,clrBlue,font_size,"Tahoma",1); yy+=line_h;
  }

  // --- ATR Shield ---
  string atr_str = "OFF";
  color atr_clr = clrDarkGray;
  if(Enable_ATR_Grid){
      if(g_current_atr_val >= ATR_Threshold_Points){
          atr_str = StringFormat("Active (x%.1f)", ATR_Grid_Multiplier);
          atr_clr = negC; // Red warning
      } else {
          atr_str = StringFormat("Safe (%.0f pts)", g_current_atr_val);
          atr_clr = posC; // Green safe
      }
  }
  SetLabel(chart_id,"VC_LBL_ATR_L","ATR Shield:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_ATR_V",atr_str,x+x_val,yy,CORNER_LEFT_UPPER,atr_clr,font_size,"Tahoma",1); yy+=line_h;

  // --- Status ---
  SetLabel(chart_id,"VC_LBL_STAT_SEP","--- Status ---",x,yy,CORNER_LEFT_UPPER,sep,font_size); yy+=line_h;
  string mode_str="AUTO";
  if(Trading_Mode==CHE_DO_CHI_BUY) mode_str="BUY";
  else if(Trading_Mode==CHE_DO_CHI_SELL) mode_str="SELL";
  else if(Trading_Mode==CHE_DO_BUY_VA_SELL) mode_str="BUY & SELL";
  SetLabel(chart_id,"VC_LBL_MODE_L","Mode:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_MODE_V",mode_str,x+x_val,yy,CORNER_LEFT_UPPER,txt,font_size,"Tahoma",1); yy+=line_h;

  string trend_str=GetTrendString();
  color trendClr=(trend_str=="UP"?posC:(trend_str=="DOWN"?negC:clrGold));
  SetLabel(chart_id,"VC_LBL_TREND_L","EMA Trend:",x,yy,CORNER_LEFT_UPPER,trendClr,font_size);
  SetLabel(chart_id,"VC_LBL_TREND_V",trend_str,x+x_val,yy,CORNER_LEFT_UPPER,trendClr,font_size,"Tahoma",1); yy+=line_h;


  

  
  if(g_paused){ status_str="Paused"; statusClr=clrGold; }
  else if(!WithinSession()){ status_str="Out of Session"; statusClr=clrGold; }
  SetLabel(chart_id,"VC_LBL_STATUS_L","Status:",x,yy,CORNER_LEFT_UPPER,statusClr,font_size);
  SetLabel(chart_id,"VC_LBL_STATUS_V",status_str,x+x_val,yy,CORNER_LEFT_UPPER,statusClr,font_size,"Tahoma",1); yy+=line_h;

  string auto_str=(g_autoOFF_active?"OFF":"ON");
  color autoClr=(g_autoOFF_active?negC:posC);
  SetLabel(chart_id,"VC_LBL_AUTO_L","Auto:",x,yy,CORNER_LEFT_UPPER,autoClr,font_size);
  SetLabel(chart_id,"VC_LBL_AUTO_V",auto_str,x+x_val,yy,CORNER_LEFT_UPPER,autoClr,font_size,"Tahoma",1); yy+=line_h;

  string cutloss_str=StringFormat("ON (%.0f%%)",DD_Cutoff_Percent);
  SetLabel(chart_id,"VC_LBL_CUTLOSS_L","Cut Loss:",x,yy,CORNER_LEFT_UPPER,posC,font_size);
  SetLabel(chart_id,"VC_LBL_CUTLOSS_V",cutloss_str,x+x_val,yy,CORNER_LEFT_UPPER,posC,font_size,"Tahoma",1); yy+=line_h;

  // Uptime
  long uptime_sec = (long)(TimeCurrent() - g_startTime);
  int up_h = (int)(uptime_sec / 3600);
  int up_m = (int)((uptime_sec % 3600) / 60);
  SetLabel(chart_id,"VC_LBL_UP_L","Uptime:",x,yy,CORNER_LEFT_UPPER,clrDimGray,font_size);
  SetLabel(chart_id,"VC_LBL_UP_V",StringFormat("%dh %dm", up_h, up_m),x+x_val,yy,CORNER_LEFT_UPPER,clrDimGray,font_size,"Tahoma",1); yy+=line_h+8;

  // --- Copyright ---
  SetLabel(chart_id,"VC_LBL_COPY","© 2024-2026 V Capital by Nguyen Manh Cuong",x,yy,CORNER_LEFT_UPPER,clrSilver,font_size-1,"Tahoma",0); yy+=line_h;

  ChartRedraw(chart_id);
}

bool AutoTradingOn()
{
    return (bool)TerminalInfoInteger(TERMINAL_TRADE_ALLOWED);
}

//========================== MT5 EVENTS ==============================
// Trích ticket position từ deal cuối cùng của CTrade
ulong GetPositionFromLastDeal()
{
   ulong deal = (ulong)Trade.ResultDeal();
   if(deal>0 && HistoryDealSelect(deal))
      return (ulong)HistoryDealGetInteger(deal, DEAL_POSITION_ID);
   return 0;
}

//============================= THEME ================================
void ApplyThesisTheme() {
   ChartSetInteger(0, CHART_MODE, CHART_CANDLES);
   ChartSetInteger(0, CHART_COLOR_BACKGROUND, clrWhite);
   ChartSetInteger(0, CHART_COLOR_FOREGROUND, clrBlack);
   ChartSetInteger(0, CHART_COLOR_GRID, clrWhite); // Hide grid
   
   ChartSetInteger(0, CHART_COLOR_CHART_UP, clrBlack);
   ChartSetInteger(0, CHART_COLOR_CHART_DOWN, clrBlack);
   ChartSetInteger(0, CHART_COLOR_CHART_LINE, clrBlack);
   
   ChartSetInteger(0, CHART_COLOR_CANDLE_BULL, clrWhite);
   ChartSetInteger(0, CHART_COLOR_CANDLE_BEAR, clrBlack);
   
   ChartSetInteger(0, CHART_SHOW_GRID, false);
   ChartSetInteger(0, CHART_SHOW_VOLUMES, false);
   
   ChartRedraw(0); // Bắt buộc Redraw để ăn màu
}

//========================== TELEGRAM MODULE =========================
// HFT-SAFE: EA KHÔNG BAO GIỜ gọi WebRequest.
// Giao tiếp 100% qua file: Đọc VQUANT.txt (lệnh), Ghi VQUANT_RESPONSE.txt (phản hồi).
// Python bot chịu trách nhiệm gửi/nhận Telegram.

void TG_WriteResponse(string msg){
   if(!Enable_Telegram) return;
   int handle = FileOpen("VQUANT_RESPONSE.txt", FILE_WRITE|FILE_TXT|FILE_UNICODE|FILE_COMMON);
   if(handle == INVALID_HANDLE) return;
   FileWriteString(handle, msg);
   FileClose(handle);
}

// Đóng TẤT CẢ lệnh (dùng cho KILL switch)
void CloseAllPositions(){
   Trade.SetAsyncMode(true);
   for(int i=PositionsTotal()-1; i>=0; i--){
      ulong tk = PositionGetTicket(i);
      if(tk > 0 && PositionSelectByTicket(tk)){
         if(PositionGetString(POSITION_SYMBOL)==Sym && PositionGetInteger(POSITION_MAGIC)==MagicNumber)
            Trade.PositionClose(tk);
      }
   }
   Trade.SetAsyncMode(false);
   g_seedBuyTicketAfterTP=0; g_seedSellTicketAfterTP=0;
}

// Mở seed chủ động khi bật bot từ Telegram (fix bug chỉ chạy 1 chiều)
void ForceOpenSeeds(){
   RefreshPositionCache();
   bool seed_buy  = (Trading_Mode==CHE_DO_CHI_BUY || Trading_Mode==CHE_DO_BUY_VA_SELL);
   bool seed_sell = (Trading_Mode==CHE_DO_CHI_SELL || Trading_Mode==CHE_DO_BUY_VA_SELL);
      ulong tk=0;
   if(seed_buy && CountPositionsByType(POSITION_TYPE_BUY)==0){
      if(OpenBuy(GetSeedLot(), tk))
         LogCSV("BUY","TG_SEED_OPEN",GetSeedLot(),0,0,0,"Telegram resume seed");
   }
   if(seed_sell && CountPositionsByType(POSITION_TYPE_SELL)==0){
      if(OpenSell(GetSeedLot(), tk))
         LogCSV("SELL","TG_SEED_OPEN",GetSeedLot(),0,0,0,"Telegram resume seed");
   }
   // Reset time gate để CheckAllEntryLogic chạy lại ngay
   g_lastM15CheckTime = 0;
   g_lastSecondCheck = 0;
}

// Thống kê: Profit theo khoảng thời gian + đếm trades
double ProfitSince(datetime from_time){
   double pnl=0.0;
   HistorySelect(from_time, TimeCurrent());
   for(int i=HistoryDealsTotal()-1; i>=0; i--){
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket>0 && HistoryDealGetString(ticket,DEAL_SYMBOL)==Sym &&
         HistoryDealGetInteger(ticket,DEAL_MAGIC)==MagicNumber &&
         HistoryDealGetInteger(ticket,DEAL_ENTRY)==DEAL_ENTRY_OUT)
         pnl += HistoryDealGetDouble(ticket,DEAL_PROFIT)+HistoryDealGetDouble(ticket,DEAL_SWAP)+HistoryDealGetDouble(ticket,DEAL_COMMISSION);
   }
   return pnl;
}
int CountDealsSince(datetime from_time){
   int cnt=0;
   HistorySelect(from_time, TimeCurrent());
   for(int i=HistoryDealsTotal()-1; i>=0; i--){
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket>0 && HistoryDealGetString(ticket,DEAL_SYMBOL)==Sym &&
         HistoryDealGetInteger(ticket,DEAL_MAGIC)==MagicNumber &&
         HistoryDealGetInteger(ticket,DEAL_ENTRY)==DEAL_ENTRY_OUT) cnt++;
   }
   return cnt;
}

string BuildStatusMsg(){
   double bal=g_cache.balance, eq=g_cache.equity;
   double ddp=(bal>1e-9 ? (bal-eq)/bal*100.0 : 0.0);
   int nB=g_cache.cnt_buy, nS=g_cache.cnt_sell;
   string ccy=AccountInfoString(ACCOUNT_CURRENCY);
   long uptime_sec = (long)(TimeCurrent() - g_startTime);
   
   return "📊 V CAPITAL STATUS\n"
      "━━━━━━━━━━━━━━━━\n"
      "💰 Balance: " + DoubleToString(bal,2) + " " + ccy + "\n"
      "💎 Equity: " + DoubleToString(eq,2) + " " + ccy + "\n"
      "📉 DD: " + StringFormat("%.1f%%", ddp>0?ddp:0.0) + "\n"
      "🔢 Orders: B:" + IntegerToString(nB) + " S:" + IntegerToString(nS)
         + " (" + IntegerToString(nB+nS) + "/" + IntegerToString(TotalMaxOrders()) + ")\n"
      "📶 Spread: " + IntegerToString((int)SymbolInfoInteger(Sym,SYMBOL_SPREAD)) + " pts\n"
      "âš¡ Status: " + (g_paused ? "PAUSED" : "Trading") + "\n"
      "⏱ Uptime: " + IntegerToString((int)(uptime_sec/3600)) + "h " + IntegerToString((int)((uptime_sec%3600)/60)) + "m";
}

// Đếm Win/Loss trong khoảng thời gian
void WinLossSince(datetime from_time, int &wins, int &losses){
   wins=0; losses=0;
   HistorySelect(from_time, TimeCurrent());
   for(int i=HistoryDealsTotal()-1; i>=0; i--){
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket>0 && HistoryDealGetString(ticket,DEAL_SYMBOL)==Sym &&
         HistoryDealGetInteger(ticket,DEAL_MAGIC)==MagicNumber &&
         HistoryDealGetInteger(ticket,DEAL_ENTRY)==DEAL_ENTRY_OUT){
         double pnl = HistoryDealGetDouble(ticket,DEAL_PROFIT)+HistoryDealGetDouble(ticket,DEAL_SWAP)+HistoryDealGetDouble(ticket,DEAL_COMMISSION);
         if(pnl >= 0) wins++; else losses++;
      }
   }
}

string BuildReportMsg(string period_cmd){
   MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
   dt.hour=0; dt.min=0; dt.sec=0;
   datetime today_start = StructToTime(dt);
   
   datetime start_time = 0;
   string period_name = "";
   
   if(period_cmd == "REPORT_TODAY"){
      start_time = today_start;
      period_name = "HÔM NAY";
   }
   else if(period_cmd == "REPORT_WEEK"){
      int dow = dt.day_of_week; if(dow==0) dow=7;
      start_time = today_start - (dow-1)*86400;
      period_name = "TUẦN NÀY";
   }
   else if(period_cmd == "REPORT_MONTH"){
      dt.day=1;
      start_time = StructToTime(dt);
      period_name = "THÁNG NÀY";
   }
   else if(period_cmd == "REPORT_QUARTER"){
      start_time = TimeCurrent() - 90*86400;
      period_name = "3 THÁNG QUA";
   }
   else if(period_cmd == "REPORT_YEAR"){
      dt.mon=1; dt.day=1;
      start_time = StructToTime(dt);
      period_name = "NĂM NAY";
   }
   else {
      return "Lỗi: Không rõ khoảng thời gian.";
   }
   
   string ccy = AccountInfoString(ACCOUNT_CURRENCY);
   double bal = g_cache.balance, eq = g_cache.equity;
   double ddp = (bal>1e-9 ? (bal-eq)/bal*100.0 : 0.0);
   double floating = eq - bal;
   
   int wins=0, losses=0;
   double gross_win=0, gross_loss=0, largest_win=0, largest_loss=0;
   double total_commission=0, total_swap=0;
   int max_consec_win=0, max_consec_loss=0, cur_consec_win=0, cur_consec_loss=0;
   
   HistorySelect(start_time, TimeCurrent());
   for(int i=0; i<HistoryDealsTotal(); i++){
      ulong ticket=HistoryDealGetTicket(i);
      if(ticket<=0 || HistoryDealGetString(ticket,DEAL_SYMBOL)!=Sym ||
         HistoryDealGetInteger(ticket,DEAL_MAGIC)!=MagicNumber ||
         HistoryDealGetInteger(ticket,DEAL_ENTRY)!=DEAL_ENTRY_OUT) continue;
      
      double pnl = HistoryDealGetDouble(ticket,DEAL_PROFIT);
      double swap = HistoryDealGetDouble(ticket,DEAL_SWAP);
      double comm = HistoryDealGetDouble(ticket,DEAL_COMMISSION);
      double net = pnl + swap + comm;
      total_swap += swap;
      total_commission += comm;
      
      if(net >= 0){
         wins++;
         gross_win += net;
         if(net > largest_win) largest_win = net;
         cur_consec_win++;
         cur_consec_loss = 0;
         if(cur_consec_win > max_consec_win) max_consec_win = cur_consec_win;
      } else {
         losses++;
         gross_loss += MathAbs(net);
         if(MathAbs(net) > largest_loss) largest_loss = MathAbs(net);
         cur_consec_loss++;
         cur_consec_win = 0;
         if(cur_consec_loss > max_consec_loss) max_consec_loss = cur_consec_loss;
      }
   }
   
   double total_net = gross_win - gross_loss;
   int total_trades = wins + losses;
   double wr = (total_trades > 0 ? (double)wins/total_trades*100.0 : 0.0);
   double avg_win  = (wins > 0 ? gross_win / wins : 0.0);
   double avg_loss = (losses > 0 ? gross_loss / losses : 0.0);
   double profit_factor = (gross_loss > 0.01 ? gross_win / gross_loss : 99.9);
   
   string msg = "📈 BÁO CÁO: " + period_name + "\n"
      "━━━━━━━━━━━━━━━━━━━━\n"
      "💰 Lợi nhuận: " + DoubleToString(total_net,2) + " " + ccy + "\n"
      "📊 Win Rate: " + StringFormat("%.0f%%", wr) + " (" + IntegerToString(wins) + "W / " + IntegerToString(losses) + "L)\n"
      "🔢 Tổng lệnh: " + IntegerToString(total_trades) + " trades\n"
      "━━━━━━━━━━━━━━━━━━━━\n"
      "🏆 Profit Factor: " + StringFormat("%.2f", profit_factor) + "\n"
      "📈 Avg Win: " + DoubleToString(avg_win,2) + " " + ccy + "\n"
      "📉 Avg Loss: " + DoubleToString(avg_loss,2) + " " + ccy + "\n"
      "🎯 Largest Win: " + DoubleToString(largest_win,2) + " " + ccy + "\n"
      "💥 Largest Loss: " + DoubleToString(largest_loss,2) + " " + ccy + "\n"
      "🔥 Max Consec Win: " + IntegerToString(max_consec_win) + "\n"
      "❄️ Max Consec Loss: " + IntegerToString(max_consec_loss) + "\n"
      "💸 Commission: " + DoubleToString(total_commission,2) + " " + ccy + "\n"
      "🔄 Swap: " + DoubleToString(total_swap,2) + " " + ccy + "\n"
      "━━━━━━━━━━━━━━━━━━━━\n"
      "💰 Balance: " + DoubleToString(bal,2) + " " + ccy + "\n"
      "🔄 Floating: " + DoubleToString(floating,2) + " " + ccy + "\n"
      "📉 DD: " + StringFormat("%.1f%%", ddp>0?ddp:0.0);
   
   return msg;
}

void TG_ReadCommand(){
   if(!Enable_Telegram) return;
   
   int handle = FileOpen("VQUANT.txt", FILE_READ|FILE_TXT|FILE_UNICODE|FILE_COMMON);
   if(handle == INVALID_HANDLE) return; // File không tồn tại → 0.01ms, bỏ qua
   
   string cmd = FileReadString(handle);
   FileClose(handle);
   
   if(cmd == "") return;
   
   FileDelete("VQUANT.txt", FILE_COMMON);
   
   StringTrimRight(cmd); StringTrimLeft(cmd);
   Print("V Capital: Telegram command received: ", cmd);
   
   if(cmd == "STOP"){
      CloseAllPositions();
      g_paused = true;
      g_autoOFF_active = true;
      g_autoOFF_reason = "Telegram STOP";
      TG_WriteResponse("🔴 Bot STOPPED. All positions closed.");
      LogCSV("","TG_STOP",0,0,0,0,"Telegram kill switch");
   }
   else if(cmd == "START"){
      g_paused = false;
      g_autoOFF_active = false;
      g_autoOFF_reason = "";
      if(AutoTradingOn() && WithinSession())
         ForceOpenSeeds();
      TG_WriteResponse("🟢 Bot STARTED. Seeds opened.");
      LogCSV("","TG_START",0,0,0,0,"Telegram start");
   }
   else if(cmd == "PAUSE"){
      g_paused = true;
      TG_WriteResponse("⏸ Bot PAUSED. Positions kept.");
   }
   else if(cmd == "RESUME"){
      g_paused = false;
      g_autoOFF_active = false;
      TG_WriteResponse("▶️ Bot RESUMED.");
   }
   else if(cmd == "CLOSE_ALL"){
      CloseAllPositions();
      TG_WriteResponse("✅ All positions CLOSED.");
   }
   else if(cmd == "CLOSE_BUY"){
      CloseBasket(POSITION_TYPE_BUY);
      TG_WriteResponse("✅ BUY basket CLOSED.");
   }
   else if(cmd == "CLOSE_SELL"){
      CloseBasket(POSITION_TYPE_SELL);
      TG_WriteResponse("✅ SELL basket CLOSED.");
   }
   else if(cmd == "MODE_BUY"){
      Trading_Mode = CHE_DO_CHI_BUY;
      CloseBasket(POSITION_TYPE_SELL);
      TG_WriteResponse("✅ Đã chuyển sang chế độ CHỈ BUY. Đã đóng các lệnh SELL (nếu có).");
      LogCSV("","TG_MODE_BUY",0,0,0,0,"Telegram mode changed to ONLY BUY");
   }
   else if(cmd == "MODE_SELL"){
      Trading_Mode = CHE_DO_CHI_SELL;
      CloseBasket(POSITION_TYPE_BUY);
      TG_WriteResponse("✅ Đã chuyển sang chế độ CHỈ SELL. Đã đóng các lệnh BUY (nếu có).");
      LogCSV("","TG_MODE_SELL",0,0,0,0,"Telegram mode changed to ONLY SELL");
   }
   else if(cmd == "MODE_BOTH"){
      Trading_Mode = CHE_DO_BUY_VA_SELL;
      TG_WriteResponse("✅ Đã chuyển sang chế độ BUY & SELL.");
      LogCSV("","TG_MODE_BOTH",0,0,0,0,"Telegram mode changed to BUY & SELL");
   }
   else if(cmd == "STATUS")  { TG_WriteResponse(BuildStatusMsg()); }
   else if(StringFind(cmd, "REPORT_") == 0) { TG_WriteResponse(BuildReportMsg(cmd)); }
}

int OnInit(){
  ArrayInitialize(g_closing_tickets, 0);
  ArrayInitialize(g_closing_times, 0);
  Trading_Mode = Trading_Mode_Input;
  ApplyThesisTheme();

  Sym = _Symbol;
  PointV = SymbolInfoDouble(Sym, SYMBOL_POINT);
  MinLot = SymbolInfoDouble(Sym,SYMBOL_VOLUME_MIN);
  MaxLot = SymbolInfoDouble(Sym,SYMBOL_VOLUME_MAX);
  LotStep= SymbolInfoDouble(Sym,SYMBOL_VOLUME_STEP);
  DigitsValue=(int)SymbolInfoInteger(Sym,SYMBOL_DIGITS);

  if(PointV<=1e-9 || DigitsValue<=0){ Print("Error: invalid point/digits for ",Sym); return INIT_FAILED; }

  g_startTime=TimeCurrent();
  Trade.SetExpertMagicNumber(MagicNumber);
  Trade.SetAsyncMode(false);           // Mặc định sync cho open (cần ResultPrice)
  Trade.SetDeviationInPoints(1000);     // HFT: cho phép trượt tối đa 1000 points để chống Broker Reject (~$0.10) để không bị reject khi giá bay
  Trade.SetTypeFilling(ORDER_FILLING_IOC); // HFT: Immediate-or-Cancel, nhanh nhất
  g_runtimeLang=Interface_Language;

  // EMA indicator handles
  g_hEmaFastH4 = iMA(Sym, Trend_Timeframe, EMA_Fast, 0, MODE_EMA, PRICE_CLOSE);
  g_hEmaSlowH4 = iMA(Sym, Trend_Timeframe, EMA_Slow,  0, MODE_EMA, PRICE_CLOSE);
  g_hEmaFastH1 = iMA(Sym, EMA_Confirm_Timeframe,   EMA_Fast, 0, MODE_EMA, PRICE_CLOSE);
  g_hEmaSlowH1 = iMA(Sym, EMA_Confirm_Timeframe,   EMA_Slow,  0, MODE_EMA, PRICE_CLOSE);
  if(g_hEmaFastH4==INVALID_HANDLE || g_hEmaSlowH4==INVALID_HANDLE ||
     g_hEmaFastH1==INVALID_HANDLE || g_hEmaSlowH1==INVALID_HANDLE)
     Print("Warning: EMA indicator init failed");
     
  if(Enable_ATR_Grid){
     g_hATR = iATR(Sym, ATR_Timeframe, ATR_Period);
     if(g_hATR == INVALID_HANDLE) Print("Warning: ATR indicator init failed");
  }
  
  InitTiers();
  EnsureLogOpened();
  EventSetTimer(1);
  g_lastM15CheckTime=0;

  ulong ticketOnInit=0;
   RefreshPositionCache(); // Cần cache trước khi check CountPositionsByType
  if (AutoTradingOn() && !IsStopped() && WithinSession()) {
    bool seed_buy =(Trading_Mode==CHE_DO_CHI_BUY || Trading_Mode==CHE_DO_BUY_VA_SELL);
    bool seed_sell=(Trading_Mode==CHE_DO_CHI_SELL || Trading_Mode==CHE_DO_BUY_VA_SELL);
    

    bool seeded=false;
    if(seed_buy && CountPositionsByType(POSITION_TYPE_BUY)==0){ if(OpenBuy(GetSeedLot(),ticketOnInit)) seeded=true; }
    if(seed_sell && CountPositionsByType(POSITION_TYPE_SELL)==0){ if(OpenSell(GetSeedLot(),ticketOnInit)) seeded=true; }
    g_lastM15CheckTime = iTime(_Symbol,Entry_Timeframe,0) - (seeded?1:0);
  } else {
    Print("OnInit - AutoTrading disabled or outside session. Seed skipped.");
    g_lastM15CheckTime = iTime(_Symbol,Entry_Timeframe,0);
  }
  Print("V Capital: Initialized. Logic on ", EnumToString(Entry_Timeframe), " close.");
  DrawDashboard(); // Vẽ Dashboard NGAY LẬP TỨC khi bật bot, không đợi OnTimer
  return INIT_SUCCEEDED;
}
void OnDeinit(const int reason){
  EventKillTimer();
  if(g_hEmaFastH4!=INVALID_HANDLE) IndicatorRelease(g_hEmaFastH4);
  if(g_hEmaSlowH4!=INVALID_HANDLE) IndicatorRelease(g_hEmaSlowH4);
  if(g_hEmaFastH1!=INVALID_HANDLE) IndicatorRelease(g_hEmaFastH1);
  if(g_hEmaSlowH1!=INVALID_HANDLE) IndicatorRelease(g_hEmaSlowH1);
  if(g_hATR!=INVALID_HANDLE) IndicatorRelease(g_hATR);
  if(g_fileHandle!=INVALID_HANDLE){ FileClose(g_fileHandle); g_fileHandle=INVALID_HANDLE; }
  DeleteObjectsByPrefix("VC_LBL_");
  DeleteObjectsByPrefix("VC_BTN_");
  Print("V Capital: Deinitialized.");
}
void OnTick(){
  // HFT: scan position 1 lần duy nhất, các hàm khác đọc từ cache
  RefreshPositionCache();
  
  if(Enable_ATR_Grid){
      datetime atr_time = iTime(Sym, ATR_Timeframe, 0);
      if(atr_time > g_last_atr_time){
         double atr_arr[1];
         // Lấy ATR của nến ĐÃ ĐÓNG (index 1), không lấy nến đang chạy (index 0)
         if(CopyBuffer(g_hATR, 0, 1, 1, atr_arr) > 0){
             g_last_atr_time = atr_time; // Chỉ update khi lấy data thành công
             g_current_atr_val = atr_arr[0] / PointV;
         }
      }
  }

  if(CheckDDCutoff()){ DrawDashboard(); return; }
  // Auto ON/OFF checks
  CheckAutoOFF_ProfitLoss();
  CheckAutoOFF_Price();
  CheckAutoON_Timer();
  CheckAutoON_Price();
  
  CheckBasketTP();
  CheckSeedMicroScalp();

  // Entry logic: phụ thuộc vào Entry_Every_Second
  if(Entry_Every_Second){
    // Quét liên tục mỗi 100ms (HFT mode)
    static uint last_entry_tick = 0;
    if(GetTickCount() - last_entry_tick >= 100){
       CheckAllEntryLogic();
       last_entry_tick = GetTickCount();
    }
  } else {
    // Chỉ quét khi nến Entry_Timeframe đóng (chế độ bình thường)
    datetime cur_bar = iTime(_Symbol, Entry_Timeframe, 0);
    if(cur_bar > g_lastM15CheckTime){
       g_lastM15CheckTime = cur_bar;
       CheckAllEntryLogic();
    }
  }
}
void OnTimer(){ TG_ReadCommand(); DrawDashboard(); }

//+------------------------------------------------------------------+

