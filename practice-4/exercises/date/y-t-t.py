from datetime import datetime, timedelta

today = datetime.now()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print(yesterday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d"))