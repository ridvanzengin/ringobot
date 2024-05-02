from ringobot.config import engine, dryRun
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import pandas as pd
import numpy as np
from sqlalchemy import text


SessionFactory = sessionmaker(bind=engine)
db_session = SessionFactory() if dryRun else None

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise
    finally:
        session.close()


def execute_query(query, db_session):
    if isinstance(query, str):
        # If query is a string, convert it to a SQLAlchemy text object
        query = text(query)

    result = db_session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    df = df.replace(np.nan, None)
    return df