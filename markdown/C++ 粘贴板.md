# C++ 粘贴板

# O,多文件写法

```
文件结构
项目文件
|-------func_def.cpp
|-------func_void.h
|-------main.cpp
```

main.cpp

![1795006762697](C:\Users\wangq\Desktop\markdown\计算机科学\mind_pic\1795006762697.png)

miller.cpp

![1795006687560](C:\Users\wangq\Desktop\markdown\计算机科学\mind_pic\1795006687560.png)

miller.h

![1795006627128](C:\Users\wangq\Desktop\markdown\计算机科学\mind_pic\1795006627128.png)

# 1，常用设置

```c++
#支持中文输出 <windows.h>
SetConsoleOutputCP(CP_UTF8);   // 控制台输出设为UTF-8
SetConsoleCP(CP_UTF8);         // 控制台输入设为UTF-8

#时间
	#获取当前时间
std::string get_time_str()
{
    std::time_t now = std::time(nullptr);
    std::tm* local_tm = std::localtime(&now);
    char buf[64] = {0};
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", local_tm);
    return std::string(buf);
}
```



