# Argparse库的使用

> `argparse` 是 Python 标准库中用于**命令行参数解析**的模块，可以轻松编写用户友好的命令行接口，自动生成帮助信息、支持位置参数 / 可选参数 / 子命令等复杂场景



实测全部通过（错误提示、退出码 2、互斥/choices 校验都正常；上面的乱码只是 Git Bash 控制台编码问题，实际运行无碍）。下面是完整讲解。

# argparse 使用详解

## 一、它是什么，独特优势在哪

`argparse` 是 Python 标准库的命令行参数解析器。和手动解析 `sys.argv` 相比：

| 能力                                      | `sys.argv` 手写    | `argparse`                         |
| ----------------------------------------- | ------------------ | ---------------------------------- |
| 自动生成 `-h/--help` 帮助                 | ❌                  | ✅ 排版整齐，随时可用               |
| 类型转换（str→int/float/Path…）           | 手写 `int()` + try | ✅ `type=` 自动转，失败给友好报错   |
| 取值合法性校验                            | 手写 if            | ✅ `choices=` / 自定义校验函数      |
| 子命令（git 风格 `git push/pull`）        | 极难维护           | ✅ `add_subparsers` 原生支持        |
| 互斥选项（`--quiet` 与 `--debug` 二选一） | 手写               | ✅ `add_mutually_exclusive_group`   |
| 参数分组、默认值显示、版本号              | 手写               | ✅ 声明式配置                       |
| 出错时的 usage 提示与退出码               | 手写               | ✅ 自动打印用法并以退出码 2 结束    |
| 可测试性                                  | 要模拟 argv        | ✅ `parse_args([...])` 直接注入列表 |

**核心思想**：声明式——你描述"参数长什么样"，它负责解析、校验、报错、生成帮助。

## 二、完整示例（已实测可运行）

一个"日志分析工具"，一张代码覆盖几乎所有用法：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""logtool.py —— argparse 完整用法演示（一个"日志分析工具"）"""

import argparse
import sys
from pathlib import Path


# ---------- 自定义 type：既是"类型转换"也是"值校验" ----------
def positive_int(text: str) -> int:
    """把命令行字符串转成"正整数"，否则抛 ArgumentTypeError。"""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} 不是整数")
    if value <= 0:
        raise argparse.ArgumentTypeError(f"{value} 必须为正整数")
    return value


def csv_list(text: str) -> list:
    """'a,b,c' -> ['a','b','c']，演示 type 可以返回任意对象。"""
    items = [item.strip() for item in text.split(",")]
    if not all(items):
        raise argparse.ArgumentTypeError(f"{text!r} 含有空字段")
    return items


# ---------- 子命令处理函数 ----------
def cmd_scan(args):
    print(f"[scan] 文件      : {[str(f) for f in args.files]}")
    print(f"[scan] 级别      : {args.level}")
    print(f"[scan] 关键字    : {args.keywords}")
    print(f"[scan] 线程 id   : {args.ids}")
    print(f"[scan] 采样比例  : {args.ratio}")
    print(f"[scan] Top N     : {args.top}")
    print(f"[scan] 输出到    : {args.output}")
    print(f"[scan] 配置文件  : {args.config}")
    print(f"[scan] -v 等级   : {args.verbose}  安静={args.quiet}  调试={args.debug}")


def cmd_stat(args):
    print(f"[stat] 文件      : {[str(f) for f in args.files]}")
    print(f"[stat] 统计字段  : {args.fields}")
    print(f"[stat] 干跑      : {args.dry_run}")
    print(f"[stat] 追加常量  : {args.filters}")
    print(f"[stat] -v 等级   : {args.verbose}")


# ---------- 组装解析器 ----------
def build_parser() -> argparse.ArgumentParser:
    # parents：公共参数组。父 parser 必须 add_help=False，
    # 否则子 parser 会重复生成 -h 导致冲突。
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-v", "--verbose", action="count", default=0,
                        help="详细输出，可叠加：-v / -vv / -vvv")

    parser = argparse.ArgumentParser(
        prog="logtool",
        description="日志分析小工具 —— argparse 用法大全演示",
        epilog="示例: python logtool.py scan app.log --config c.toml --level error -vv",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # help 里自动显示默认值
        allow_abbrev=True,  # 允许 --lev 这种唯一前缀缩写（默认即 True）
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    # 互斥组：两者不能同时给
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quiet", action="store_true", help="安静模式")
    mode.add_argument("--debug", action="store_true", help="调试模式")

    # 子命令（git 风格）
    sub = parser.add_subparsers(title="子命令", dest="cmd", metavar="{scan,stat}",
                                required=True)  # 3.7+ 可直接要求必须给子命令

    p_scan = sub.add_parser("scan", parents=[common], help="扫描日志，输出出现最多的行")
    p_scan.add_argument("files", nargs="+", metavar="FILE", type=Path,
                        help="要分析的日志文件，至少一个（位置参数 + nargs='+'）")
    p_scan.add_argument("-o", "--output", metavar="OUT", type=Path,
                        default=Path("result.txt"),
                        help="结果输出文件（演示 default / metavar / Path 类型）")
    p_scan.add_argument("-l", "--level",
                        choices=["debug", "info", "warning", "error"],  # 限定取值
                        default="info",
                        help="最低日志级别（演示 choices，help 中可写 %(choices)s）")
    p_scan.add_argument("-k", "--keyword", action="append", dest="keywords",
                        metavar="KW", default=None,
                        help="只保留含关键字的行，可多次指定（演示 append 与 dest）")
    p_scan.add_argument("--ids", nargs="+", type=positive_int, metavar="N",
                        help="线程 id 列表（演示 nargs='+' 与自定义 type 校验）")
    p_scan.add_argument("--ratio", type=float, default=0.8,
                        help="采样比例（演示 float；help 中可用 %(default)s）")
    p_scan.add_argument("--top", type=positive_int, default=10,
                        help="打印出现次数最多的前 N 行")
    p_scan.add_argument("--config", required=True, metavar="PATH",
                        help="必填选项演示：不给就报错")
    p_scan.set_defaults(func=cmd_scan)

    p_stat = sub.add_parser("stat", parents=[common], help="汇总统计")
    p_stat.add_argument("files", nargs="*", metavar="FILE", type=Path,
                        help="日志文件，0 个或多个（演示 nargs='*'）")
    p_stat.add_argument("--fields", type=csv_list, default=["ip", "status"],
                        help="统计字段，逗号分隔（演示 type 返回列表）")
    p_stat.add_argument("--dry-run", action="store_true",
                        help="只演示不执行（action='store_true'）")
    p_stat.add_argument("--tag", action="append_const", const="TAGGED", dest="filters",
                        help="每给一次就向 filters 追加常量 TAGGED（append_const）")
    p_stat.set_defaults(func=cmd_stat)

    return parser


def main():
    args = build_parser().parse_args()  # 想容忍未知参数则改用 parse_known_args()
    args.func(args)                     # 通过 set_defaults(func=...) 分发到子命令


if __name__ == "__main__":
    main()
```

## 三、运行效果（实测输出）

正常调用：

```
$ python logtool.py scan app.log access.log --config cfg.toml --level error -vv \
      -k timeout -k 500 --ids 1 2 3 --ratio 0.5 --top 3 -o out.txt
[scan] 文件      : ['app.log', 'access.log']
[scan] 级别      : error
[scan] 关键字    : ['timeout', '500']
[scan] 线程 id   : [1, 2, 3]
[scan] 采样比例  : 0.5
[scan] Top N     : 3
[scan] 输出到    : out.txt
[scan] 配置文件  : cfg.toml
[scan] -v 等级   : 2  安静=False  调试=False
```

各类错误（自动打印 usage、退出码 = 2）：

```
$ python logtool.py scan app.log              # 缺必填项
logtool scan: error: the following arguments are required: --config

$ python logtool.py scan app.log --config c --level fatal    # choices 校验
logtool scan: error: argument -l/--level: invalid choice: 'fatal'
                  (choose from 'debug', 'info', 'warning', 'error')

$ python logtool.py --quiet --debug scan app.log --config c  # 互斥校验
logtool: error: argument --debug: not allowed with argument --quiet
```

帮助长这样（`ArgumentDefaultsHelpFormatter` 自动带默认值，`--help` 零成本获得）：

```
$ python logtool.py scan --help
usage: logtool scan [-h] [-v] [-o OUT] [-l {debug,info,warning,error}]
                    [-k KW] [--ids N [N ...]] [--ratio RATIO] [--top TOP]
                    --config PATH
                    FILE [FILE ...]
```

## 四、用法速查表（尽可能全）

**`add_argument()` 参数**：

| 用法                                            | 作用                                                    |
| ----------------------------------------------- | ------------------------------------------------------- |
| `add_argument("files")`                         | 位置参数（必选）                                        |
| `add_argument("-o", "--output")`                | 短/长选项，二者等价                                     |
| `type=int/float/Path/自定义函数`                | 转换+校验；抛 `ArgumentTypeError` 得友好报错            |
| `default=值`                                    | 缺省值                                                  |
| `required=True`                                 | 可选参数设为必填                                        |
| `choices=[...]`                                 | 限定取值集合                                            |
| `nargs=N / '?' / '*' / '+'`                     | consumes N 个 / 0或1 / ≥0 / ≥1 个值；`'?'` 常配 `const` |
| `nargs='*'` + `default=`                        | 不传时为 default，传了就收列表                          |
| `action=`                                       | 见下表                                                  |
| `metavar="OUT"`                                 | help/usage 里显示的参数名                               |
| `dest="keywords"`                               | 结果属性名（默认取长选项名去 `--`）                     |
| `help="..."`                                    | 支持 `%(default)s`、`%(prog)s`、`%(choices)s` 插值      |
| `const=值`                                      | 搭配 `'?'`/`store_const`/`append_const` 使用            |
| `version="%(prog)s 1.0.0"` + `action="version"` | `--version` 打印后退出                                  |

**`action` 全家桶**：

| action                                   | 效果                                   |
| ---------------------------------------- | -------------------------------------- |
| `store`（默认）                          | 存值                                   |
| `store_true` / `store_false`             | 出现即 True/False（不需要值）          |
| `store_const`                            | 出现即存 `const` 指定的常量            |
| `append`                                 | 每出现一次往列表追加一个值             |
| `append_const`                           | 每出现一次往列表追加 `const`           |
| `count`                                  | 数出现次数（`-vvv` → 3）               |
| `version`                                | 打印版本并退出                         |
| `extend`（3.8+）                         | `nargs='+'` 时把多个值一次性展平进列表 |
| `argparse.BooleanOptionalAction`（3.9+） | 一个参数自动生成 `--foo` 与 `--no-foo` |

**解析器级别**：

| 用法                                                   | 作用                                                         |
| ------------------------------------------------------ | ------------------------------------------------------------ |
| `ArgumentParser(prog, usage, description, epilog)`     | 程序名、自定义 usage、帮助头尾说明                           |
| `formatter_class=`                                     | `ArgumentDefaultsHelpFormatter`（显示默认值）/ `RawTextHelpFormatter`（保留换行） |
| `add_argument_group("名称")`                           | 帮助信息里给参数分组                                         |
| `add_mutually_exclusive_group(required=True)`          | 互斥 + 必选其一                                              |
| `add_subparsers(dest="cmd", required=True)`            | 子命令体系，配合各 `add_parser(...).set_defaults(func=...)` 分发 |
| `parents=[common]`                                     | 复用一组公共参数（父 parser 要 `add_help=False`）            |
| `set_defaults(x=...)` / `parser.set_defaults(func=fn)` | 设属性默认值 / 绑处理函数                                    |
| `parse_args(args=[...])`                               | 传入列表代替 `sys.argv`，**单元测试神器**                    |
| `parse_known_args()`                                   | 未知参数不报错，返回 `(args, remaining)`                     |
| `parser.error("消息")`                                 | 手动触发"打印 usage + 退出码 2"                              |
| `parser.print_help()` / `format_help()`                | 打印/获取帮助文本                                            |
| `allow_abbrev=False`                                   | 关掉前缀缩写                                                 |
| `prefix_chars="+"`                                     | 用 `+flag` 风格前缀（罕见）                                  |
| `fromfile_prefix_chars="@"`                            | `@args.txt` 从文件读取参数                                   |
| `conflict_handler="resolve"`                           | 允许后加的同名参数覆盖先加的                                 |
| `exit_on_error=False`（3.9+）                          | 解析失败抛 `argparse.ArgumentError` 而非直接退出             |

**与解析器交互的异常/类型**：

- `argparse.ArgumentTypeError`：自定义 `type` 函数里抛，错误信息会被自动包装进提示；
- 继承 `argparse.Action` 可写完全自定义的 action；
- `argparse.FileType("w")`：把参数直接转成打开的文件对象（注意句柄要自己关，现代代码更推荐 `type=Path`）。

## 五、三个最常见的坑

1. **全局选项要放在子命令前面**：`logtool --quiet scan app.log` ✅，`logtool scan app.log --quiet` ❌（`--quiet` 属于主 parser）。想让 `-v` 出现在子命令后，就像我一样把它放进 `parents=[common]` 注入子 parser。
2. **`action="append"` 别用可变默认值**：写 `default=None` 再在代码里 `args.keywords or []`，避免多个 parse 调用共享同一个列表。
3. **别重复造轮子**：只是 1~2 个简单参数可以直接 `sys.argv`；想要更漂亮的 API 可以看 `click` / `typer`（基于类型注解），但**子命令 + 互斥 + 校验**这套需求，`argparse` 零依赖、标准库、生态成熟（如 `sphinx-argparse` 可自动生成文档），通常是首选。

把上面的代码存成 `logtool.py`，先跑一次 `python logtool.py --help`，再照"运行效果"里的命令逐条试，argparse 的核心就都在你手里了。



## 

