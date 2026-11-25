"""Command line entry point for pr-guard."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from pr_guard.core import REQUIRED_SECTIONS, check_body


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``pr-guard`` command."""
    parser = argparse.ArgumentParser(
        prog="pr-guard",
        description="检查 PR 描述是否包含必需章节，且各章节内容非空。",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--body", help="直接传入 PR 描述文本")
    source.add_argument("--body-file", help="从文件读取 PR 描述")
    source.add_argument("--stdin", action="store_true", help="从标准输入读取 PR 描述")
    parser.add_argument(
        "--required",
        default=",".join(REQUIRED_SECTIONS),
        help="逗号分隔的必需章节标题",
    )
    parser.add_argument("--min-chars", type=int, default=10, help="章节正文最少字符数")
    parser.add_argument("--quiet", action="store_true", help="仅在失败时输出")
    return parser


def read_body(args: argparse.Namespace) -> str:
    """Read the PR description from the selected source."""
    if args.body is not None:
        return str(args.body)
    if args.body_file is not None:
        with open(args.body_file, encoding="utf-8") as handle:
            return handle.read()
    return sys.stdin.read()


def main(argv: Sequence[str] | None = None) -> int:
    """Run the check and return a process exit code."""
    args = build_parser().parse_args(argv)
    body = read_body(args)
    required = [item.strip() for item in str(args.required).split(",") if item.strip()]
    result = check_body(body, required, min_chars=int(args.min_chars))
    if not args.quiet or not result.ok:
        print(result.describe())
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
