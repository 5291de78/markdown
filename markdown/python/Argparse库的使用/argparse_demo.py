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
