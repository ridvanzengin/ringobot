
import time
from ringobot.db.utils import execute_query
from ringobot.serviceData.simulation import get_symbol_data
from datetime import datetime, timedelta
from ringobot.serviceData.binance import BinanceAPI
from ringobot.serviceData.graphCreator import createGraphs
import json
import plotly


class Session:
    def __init__(self, id, coin_id, name, buy_price, quantity, buy_timestamp, status, sell_price=None, sell_timestamp=None, data=None, graph=None):
        self.id = int(id)
        self.coin_id = int(coin_id)
        self.name = name
        self.buy_price = round(float(buy_price), 5)
        self.quantity = float(quantity)
        self.buy_timestamp = int(buy_timestamp)
        self.buy_time_offset = datetime.fromtimestamp(self.buy_timestamp) + timedelta(hours=3)
        self.buy_time = self.buy_time_offset.strftime('%Y-%m-%d %H:%M')
        self.status = int(status)
        if self.status == 1:
            self.live_price = BinanceAPI().get_symbol_ticker(self.name)

        self.sell_price = round(float(sell_price), 5) if sell_price else self.live_price
        self.sell_timestamp = int(sell_timestamp) if sell_timestamp else None
        self.sell_time_offset = datetime.fromtimestamp(self.sell_timestamp) + timedelta(hours=3) if sell_timestamp else None
        self.sell_time = self.sell_time_offset.strftime('%Y-%m-%d %H:%M') if sell_timestamp else None
        if self.status == 0:
            self.profit = round((self.sell_price - self.buy_price) * self.quantity, 2)
            self.profit_percent = round((self.profit / (self.buy_price * self.quantity)) * 100, 2)
        else:
            self.profit = round((self.live_price - self.buy_price) * self.quantity, 2)
            self.profit_percent = round((self.profit / (self.buy_price * self.quantity)) * 100, 2)
        if self.profit is not None:
            self.is_profit = 1 if self.profit >= 0 else 0
        self.data = data
        self.graph = graph


    @staticmethod
    def get_sessions(db_session, session_id=None, coin_id=None, status=None, symbol=None, last_n_hours=None):
        query = "SELECT t.*, co.name  FROM transactions t LEFT JOIN coins co ON t.coin_id = co.id  WHERE 1=1"
        if session_id:
            query += f" AND t.id = {session_id}"
        if coin_id:
            query += f" AND coin_id = {coin_id}"
        if status is not None:
            query += f" AND t.status = {status}"
        if symbol:
            query += f" AND name = {symbol}"
        if last_n_hours:
            hour_ago = int(time.time()) - last_n_hours * 60 * 60
            query += f" AND sell_timestamp > {hour_ago}"
        query += ";"
        df = execute_query(query, db_session)
        sessions = []
        for i in df.to_dict(orient='records'):
            sessions.append(Session(**i))
        return sessions

    @staticmethod
    def get_active_sessions(db_session):
        return Session.get_sessions(db_session, status=1)

    @staticmethod
    def get_completed_sessions(db_session):
        return Session.get_sessions(db_session, status=0)

    @staticmethod
    def get_session_by_id(db_session, session_id):
        return Session.get_sessions(db_session, session_id=session_id)[0]

    @staticmethod
    def get_session_by_coin_id(db_session, coin_id):
        return Session.get_sessions(db_session, coin_id=coin_id)

    @staticmethod
    def get_session_by_symbol(db_session, symbol):
        return Session.get_sessions(db_session, symbol=symbol)

    @staticmethod
    def get_sold_within_1_hour(db_session):
        return Session.get_sessions(db_session, last_n_hours=0.5)

    @staticmethod
    def get_session_data(session, data_interval="15m"):
        session.data = get_symbol_data(session.name, data_interval, limit=240)
        return session

    @staticmethod
    def get_symbol_graph(session):
        graphs = createGraphs(session)
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        session.graph = graphJSON
        session.data = None
        return session

    @staticmethod
    def get_session_details(db_session, session_id, data_interval):
        session = Session.get_session_by_id(db_session, session_id)
        session = Session.get_session_data(session, data_interval)
        session = Session.get_symbol_graph(session)
        return session


class Coin:
    def __init__(self, id, name, status):
        self.id = int(id)
        self.name = name
        self.status = int(status)

    @staticmethod
    def get_coins(db_session, coin_id=None, name=None, status=None):
        query = "SELECT * FROM coins WHERE 1=1"
        if coin_id:
            query += f" AND id = {coin_id}"
        if name:
            query += f" AND name = {name}"
        if status:
            query += f" AND status = {status}"
        query += ";"
        df = execute_query(query, db_session)
        coins = []
        for i in df.to_dict(orient='records'):
            coins.append(Coin(**i))
        return coins

    @staticmethod
    def get_active_coins(db_session):
        return Coin.get_coins(db_session, status=1)

    @staticmethod
    def get_inactive_coins(db_session):
        return Coin.get_coins(db_session, status=0)

    @staticmethod
    def get_coin_by_id(db_session, coin_id):
        return Coin.get_coins(db_session, coin_id=coin_id)

    @staticmethod
    def get_coin_by_name(db_session, name):
        return Coin.get_coins(db_session, name=name)

    @staticmethod
    def get_coin_by_status(db_session, status):
        return Coin.get_coins(db_session, status=status)


class Dashboard:
    def __init__(self, total_profit, successful_trade_count, failed_trade_count, active_session_count, completed_session_count, balance=None):
        self.balance = round(balance, 2)
        self.total_profit = round(total_profit, 2) if total_profit else 0
        self.successful_trade_count = int(successful_trade_count)
        self.failed_trade_count = failed_trade_count
        self.active_session_count = active_session_count
        self.completed_session_count = completed_session_count

    @staticmethod
    def get_dashboard(db_session):
        query = """SELECT SUM((sell_price - buy_price) * quantity) as total_profit,
                          SUM(CASE WHEN buy_price < sell_price THEN 1 ELSE 0 END) as successful_trade_count,
                          SUM(CASE WHEN buy_price >= sell_price THEN 1 ELSE 0 END) as failed_trade_count,
                          SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as active_session_count,
                          SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as completed_session_count
                          FROM transactions;"""
        df = execute_query(query, db_session)
        df['balance'] = BinanceAPI().get_account_balance()['USDT']
        return Dashboard(**df.to_dict(orient='records')[0])

class LiveDashboard:
    def __init__(self, total_profit, mean_profit_percent, balance):
        self.total_profit = round(total_profit, 2) if total_profit else 0
        self.mean_profit_percent = round(mean_profit_percent, 2) if mean_profit_percent else 0
        self.balance = round(balance, 2)

    @staticmethod
    def get_active_dashboard(db_session):
        active_sessions = Session.get_active_sessions(db_session)
        total_profit = 0
        for session in active_sessions:
            total_profit += session.profit
        mean_profit_percent = 0
        if active_sessions:
            mean_profit_percent = sum([session.profit_percent for session in active_sessions]) / len(active_sessions)
        balance = BinanceAPI().get_account_balance()['USDT']
        return LiveDashboard(total_profit, mean_profit_percent, balance)



