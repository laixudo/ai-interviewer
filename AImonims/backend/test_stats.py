import requests
import time

time.sleep(1)

response = requests.get('http://localhost:8001/api/admin/stats')
print('状态码:', response.status_code)
data = response.json()
print('返回数据:', data)
print()
print('平均分数:', data.get('avgScore'))
