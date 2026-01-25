class Portfolio:
    def __init__(self, initial_cash: float):
        self.cash = initial_cash
        self.pnl = 0.0
        self.trades = 0

    def apply_trade(self, pnl: float):
        self.cash += pnl
        self.pnl += pnl
        self.trades += 1
        