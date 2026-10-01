# Australian Major Bank Hybrids: Rich/Cheap Screen

A short Python (pandas) screen of the 16 ASX-listed capital notes issued by CBA, Westpac, NAB and ANZ. It estimates each hybrid's trading margin over 3 month BBSW, fits a fair value line against years to first call, and flags hybrids trading cheap (above the line) or rich (below it). Data is end-of-day, not real-time.

**Why it matters now.** APRA is removing AT1 from the bank capital framework. From 1 January 2027 existing AT1 counts as Tier 2 until its first call date, and all of it reaches first call by 2032. Bank hybrids are a shrinking market.

## How it works

1. **Years to call:** days from the price date to the first call date, divided by 365.
2. **Clean price:** the ASX price less the distribution built up since the last payment.
3. **Trading margin (approximation):** issue margin less the premium above $100 spread evenly over the years to call. For example, a price of $104 with 4 years to call gives up $1 a year, so 100bp comes off the margin.
4. **No-franking margin:** the same figure for an investor who cannot use franking credits and receives only 70% of the gross distribution.
5. **Fair value line:** the best straight line through margin against years to call.
6. **Signal:** a residual of 5bp or more above the line is CHEAP, and 5bp or more below it is RICH.

**Limitations.** The margin formula ignores discounting, assumes each hybrid is called at its first call date, and uses a single BBSW rate. It is a screening tool, not a valuation.

## Run it

```
python3 -m pip install pandas matplotlib
python3 hybrid_screen.py
```

Results are saved to `outputs/screen.csv` and `outputs/curve.png`.

## Data

`hybrids.csv` is taken from the ASX Hybrids Monthly Report for August 2026 (prices as at 31/08/2026). BBSW comes from RBA table F1. See `SOURCES.md`.

*Student research project. Not financial advice.*
