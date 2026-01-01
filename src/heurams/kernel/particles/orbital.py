from heurams.utils.evalizor import Evalizer
from heurams.utils.lict import Lict


class Orbital:
    @classmethod
    def create_orbital(cls, schedule: list, phase_def: dict):
        phase_def = Lict(initdict=phase_def)  # type: ignore
        orbital = Lict()
        for i in schedule:
            orbital[i] = Lict(phase_def[i])
        return orbital

    @classmethod
    def create_orbital_on_orbitic_data(cls, orbitic_data):
        return cls.create_orbital(orbitic_data["schedule"], orbitic_data["phases"])
