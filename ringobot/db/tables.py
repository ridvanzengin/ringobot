from ringobot.serviceData.bulkDataImport import symbols
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import VARCHAR, Integer, Float, Column, ForeignKey
from ringobot.db.utils import session_scope
from ringobot.config import engine
Base = declarative_base()


class Coins(Base):
    __tablename__ = 'coins'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(10))
    status = Column(Integer, default=1)


class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'))
    buy_price = Column(Float)
    sell_price = Column(Float)
    quantity = Column(Float)
    buy_timestamp = Column(Integer)
    sell_timestamp = Column(Integer)
    status = Column(Integer)


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    allow_buy = Column(Integer)
    allow_sell = Column(Integer)
    budget = Column(Float)
    tolerance = Column(Float)
    hold_time = Column(Float)
    max_trade = Column(Float)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tables created successfully")
    with session_scope() as db_session:
        for symbol in symbols:
            coin = Coins(name=symbol)
            db_session.add(coin)
        db_session.commit()
        print("Coins added successfully")




