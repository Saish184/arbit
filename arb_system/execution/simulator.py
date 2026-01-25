def execute_arbitrage(signal, trade_size, fee_pct):
    """
    Simulates execution of an arbitrage trade.
    Returns PnL from the trade.
    """

    price_a = signal["price_a"]
    price_b = signal["price_b"]
    direction = signal["direction"]

    if direction == "BUY_A_SELL_B":
        cost = trade_size * price_a * (1 + fee_pct)
        revenue = trade_size * price_b * (1 - fee_pct)

    elif direction == "BUY_B_SELL_A":
        cost = trade_size * price_b * (1 + fee_pct)
        revenue = trade_size * price_a * (1 - fee_pct)
    
    else:
        return 0.0
    
    return revenue - cost