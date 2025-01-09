

class Student:
    __slots__: tuple[str, ...] = ("studentnummer", "vaknamen")

    def __init__(self, studentnummer: int, vaknamen: tuple[str, ...]) -> None:
        self.studentnummer: int = studentnummer
        self.vaknamen: tuple[str, ...] = vaknamen

    def __hash__(self) -> int:
        return hash(self.studentnummer)
