from typing import Callable
from ctypes import CDLL, c_double, c_int8

from ..constants.constant import sharedlibraryfuncties


c_functions: CDLL = CDLL(sharedlibraryfuncties.PAD_DLL_SO_BESTAND_C_FUNCTIES)

bereken_temperatuur: Callable[[c_double, c_double, c_double], float] = c_functions.bereken_temperatuur
bereken_temperatuur.argtypes = [c_double, c_double, c_double]
bereken_temperatuur.restype = c_double

accepteer_slechtste_oplossing: Callable[[c_double, c_double, c_double, c_double], int] = c_functions.accepteer_slechtste_oplossing
accepteer_slechtste_oplossing.argtypes = [c_double, c_double, c_double, c_double]
accepteer_slechtste_oplossing.restype = c_int8
