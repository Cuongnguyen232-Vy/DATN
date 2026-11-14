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


#include <VQuant/Config/Enums.mqh>
#include <VQuant/Config/Inputs.mqh>
#include <VQuant/Communication/FileBridge.mqh>
#include <VQuant/Indicators/Filters.mqh>
#include <VQuant/Trading/GridManager.mqh>
#include <VQuant/Trading/OrderManager.mqh>
#include <VQuant/UI/Dashboard.mqh>

int OnInit(){
  ArrayInitialize(g_closing_tickets, 0);
  ArrayInitialize(g_closing_times, 0);
  Trading_Mode = Trading_Mode_Input;
  g_runtime_AI_Bridge = Enable_AI_Bridge;
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

  // Cập nhật Dashboard thời gian thực trên mỗi nhịp giá (throttled 200ms để tối ưu hiệu năng)
  static uint last_dash_tick = 0;
  if(GetTickCount() - last_dash_tick >= 200){
     DrawDashboard();
     last_dash_tick = GetTickCount();
  }
}
void OnTimer(){ TG_ReadCommand(); DrawDashboard(); }

void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if(id == CHARTEVENT_OBJECT_CLICK)
   {
      if(sparam == "VC_BTN_MODE") {
         if(Trading_Mode == CHE_DO_BUY_VA_SELL) Trading_Mode = CHE_DO_CHI_BUY;
         else if(Trading_Mode == CHE_DO_CHI_BUY) Trading_Mode = CHE_DO_CHI_SELL;
         else Trading_Mode = CHE_DO_BUY_VA_SELL;
         ObjectSetInteger(0, sparam, OBJPROP_STATE, false);
         DrawDashboard();
         Print("[VQuant UI] Chế độ giao dịch chuyển sang: ", EnumToString(Trading_Mode));
      }
      else if(sparam == "VC_BTN_AI") {
         g_runtime_AI_Bridge = !g_runtime_AI_Bridge;
         ObjectSetInteger(0, sparam, OBJPROP_STATE, false);
         DrawDashboard();
         Print("[VQuant UI] Bộ lọc AI chuyển sang: ", (g_runtime_AI_Bridge ? "BẬT (FILTER)" : "TẮT (FREE)"));
      }
      else if(sparam == "VC_BTN_CLOSE_ALL") {
         ObjectSetInteger(0, sparam, OBJPROP_STATE, false);
         CloseBasket(POSITION_TYPE_BUY);
         CloseBasket(POSITION_TYPE_SELL);
         DrawDashboard();
         Print("[VQuant UI] Nút ĐÓNG TẤT CẢ LỆNH đã được kích hoạt!");
      }
   }
}

