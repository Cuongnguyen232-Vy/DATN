//+------------------------------------------------------------------+
//| OrderManager.mqh                                                 |
//+------------------------------------------------------------------+
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
  
  // Tính toán khoảng cách lưới tự thích ứng theo mô hình biến động của ExtGridManager
  int grid_pts = ExtGridManager.CalculateAdaptiveGridDistance(
                    type, 
                    Enable_ATR_Grid ? g_current_atr_val : 0.0, 
                    ATR_Threshold_Points, 
                    ATR_Grid_Multiplier);
  
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
  return ExtGridManager.CalculateNextLot(type);
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
    string file_name = StringFormat("vc_signal_%s.txt", Symbol());
    int handle = FileOpen(file_name, FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
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
  if(g_runtime_AI_Bridge){
      ReadAISignal();
      bool ai_buy = false, ai_sell = false;
      if(TimeCurrent() - g_ai_signal_time < 4 * 3600) {
          if(g_ai_signal == "LONG_POSITION_ON" && g_ai_confidence >= AI_Min_Confidence) ai_buy = true;
          if(g_ai_signal == "SHORT_POSITION_ON" && g_ai_confidence >= AI_Min_Confidence) ai_sell = true;
      }
      
      if(CountPositionsByType(POSITION_TYPE_BUY) == 0) {
          if(!ai_buy) can_buy = false; 
      }
      if(CountPositionsByType(POSITION_TYPE_SELL) == 0) {
          if(!ai_sell) can_sell = false;
      }
  }
  // --- END AI LOGIC INJECTION ---

  if(can_buy || CountPositionsByType(POSITION_TYPE_BUY) > 0)  TryDCAOrBalance(POSITION_TYPE_BUY);
  if(can_sell || CountPositionsByType(POSITION_TYPE_SELL) > 0) TryDCAOrBalance(POSITION_TYPE_SELL);
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
bool AutoTradingOn()
{
    return (bool)TerminalInfoInteger(TERMINAL_TRADE_ALLOWED);
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
