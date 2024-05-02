from ringobot.tools import timing
from ringobot.db.utils import session_scope
from apscheduler.schedulers.background import BackgroundScheduler
from ringobot.serviceData.runner import trade, safety_sell, expire_sell, slack
import time
import logging
from ringobot.db.session import Session
from ringobot.db.configurations import Configurations
logging.basicConfig(level=logging.INFO)
# Set the logging level for the apscheduler logger to WARNING
logging.getLogger('apscheduler').setLevel(logging.WARNING)


# Initialize the scheduler
sched = BackgroundScheduler({'apscheduler.timezone': 'utc'})


@sched.scheduled_job('cron', minute='0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55')
@timing
def minute5_job():
    with session_scope() as db_session:
        active_sessions = Session.get_active_sessions(db_session)
        conf = Configurations.get_config(db_session)
        safety_sell(db_session, active_sessions, conf)
        expire_sell(db_session, active_sessions, conf)


@sched.scheduled_job('cron', minute='0')
@timing
def hourly_job():
    with session_scope() as db_session:
        trade(db_session)
        slack(db_session)


if __name__ == "__main__":
    logging.info("Scheduler started")
    hourly_job()
    sched.start()
    while True:
        time.sleep(60)


