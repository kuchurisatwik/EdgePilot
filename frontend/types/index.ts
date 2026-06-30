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
