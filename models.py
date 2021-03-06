

class Balance:
    def __init__(self, info, exchange):
        if exchange == 'Binance':
            self.initial_margin = float(info['initialMargin'])
            self.maintenance_margin = float(info['maintMargin'])
            self.margin_balance = float(info['marginBalance'])
            self.wallet_balance = float(info['walletBalance'])
            self.unrealized_pnl = float(info['unrealizedProfit'])


class Candle:
    def __init__(self, data, timeframe, exchange):
        if exchange == 'Binance':
            self.timestamp = data[0]
            self.open = float(data[1])
            self.high = float(data[2])
            self.low = float(data[3])
            self.close = float(data[4])
            self.volume = float(data[5])

        elif exchange == 'parse_trade':
            self.timestamp = data['ts']
            self.open = float(data[1])
            self.high = float(data[2])
            self.low = float(data[3])
            self.close = float(data[4])
            self.volume = float(data[5])

class Contract:
    def __init__(self, info, exchange):
        if exchange == 'Binance':
            self.symbol = info['symbol']
            self.base_asset = info['baseAsset']
            self.quote_asset = info['quoteAsset']
            self.price_decimals = info['pricePrecision']  # Used to round for Binance
            self.quantity_decimals = info['quantityPrecision']
            self.tick_size = 1 / pow(10, info['pricePrecision'])
            self.lot_size = 1 / pow(10, info['quantityPrecision'])

class OrderStatus:
    def __init__(self, data):
        self.order_id = data['orderId']
        self.status = data['status']
        self.avg_price = float(data['avgPrice'])
