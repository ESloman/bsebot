
"""
File for other small and useful classes that we may need in other parts of the code
"""

class PlaceHolderLogger():
    """
    Placeholder logger for when we don't have a logging object
    replaces logging functions with just printing
    """
    @staticmethod
    def info(msg: str) -> None:
        print(msg)

    def debug(msg: str) -> None:
        print(msg)

    def warning(msg: str) -> None:
        print(msg)
