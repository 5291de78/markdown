# PHP反序列化

[PHP 反序列化从入门到精通：原理与 POP 链构造详解_php反序列化pop链-CSDN博客](https://blog.csdn.net/2301_79944585/article/details/149651205)

# 一、PHP 反序列化基础原理

## 1.1 序列化与反序列化的概念

在 PHP 中，序列化 (Serialization)是将对象的状态信息转化为可存储或传输的形式（通常是字符串）的过程。而反序列化 (Deserialization) 则是将序列化后的字符串重新转换回对象的过程。这两个过程相辅相成，为数据的存储和传输提供了便利。

PHP 提供了两个主要函数来处理序列化和反序列化：

- `serialize()`：将对象转换为字符串
- `unserialize()`：将字符串转换回对象

序列化的主要目的是：

1. 将对象状态保存在文件或数据库中
2. 将对象进行远程传输（如前后端交互发送数据）

## 1.2 序列化的实现方式

```php
class Test {
    public $flag = "flag{*****}";
    public $name = "lang";
    public $age = 10;
}

$test1 = new Test();		`new Test()` 实例化，创建对象 `$test1`
$test1->flag = true;
$test1->name = "xiaoming";
$test1->age = 20;

// 序列化对象
echo serialize($test1);
//输出
O:4:"Test":3:{s:4:"flag";b:1;s:4:"name";s:8:"xiaoming";s:3:"age";i:20;}

```

- `O` = Object 对象

- `4`：类名长度，`Test` 4 个字符

- `"Test"`：类名

- `3`：这个对象有**3 个属性**

- { 。 。 。}里面是属性列表，用分号隔开

   里面是属性列表，用分号隔开 

  - `s:4:"flag"`：s=string 字符串，名字长度 4，属性名叫`flag`
  - `b:1`：b=boolean 布尔，`1`代表`true`（0=false）
  - `s:4:"name"`：属性名 name
  - `s:8:"xiaoming"`：字符串，长度 8，值 xiaoming
  - `s:3:"age"`：属性名 age
  - `i:20`：i=int 整数，值 20

## 1.3 访问控制修饰符对序列化的影响

  PHP 中的访问控制修饰符（public、protected、private）会影响序列化后的字符串格式：

```php
class Test {
    public $publicProp = "public";
    protected $protectedProp = "protected";
    private $privateProp = "private";
}

$test = new Test();
echo serialize($test);
//输出
O:4:"Test":3:{s:10:"publicProp";s:6:"public";s:16:"*protectedProp";s:9:"protected";s:17:"TestprivateProp";s:7:"private";}
```

注意观察不同访问修饰符的处理方式：

public 属性保持原样

protected 属性被序列化为属性名格式（前面有一个空字符）

private 属性被序列化为类名属性名格式（前后都有空字符）

这些空字符在 URL 编码中会表示为%00，例如%00*%00protectedProp和%00Test%00privateProp。

