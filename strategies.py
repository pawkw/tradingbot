import logging
from typing import *

from models import *
logger = logging.getLogger()

# Convert '1m' into 60000, '2h' into 7200000.
def timeframe_equiv(tf: str) -> int:
    bases ={
        's': 1000,
        'm': 60*1000,
        'h': 60*60*1000,
        'd': 24*60*60*1000,
        'w': 7*24*60*60*1000
    }
    base = bases[tf[-1]]
    mult = int(tf[:-1])
    return base * mult

class Strategy:
    def __init__(self, contract: Contract, exchange: str, timeframe: str, balance_pct: float, take_profit: float,
                 stop_loss: float):
        self.contract = contract
        self.exchange = exchange
        self.timeframe = timeframe
        self.timeframe_ms = timeframe_equiv(timeframe)
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss

        self.candles: List[Candle] = []

    def parse_trades(self, price: float, size: float, timestamp: int):
        last_candle = self.candles[-1]
        # Same candle
        if timestamp < last_candle.timestamp + self.timeframe_ms:
            last_candle.close = price
            last_candle.volume += size

            if price > last_candle.high:
                last_candle.high = price
            elif price < last_candle.low:
                last_candle.low = price
            return 'Same candle'

        # Missing candles
        elif timestamp >= last_candle.timestamp + (2 * self.timeframe_ms):
            missing_candles = int((timestamp - last_candle.timestamp) / self.timeframe_ms) - 1

            logger.info("%s is missing %d candles for %s %s.", self.exchange, missing_candles, self.contract.symbol,
                        self.timeframe)
            new_timestamp = last_candle.timestamp + self.timeframe_ms
            candle_info = {'ts': new_timestamp, 'open': price, 'close': price, 'low': price, 'high': price,
                           'volume': size}
            new_candle = Candle(candle_info, self.timeframe, 'parse_trade')
            self.candles.append(new_candle)
            for missing in range(missing_candles):
                new_timestamp = last_candle.timestamp + self.timeframe_ms
                candle_info = {'ts': new_timestamp, 'open': last_candle.close, 'close': last_candle.close,
                               'low': last_candle.close, 'high': last_candle.close, 'volume': 0}
                new_candle = Candle(candle_info, self.timeframe, 'parse_trade')
                self.candles.append(new_candle)
                last_candle = new_candle
            new_timestamp = last_candle.timestamp + self.timeframe_ms
            candle_info = {'ts': new_timestamp, 'open': price, 'close': price, 'low': price, 'high': price,
                           'volume': size}
            new_candle = Candle(candle_info, self.timeframe, 'parse_trade')
            self.candles.append(new_candle)
            return 'New candle. Missing some.'
        # New candle
        elif timestamp >= last_candle.timestamp + self.timeframe_ms:
            new_timestamp = last_candle.timestamp + self.timeframe_ms
            candle_info = {'ts': new_timestamp, 'open': price, 'close': price, 'low': price, 'high': price,
                           'volume': size}
            new_candle = Candle(candle_info, self.timeframe, 'parse_trade')
            self.candles.append(new_candle)
            logger.info(f"New candle for {self.contract.symbol} on {self.exchange}.")
            return 'New candle.'

class TechnicalStrategy(Strategy):
    def __init__(self, contract: Contract, exchange: str, timeframe: str, balance_pct: float, take_profit: float,
                 stop_loss: float, other_params: Dict):
        super().__init__(contract, exchange, timeframe, balance_pct, take_profit, stop_loss)
        self._ema_fast = other_params['ema_fast']
        self._ema_slow = other_params['ema_slow']
        self._ema_signal = other_params['ema_signal']
        logger.debug(f"Started Technical strategy on {contract}.")


class BreakoutStrategy(Strategy):
    def __init__(self, contract: Contract, exchange: str, timeframe: str, balance_pct: float, take_profit: float,
                 stop_loss: float, other_params: Dict):
        super().__init__(contract, exchange, timeframe, balance_pct, take_profit, stop_loss)
        self._min_volume = other_params['min_volume']
        logger.debug(f"Started Breakout strategy on {contract}.")
