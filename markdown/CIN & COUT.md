# CIN & COUT

```
#include <bits/stdc++.h>
using namespace std;
int main(){
	ios::sync_with_stdio(false);
	cin.tie(nullptr);
	/*		code		*/
}
```

## 2. 四种常见输入格式 + 对应写法
|     format     |     character      |                写法                |
| :------------: | :----------------: | :--------------------------------: |
|    已知数组    |    第一行给`T`     | int T; cin >> T; while (T--) {...} |
| 未知数组（EOF) | 不给组数，读完为止 |       while (cin >> x) {...}       |
|   以哨兵结束   |    读到`0 0` 停    |     while (cin >> m >> n && (m     |
|   混合行读取   |   一行一个字符串   |          getline(cin, s)           |

到 EOF 的两种等价写法：

