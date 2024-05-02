from ringobot.db.tables import Config
from ringobot.db.utils import execute_query


class Configurations:
    def __init__(self, id, allow_buy, allow_sell, budget, tolerance, hold_time, max_trade):
        self.id = int(id)
        self.allow_buy = int(allow_buy)
        self.allow_sell = int(allow_sell)
        self.budget = float(budget)
        self.tolerance = float(tolerance)
        self.hold_time = int(hold_time) * 60 * 60  # Convert hours to seconds
        self.max_trade = int(max_trade)  # Maximum number of concurrent trades


    @staticmethod
    def get_config(db_session):
        query = "SELECT * FROM config;"
        df = execute_query(query, db_session)
        return Configurations(**df.to_dict(orient='records')[0])

    @staticmethod
    def update_config(db_session, allow_buy, allow_sell, budget, tolerance, hold_time, max_trade):
        new_config = db_session.query(Config).first()
        new_config.allow_buy = allow_buy
        new_config.allow_sell = allow_sell
        new_config.budget = budget
        new_config.tolerance = tolerance
        new_config.hold_time = hold_time
        new_config.max_trade = max_trade
        db_session.commit()
        return Configurations.get_config(db_session)



