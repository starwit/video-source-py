class NoFrameError(IOError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ClosedError(IOError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)