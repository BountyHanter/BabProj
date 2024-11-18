import os
from dotenv import load_dotenv

load_dotenv()

MEDIA_SERVER_REPORTS_URL = os.getenv('MEDIA_SERVER_REPORTS_URL')
MEDIA_SERVER_RECEIPT_URL = os.getenv('MEDIA_SERVER_RECEIPT_URL')
MEDIA_IP_URL = os.getenv('MEDIA_IP_URL')
SITE_URL = os.getenv('SITE_URL')
DOMAIN = os.getenv('DOMAIN')
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')


TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
API_URL = f'https://api.telegram.org/bot{TG_BOT_TOKEN}'
TG_FLASK_ADDRESS = os.getenv('TG_FLASK_ADDRESS')

active_timers = {}
