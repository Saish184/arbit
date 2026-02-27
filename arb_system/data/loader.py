import os
from pathlib import Path

import pandas as pd

def load_price_data(filename: str) -> pd.DataFrame:
    """
    Load historical BTC price data from CSV.
    Uses BTC_CSV_PATH if set; otherwise resolves relative to this file.
    BTC_CSV_PATH may point to a file or a directory.
    """

    env_csv_path = os.getenv("BTC_CSV_PATH")
    if env_csv_path:
        raw_path = Path(env_csv_path).expanduser()
        csv_path = (raw_path / filename) if raw_path.is_dir() else raw_path
    else:
        data_dir = Path(__file__).resolve().parent
        csv_path = data_dir / filename

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV not found at: {csv_path} "
            f"(BTC_CSV_PATH={'set' if env_csv_path else 'not set'})"
        )

    df = pd.read_csv(csv_path)

    df.columns = [c.lower() for c in df.columns]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df.set_index("timestamp", inplace=True)

    return df[["close"]]
