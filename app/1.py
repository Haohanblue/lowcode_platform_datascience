import requests

url = "http://127.0.0.1:8000/ceb450dca/QQ浏览器截图20240401222357.png"
response = requests.get(url)
print(response.text)