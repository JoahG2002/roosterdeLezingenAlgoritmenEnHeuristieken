import os

from typing import Optional
from polars import read_csv, DataFrame

from ..modellen.bundel import Roosterdata


def lees_roosterdata(pad_vakken_csv: str, pad_zalen_csv: str, pad_studenten_vakken_csv: str) -> Optional[Roosterdata]:
    """
    Leest alle benodigde data voor een rooster in.
    """
    if not all(os.path.exists(pad) for pad in (pad_vakken_csv, pad_zalen_csv, pad_studenten_vakken_csv)):
        return None

    rooster_data: Roosterdata = Roosterdata()

    dataframe_vakken: DataFrame = read_csv(pad_vakken_csv, infer_schema=35, encoding="ascii")

    print(dataframe_vakken)
