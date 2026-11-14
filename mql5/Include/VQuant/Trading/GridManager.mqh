//+------------------------------------------------------------------+
//|                                                  GridManager.mqh |
//|                     VQuant Quantitative Algorithmic Trading Suite |
//|        Author: Nguyễn Mạnh Cường_B22DCCN099                      |
//|        Institution: Posts and Telecommunications Institute of Tech|
//|        Architecture: Object-Oriented Quant Risk & Execution Core  |
//+------------------------------------------------------------------+
#property copyright "Nguyễn Mạnh Cường_B22DCCN099"
#property link      "https://github.com/cuongb22dccn099/VQuant-Thesis"
#property strict

//+------------------------------------------------------------------+
//| Enumeration of Volatility Regimes for Dynamic Grid Spacing       |
//+------------------------------------------------------------------+
enum ENUM_VOLATILITY_REGIME
{
   VOLATILITY_REGIME_LOW        = 0, // Thấp (Sideway tích lũy nén biên độ)
   VOLATILITY_REGIME_NORMAL     = 1, // Bình thường (Dao động tiêu chuẩn)
   VOLATILITY_REGIME_ELEVATED   = 2, // Biến động tăng (Tin tức nhẹ / Trend mở rộng)
   VOLATILITY_REGIME_EXTREME    = 3  // Bão giá / High Impact News (Giãn lưới tối đa)
};

//+------------------------------------------------------------------+
//| Class: CGridManager                                              |
//| Purpose: Enterprise-grade Dynamic DCA Grid & Volatility Engine    |
//|          Handles 2D Matrix Nested Cycles, ATR adaptive spacing,   |
//|          Tier volume allocation, and Breakeven calculations.      |
//+------------------------------------------------------------------+
class CGridManager
{
private:
   CycleConfig          m_cycles[];
   int                  m_cycleCount;
   bool                 m_initialized;
   
   // Internal parsing utilities
   int ParseCSVToDoubles(const string csv, double &arr[])
   {
      string parts[];
      int count = StringSplit(csv, ',', parts);
      ArrayResize(arr, count);
      for(int i = 0; i < count; i++)
      {
         StringTrimLeft(parts[i]);
         StringTrimRight(parts[i]);
         arr[i] = StringToDouble(parts[i]);
      }
      return count;
   }
   
   int ParseCSVToInts(const string csv, int &arr[])
   {
      string parts[];
      int count = StringSplit(csv, ',', parts);
      ArrayResize(arr, count);
      for(int i = 0; i < count; i++)
      {
         StringTrimLeft(parts[i]);
         StringTrimRight(parts[i]);
         arr[i] = (int)StringToInteger(parts[i]);
      }
      return count;
   }

public:
   // Constructor & Destructor
   CGridManager() : m_cycleCount(0), m_initialized(false) {}
   ~CGridManager() { ArrayFree(m_cycles); }

   //+---------------------------------------------------------------+
   //| Initialize Matrix Cycles from comma & semicolon delimited CSV |
   //+---------------------------------------------------------------+
   bool Initialize(const string volumeCapsCsv, const string startLotsCsv, const string gridDistancesCsv)
   {
      string cycles_vol[], cycles_lot[], cycles_dist[];
      int nC_vol  = StringSplit(volumeCapsCsv, ';', cycles_vol);
      int nC_lot  = StringSplit(startLotsCsv, ';', cycles_lot);
      int nC_dist = StringSplit(gridDistancesCsv, ';', cycles_dist);
      
      m_cycleCount = MathMax(nC_vol, MathMax(nC_lot, nC_dist));
      if(m_cycleCount <= 0)
      {
         Print("[CGridManager] Critical: No valid cycle definitions found in inputs.");
         m_initialized = false;
         return false;
      }
      
      ArrayResize(m_cycles, m_cycleCount);
      
      for(int c = 0; c < m_cycleCount; c++)
      {
         string s_vol  = (c < nC_vol)  ? cycles_vol[c]  : (nC_vol > 0  ? cycles_vol[nC_vol - 1]  : "99.0");
         string s_lot  = (c < nC_lot)  ? cycles_lot[c]  : (nC_lot > 0  ? cycles_lot[nC_lot - 1]  : "0.01");
         string s_dist = (c < nC_dist) ? cycles_dist[c] : (nC_dist > 0 ? cycles_dist[nC_dist - 1] : "2000");
         
         double arr_vol[], arr_lot[];
         int arr_dist[];
         int nT_vol  = ParseCSVToDoubles(s_vol, arr_vol);
         int nT_lot  = ParseCSVToDoubles(s_lot, arr_lot);
         int nT_dist = ParseCSVToInts(s_dist, arr_dist);
         
         int t_count = MathMax(nT_vol, MathMax(nT_lot, nT_dist));
         if(t_count == 0) t_count = 1; // Failsafe
         
         m_cycles[c].tier_count = t_count;
         ArrayResize(m_cycles[c].tiers, t_count);
         
         for(int t = 0; t < t_count; t++)
         {
            m_cycles[c].tiers[t].volume_cap    = (t < nT_vol)  ? arr_vol[t]  : (nT_vol > 0  ? arr_vol[nT_vol - 1]  : 99.0);
            m_cycles[c].tiers[t].start_lot     = (t < nT_lot)  ? arr_lot[t]  : (nT_lot > 0  ? arr_lot[nT_lot - 1]  : 0.01);
            m_cycles[c].tiers[t].grid_distance = (t < nT_dist) ? arr_dist[t] : (nT_dist > 0 ? arr_dist[nT_dist - 1] : 2000);
         }
      }
      
      m_initialized = true;
      LogMatrixTopology();
      return true;
   }

   //+---------------------------------------------------------------+
   //| Log Matrix Topology to journal for audit & verification       |
   //+---------------------------------------------------------------+
   void LogMatrixTopology()
   {
      PrintFormat("========== [VQuant Matrix Engine] Initialized: %d Nested Cycle(s) ==========", m_cycleCount);
      for(int c = 0; c < m_cycleCount; c++)
      {
         PrintFormat(" [Cycle #%02d] Total Tiers: %d", c + 1, m_cycles[c].tier_count);
         for(int t = 0; t < m_cycles[c].tier_count; t++)
         {
            PrintFormat("   -> Tier %d | StartLot: %.2f | VolCap: %.2f | GridDist: %d pts",
                        t + 1,
                        m_cycles[c].tiers[t].start_lot,
                        m_cycles[c].tiers[t].volume_cap,
                        m_cycles[c].tiers[t].grid_distance);
         }
      }
      PrintFormat("=========================================================================");
   }

   //+---------------------------------------------------------------+
   //| Determine Current Tier and Cycle based on Cumulative Volume    |
   //+---------------------------------------------------------------+
   void GetTierAndCycle(ENUM_POSITION_TYPE type, int &out_tier, int &out_cycle)
   {
      out_tier = 0;
      out_cycle = 0;
      if(!m_initialized || m_cycleCount <= 0) return;
      
      double total_vol = SumLotsByType(type);
      if(total_vol <= 1e-9) return;
      
      double remaining_vol = NormalizeDouble(total_vol, 2);
      int cycle = 0;
      
      while(remaining_vol >= 0.009) // Float precision threshold
      {
         int c_idx = (cycle < m_cycleCount) ? cycle : (m_cycleCount - 1);
         int t_count = m_cycles[c_idx].tier_count;
         bool cycle_completed = false;
         
         for(int t = 0; t < t_count; t++)
         {
            double tier_cap = m_cycles[c_idx].tiers[t].volume_cap;
            if(remaining_vol >= tier_cap - 0.001)
            {
               remaining_vol -= tier_cap;
               remaining_vol = NormalizeDouble(remaining_vol, 2);
               if(t == t_count - 1) cycle_completed = true;
            }
            else
            {
               out_tier = t;
               out_cycle = cycle;
               return;
            }
         }
         
         if(cycle_completed)
         {
            cycle++;
            if(cycle >= 100) // Circuit breaker safety
            {
               out_tier = m_cycles[c_idx].tier_count - 1;
               out_cycle = cycle;
               return;
            }
         }
         else
         {
            break;
         }
      }
   }

   //+---------------------------------------------------------------+
   //| Detect Market Volatility Regime based on Normalized ATR       |
   //+---------------------------------------------------------------+
   ENUM_VOLATILITY_REGIME DetectVolatilityRegime(double currentAtr, double atrThreshold)
   {
      if(currentAtr <= 0 || atrThreshold <= 0) return VOLATILITY_REGIME_NORMAL;
      
      double ratio = currentAtr / atrThreshold;
      if(ratio < 0.5) return VOLATILITY_REGIME_LOW;
      if(ratio < 1.0) return VOLATILITY_REGIME_NORMAL;
      if(ratio < 1.5) return VOLATILITY_REGIME_ELEVATED;
      return VOLATILITY_REGIME_EXTREME;
   }

   //+---------------------------------------------------------------+
   //| Calculate Dynamic Adaptive Grid Distance (Points)             |
   //+---------------------------------------------------------------+
   int CalculateAdaptiveGridDistance(ENUM_POSITION_TYPE type, double currentAtr, double atrThreshold, double atrMultiplier)
   {
      int base_grid = 2000;
      if(m_cycleCount > 0)
      {
         int tier = 0, cycle = 0;
         GetTierAndCycle(type, tier, cycle);
         int c_idx = (cycle < m_cycleCount) ? cycle : (m_cycleCount - 1);
         base_grid = m_cycles[c_idx].tiers[tier].grid_distance;
      }
      
      // Dynamic ATR expansion logic
      if(currentAtr > 0 && atrThreshold > 0)
      {
         ENUM_VOLATILITY_REGIME regime = DetectVolatilityRegime(currentAtr, atrThreshold);
         switch(regime)
         {
            case VOLATILITY_REGIME_LOW:
               // Slight compression during low volatility sideway consolidation
               base_grid = (int)(base_grid * 0.9);
               break;
               
            case VOLATILITY_REGIME_NORMAL:
               // Standard matrix spacing
               break;
               
            case VOLATILITY_REGIME_ELEVATED:
               // Mild expansion to avoid rapid stacking
               base_grid = (int)(base_grid * MathMax(1.2, atrMultiplier * 0.75));
               break;
               
            case VOLATILITY_REGIME_EXTREME:
               // Full storm shelter expansion
               base_grid = (int)(base_grid * MathMax(1.5, atrMultiplier));
               break;
         }
      }
      
      return base_grid;
   }

   //+---------------------------------------------------------------+
   //| Calculate Next DCA Lot with Safety Volume Boundaries         |
   //+---------------------------------------------------------------+
   double CalculateNextLot(ENUM_POSITION_TYPE type)
   {
      if(m_cycleCount <= 0) return GetSeedLot();
      
      int tier = 0, cycle = 0;
      GetTierAndCycle(type, tier, cycle);
      
      if(cycle >= m_cycleCount)
      {
         PrintFormat("[CGridManager] Warning: Cycle overflow limit reached (Cycle %d >= Max %d). Halting DCA!",
                     cycle + 1, m_cycleCount);
         return 0.0;
      }
      
      int c_idx = cycle;
      int t_count = m_cycles[c_idx].tier_count;
      int t_idx = (tier < t_count) ? tier : (t_count - 1);
      
      double lot = m_cycles[c_idx].tiers[t_idx].start_lot;
      return NormalizeLot(lot);
   }

   //+---------------------------------------------------------------+
   //| Get Initial Seed Lot from Cycle 0, Tier 0                     |
   //+---------------------------------------------------------------+
   double GetSeedLot()
   {
      if(m_cycleCount > 0 && m_cycles[0].tier_count > 0)
      {
         return NormalizeLot(m_cycles[0].tiers[0].start_lot);
      }
      return NormalizeLot(0.01);
   }

   //+---------------------------------------------------------------+
   //| Calculate Breakeven Price & Volume Weighted Average           |
   //+---------------------------------------------------------------+
   double CalculateBreakevenPrice(ENUM_POSITION_TYPE type, double &out_total_vol)
   {
      double sum_weighted = 0.0;
      out_total_vol = 0.0;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         ulong ticket = PositionGetTicket(i);
         if(ticket <= 0) continue;
         if(PositionGetString(POSITION_SYMBOL) != Sym) continue;
         if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;
         if((ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE) != type) continue;
         
         double lot = PositionGetDouble(POSITION_VOLUME);
         double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
         
         sum_weighted += (lot * open_price);
         out_total_vol += lot;
      }
      
      if(out_total_vol <= 1e-9) return 0.0;
      return NormalizeDouble(sum_weighted / out_total_vol, DigitsValue);
   }

   //+---------------------------------------------------------------+
   //| Accessors & State Inquiries                                   |
   //+---------------------------------------------------------------+
   int  GetCycleCount() const { return m_cycleCount; }
   bool IsInitialized() const { return m_initialized; }
   
   // Sync internal state to legacy global structures for backwards compatibility
   void SyncToLegacyGlobals(CycleConfig &legacyCycles[], int &legacyCount)
   {
      legacyCount = m_cycleCount;
      ArrayResize(legacyCycles, m_cycleCount);
      for(int c = 0; c < m_cycleCount; c++)
      {
         legacyCycles[c].tier_count = m_cycles[c].tier_count;
         ArrayResize(legacyCycles[c].tiers, m_cycles[c].tier_count);
         for(int t = 0; t < m_cycles[c].tier_count; t++)
         {
            legacyCycles[c].tiers[t] = m_cycles[c].tiers[t];
         }
      }
   }
};

//+------------------------------------------------------------------+
//| Global Grid Manager Engine Instance                              |
//+------------------------------------------------------------------+
CGridManager ExtGridManager;

//+------------------------------------------------------------------+
//| Backward Compatibility Wrapper Layer                             |
//| Ensures existing V_Capital_OOP, Dashboard, and OrderManager code |
//| runs identically with 100% interoperability.                     |
//+------------------------------------------------------------------+
void InitTiers()
{
   if(ExtGridManager.Initialize(Matrix_Volume_Caps, Matrix_Start_Lots, Matrix_Grid_Distances))
   {
      ExtGridManager.SyncToLegacyGlobals(g_cycles, g_cycleCount);
   }
}

void GetTierAndCycleIndex(ENUM_POSITION_TYPE type, int &out_tier, int &out_cycle)
{
   ExtGridManager.GetTierAndCycle(type, out_tier, out_cycle);
}

int TotalMaxOrders()
{
   return 999; // Matrix cycle controls max orders
}

double GetSeedLot()
{
   return ExtGridManager.GetSeedLot();
}
