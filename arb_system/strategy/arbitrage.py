# strategy/arbitrage.py

def check_arbitrage(price_a: float, price_b: float, threshold_pct: float):
    """
    Check for arbitrage opportunity between two prices.
    
    Returns
    -------None if no opportunity
           Dict with direction and spread_pct if opportunity exists
    """

    # Mid price for scale-invariant comparison
    mid_price = (price_a + price_b) / 2

    # Percentage spread
    spread_pct = (price_b - price_a) / mid_price

    if spread_pct > threshold_pct:
        return {
            "direction": "BUY_A_SELL_B",
            "spread_pct": spread_pct,
            "price_a": price_a,
            "price_b": price_b
        }
    elif spread_pct < -threshold_pct:
        return {
            "direction": "BUY_B_SELL_A",
            "spread_pct": -spread_pct,
            "price_a": price_a,
            "price_b": price_b
        }
    
    else:
        return None
    