import talib
import numpy as np


def calculateSMA(hist):
    """
    Returns the Simple Moving Average for a coin pair
    """
    return talib.SMA(hist, 15)


def calculateEMA(hist):
    """
    Returns the Exponential Moving Average for a coin pair
    """
    ema = talib.EMA(hist)
    return ema


def calcMACD(hist):
    macd, diff, hist = talib.MACD(hist, 12, 26, 9)
    return hist[-5:]


def calculateRSI(hist):
    """
    Calculates the Relative Strength Index for a coin_pair
    If the returned value is above 70, it's overbought (SELL IT!)
    If the returned value is below 30, it's oversold (BUY IT!)
    """
    rsi = talib.RSI(hist, 6)
    return rsi


def calculateBaseLine(hist):
    """
    Calculates (26 period high + 26 period low) / 2
    Also known as the "Kijun-sen" line
    """
    period_high = max(hist.tolist())
    period_low = min(hist.tolist())
    return (period_high + period_low) / 2


def calculateConversionLine(hist):
    """
    Calculates (9 period high + 9 period low) / 2
    Also known as the "Tenkan-sen" line
    """

    period_high = max(hist)
    period_low = min(hist)
    return (period_high + period_low) / 2


def calculateLeadingSpanA(hist):
    """
    Calculates (Conversion Line + Base Line) / 2
    Also known as the "Senkou Span A" line
    """

    base_line = calculateBaseLine(hist)
    conversion_line = calculateConversionLine(hist)
    return (base_line + conversion_line) / 2


def calculateLeadingSpanB(hist):
    """
    Calculates (52 period high + 52 period low) / 2
    Also known as the "Senkou Span B" line
    """

    period_high = max(hist)
    period_low = min(hist)
    return (period_high + period_low) / 2


def findBreakout(hist, period):
    """
    Finds breakout based on how close the High was to Closing and Low to Opening
    """
    hit = 0
    historical_data = hist
    for i in historical_data:
        if (i['C'] == i['H']) and (i['O'] == i['L']):
            hit += 1

    if (hit / period) >= .75:
        #todo notify
        return "Breaking out!"
    else:
        return "hold"
