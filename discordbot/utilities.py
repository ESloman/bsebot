

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
