# Python工具

字符串md5

```python
import hashlib
s = "(-3469,65,-1282)"
md5_obj = hashlib.md5(s.encode("utf-8"))
result ="YulinSec{" + md5_obj.hexdigest() + "}"
print(result)
```

图片转base64(md)

```
import base64
with open("test.webp", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
print(f"![test](data:image/webp;base64,{b64})")
```

