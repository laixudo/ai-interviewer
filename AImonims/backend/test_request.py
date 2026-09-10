import requests

response = requests.get('http://localhost:8001/api/admin/user/1/ability-profile')
print('状态码:', response.status_code)
print('返回数据:', response.json())
