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

export type RuleStatus = "PASS" | "WARNING" | "BLOCK";
export type RuleSeverity = "warning" | "block";
export type RuleType =
  | "max_risk_per_trade"
  | "daily_loss_limit"
  | "weekly_loss_limit"
  | "consecutive_loss_limit";

export type RuleViolation = {
  rule_type: RuleType;
  severity: RuleSeverity;
  message: string;
  observed: string;
  threshold: string;
};

export type RuleEvaluationResult = {
  status: RuleStatus;
  violations: RuleViolation[];
};

export type RiskRule = {
  rule_type: RuleType;
  threshold: string;
  severity: RuleSeverity;
  is_enabled: boolean;
};

export type RiskCalcResponse = {
  risk: TradeRiskBreakdown;
  rules: RuleEvaluationResult;
};

export type TradeResult = "win" | "loss" | "breakeven";

export type Trade = {
  id: string;
  strategy_id: string;
  strategy_name: string;
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
  rule_overridden: boolean;
  notes: string | null;
  thesis: string | null;
  created_at: string;
  opened_at: string | null;
  closed_at: string | null;
  exit_price: string | null;
  pnl: string | null;
  r_multiple: string | null;
  result: TradeResult | null;
  risk: TradeRiskBreakdown;
};

export type TradeListResponse = {
  items: Trade[];
  total: number;
  page: number;
  page_size: number;
};

export type JournalFilters = {
  strategy_id?: string;
  symbol?: string;
  result?: TradeResult;
  status?: TradeStatus;
  page?: number;
  page_size?: number;
};

export type AnalyticsSummary = {
  trade_count: number;
  win_rate: string | null;
  profit_factor: string | null;
  expectancy: string | null;
  average_r: string | null;
  net_pnl: string;
  gross_profit: string;
  gross_loss: string;
  max_drawdown: string;
  max_drawdown_pct: string | null;
};

export type EquityPoint = { date: string; equity: string; drawdown: string };
export type EquityCurveResponse = { starting_balance: string; points: EquityPoint[] };

export type GroupPerformance = {
  key: string;
  label: string;
  trade_count: number;
  win_rate: string | null;
  profit_factor: string | null;
  expectancy: string | null;
  average_r: string | null;
  net_pnl: string;
};

export type DashboardSummary = {
  quote_currency: string;
  account_size: string;
  account_balance: string;
  realized_pnl: string;
  today_pnl: string;
  risk_exposure: string;
  current_drawdown: string;
  trade_score: number | null;
  open_trades: number;
  closed_trades: number;
};
