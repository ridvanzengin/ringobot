import os
from sqlalchemy import create_engine
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from binance.client import Client
from keys import ringobot_api_key, ringobot_secret_key


dryRun = False
LocalInfluxDB = True
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#######################################
######## INFLUXDB-END-POINTS ##########

influxDBurl = "http://localhost:8086/" if LocalInfluxDB else ""

################################
######## INFLUXDB-MAIN ##########
token = "gsofpwopdfgr0342fj54fg24u4"
org = "ringobot"
bucketMain = "main"

influxDBclient = InfluxDBClient(url=influxDBurl, token=token, org=org, bucket=bucketMain)
influxDBqueryApi = influxDBclient.query_api()
influxDBwriteApi = influxDBclient.write_api(write_options=SYNCHRONOUS)


################################
######## BINANCE ##########
binance_client = Client(ringobot_api_key, ringobot_secret_key)

################################
######## MYSQL #################
MYSQL_HOST = "51.21.59.200"
MYSQL_USER = "system"
MYSQL_PASSWORD = "wopdfgr0342fj54f"
MYSQL_DB = "ringobot"
engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4', pool_recycle=3600, pool_pre_ping=True)


################################
######## SLACK #################
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/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'

################################
######## APP #################
APP_URL = "https://ringobot.space"
SECRET_KEY = "VSPDKFSFNPFNSPOG4545446354358"
USERNAME = "ringolog"
PASSWORD = "ringolog"

################################
######## COINS #################

train_symbols = ['AAVEUSDT', 'ADAUSDT', 'ALGOUSDT', 'ATOMUSDT', 'BANDUSDT', 'BATUSDT', 'BCHUSDT', 'BNBUSDT', 'BTCUSDT',
           'COMPUSDT', 'CRVUSDT', 'DASHUSDT', 'DOGEUSDT', 'DOTUSDT', 'EOSUSDT', 'ETHUSDT', 'FILUSDT',
           'KAVAUSDT', 'KNCUSDT', 'KSMUSDT', 'LINKUSDT', 'LTCUSDT', 'MKRUSDT', 'NMRUSDT', 'OMGUSDT', 'PAXGUSDT',
           'RENUSDT', 'RSRUSDT', 'SNXUSDT', 'SOLUSDT', 'SUSHIUSDT', 'THETAUSDT', 'TRXUSDT', 'UMAUSDT', 'UNIUSDT',
           'VETUSDT', 'WBTCUSDT', 'XLMUSDT', 'XRPUSDT', 'XVGUSDT', 'YFIUSDT', 'ZECUSDT', 'ZILUSDT', 'ZRXUSDT']

new_symbols = ['ANKRUSDT', 'APEUSDT', 'APTUSDT', 'ARBUSDT', 'ARUSDT', 'AVAXUSDT', 'BOMEUSDT', 'BONKUSDT',
               'ENAUSDT', 'ETCUSDT', 'ETHFIUSDT', 'FETUSDT', 'FLOKIUSDT', 'FLOWUSDT', 'FRONTUSDT', 'GALAUSDT', 'GRTUSDT',
               'HBARUSDT', 'HOTUSDT', 'ICPUSDT', 'IMXUSDT', 'INJUSDT', 'JUPUSDT', 'LUNAUSDT', 'MATICUSDT', 'MINAUSDT',
               'NEARUSDT', 'NEOUSDT', 'OPUSDT', 'ORDIUSDT', 'PEPEUSDT', 'RNDRUSDT', 'RONINUSDT', 'RUNEUSDT', 'RVNUSDT',
               'SANDUSDT', 'SHIBUSDT', 'STXUSDT', 'SUIUSDT', 'TAOUSDT', 'WIFUSDT', 'WLDUSDT']

symbols = train_symbols + new_symbols


