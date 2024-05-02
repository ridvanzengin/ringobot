from ringobot.config import binance_client, dryRun
import time


class BinanceAPI:
    def __init__(self):
        self.client = binance_client
        self.dry_run = dryRun

    def get_account_balance(self):
        # Get account balance for all assets
        account_info = self.client.get_account()
        balances = {item['asset']: float(item['free']) for item in account_info['balances']}
        return balances

    def place_market_buy_order(self, symbol, quantity):
        # Place a market buy order
        if self.dry_run:
            print(f"Dry run: Placing market buy order for {symbol} with quantity {quantity}")
            return {'order_id': 'dry_run_order_id'}  # Return dummy order data
        else:
            order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
            return order

    def place_market_sell_order(self, symbol, quantity):
        # Place a market sell order
        if self.dry_run:
            print(f"Dry run: Placing market sell order for {symbol} with quantity {quantity}")
            return {'order_id': 'dry_run_order_id'}  # Return dummy order data
        else:
            order = self.client.order_market_sell(symbol=symbol, quantity=quantity)
            return order

    def get_symbol_ticker(self, symbol):
        # Get latest price for a symbol
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])

    def wait_for_order_completion(self, symbol, order_id, timeout=60):
        # Wait for an order to be completed
        start_time = time.time()
        while True:
            order_status = self.client.get_order(symbol=symbol, orderId=order_id)
            if order_status['status'] == 'FILLED':
                return True
            elif time.time() - start_time > timeout:
                return False
            time.sleep(1)

    def get_latest_kline_data(self, symbol, interval, limit=1000):
        # Get the latest N hours of candlestick data (kline data)
        # Interval options: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        # Limit: Maximum 1000
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return klines

    def get_all_symbols(self):
        # Get all symbols from Binance
        exchange_info = self.client.get_exchange_info()
        symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
        return symbols

    def get_symbol_minQty(self, symbol):
        # Get the lot size for a symbol
        symbol_info = self.client.get_symbol_info(symbol=symbol)
        # return stepSize, minQty, minNotional
        filters = symbol_info['filters']
        minQty = None
        for filter_item in filters:
            if filter_item['filterType'] == 'LOT_SIZE':
                minQty = float(filter_item['minQty'])
        return minQty











