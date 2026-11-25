"""Validation of pull request descriptions against required sections."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

REQUIRED_SECTIONS: tuple[str, ...] = (
    "变更说明",
    "影响面",
    "验证方式",
    "回滚方案",
    "关联",
)

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_SECTION_LEVEL = 2


@dataclass(frozen=True)
class CheckResult:
    """Outcome of validating one pull request description."""

    ok: bool
    missing: tuple[str, ...]
    empty: tuple[str, ...]

    def describe(self) -> str:
        """Return a human readable summary of this result."""
        if self.ok:
            return "PR 描述通过检查"
        parts: list[str] = []
        if self.missing:
            parts.append("缺少章节: " + "、".join(self.missing))
        if self.empty:
            parts.append("内容为空: " + "、".join(self.empty))
        return "; ".join(parts)


def split_sections(body: str) -> dict[str, str]:
    """Split ``body`` into level-2 sections keyed by heading title.

    HTML comments are stripped before parsing, so a section that only holds
    template hints counts as empty. Deeper headings stay part of the enclosing
    section; a level-1 heading ends it.
    """
    text = _COMMENT.sub(" ", body or "")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = _HEADING.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2)
            if level < _SECTION_LEVEL:
                current = None
                continue
            if level == _SECTION_LEVEL:
                current = title
                sections.setdefault(title, [])
                continue
        if current is not None:
            sections[current].append(line)
    return {title: "\n".join(lines) for title, lines in sections.items()}


def check_body(
    body: str,
    required: Sequence[str] = REQUIRED_SECTIONS,
    min_chars: int = 10,
) -> CheckResult:
    """Validate ``body`` against the ``required`` section titles."""
    sections = split_sections(body)
    missing: list[str] = []
    empty: list[str] = []
    for title in required:
        content = sections.get(title)
        if content is None:
            missing.append(title)
        elif len(content.strip()) < min_chars:
            empty.append(title)
    return CheckResult(
        ok=not missing and not empty,
        missing=tuple(missing),
        empty=tuple(empty),
    )
