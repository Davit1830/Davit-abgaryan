import pandas as pd
import yfinance as yf
import telebot
import time

# ✅ Քո Token-ը և Chat ID-ն այստեղ տեղադրիր
BOT_TOKEN = "ՔՈ_BOT_TOKEN"
CHAT_ID = "ՔՈ_CHAT_ID"

bot = telebot.TeleBot(BOT_TOKEN)

def hashvel_rsi(series, mijin_jam=14):
    tarberutyun = series.diff()
    shtamb = tarberutyun.where(tarberutyun > 0, 0)
    vesht = -tarberutyun.where(tarberutyun < 0, 0)
    mijin_shtamb = shtamb.rolling(window=mijin_jam).mean()
    mijin_vesht = vesht.rolling(window=mijin_jam).mean()
    rs = mijin_shtamb / mijin_vesht
    return 100 - (100 / (1 + rs))

def stanq_azdasnashan(tivanshan):
    df = yf.download(tivanshan, period="3mo", interval="1h")
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["RSI"] = hashvel_rsi(df["Close"])

    verjin = df.iloc[-1]
    nkarum = df.iloc[-2]

    if (verjin["MACD"] > verjin["Signal"]) and (nkarum["MACD"] < nkarum["Signal"]) and (verjin["RSI"] < 70):
        return "ԳՆԵԼ ազդանշան"
    elif (verjin["MACD"] < verjin["Signal"]) and (nkarum["MACD"] > nkarum["Signal"]) and (verjin["RSI"] > 30):
        return "ՎԱՃԱՌԵԼ ազդանշան"
    else:
        return "Առայժմ չկա ազդանշան"

def uxarkel_azdasnashan(text):
    bot.send_message(chat_id=CHAT_ID, text=text)

while True:
    try:
        tivanshan = "BTC-USD"
        azdasnashan = stanq_azdasnashan(tivanshan)
        if azdasnashan != "Առայժմ չկա ազդանշան":
            uxarkel_azdasnashan(f"{tivanshan} — {azdasnashan}")
        time.sleep(3600)
    except Exception as e:
        uxarkel_azdasnashan(f"Սխալ՝ {e}")
        time.sleep(3600)
