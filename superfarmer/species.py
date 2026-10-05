from enum import Enum, auto


class Species(Enum):
    RABBIT = auto()
    SHEEP = auto()
    PIG = auto()
    COW = auto()
    HORSE = auto()
    WOLF = auto()
    FOX = auto()
    SMALL_DOG = auto()
    BIG_DOG = auto()

    def __lt__(self, other: "Species") -> bool:
        return self.value < other.value

    def __str__(self) -> str:
        return self.name.lower().replace("_", " ")


WILD_ANIMALS = (Species.FOX, Species.WOLF)
