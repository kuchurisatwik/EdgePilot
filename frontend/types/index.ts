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
