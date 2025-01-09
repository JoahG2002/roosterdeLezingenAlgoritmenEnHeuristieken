import sys

from rooster.modellen.vak import Vak
from rooster.modellen.zaal import Zaal
from rooster.modellen.bundel import Roosterdata
from rooster.modellen.genereer import Roostermaker
from rooster.dataverwerking.lees import lees_roosterdata
from rooster.dataverwerking.schrijf import schrijf_foutmelding
from rooster.constants.constant import returncodes, teksten


def main(argc: int, argv: list[str]) -> None:
    if not argc == 4:
        schrijf_foutmelding(teksten.TOELICHTING_VLAGGEN)
        exit(returncodes.MISLUKT)

    roosterdata: Roosterdata | None = lees_roosterdata()

    if not roosterdata:
        schrijf_foutmelding("minstens één van de opgegeven csv-bestandpaden bestaat niet.")
        exit(returncodes.MISLUKT)

    vakken: tuple[Vak, ...] = (
        Vak("Advanced Heuristics", 1, 0, 1, 10, 22),
        Vak("Algoritmen en complexiteit", 1, 0, 25, 10, 60),
        Vak("Analysemethoden en -technieken", 1, 0, 1, 25, 47),
    )
    zalen: tuple[Zaal, ...] = (
            Zaal("A1.04", 41),
            Zaal("A1.06", 22),
            Zaal("A1.08", 20),
            Zaal("A1.10", 56),
            Zaal("B0.201", 48),
            Zaal("C0.110", 117),
            Zaal("C1.112", 60)
        )

    roostermaker: Roostermaker = Roostermaker(zalen)
    roostermaker.genereer_rooster(vakken)

    roostermaker.genereer_rooster(vakken)
    roostermaker.print_rooster()

    exit(returncodes.SUCCES)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
