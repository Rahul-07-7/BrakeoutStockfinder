import os
import time
import requests
import pyotp
import pandas as pd
from SmartApi import SmartConnect
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# --- CONFIG ---
API_KEY = "4kuX4Lor"
CLIENT_ID = "AABP855222"
MPIN = "9909"
TOTP_SECRET = "AA5BQYP7WD5TWNKOEIMRG4D5CA"

TOTAL_BUDGET = 20000
MAX_STOCKS_TO_BUY = 2
ALLOCATION_PER_STOCK = TOTAL_BUDGET / MAX_STOCKS_TO_BUY

# --- LOGIN ---
def login():
    obj = SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()
    obj.generateSession(CLIENT_ID, MPIN, totp)
    return obj

# --- MASTER FILE ---
def get_all_nse_tokens():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    file_path = "nse_master.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            d = json.load(f)
    else:
        print("Downloading master file...")
        res = requests.get(url)
        d = res.json()
        with open(file_path, "w") as f:
            json.dump(d, f)

    df = pd.DataFrame(d)
    df = df[
    (df['exch_seg'] == 'NSE') &
    (df['symbol'].str.endswith('-EQ')) &
    (~df['symbol'].str.contains('INAV', na=False)) &
    (~df['symbol'].str.contains('ETF', na=False)) &
    (~df['symbol'].str.contains('NIFTY', na=False))
]

    return df[['symbol', 'token']]

# --- SCANNER LOGIC ---
def scan_stock(row):
    try:
        time.sleep(1)  # prevent rate limit

        to_date = datetime.now()
        from_date = to_date - timedelta(days=40)

        params = {
            "exchange": "NSE",
            "symboltoken": row['token'],
            "interval": "ONE_DAY",
            "fromdate": from_date.strftime("%Y-%m-%d 09:15"),
            "todate": to_date.strftime("%Y-%m-%d 15:30")
        }

        res = api.getCandleData(params)
        

        if not res or not res.get('data'):
            return None
        

        df = pd.DataFrame(res['data'], columns=['date', 'open', 'high', 'low', 'close', 'volume'])

        if len(df) < 20:
            return None

        last = df.iloc[-1]
        prev_df = df.iloc[:-1]

        # --- PRICE FILTER ---
        if not (200 <= last['close'] <= 600):
            return None
        

        
        # --- EMA TREND ---
        df['ema20'] = df['close'].ewm(span=20).mean()
        df['ema50'] = df['close'].ewm(span=50).mean()
        trend_ok = last['close'] > df.iloc[-1]['ema20'] > df.iloc[-1]['ema50']

        # --- BREAKOUT ZONE ---
        recent_high = prev_df['high'].tail(10).max()

        # --- VOLUME ---
        avg_vol = prev_df['volume'].tail(10).mean()
        vol_ratio = last['volume'] / avg_vol
        
        range_5 = prev_df['high'].tail(5).max() - prev_df['low'].tail(5).min()
        range_10 = prev_df['high'].tail(10).max() - prev_df['low'].tail(10).min()
        tight_range = range_5 < (range_10 * 0.6)

        # --- VOLATILITY EXPANSION ---
        day_range = last['high'] - last['low']
        prev_range = (prev_df['high'] - prev_df['low']).tail(5)
        atr_expand = day_range > prev_range.mean()

        # --- CLOSING STRENGTH ---
        if (last['high'] - last['low']) == 0:
           return None

        strength = (
    (last['close'] - last['low']) /
    (last['high'] - last['low'])
)

# --- REMOVE EXHAUSTION CANDLES ---
        if vol_ratio > 8 and strength < 0.7:
          return None
        
        

        # --- SCORING SYSTEM ---
        score = 0

        # breakout proximity
        if last['close'] > recent_high * 0.98:
            score += 2

        # volume strength
        if vol_ratio > 1.8:
            score += 2
        elif vol_ratio > 1.4:
            score += 1

        # consolidation
        if tight_range:
            score += 1

        # trend
        if trend_ok:
            score += 1

        # strong closing
        if strength > 0.7:
            score += 2

        # volatility expansion
        if atr_expand:
            score += 1

        # --- FINAL FILTER ---
        distance_from_ema20 = (last['close'] - df.iloc[-1]['ema20']) / df.iloc[-1]['ema20']

        if distance_from_ema20 > 0.06:
           return None
       
        if (
         
            vol_ratio > 2.5 and
    strength > 0.75 and
    trend_ok and
    score >= 7
):
            qty = int(ALLOCATION_PER_STOCK / last['close'])

            return {
    "symbol": row['symbol'],
    "token": str(row['token']),
    "price": round(last['close'], 2),
    "qty": qty,
    "vol_ratio": round(vol_ratio, 2),
    "score": score
}

        return None
        

    except Exception:
        return None
    
        
        

api = login()

if api:
    master_list = get_all_nse_tokens()
    print(f"Scanning {len(master_list)} stocks...")

    results = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(scan_stock, row) for _, row in master_list.iterrows()]

        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                print(f"\n💎 {res['symbol']} | ₹{res['price']} | Score: {res['score']} | Vol: {res['vol_ratio']}")

    print(f"\n✅ Found {len(results)} high-quality breakout stocks")
    
    # --- SORT BEST ---
    results = sorted(results, key=lambda x: (x['score'], x['vol_ratio']), reverse=True)

    print("\n🔥 TOP PICKS:")
    for r in results[:3]:
        print(f"{r['symbol']} → ₹{r['price']} | Score: {r['score']} | Vol x{r['vol_ratio']}")
with open("candidates.json", "w") as f:
     json.dump(results[:10], f, indent=4)

print("💾 Saved breakout candidates")
