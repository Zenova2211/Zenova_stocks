import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

# Nifty 500 list
try:
    nifty500 = pd.read_csv('https://archives.nseindia.com/content/indices/ind_nifty500list.csv')
    symbols = [s + '.NS' for s in nifty500['Symbol']]
except:
    # Backup list agar NSE down ho
    symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']

results = []
exit_results = []

for symbol in symbols:
    try:
        df = yf.download(symbol, period='60d', interval='1d', progress=False, auto_adjust=True)
        if len(df) < 30:
            continue
            
        df['EMA10'] = df['Close'].ewm(span=10, adjust=False).mean()
        
        # Entry Logic
        lookback = 20
        below_ema = df['Close'][-lookback:] < df['EMA10'][-lookback:]
        downtrend = below_ema.sum() > lookback * 0.7
        
        day1_above = df['Close'].iloc[-2] > df['EMA10'].iloc[-2]
        day2_above = df['Close'].iloc[-1] > df['EMA10'].iloc[-1]
        higherHigh = df['High'].iloc[-1] > df['High'].iloc[-2] > df['High'].iloc[-3]
        
        if downtrend and day1_above and day2_above and higherHigh:
            results.append(symbol.replace('.NS', ''))
        
        # Exit Logic
        day1_below = df['Close'].iloc[-2] < df['EMA10'].iloc[-2]
        day2_below = df['Close'].iloc[-1] < df['EMA10'].iloc[-1]
        
        if day1_below and day2_below:
            exit_results.append(symbol.replace('.NS', ''))
            
    except Exception as e:
        continue

# IST time
ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist).strftime('%d %b %Y, %I:%M %p')

# Telegram Message
msg = f"📊 10 EMA Scanner - {now_ist}\n"
msg += f"{'='*30}\n\n"

if results:
    msg += f"✅ BUY SIGNALS: {len(results)}\n" + '\n'.join([f"• {s}" for s in results])
else:
    msg += "✅ BUY SIGNALS: None"

msg += f"\n\n🔴 EXIT SIGNALS: {len(exit_results)}\n"
if exit_results:
    msg += '\n'.join([f"• {s}" for s in exit_results[:20]]) # Max 20 dikhao
    if len(exit_results) > 20:
        msg += f"\n...and {len(exit_results)-20} more"

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
requests.post(url, data={'chat_id': CHAT_ID, 'text': msg})
