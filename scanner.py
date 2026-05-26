import yfinance as yf
import pandas as pd
import requests
import os
import time
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

# NSE FNO Stock List - Updated Sep 2026
fno_stocks = ['ABB',
'AMBER',
'ALKEM',
'APOLLOHOSP',
'ASTRAL',
'360ONE',
'AXISBANK',
'ADANIENSOL',
'BAJAJ-AUTO',
'ADANIENT',
'ADANIGREEN',
'ADANIPORTS',
'BANDHANBNK',
'BAJAJHLDNG',
'BANKBARODA',
'APLAPOLLO',
'BHARATFORG',
'ASHOKLEY',
'BHARTIARTL',
'BIOCON',
'BLUESTARCO',
'ASIANPAINT',
'CANBK',
'BAJAJFINSV',
'BAJFINANCE',
'COLPAL',
'BANKINDIA',
'ABCAPITAL',
'DIXON',
'FEDERALBNK',
'FORTIS',
'EICHERMOT',
'GAIL',
'BEL',
'GLENMARK',
'ANGELONE',
'GMRAIRPORT',
'GODREJCP',
'BHEL',
'GRASIM',
'BOSCHLTD',
'BPCL',
'HDFCAMC',
'BSE',
'CAMS',
'CGPOWER',
'CIPLA',
'HINDPETRO',
'ICICIPRULI',
'COALINDIA',
'AUBANK',
'IEX',
'INDIANB',
'CONCOR',
'IOC',
'INDUSINDBK',
'CROMPTON',
'CUMMINSIND',
'IREDA',
'AUROPHARMA',
'DABUR',
'IRFC',
'JINDALSTEL',
'DALBHARAT',
'DELHIVERY',
'JSWENERGY',
'DIVISLAB',
'JSWSTEEL',
'KEI',
'DMART',
'LTF',
'MARICO',
'MCX',
'NTPC',
'BDL',
'GODREJPROP',
'NUVAMA',
'HDFCLIFE',
'HEROMOTOCO',
'ONGC',
'LAURUSLABS',
'HINDUNILVR',
'HINDZINC',
'PFC',
'ICICIBANK',
'ICICIGI',
'IDFCFIRSTB',
'INDHOTEL',
'INDUSTOWER',
'INFY',
'LICHSGFIN',
'PIIND',
'PNBHOUSING',
'BRITANNIA',
'JUBLFOOD',
'POWERINDIA',
'KAYNES',
'KOTAKBANK',
'LICI',
'LODHA',
'RBLBANK',
'CDSL',
'MANKIND',
'LUPIN',
'MARUTI',
'RECLTD',
'RELIANCE',
'NMDC',
'COFORGE',
'PETRONET',
'SAIL',
'POLYCAB',
'SBICARD',
'SHREECEM',
'DRREDDY',
'SHRIRAMFIN',
'MFSL',
'SOLARINDS',
'MOTHERSON',
'SAMMAANCAP',
'SRF',
'SUPREMEIND',
'CHOLAFIN',
'SWIGGY',
'NATIONALUM',
'TATACONSUM',
'ETERNAL',
'SUNPHARMA',
'EXIDEIND',
'TATASTEEL',
'TCS',
'TIINDIA',
'OIL',
'HAVELLS',
'TITAN',
'HDFCBANK',
'TORNTPOWER',
'TORNTPHARM',
'TRENT',
'TVSMOTOR',
'UPL',
'INOXWIND',
'ZYDUSLIFE',
'KPITTECH',
'PATANJALI',
'PGEL',
'ITC',
'PNB',
'POWERGRID',
'HINDALCO',
'KFINTECH',
'PPLPHARMA',
'PREMIERENE',
'PRESTIGE',
'LTM',
'MANAPPURAM',
'SBILIFE',
'SBIN',
'MAXHEALTH',
'MAZDOCK',
'SIEMENS',
'MUTHOOTFIN',
'NYKAA',
'OBEROIRLTY',
'OFSS',
'SONACOMS',
'PAGEIND',
'PAYTM',
'PHOENIXLTD',
'PIDILITIND',
'KALYANKJIL',
'SYNGENE',
'TATAPOWER',
'LT',
'NESTLEIND',
'ULTRACEMCO',
'TATAELXSI',
'UNIONBANK',
'TATATECH',
'UNITDSPR',
'VEDL',
'VOLTAS',
'TMPV',
'UNOMINDA',
'WIPRO',
'YESBANK',
'AMBUJACEM',
'MPHASIS',
'DLF',
'NAUKRI',
'NBCC',
'HAL',
'HCLTECH',
'HUDCO',
'PERSISTENT',
'INDIGO',
'M&M',
'NHPC',
'VBL',
'POLICYBZR',
'RVNL',
'SUZLON',
'IDEA',
'TECHM',
'WAAREEENER',
'JIOFIN',
'GODFRYPHLP',
'ADANIPOWER',
'COCHINSHIP',
'FORCEMOT',
'NAM-INDIA',
'MOTILALOFS',
'VMM',
'HYUNDAI']

symbols = [s + '.NS' for s in fno_stocks]

results = []
exit_results = []

for i, symbol in enumerate(symbols):
    try:
        if i % 30 == 0:
            time.sleep(1)
            
        df = yf.download(symbol, period='60d', interval='1d', progress=False, auto_adjust=True, threads=False)
        
        if df.empty or len(df) < 30:
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
msg = f"📊 <b>10 EMA FNO Scanner</b> - {now_ist}\n"
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
