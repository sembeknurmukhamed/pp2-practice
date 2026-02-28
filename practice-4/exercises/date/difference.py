from datetime import datetime

date1 = datetime.strptime(input().strip(), "%Y-%m-%d")
date2 = datetime.strptime(input().strip(), "%Y-%m-%d")
print(int(date1.timestamp() - date2.timestamp()))