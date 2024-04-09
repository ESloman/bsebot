"""Checks the docker logs output of bsebot to check for errors."""

import subprocess  # noqa: S404
import sys

DEBUG: bool = False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        print("Debug mode enabled.")
        DEBUG = True

    bytes_output: bytes = subprocess.check_output(["docker", "logs", "bsebot"])  # noqa: S603, S607
    output: list[str] = str(bytes_output).split("\n")

    if DEBUG:
        print(f"Length of bytes output is: {len(bytes_output)}")
        print(f"Length of output is: {len(output)}")

    errors: int = 0
    for line in output:
        if DEBUG:
            print(line)
        if any(x in line.lower() for x in ["error", "traceback", "exception"]):
            errors += 1
            if DEBUG:
                print(f"Line '{line.strip()}' was NOT clean - increased error count to {errors=}.")
    print(errors)
