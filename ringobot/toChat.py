import requests
from statistics import mean
import time
from ringobot.db.session import Session
from ringobot.config import SLACK_WEBHOOK_URL, APP_URL


def send_slack_message(message=None, attachments=None):
    webhook_url = SLACK_WEBHOOK_URL
    payload = {"text": message, "attachments": attachments} if message or attachments else None
    if payload:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 200:
            print(f'Failed to send message to Slack: {response.text}')


def to_slack(db_session):
    recent_sells = Session.get_sold_within_1_hour(db_session)
    if not recent_sells:
        return
    fields = []
    total_profit = round(sum([sell.profit for sell in recent_sells]), 2)
    color = "danger" if total_profit <= 0 else "good"
    for sell in recent_sells:
        transaction_link = f"{APP_URL}/transactions/{sell.id}"
        fields.append({
            "value": f"<{transaction_link}|{sell.name}>   :   {sell.profit_percent} %",
            "short": False,
        })
    fields.append({
        "value": f"Profit: ${total_profit}",
        "short": False,
    })

    attachment = {
        "fallback": "Recent Sells",
        "title": "Recent Sells",
        "title_link": f"{APP_URL}",
        "fields": fields,
        "footer": "Ringobot",
        "color": color,
        "ts": int(time.time())
    }
    return attachment
