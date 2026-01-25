import pandas as pd
from pathlib import Path

def load_price_data(filename: str) -> pd.DataFrame:
    """
    Load historical BTC price data from CSV.
    Path is resolved relative to this file, not the working directory.
    """

    data_dir = Path(__file__).resolve().parent
    csv_path = data_dir / filename

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    df.columns = [c.lower() for c in df.columns]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df.set_index("timestamp", inplace=True)

    return df[["close"]]
