//+------------------------------------------------------------------+
//| Dashboard.mqh                                                    |
//+------------------------------------------------------------------+
//============================= I18N =================================
string L(const string key){
  const bool EN=(g_runtimeLang==LANG_EN);
  if(EN){
    if(key=="EA_TITLE")          return "Nguyen Manh Cuong _ B22DCCN099";
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
    if(key=="EA_TITLE")          return "Nguyen Manh Cuong _ B22DCCN099";
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
//============================= HELPERS: UI CLEANUP ===================
void DeleteObjectsByPrefix(const string prefix){
   int total = ObjectsTotal(0);
   for(int i=total-1;i>=0;i--){
      string name = ObjectName(0,i);
      if(StringFind(name,prefix,0)==0) ObjectDelete(0,name);
   }
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

void SetButton(long chart_id, string name, string text, int x, int y, int w, int h, color bgClr, color textClr, int font_size=8) {
   if(ObjectFind(chart_id, name) < 0) {
      ObjectCreate(chart_id, name, OBJ_BUTTON, 0, 0, 0);
   }
   ObjectSetInteger(chart_id, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(chart_id, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(chart_id, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(chart_id, name, OBJPROP_XSIZE, w);
   ObjectSetInteger(chart_id, name, OBJPROP_YSIZE, h);
   ObjectSetString(chart_id, name, OBJPROP_TEXT, text);
   ObjectSetInteger(chart_id, name, OBJPROP_BGCOLOR, bgClr);
   ObjectSetInteger(chart_id, name, OBJPROP_COLOR, textClr);
   ObjectSetInteger(chart_id, name, OBJPROP_FONTSIZE, font_size);
   ObjectSetString(chart_id, name, OBJPROP_FONT, "Segoe UI");
   ObjectSetInteger(chart_id, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(chart_id, name, OBJPROP_STATE, false);
}

void DrawDashboard(){
  string status_str="Running";
  color statusClr=clrLime;
  if(!Show_Dashboard){ DeleteObjectsByPrefix("VC_"); return; }

  long chart_id=ChartID();
  int font_size=(Dashboard_FontSize==CO_NHO?8:(Dashboard_FontSize==CO_VUA?10:12));
  int line_h=(int)(font_size * 1.8); color txt=clrBlack, posC=clrForestGreen, negC=clrFireBrick, sep=clrDimGray;

  int panel_w=290, x=16, y=16; int x_val=panel_w-20;

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

  // --- AI Model & Sentinel Telemetry ---
  ReadAISignal();
  string ai_bridge_str = "STANDALONE";
  color ai_bridge_clr = clrDimGray;
  string ai_signal_str = "NEUTRAL";
  color ai_signal_clr = clrDimGray;

  if(g_runtime_AI_Bridge){
      if(g_ai_signal_time > 0 && (TimeCurrent() - g_ai_signal_time < 4 * 3600)){
          ai_bridge_str = "ONLINE (Bridge OK)";
          ai_bridge_clr = posC;
          if(g_ai_signal == "LONG_POSITION_ON"){
              ai_signal_str = StringFormat("BUY (%.1f%%)", g_ai_confidence * 100.0);
              ai_signal_clr = posC;
          } else if(g_ai_signal == "SHORT_POSITION_ON"){
              ai_signal_str = StringFormat("SELL (%.1f%%)", g_ai_confidence * 100.0);
              ai_signal_clr = negC;
          } else {
              ai_signal_str = StringFormat("HOLD (%.1f%%)", g_ai_confidence * 100.0);
              ai_signal_clr = clrGold;
          }
      } else {
          ai_bridge_str = "WAITING PYTHON...";
          ai_bridge_clr = clrDarkOrange;
          ai_signal_str = "DCA BASE MODE";
          ai_signal_clr = clrDimGray;
      }
  } else {
      ai_bridge_str = "OFF (Manual DCA)";
      ai_bridge_clr = clrDimGray;
      ai_signal_str = "STANDALONE";
      ai_signal_clr = clrDimGray;
  }
  SetLabel(chart_id,"VC_LBL_AIBRIDGE_L","AI Bridge:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_AIBRIDGE_V",ai_bridge_str,x+x_val,yy,CORNER_LEFT_UPPER,ai_bridge_clr,font_size,"Tahoma",1); yy+=line_h;
  SetLabel(chart_id,"VC_LBL_AISIG_L","AI Signal:",x,yy,CORNER_LEFT_UPPER,txt,font_size);
  SetLabel(chart_id,"VC_LBL_AISIG_V",ai_signal_str,x+x_val,yy,CORNER_LEFT_UPPER,ai_signal_clr,font_size,"Tahoma",1); yy+=line_h;


  

  
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
  SetLabel(chart_id,"VC_LBL_COPY","Ban quyen: Nguyen Manh Cuong _ B22DCCN099",x,yy,CORNER_LEFT_UPPER,clrSilver,font_size-1,"Tahoma",0); yy+=line_h;

  // --- INTERACTIVE BUTTONS ---
  yy += 6;
  string btn_mode_text = (Trading_Mode==CHE_DO_BUY_VA_SELL?"MODE: BUY & SELL":(Trading_Mode==CHE_DO_CHI_BUY?"MODE: ONLY BUY":"MODE: ONLY SELL"));
  color btn_mode_bg = (Trading_Mode==CHE_DO_BUY_VA_SELL? C'40,60,90' : (Trading_Mode==CHE_DO_CHI_BUY? C'20,80,40' : C'120,40,40'));
  SetButton(chart_id, "VC_BTN_MODE", btn_mode_text, x, yy, 130, 22, btn_mode_bg, clrWhite, 8);
  
  string btn_ai_text = (g_runtime_AI_Bridge ? "AI: ON (FILTER)" : "AI: OFF (FREE)");
  color btn_ai_bg = (g_runtime_AI_Bridge ? C'20,100,50' : C'120,50,50');
  SetButton(chart_id, "VC_BTN_AI", btn_ai_text, x + 135, yy, 125, 22, btn_ai_bg, clrWhite, 8);
  
  yy += 25;
  SetButton(chart_id, "VC_BTN_CLOSE_ALL", "⚠️ DONG TAT CA LENH (CLOSE ALL)", x, yy, 260, 22, C'160,30,30', clrWhite, 8);

  ChartRedraw(chart_id);
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
