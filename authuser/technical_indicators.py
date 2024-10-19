import numpy as np

def MA_Bollinger(data, period, column="Close"):
        data['MA'] = data[column].rolling(window=period).mean()
        data['BB_upper'] = data['MA'] + 2 * data[column].rolling(window=period).std()
        data['BB_lower'] = data['MA'] - 2 * data[column].rolling(window=period).std()
        return data
def MA(data, period, column="Close"):
    data['MA'] = data[column].rolling(window=period).mean()

    return data
    
def ROC(data, period=12, column="Close"):
    data['ROC'] = data[column].pct_change(periods=period) * 100
    return data
    
def MACD(data, short_period=12, long_period=26, signal_period=9, column="Close"):
    short_ema = data[column].ewm(span=short_period, adjust=False).mean()
    long_ema = data[column].ewm(span=long_period, adjust=False).mean()
    data['MACD'] = short_ema - long_ema
    data['MACD_Signal'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
    return data
    
def Stochastic_Oscillator(data, k_period=14, d_period=3, column="Close"):
    data['L14'] = data[column].rolling(window=k_period).min()
    data['H14'] = data[column].rolling(window=k_period).max()
    data['%K'] = (data[column] - data['L14']) / (data['H14'] - data['L14']) * 100
    data['%D'] = data['%K'].rolling(window=d_period).mean()
    return data.drop(columns=['L14', 'H14'])
    
def ATR(data, period=14, column="Close"):
    data['H-L'] = data['High'] - data['Low']
    data['H-C'] = (data['High'] - data['Close'].shift(1)).abs()
    data['L-C'] = (data['Low'] - data['Close'].shift(1)).abs()
    data['TR'] = data[['H-L', 'H-C', 'L-C']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=period).mean()
    return data.drop(columns=['H-L', 'H-C', 'L-C', 'TR'])
def OBV(data, column="Close"):
    data['OBV'] = (np.sign(data[column].diff()) * data['Volume']).cumsum()
    return data

def RSI(data, period=14, column="Close"):
    delta = data[column].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    RS = gain / loss
    data['RSI'] = 100 - (100 / (1 + RS))
    return data