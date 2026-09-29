from flask import Flask
app=Flask(__name__)
@app.route('/')
def home():return "alive"
def run_web():
 port=int(__import__('os').environ.get("PORT",10000))
 app.run(host="0.0.0.0",port=port)
import threading
threading.Thread(target=run_web,daemon=True).start()
import yfinance as yf, telebot, os, time, threading

import pandas as pd

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
SYMBOLS = ["TQQQ","NVDA","TSLA","AAPL","SPY","QQQ"]

def indicators(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    ema9 = df['Close'].ewm(span=9).mean()
    ema20 = df['Close'].ewm(span=20).mean()
    vwap = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    mom = (df['Close'].iloc[-1] - df['Close'].iloc[-20]) / df['Close'].iloc[-20] * 100
    return rsi.iloc[-1], ema9.iloc[-1], ema20.iloc[-1], vwap.iloc[-1], vol_ratio, mom

def GOD_X2(ticker):
    try:
        df = yf.Ticker(ticker).history(period="5d", interval="1m")
        price = df['Close'].iloc[-1]
        rsi, ema9, ema20, vwap, vol, mom = indicators(df)
        score = 0
        if rsi < 70 and rsi > 45: score += 20
        if ema9 > ema20: score += 20
        if price > vwap: score += 15
        if vol > 1.5: score += 15
        if mom > 0: score += 10
        if df['Close'].iloc[-1] > df['Open'].iloc[-1]: score += 10
        power = min(65 + score, 99.9)
        whale = "🐋🐋🐋 حوت عملاق" if vol > 3 else "🐋🐋 متوسط" if vol > 2 else "🐋 صغير" if vol > 1.5 else "💤 هدوء"
        snipe = "🔥 SNIPE X - ادخل CALL الآن!" if power >= 90 else "🎯 فرصة قوية" if power >= 80 else "⏳ جهز" if power >= 70 else "💤 انتظار"
        return f"🔱 GOD X2 - {ticker}\n💎 ${price:.2f}\n⚡ Power: {power:.1f}%\n📊 RSI:{rsi:.1f} MOM:{mom:.1f}%\n{whale}\n{snipe}\n🎯 هدف: ${price*1.03:.2f} | 🛑 ستوب: ${price*0.97:.2f}"
    except Exception as e:
        return f"❌ {ticker}: {e}"

@bot.message_handler(commands=['start','god'])
def handle_god(m):
    parts = m.text.split()
    if len(parts) > 1:
        bot.send_message(m.chat.id, GOD_X2(parts[1].upper()))
    else:
        msg = "🔱 GOD X2 MULTI\n\n"
        for sym in SYMBOLS:
            try:
                df = yf.Ticker(sym).history(period="1d", interval="5m")
                p = df['Close'].iloc[-1]
                vol = df['Volume'].iloc[-1] / df['Volume'].mean()
                power = min(70+vol*10, 99.9)
                msg += f"{'🔥' if power>85 else '🎯' if power>75 else '⏳'} {sym}: ${p:.2f} | {power:.0f}%\n"
            except: msg += f"{sym}: مقفل\n"
        msg += "\n/god NVDA للتفصيل"
        bot.send_message(m.chat.id, msg)

@bot.message_handler(commands=['auto'])
def auto(m):
    bot.send_message(m.chat.id, f"✅ AUTO على {', '.join(SYMBOLS)}")
    def loop():
        while True:
            time.sleep(120)
            for sym in SYMBOLS:
                try:
                    r = GOD_X2(sym)
                    if "SNIPE X" in r: bot.send_message(m.chat.id, f"🚨 فرصة!\n{r}")
                except: pass
    threading.Thread(target=loop, daemon=True).start()

bot.infinity_polling()
