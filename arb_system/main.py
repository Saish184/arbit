from data.loader import load_price_data

if __name__ == "__main__":
    df = load_price_data("data/btc.csv")

    print("=== HEAD ===")
    print(df.head())

    print("\n=== TAIL ===")
    print(df.tail())

    print("\n === TIME RANGE ===")
    print(df.index.min(), "→", df.index.max())

    