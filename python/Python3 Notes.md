# Python3 Notes

### 字符串的操作

```python
s = "Hello Python"

s[0]        # H，正向索引，从0开始
s[-1]       # n，反向索引，-1是最后一个字符
s[0:5]      # Hello，切片 [start:end)，end取不到
s[6:]       # Python，从6到末尾
s[:5]       # Hello，从头取到5
s[::2]      # HloPto，步长2
s[::-1]     # nohtyP olleH，字符串反转

s.upper()    # HELLO PYTHON 全部大写
s.lower()    # hello python 全部小写
s.title()    # Hello Python 每个单词首字母大写
s.capitalize() # Hello python 首字母大写，其余小写
s.swapcase() # hELLO pYTHON 大小写互换

s.strip()   # 两端空白
s.lstrip()  # 左侧空白
s.rstrip()  # 右侧空白
# 也可以删除指定字符：s.strip("!")

s.find("Py")     # 6，找到返回下标；找不到返回 -1
s.index("Py")    # 6，找不到抛异常 ValueError
s.rfind("o")     # 从右往左查找
s.count("l")     # 统计子串出现次数

s.split(" ")          # ['Hello', 'Python'] 按指定字符分割成列表
s.splitlines()        # 按换行符分割
"_".join(["a","b"])   # a_b，用字符串拼接序列

s.startswith("He")   # 是否以xx开头
s.endswith("on")     # 是否以xx结尾
s.isalpha()          # 是否全字母
s.isdigit()          # 是否全数字
s.isalnum()          # 是否字母+数字
s.isspace()          # 是否全空白字符

s.center(20, "*")   # 居中，总长度20，不足用*填充
s.ljust(20,"-")     # 左对齐
s.rjust(20,"-")     # 右对齐
s.zfill(8)          # 右侧补0，常用于数字字符串

```

