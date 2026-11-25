# pr-guard

在 CI 中校验 PR 描述是否包含必需章节，且每个章节都填了实际内容。

流程里「代码评审」的进入条件是「PR 已提交且信息完整」，但这件事靠人盯必然失守——评审人总要回头问「影响哪些模块」「怎么验证的」。这个工具把那几条要求变成**可判定的检查**。

## 规则

一个章节算「已填写」需要同时满足：

1. 存在二级标题 `## <章节名>`
2. 去掉 HTML 注释后的正文长度 ≥ `--min-chars`（默认 10）

模板里的 `<!-- 必填：... -->` 提示不会被误认为内容——这正是最容易造假的地方。

默认必需章节：`变更说明`、`影响面`、`验证方式`、`回滚方案`、`关联`。

## 用法

```bash
# 从文件读取
python -m pr_guard --body-file pr_body.md

# 从标准输入
gh pr view 42 --json body -q .body | python -m pr_guard --stdin

# 直接传文本
python -m pr_guard --body "$PR_BODY"

# 自定义必需章节
python -m pr_guard --body-file body.md --required "变更说明,验证方式"

# 只在失败时输出
python -m pr_guard --body-file body.md --quiet
```

退出码：`0` 通过，`1` 不通过。可直接作为 CI 步骤。

## 在 GitHub Actions 中使用

```yaml
- name: Validate PR description
  env:
    PR_BODY: ${{ github.event.pull_request.body }}
  run: python -m pr_guard --body "$PR_BODY" --quiet
```

本仓库的 `.github/workflows/pr-guard.yml` 就是这么做的。

## 作为库使用

```python
from pr_guard import check_body

result = check_body(body)
if not result.ok:
    print(result.describe())   # 缺少章节: 回滚方案; 内容为空: 验证方式
```

## 解析规则

- 章节边界是**二级标题**（`##`）
- `###` 及更深的小标题留在所属章节内部，不会被当成新章节
- 一级标题（`#`）会结束当前章节
- HTML 注释在解析前被剔除
- `##标题`（井号后无空格）不算标题

## 开发

```bash
python -m unittest discover -s tests -v   # 测试
ruff check .                              # 风格
mypy pr_guard                             # 类型
```

## 许可

MIT
