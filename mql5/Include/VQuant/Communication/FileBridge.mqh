//+------------------------------------------------------------------+
//| FileBridge.mqh                                                   |
//+------------------------------------------------------------------+
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
