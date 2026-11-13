# PY bug

> requests库的使用



```python
import requests
url = "https://673670eeaa50ea8a.yulinsec.cn/"
headers = {}

requests.method(url , param1 , param2 .....) #返回一个response对象

#GET + url参数
r = requests.get(url",params={"name": "小明", "page": 2})
	# 实际请求: .../get?name=%E5%B0%8F%E6%98%8E&page=2
requests.post(url , data={"user": "tom", "pwd": "123"})





```

