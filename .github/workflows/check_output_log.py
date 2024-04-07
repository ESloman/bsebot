"""Checks the output in output.log for any errors."""

from pathlib import Path

if __name__ == "__main__":
    path: Path = Path(".", "output.log")
    errors: int = 0
    with open(path, encoding="utf-8") as output:
        for line in output:
            if any(x in line.lower() for x in ["error", "traceback", "exception"]):
                errors += 1
    print(errors)
