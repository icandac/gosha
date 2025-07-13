import pandas as pd
from binance.client import Client

import config.config_binance as config


def get_binance_client():
    """
    Returns a binance client object, configured for testnet or live.
    """
    client = Client(config.API_KEY, config.API_SECRET, testnet=config.TESTNET)
    return client


def fetch_historical_data(symbol: str, interval: str, start_str=int, end_str=int):
    """
    Fetches historical candle data for `symbol` from Binance.
    Args:
        symbol (str): Trading pair symbol (e.g., "BTCUSDT").
        interval (str): Kline interval (e.g., "1h", "1d").
        start_str (int): Start datetime in ms.
        end_str (int): End datetime in ms
    Returns:
        pd.DataFrame: DataFrame with historical OHLCV data.
    """
    client = get_binance_client()
    # Example uses the KLINE_INTERVAL_1HOUR from the binance library
    # You can map your config.TIMEFRAME to binance enums
    kline_data = client.get_historical_klines(
        symbol=symbol, interval=interval, start_str=start_str, end_str=end_str
    )

    # Convert to DataFrame
    df = pd.DataFrame(
        kline_data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    # Convert numeric columns appropriately
    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
    ]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    return df[
        [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
        ]
    ]
