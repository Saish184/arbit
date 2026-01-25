import pandas as pd

def load_price_data(csv_path: str) -> pd.DataFrame:
    """
    Loads historical price data from a CSV file.
    Expects a UNIX timestamp in seconds.
    Returns a DataFrame indexed by datetime.
    """

    df = pd.read_csv(csv_path)

    # normalize column names

    df.columns = [c.lower() for c in df.columns]

    # Convert UNIX  timestamp (seconds) -> datetime(UTC)

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s" , utc=True)
    df.set_index("timestamp", inplace=True)

    # keep only close price for MVP
    df = df[["close"]].dropna()

    return df