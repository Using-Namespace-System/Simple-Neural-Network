from typing import Iterator, Protocol, Tuple


class Unit(Protocol):

    def reverse_excited(self) -> bool:
        """parent connection is active"""
        ...

    def forward_excited(self) -> bool:
        """child connection is active"""
        ...

    def reverse_inhibited(self) -> bool:
        """parent connection is inhibited"""
        ...

    def forward_inhibited(self) -> bool:
        """child connection is inhibited"""
        ...

    def reverse_units(self, unit: "Unit") -> Iterator["Unit"]:
        """parent units"""
        ...

    def forward_units(self, unit: "Unit") -> Iterator["Unit"]:
        """child units"""
        ...

class Unit_Set(Protocol):

    def units(self, unit: Unit) -> Iterator[Unit]:
        """units in set"""
    