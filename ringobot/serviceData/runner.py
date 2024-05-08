from ringobot.serviceData.binance import BinanceAPI
from ringobot.serviceData.simulation import create_signals, predict_signals
import time
from ringobot.db.session import Session, Coin
from ringobot.db.configurations import Configurations
from ringobot.db.tables import Coins, Transactions
from ringobot.tools import calculate_max_qty, calculate_max_sell_qty
from ringobot.toChat import send_slack_message, to_slack
import logging

# Initialize Binance API
binance = BinanceAPI()


def make_buy_sell_decision(symbol, interval='1h'):
    # Get historical data for a symbol
    df = binance.get_symbol_data(symbol, interval, limit=240)
    # Create signals from the data
    windows, _ = create_signals(df)
    # Predict signals using the trained model
    probs = predict_signals(windows)
    return probs


def detect_buy_sell_signal(db_session):
    buys = []
    sells = []
    symbols = Coin.get_active_coins(db_session)
    symbols = [symbol.name for symbol in symbols]
    for symbol in symbols:
        probs = make_buy_sell_decision(symbol)
        if probs[-1] == 1:
            buys.append(symbol)
        elif probs[-1] == -1:
            sells.append(symbol)
    return buys, sells


def update_transaction(db_session, session, price):
    transaction = db_session.query(Transactions).filter(Transactions.id == session.id).first()
    transaction.sell_price = price
    transaction.sell_timestamp = int(time.time())
    transaction.status = 0
    db_session.commit()


def safety_sell(db_session, active_sessions, config):
    if not active_sessions:
        return
    tolerance = config.tolerance
    for session in active_sessions:
        symbol = session.name
        try:
            price = binance.get_symbol_ticker(symbol)
            quantity = session.quantity
            df = binance.get_symbol_data(symbol, interval='1m', limit=5)
            if df['close'].mean() < session.buy_price * (1 - tolerance):
                    order = binance.place_market_sell_order(symbol, quantity=quantity)
                    logging.info(f"Safety sell order placed for {symbol} at price {price}")
                    update_transaction(db_session, session, price)
            else:
                pass
        except Exception as e:
            logging.error(f"{symbol} safety sell failed")
            logging.error(e)


def expire_sell(db_session, active_sessions, config):
    if not active_sessions:
        return
    timeout = config.hold_time
    for session in active_sessions:
        symbol = session.name
        try:
            is_profit = session.profit_percent > 0
            if int(time.time()) - session.buy_timestamp > timeout and is_profit:
                price = binance.get_symbol_ticker(symbol)
                #quantity = session.quantity
                asset_balance = binance.get_account_balance()[symbol.replace("USDT", "")]  # Get the asset balance
                min_quantity = binance.get_symbol_minQty(symbol)  # Get the minimum quantity for the symbol
                quantity = calculate_max_sell_qty(asset_balance, min_quantity)
                order = binance.place_market_sell_order(symbol, quantity=quantity)
                logging.info(f"Expire sell order placed for {symbol} at price {price}")
                update_transaction(db_session, session, price)
            else:
                pass
        except Exception as e:
            logging.error(f"{symbol} expire sell failed")
            logging.error(e)


def insert_transaction(db_session, symbol, price, quantity):
    coin = db_session.query(Coins).filter(Coins.name == symbol).first()
    now = int(time.time())
    transaction = Transactions(coin_id=coin.id, buy_price=price, quantity=quantity, buy_timestamp=now, status=1)
    db_session.add(transaction)
    db_session.commit()


def buy_crypto(buys, config, db_session):
    if not buys:
        return
    allow_buy = config.allow_buy
    max_trade = config.max_trade
    budget = config.budget  # Budget per trade
    if not allow_buy:
        return
    active_sessions = Session.get_active_sessions(db_session)
    if len(active_sessions) >= max_trade:
        return
    owned_symbols = [session.name for session in active_sessions]
    buys = [symbol for symbol in buys if symbol not in owned_symbols]  # Remove already owned symbols
    allowed_trade_count = max_trade - len(owned_symbols) # Calculate the number of trades allowed
    buys = buys[:allowed_trade_count]  # Limit the number of trades to max_trade
    cash = binance.get_account_balance()['USDT']
    if cash < budget:
        return
    for symbol in buys:
        if symbol not in owned_symbols:
            price = binance.get_symbol_ticker(symbol)
            min_quantity = binance.get_symbol_minQty(symbol)
            quantity = calculate_max_qty(price, budget, min_quantity)
            try:
                order = binance.place_market_buy_order(symbol, quantity=quantity)
                insert_transaction(db_session, symbol, price, quantity)
                logging.info(f"Buy order placed for {symbol} at price {price}")
            except Exception as e:
                logging.error(f"{symbol} buy order failed")
                logging.error(e)
        else:
            pass


def sell_crypto(sells, config, db_session, min_hold_time=3):  # Minimum hold time in hours
    if not sells:
        return
    allow_sell = config.allow_sell
    if not allow_sell:
        return
    active_sessions = Session.get_active_sessions(db_session)
    for session in active_sessions:
        is_profit = session.profit_percent > 0
        is_min_hold_time_over = int(time.time()) - session.buy_timestamp > min_hold_time * 3600
        if session.name in sells and is_profit and is_min_hold_time_over:
            symbol = session.name
            price = binance.get_symbol_ticker(symbol)
            quantity = session.quantity

            try:
                order = binance.place_market_sell_order(symbol, quantity=quantity)
                update_transaction(db_session, session, price)
                logging.info(f"Sell order placed for {symbol} at price {price}")
            except Exception as e:
                logging.error(f"{symbol} sell order failed")
                logging.error(e)
        else:
            pass


def manual_cripto_sell(db_session, session_id):
    session = Session.get_session_by_id(db_session, session_id)
    symbol = session.name
    price = binance.get_symbol_ticker(symbol)
    quantity = session.quantity
    try:
        order = binance.place_market_sell_order(symbol, quantity=quantity)
        update_transaction(db_session, session, price)
        logging.info(f"Manual sell order placed for {symbol} at price {price}")
    except Exception as e:
        logging.error(f"{symbol} manual sell order failed")
        logging.error(e)


def trade(db_session):
    active_sessions = Session.get_active_sessions(db_session)
    config = Configurations.get_config(db_session)
    if len(active_sessions) < config.max_trade:
        buys, sells = detect_buy_sell_signal(db_session)
        sell_crypto(sells, config, db_session)
        buy_crypto(buys, config, db_session)



def slack(db_session):
    attachments = to_slack(db_session)
    if attachments:
        send_slack_message(attachments=[attachments])

