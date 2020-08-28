import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def getData(symbol, start='2000-01-01', interval='1d', end=None):
    data = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=True)
    return data

def addSignal(data,
              fast=5,
              slow=20,
              rsi_q=14,
              buy_cr=0,
              buy_rsi=60,
              sell_cr=0,
              sell_rsi=35):

    data['Cruce'] = (data.Close.rolling(fast).mean() /
                     data.Close.rolling(slow).mean() - 1) * 100

    dif = data['Close'].diff()
    win = pd.DataFrame(np.where(dif > 0, dif, 0))
    loss = pd.DataFrame(np.where(dif < 0, abs(dif), 0))
    ema_win = win.ewm(alpha=1 / rsi_q).mean()
    ema_loss = loss.ewm(alpha=1 / rsi_q).mean()
    rs = ema_win / ema_loss
    rsi = 100 - (100 / (1 + rs))
    rsi.index = data.index
    data["rsi"] = rsi

    data['Señal'] = 'Sin Señal'
    comprar = (data.Cruce > buy_cr) & (data.rsi > buy_rsi)
    data.loc[comprar, 'Señal'] = 'Compra'

    vender = (data.Cruce < sell_cr) & (data.rsi < sell_rsi) 
    data.loc[vender, 'Señal'] = 'Venta'

    return data

def getTrades(data):
    
    # Una sola entrada y salida por vez
    trades = data.loc[data.Señal != 'Sin Señal'].copy()
    trades['Señal'] = np.where(trades.Señal != trades.Señal.shift(), trades.Señal,'Sin Señal')
    trades = trades.loc[trades.Señal != 'Sin Señal'].copy()

    try:
        # Supuesto estrategia long, debe empezar con compra y terminar con venta
        if trades.iloc[0,7]=='Venta':
            trades = trades.iloc[1:]

        if trades.iloc[-1,7]=='Compra':
            trades = trades.iloc[:-1]
    except:
        pass
    
    return(trades)

def getYields(trades):
    precios_compra = trades.iloc[::2].reset_index().Close
    precios_venta = trades.iloc[1::2].reset_index().Close

    fechas_compra = trades.iloc[::2].index
    fechas_venta = trades.iloc[1::2].index
    
    yields = (precios_venta/precios_compra-1).to_frame()
    yields.columns = ['yield']
    yields['days'] = (fechas_venta - fechas_compra).days
    yields['ok'] = np.where(yields['yield'] > 0 , True , False)
    yields['yield_cum'] = (yields['yield']+1).cumprod()
    
    return yields



data = getData("TSLA")
df = addSignal(data,fast=5, slow=20, rsi_q=14, buy_cr=0, buy_rsi=70, sell_cr=0, sell_rsi=35)
trades = getTrades(df)
yields = getYields(trades)
resultado = float((yields.iloc[-1:].yield_cum-1)*100)
results = []
for i in range(5,100):
    data = addSignal(data,fast=5, slow=20, rsi_q=i, buy_cr=1, buy_rsi=55, sell_cr=0.98, sell_rsi=45)
    trades = getTrades(data)
    yields = getYields(trades)
    resultado = float((yields.iloc[-1:].yield_cum-1)*100)
    results.append(resultado)
    
df = pd.DataFrame(results, index=range(5,100))
df.plot()
plt.show()


