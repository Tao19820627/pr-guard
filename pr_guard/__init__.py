"""pr-guard: validate pull request descriptions against required sections."""

from pr_guard.core import REQUIRED_SECTIONS, CheckResult, check_body, split_sections

__all__ = ["REQUIRED_SECTIONS", "CheckResult", "check_body", "split_sections"]
__version__ = "0.1.0"
