# config.py

# Minimum percentage spread required to consider arbitrage
# Represents: Fees + slippage + safety margin (ROUND-TRIP)
#
# Example:
# 0.001 = 0.1%
# 0.002 = 0.2%

MIN_SPREAD_PCT = 0.001

# Execution assumption
TRADE_SIZE_BTC = 0.01
FEE_PCT = 0.0005
INITIAL_CASH = 100_000
