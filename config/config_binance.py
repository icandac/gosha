# Sample configuration file for a trading bot using Binance API
import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env/.binance.env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("ENEKTAR")
API_SECRET = os.getenv("COGZIL")

TRADING_SYMBOL = "ETHUSDT"
TIMEFRAME = "1m"
TESTNET = False  # set to False if using live environment

# Basic strategy parameters (example)
SHORT_WINDOW = 10
LONG_WINDOW = 20

# Risk parameters
MAX_POSITION_SIZE = 0.01  # e.g., fraction of portfolio or absolute quantity

# Slippage, fees (for more realistic backtests)
SLIPPAGE = 0.0005
TRADING_FEE = 0.00075
