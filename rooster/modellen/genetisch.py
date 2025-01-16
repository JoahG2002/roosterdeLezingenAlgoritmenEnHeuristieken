from .vak import Vak
from .zaal import Zaalslot
from .student import Student
from .activiteit import Activiteit


class GenetischRooster:
    def __init__(self,
                 rooster: list[Activiteit | None],
                 zaalsloten: set[Zaalslot],
                 studenten: set[Student],
                 vakken: list[Vak]) -> None:
        self.rooster: list[Activiteit | None] = rooster
        self.zaalsloten: set[Zaalslot] = zaalsloten
        self.studenten: set[Student] = studenten
        self.vakken: list[Vak] = vakken
