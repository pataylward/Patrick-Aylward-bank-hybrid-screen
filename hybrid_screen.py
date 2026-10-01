# Australian major bank hybrids: simple rich/cheap screen
# Run with:  python3 hybrid_screen.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- Settings -------------------------------------------------------------
PRICE_DATE = "31/08/2026"   # date of the prices in hybrids.csv
BBSW = 4.55                 # 3 month BBSW (%) on that date: RBA table F1, EOD 3-month BABs/NCDs (4.5500)
FLAG_BP = 5                 # residual (bp) beyond which a hybrid is flagged
# ---------------------------------------------------------------------------

df = pd.read_csv("hybrids.csv", parse_dates=["first_call", "next_payment"], dayfirst=True)
date = pd.to_datetime(PRICE_DATE, dayfirst=True)

# 1. Years until the bank is expected to call (repay) the hybrid at $100
df["years_to_call"] = (df["first_call"] - date).dt.days / 365

# 2. Distribution built up since the last payment. The ASX price includes it,
#    so we take it off to get the 'clean' price.
last_payment = df["next_payment"] - pd.DateOffset(months=3)
days_accrued = (date - last_payment).dt.days
df["accrued"] = (BBSW + df["issue_margin_bp"] / 100) * days_accrued / 365

df["clean_price"] = df["price"] - df["accrued"]

# 3. Trading margin (simple approximation): the issue margin, less the
#    premium above $100 spread evenly over the years to call.
#    Price $104, 4 years to call: lose $1 a year = 100bp off the margin.
df["premium_per_year"] = (df["clean_price"] - 100) / df["years_to_call"]
df["trading_margin_bp"] = df["issue_margin_bp"] - df["premium_per_year"] * 100

# 4. Same margin for an investor who gets NO value from franking credits.
#    They receive only 70% of the gross distribution in cash.
df["margin_no_franking_bp"] = df["trading_margin_bp"] - 0.30 * (BBSW * 100 + df["issue_margin_bp"])

# 5. Fair value line: best straight line of margin against years to call
slope, intercept = np.polyfit(df["years_to_call"], df["trading_margin_bp"], 1)
df["fair_value_bp"] = intercept + slope * df["years_to_call"]

# 6. Residual: above the line = CHEAP, below the line = RICH
df["residual_bp"] = df["trading_margin_bp"] - df["fair_value_bp"]
df["signal"] = np.where(df["residual_bp"] >= FLAG_BP, "CHEAP",
               np.where(df["residual_bp"] <= -FLAG_BP, "RICH", "FAIR"))

# ---- Output ---------------------------------------------------------------
cols = ["code", "bank", "price", "years_to_call", "trading_margin_bp",
        "margin_no_franking_bp", "fair_value_bp", "residual_bp", "signal"]
table = df[cols].sort_values("residual_bp", ascending=False).round(1)
table.to_csv("outputs/screen.csv", index=False)
print(table.to_string(index=False))
print(f"\nFair value line: {intercept:.0f}bp + {slope:.1f}bp per year to call")

colours = {"CHEAP": "green", "RICH": "red", "FAIR": "grey"}
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.scatter(df["years_to_call"], df["trading_margin_bp"], c=df["signal"].map(colours), zorder=3)
for _, r in df.iterrows():
    ax.annotate(r["code"], (r["years_to_call"], r["trading_margin_bp"]),
                textcoords="offset points", xytext=(5, 4), fontsize=8)
x = np.linspace(0, df["years_to_call"].max(), 50)
ax.plot(x, intercept + slope * x, color="#0079C1", label="Fair value line")
ax.set_xlabel("Years to first call")
ax.set_ylabel("Trading margin over 3m BBSW (bp)")
ax.set_title(f"Major bank hybrids at {PRICE_DATE}: green = cheap, red = rich")
ax.grid(alpha=0.3)
ax.legend(frameon=False)
fig.text(0.01, 0.01, f"Source: ASX Hybrids Monthly Report, RBA. BBSW {BBSW}%. "
         "Simple margin approximation, franking fully valued.", fontsize=7, color="#555555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("outputs/curve.png", dpi=150)
print("Saved outputs/screen.csv and outputs/curve.png")
