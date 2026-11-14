//+------------------------------------------------------------------+
//| Filters.mqh                                                      |
//+------------------------------------------------------------------+
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
string GetTrendString(){
  if(EMA_Fast<=0 || EMA_Slow<=0) return "OFF";
  bool up=IsTrendBuy(), dn=IsTrendSell();
  if(up && !dn) return "UP";
  if(dn && !up) return "DOWN";
  return "NEUTRAL";
}
