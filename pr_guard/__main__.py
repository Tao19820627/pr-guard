"""Allow running the checker with ``python -m pr_guard``."""

from pr_guard.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
