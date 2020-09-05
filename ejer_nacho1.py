import pandas
import yfinance
import numpy

def rsi(data,ruedas):
    
    
    data['dif'] = data['Adj Close'].diff()
    data['win'] = numpy.where(data['dif'] > 0, data['dif'], 0)
    data['loss'] = numpy.where(data['dif'] < 0, abs(data['dif']), 0)
    data['ema_win'] = data.win.ewm(alpha=1/ruedas).mean()
    data['ema_loss'] = data.loss.ewm(alpha=1/ruedas).mean()
    data['rs'] = data.ema_win / data.ema_loss
    data['rsi'] = 100 - (100 / (1+data.rs))
    data = data.reset_index().dropna().round(2)
    
    return data

def desvio_standar(data):

    data["Desvio"]=data["Adj Close"].std()
    data = data.reset_index().dropna().round(2)#para redondear
    
    return data

def media_movil(data):
    
    data['Media Movil'] = data['Adj Close'].rolling(20).mean()
    data=data.reset_index().dropna().round(2)

    return data
    
    
data=yfinance.download("4502.T")#Farmacia Takeda

print(rsi(data,14))
print(desvio_standar(data))
print(media_movil(data))


