"""
    
    Toy, personal framework built on Pygame.

    This file is a part of the lucyframework
    project and distributed under MIT license.
    https://github.com/kadir014/lucyframework

"""

from dataclasses import dataclass
from contextlib import contextmanager
from time import perf_counter


@dataclass
class ProfiledStat:
    avg: float
    min: float
    max: float


class Profiler:
    """
    Profiler and stat storage class.
    """
    
    def __init__(self) -> None:
        self.__timings = dict()

        self.accumulate_limit = 30

    def __getitem__(self, key: str) -> ProfiledStat:
        """ Return a profiled stat. """
        return ProfiledStat(
            self.__timings[key]["avg"],
            self.__timings[key]["min"],
            self.__timings[key]["max"]
        )

    def register(self, stat: str) -> None:
        """
        Register and initialize a stat.
        
        Parameters
        ----------
        stat
            Stat name to register to the profiler.
        """
        self.__timings[stat] = {"avg": 0.0, "min": 0.0, "max": 0.0, "acc": []}

    @contextmanager
    def profile(self, stat: str):
        """
        Profile piece of code.
        
        Parameters
        ----------
        stat
            Stat name to store the profiled code as.
        """

        start = perf_counter()
        
        try: yield None

        finally:
            elapsed = perf_counter() - start
            self.accumulate(stat, elapsed)

    def accumulate(self, stat: str, value: float) -> None:
        """
        Accumulate stat value.
        
        Parameters
        ----------
        stat
            Stat name to accumulate.
        value
            Stat value to accumulate.
        """

        acc = self.__timings[stat]["acc"]
        acc.append(value)

        if len(acc) > self.accumulate_limit:
            acc.pop(0)

            self.__timings[stat]["avg"] = sum(acc) / len(acc)
            self.__timings[stat]["min"] = min(acc)
            self.__timings[stat]["max"] = max(acc)