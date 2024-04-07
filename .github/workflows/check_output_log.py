"""Checks the output in output.log for any errors."""

import sys
from pathlib import Path

DEBUG: bool = False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        print("Debug mode enabled.")
        DEBUG = True

    path: Path = Path("output.log")
    errors: int = 0
    with open(path, encoding="utf-8") as output:
        for line in output:
            if any(x in line.lower() for x in ["error", "traceback", "exception"]):
                errors += 1
                if DEBUG:
                    print(f"Line '{line.strip()}' was NOT clean - increased error count to {errors=}.")
            elif DEBUG:
                print(f"Line '{line.lower()}' was clean.")
    print(errors)
