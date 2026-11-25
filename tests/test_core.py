"""Tests for pr_guard.core."""

from __future__ import annotations

import unittest

from pr_guard.core import REQUIRED_SECTIONS, check_body, split_sections

FULL_BODY = """\
## 变更说明

新增 pr-guard 模块，用于在 CI 中校验 PR 描述是否完整。

### 做了什么

实现章节解析与必填校验。

## 影响面

- [ ] 涉及对外接口变更
- [x] 无外部影响

## 验证方式

1. 运行 `python -m unittest discover -s tests -v`

## 回滚方案

回退该 commit 即可，无数据变更。

## 关联

- Issue：#1
- 看板条目：补 PR 模板
"""


class CheckBodyTests(unittest.TestCase):
    def test_full_body_passes(self) -> None:
        result = check_body(FULL_BODY)
        self.assertTrue(result.ok)
        self.assertEqual(result.missing, ())
        self.assertEqual(result.empty, ())

    def test_missing_section_is_reported(self) -> None:
        body = FULL_BODY.replace("## 回滚方案", "## 其它说明")
        result = check_body(body)
        self.assertFalse(result.ok)
        self.assertIn("回滚方案", result.missing)

    def test_comment_only_section_counts_as_empty(self) -> None:
        body = FULL_BODY.replace(
            "回退该 commit 即可，无数据变更。",
            "<!-- 必填：出问题时如何回退 -->",
        )
        result = check_body(body)
        self.assertFalse(result.ok)
        self.assertIn("回滚方案", result.empty)

    def test_checkbox_list_counts_as_content(self) -> None:
        body = FULL_BODY.replace(
            "- [ ] 涉及对外接口变更\n- [x] 无外部影响",
            "- [ ] 无\n- [ ] 有\n- [ ] 不确定",
        )
        result = check_body(body)
        self.assertNotIn("影响面", result.empty)

    def test_empty_body_reports_every_section(self) -> None:
        result = check_body("")
        self.assertFalse(result.ok)
        self.assertEqual(result.missing, REQUIRED_SECTIONS)

    def test_custom_required_sections(self) -> None:
        body = "## 说明\n\n这只是一个简单说明。\n"
        self.assertTrue(check_body(body, ["说明"]).ok)
        self.assertIn("影响面", check_body(body, ["说明", "影响面"]).missing)

    def test_min_chars_threshold(self) -> None:
        body = "## 变更说明\n\n短\n"
        self.assertIn("变更说明", check_body(body, ["变更说明"]).empty)
        self.assertTrue(check_body(body, ["变更说明"], min_chars=1).ok)

    def test_describe_mentions_what_is_wrong(self) -> None:
        result = check_body("## 变更说明\n\n内容足够长了这里\n", ["变更说明", "验证方式"])
        text = result.describe()
        self.assertIn("验证方式", text)


class SplitSectionsTests(unittest.TestCase):
    def test_nested_heading_stays_inside_parent(self) -> None:
        body = "## 变更说明\n\n### 做了什么\n\nalpha\n\n### 为什么\n\nbeta\n"
        sections = split_sections(body)
        self.assertIn("alpha", sections["变更说明"])
        self.assertIn("beta", sections["变更说明"])
        self.assertNotIn("做了什么", sections)

    def test_h1_ends_the_current_section(self) -> None:
        body = "# 标题\n\n## 第一节\n\n内容甲\n\n# 另一个标题\n\n## 第二节\n\n内容乙\n"
        sections = split_sections(body)
        self.assertEqual(set(sections), {"第一节", "第二节"})
        self.assertNotIn("内容乙", sections["第一节"])

    def test_comments_are_stripped(self) -> None:
        body = "## 变更说明\n\n<!-- 这里只是提示 -->\n\n真正的内容在后面。\n"
        sections = split_sections(body)
        self.assertNotIn("这里只是提示", sections["变更说明"])
        self.assertIn("真正的内容在后面", sections["变更说明"])

    def test_heading_requires_space_after_hashes(self) -> None:
        body = "##变更说明\n\n没有空格的行不算标题。\n"
        self.assertEqual(split_sections(body), {})


if __name__ == "__main__":
    unittest.main()
