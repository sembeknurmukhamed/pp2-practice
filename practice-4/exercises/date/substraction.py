from datetime import datetime, timedelta

now = datetime.now()
past = now - timedelta(days=5)
print(past)
