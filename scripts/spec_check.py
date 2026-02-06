from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
	required_paths = [
		Path("Dockerfile"),
		Path("Makefile"),
		Path("app/skills/trend_analyzer.py"),
		Path("app/skills/safety_judge.py"),
		Path("tests/test_trend_fetcher.py"),
	]

	all_present = True
	for path in required_paths:
		if path.exists():
			print(f"{path}: MATCH")
		else:
			print(f"{path}: MISSING")
			all_present = False

	if all_present:
		print("Governance Check: PASS")
		return 0

	print("Governance Check: FAIL")
	return 1


if __name__ == "__main__":
	sys.exit(main())
