def scanAll(day, idx):
    pass

def doji(day, idx):
    candle = day.iloc[idx]

    close = candle.close
    open = candle.open
    high = candle.high
    low = candle.low

    return abs(close - open) / ((high - low) + 0.001) < 0.1 and \
           (high - max(close, open)) > (3 * abs(close - open)) and \
           (min(close, open) - low) > (3 * abs(close - open))

def hammer(day, idx):
    candle = day.iloc[idx]

    close = candle.close
    open = candle.open
    high = candle.high
    low = candle.low

    return (((high - low) > 3 * (open - close)) and
                ((close - low) / (.001 + high - low) > 0.6) and
                ((open - low) / (.001 + high - low) > 0.6))

def dojiStar(day, idx):
    candle = day.iloc[idx]
    prev_candle = day.iloc[idx - 1]

    close = candle.close
    open = candle.open
    high = candle.high
    low = candle.low

    prev_close = prev_candle.close
    prev_open = prev_candle.open
    prev_high = prev_candle.high
    prev_low = prev_candle.low

    return prev_close > prev_open and \
           abs(prev_close - prev_open) / (prev_high - prev_low) >= 0.7 and \
           abs(close - open) / (high - low) < 0.1 and \
           prev_close < close and \
           prev_close < open and \
           (high - max(close, open)) > (3 * abs(close - open)) and \
           (min(close, open) - low) > (3 * abs(close - open))

def bullishEngulfing(day, idx):
    candle = day.iloc[idx]
    prev_candle = day.iloc[idx - 1]

    close = candle.close
    open = candle.open
    high = candle.high
    low = candle.low

    prev_close = prev_candle.close
    prev_open = prev_candle.open
    prev_high = prev_candle.high
    prev_low = prev_candle.low

    return (close >= prev_open > prev_close and
                close > open and
                prev_close >= open and
                close - open > prev_open - prev_close)

def bearishEngulfing(day, idx):
    candle = day.iloc[idx]
    prev_candle = day.iloc[idx - 1]

    close = candle.close
    open = candle.open
    high = candle.high
    low = candle.low

    prev_close = prev_candle.close
    prev_open = prev_candle.open
    prev_high = prev_candle.high
    prev_low = prev_candle.low

    return (open >= prev_close > prev_open and
                open > close and
                prev_open >= close and
                open - close > prev_close - prev_open)
