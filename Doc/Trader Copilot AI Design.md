## Trader Copilot AI 

## Product Design & UX Specification 

Version 1.0 

This document defines the visual design language, user experience principles, screen behavior, layout rules, and interaction patterns for Trader Copilot AI. 

This document is the source of truth for all frontend development. 

## Product Identity 

Trader Copilot AI is not: 

- A broker 

- A trading terminal 

- A signal provider 

- A social trading platform 

Trader Copilot AI is: 

- A Risk Management Platform 

- A Trading Intelligence Platform 

- A Strategy Validation System 

- A Trading Performance Operating System 

The interface should feel like a professional risk desk used by prop traders. 

## Core Design Philosophy 

The product should answer three questions instantly: 

1. What am I risking? 

2. Should I take this trade? 

3. What does my historical data say? 

Every screen should support one of these goals. 

## Design Principles 

## Principle 1 

Data First 

Avoid decorative UI. 

Prioritize useful information. 

## Principle 2 

Professional Appearance 

The product should resemble: 

- TradingView 

- Bloomberg 

- Prop Trading Dashboards 

Avoid: 

- Social media aesthetics 

- Gaming aesthetics 

- Crypto casino aesthetics 

## Principle 3 

Minimal Manual Input 

Users should enter: 

- Strategy 

Optional: 

- Notes 

Everything else should be: 

- Calculated 

- Inferred 

- Auto-filled 

## Principle 4 

Risk Always Visible 

Risk metrics must never be hidden. 

Visible on: 

- Dashboard 

- Trade Entry 

- Trade Review 

- Active Trade Screen 

## Principle 5 

AI Explains 

AI should explain. 

AI should never dominate the screen. 

The user must always understand: 

Why a recommendation exists. 

## Visual Style 

Theme: 

Dark Mode First 

Color Palette: 

Background: 

- Near Black 

Panels: 

- Dark Slate 

Success: 

- Green 

Warning: 

- Amber 

Danger: 

- Red 

Neutral: 

- Gray 

Accent: 

- Blue 

Avoid: 

- Bright gradients 

- Neon effects 

- Excessive animations 

## Typography 

Use: 

- Inter or 

- Geist 

Requirements: 

- High readability 

- Large numeric displays 

Important metrics should be readable from a distance. 

## Layout Philosophy 

Desktop First 

The application is designed for serious traders. 

Primary focus: 

Large desktop displays. 

Secondary: 

Laptop screens. 

Mobile support is not required in MVP. 

## Global Navigation 

Left Sidebar Navigation 

Sections: 

Dashboard 

Trade Planner 

Journal 

Analytics 

Strategy Insights 

AI Coach 

Settings 

## Dashboard Design 

Purpose: 

Overall account health. 

Top Section 

Cards: 

Account Balance 

Today’s PnL 

Risk Exposure 

Trade Score 

Current Drawdown 

Middle Section 

Charts: 

Equity Curve 

Win Rate Trend 

Weekly Performance 

Right Panel 

Always Visible AI Insights 

Examples: 

Reduce position size. 

Avoid afternoon breakout setups. 

Current trade exceeds normal risk. 

Bottom Section 

Recent Trades 

Recent Recommendations Recent Mistakes 

## Trade Planner Screen 

Most Important Screen 

Purpose: 

Validate a trade before execution. 

Left Panel 

Strategy Selection 

## Strategy Notes 

## Market / Limit Selection 

Center Panel Trade Details Entry Stop Loss Target Current Price Right Panel Always Visible Risk Analysis Risk Amount Position Size Reward Risk Ratio Maximum Loss Capital Exposure Rule Validation PASS WARNING BLOCK 

Bottom Panel 

AI Recommendation Examples: Historical Similarity: 82% 

Historical Win Rate: 63% 

Recommendation: 

Take Trade 

Reduce Size 

Avoid Trade 

## Trade Review Screen 

Purpose: 

Review completed trades. 

Display: 

Trade Details 

Risk Metrics 

Market Context 

Entry Screenshot 

Exit Screenshot 

AI Summary 

## Journal Screen 

Purpose: 

Trade Database 

Filters: 

Strategy 

Symbol 

Date Range 

## Win/Loss 

Session 

Table Columns 

Date 

Strategy 

Symbol 

Risk 

Result 

PnL 

R Multiple 

Notes 

## Analytics Screen 

Purpose: 

Performance Intelligence 

Sections: 

Strategy Performance 

Session Performance 

Weekly Performance 

Monthly Performance 

Risk Metrics 

Charts: 

Equity Curve 

Profit Factor 

Drawdown 

Strategy Win Rates 

## Strategy Insights Screen 

Purpose: 

Identify when strategies work. 

Example Output: 

Breakout Strategy 

Best Conditions: 

High Volume 

High ATR 

Morning Session 

Avoid: 

Friday Afternoon 

Low Volatility Range Markets 

This screen should feel like a strategy research terminal. 

## AI Coach Screen 

Purpose: 

Personalized coaching. 

Sections: 

Risk Coaching 

Behavior Coaching Strategy Coaching 

Performance Coaching 

Examples: 

You increase risk after losses. 

Your breakout trades perform better before 11AM. 

You frequently close winning trades too early. 

## Risk Visibility Rules 

Risk metrics should always be visible. 

Display: 

Risk % 

Risk Amount 

Current Drawdown 

Exposure 

Rule Status 

No screen should hide these metrics. 

## Empty State Design 

When data is insufficient: 

Show: 

Not enough historical data available. 

Continue collecting trades to unlock insights. 

Never fabricate confidence. 

Never invent recommendations. 

## AI Behavior Design 

AI should communicate: Confidence Levels High Confidence Medium Confidence Low Confidence Insufficient Data 

Every recommendation must include reasoning. 

Bad Example: 

Take this trade. 

Good Example: 

Take this trade because similar setups achieved a 64% win rate over 132 historical trades. 

## User Experience Goal 

A trader should be able to: 

Create a trade 

Review risk 

Receive guidance 

Understand reasoning 

Make a decision 

in less than 30 seconds. 

## Final Design Goal 

The platform should feel like: 

A professional trading risk desk powered by AI. 

Not a broker. 

Not a charting platform. 

Not a signal service. 

The trader remains responsible for execution. 

The platform provides intelligence, risk management, validation, and coaching. 

