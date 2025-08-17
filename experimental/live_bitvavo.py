import os, sys, uuid, time
import ccxt
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv(os.path.join(".env", ".bitvavo.env"))

KEY    = os.getenv("BITVAVO_API_KEY")
SECRET = os.getenv("BITVAVO_API_SECRET")
OPID = int(os.getenv("BITVAVO_OPERATOR_ID"))

# Diagnostics (masked)
def mask(s): 
    return s[:4] + "…" + s[-4:] if s and len(s) > 8 else str(s)

print("KEY  :", mask(KEY))
print("SECRET:", mask(SECRET))
print("OPID :", OPID)

if not KEY or not SECRET:
    print("\n❌ Missing env vars. Ensure .env is in the same folder and you ran the script from that folder.")
    print("   Alternatively, export them in the shell before running:")
    print('   export BITVAVO_API_KEY=...; export BITVAVO_API_SECRET=...; export BITVAVO_OPERATOR_ID=1001')
    sys.exit(1)

ex = ccxt.bitvavo({
    "apiKey": KEY,
    "secret": SECRET,
    "enableRateLimit": True,
    "options": {"operatorId": OPID},
})
ex.verbose = True

# Quick auth sanity check (no trading)
bal = ex.fetch_balance()
print("OK, fetched balance keys:", [k for k in ["EUR","BTC","USDT"] if k in bal])

symbol = "XRP/EUR"                # Bitvavo format via ccxt
quote_eur = Decimal("10.00")       # minimum €5
ticker = ex.fetch_ticker(symbol)  # get price
last = Decimal(str(ticker["last"]))
# buy amount in BTC with a safety buffer for fees/price movement
amount_btc = (quote_eur / last) * Decimal("0.995")
# round to exchange precision
market = ex.market(symbol)
amount_btc = Decimal(amount_btc).quantize(Decimal(10) ** -market["precision"]["amount"])

cid_buy = str(uuid.uuid4())      # Bitvavo clientOrderId allowed and useful for tracking
print(f"Placing market BUY ~€{quote_eur} {symbol} (amount ≈ {amount_btc} BTC)")

order = ex.create_order(
    symbol=symbol,
    type="market",
    side="buy",
    amount=float(amount_btc),
    params={
        "clientOrderId": cid_buy,
        "operatorId": OPID,
        }
)
print("BUY order:", order)

# get average fill price
fills = order.get("trades", []) or []
if fills and "price" in fills[0]:
    fill_price = Decimal(str(fills[0]["price"]))
else:
    # fallback to ticker if exchange doesn’t return trade breakdown
    fill_price = last

# place a stop-loss ~0.5% below fill (or tighter if you prefer)
stop_trigger = (fill_price * Decimal("0.995")).quantize(Decimal("0.01"))
time.sleep(1)

# Bitvavo supports stopLoss orders via API
# We'll sell the same amount with a stopLoss market order
cid_sl = str(uuid.uuid4())
print(f"Placing STOP-LOSS at €{stop_trigger} ({symbol})")
sl = ex.private_post_order({
    "market": symbol.replace("/", "-"),
    "side": "sell",
    "orderType": "stopLoss",
    "amount": str(amount_btc),
    "triggerType": "price",               # REQUIRED
    "triggerReference": "lastTrade",      # REQUIRED: lastTrade|bestBid|bestAsk|midPrice
    "triggerAmount": str(stop_trigger),   # REQUIRED: your stop price
    "clientOrderId": cid_sl,
    "operatorId": OPID,
})
print("STOP-LOSS order:", sl)

print("Done. You can query by clientOrderId later.")
