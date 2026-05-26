import pandas as pd
import requests
import os
import time
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

# FNO Stock List
fno_stocks = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 
    'KOTAKBANK', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 'ULTRACEMCO', 
    'BAJFINANCE', 'NESTLEIND', 'WIPRO', 'ONGC', 'NTPC', 'POWERGRID', 'TATAMOTORS', 'M&M', 
    'HCLTECH', 'ADANIENT', 'ADANIPORTS', 'COALINDIA', 'TATASTEEL', 'JSWSTEEL', 'HINDALCO', 
    'GRASIM', 'BAJAJFINSV', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'TECHM', 'CIPLA', 'DRREDDY', 
    'DIVISLAB', 'APOLLOHOSP', 'INDUSINDBK', 'SBILIFE', 'HDFCLIFE', 'BRITANNIA', 'DABUR', 'GODREJCP', 
    'MARICO', 'PIDILITIND', 'BERGEPAINT', 'HAVELLS', 'SIEMENS', 'ABB', 'BEL', 'HAL', 'BHEL', 
    'IRCTC', 'ZOMATO', 'ADANIGREEN', 'ADANIPOWER', 'TATAPOWER', 'TATACONSUM', 'TRENT', 'DMART', 
    'VEDL', 'SAIL', 'JINDALSTEL', 'GAIL', 'BPCL', 'IOC', 'RECLTD', 'PFC', 'DLF', 'AMBUJACEM', 
    'ACC', 'SHREECEM', 'UPL', 'PIIND', 'SRF', 'TATACHEM', 'MPHASIS', 'LTTS', 'LTIM', 'PERSISTENT', 
    'COFORGE', 'INDUSTOWER', 'INDIGO', 'BANKBARODA', 'PNB', 'CANBK', 'FEDERALBNK', 'AUBANK', 
    'IDFCFIRSTB', 'BANDHANBNK', 'ICICIPRULI', 'HDFCAMC', 'SBICARD', 'CHOLAFIN', 'MUTHOOTFIN', 
    'LICHSGFIN', 'MANAPPURAM', 'CUB', 'RBLBANK', 'ABCAPITAL', 'PEL', 'M&MFIN', 'SHRIRAMFIN', 
    'ASTRAL', 'POLYCAB', 'CROMPTON', 'VOLTAS', 'DIXON', 'JUBLFOOD', 'METROPOLIS', 'LALPATHLAB', 
    'SYNGENE', 'LAURUSLABS', 'GLAND', 'AUROPHARMA', 'LUPIN', 'TORNTPHARM', 'ALKEM', 'IPCALAB', 
    'BIOCON', 'ZYDUSLIFE', 'UBL', 'VBL', 'PAGEIND', 'ABFRL', 'PVRINOX', 'TVSMOTOR', 'BALKRISIND', 
    'MRF', 'APOLLOTYRE', 'BOSCHLTD', 'MOTHERSON', 'BHARATFORG', 'ASHOKLEY', 'CUMMINSIND', 'RVNL'
]

# NSE ko lagega ki browser se request aa rahi hai
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE'
}

session = requests.Session()
session.get('https://www.nseindia.com', headers=headers)  # Cookie le lo pehle

results = []
exit_results = []
success_count = 0

for i, symbol in enumerate(fno_stocks):
    try:
        if i % 5 == 0:  # Har 5 stocks pe 2 sec ruk
            time.sleep(2)
            
        url = f'https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from=01-01-2026&to=26-05-2026'
        data = session.get(url, headers=headers, timeout=10).json()
        
        if 'data' not in data or len(data['data']) < 30:
            continue
            
        df = pd.DataFrame(data['data'])
        df = df.iloc[::-1].reset_index(drop=True)  # Reverse - oldest first
        df['Close'] = df['CH_CLOSING_PRICE']
        df['High'] = df['CH_TRADE_HIGH_PRICE']
        df['EMA10'] = df['Close'].ewm(span=10, adjust=False).mean()
        success_count += 1
        
        # Entry Logic
        lookback = 20
        below_ema = df['Close'].tail(lookback) < df['EMA10'].tail(lookback)
        downtrend = below_ema.sum() > lookback * 0.7
        
        day1_above = df['Close'].iloc[-2] > df['EMA10'].iloc[-2]
        day2_above = df['Close'].iloc[-1] > df['EMA10'].iloc[-1]
        higherHigh = df['High'].iloc[-1] > df['High'].iloc[-2] > df['High'].iloc[-3]
        
        if downtrend and day1_above and day2_above and higherHigh:
            results.append(symbol)
        
        # Exit Logic
        day1_below = df['Close'].iloc[-2] < df['EMA10'].iloc[-2]
        day2_below = df['Close'].iloc[-1] < df['EMA10'].iloc[-1]
        
        if day1_below and day2_below:
            exit_results.append(symbol)
            
    except Exception:
        continue

# IST time
ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist).strftime('%d %b %Y, %I:%M %p')

# Telegram Message
msg = f"📊 <b>10 EMA FNO Scanner</b> - {now_ist}\n"
msg += f"Scanned: {success_count}/{len(fno_stocks)} stocks\n"
msg += f"{'='*30}\n\n"

if results:
    msg += f"✅ <b>BUY SIGNALS: {len(results)}</b>\n" + '\n'.join([f"• {s}" for s in results])
else:
    msg += "✅ <b>BUY SIGNALS:</b> None found today"

msg += f"\n\n🔴 <b>EXIT SIGNALS: {len(exit_results)}</b>\n"
if exit_results:
    msg += '\n'.join([f"• {s}" for s in exit_results])

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
requests.post(url, data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'HTML'})
