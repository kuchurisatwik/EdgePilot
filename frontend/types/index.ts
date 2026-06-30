export type AuthUser = {
  id: string;
  email: string;
  name: string;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type UserSettings = {
  account_size: string;
  default_risk_pct: string;
  quote_currency: string;
  timezone: string;
};

export type RiskAppetite = "conservative" | "moderate" | "aggressive";

export type Strategy = {
  id: string;
  name: string;
  description: string | null;
  risk_appetite: RiskAppetite;
  notes: string | null;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
};

export type TradeDirection = "long" | "short";
export type OrderType = "market" | "limit";
export type TradeStatus = "draft" | "open" | "closed";

export type TradeRiskBreakdown = {
  per_unit_risk: string;
  risk_amount: string;
  position_size: string;
  max_loss: string;
  capital_exposure: string;
  rr_ratio: string | null;
  exposure_pct: string | null;
};

export type Trade = {
  id: string;
  strategy_id: string;
  symbol: string;
  direction: TradeDirection;
  order_type: OrderType;
  entry_price: string;
  stop_loss: string;
  take_profit: string | null;
  current_price: string | null;
  account_size_at_entry: string;
  risk_pct: string;
  status: TradeStatus;
  notes: string | null;
  thesis: string | null;
  created_at: string;
  risk: TradeRiskBreakdown;
};
