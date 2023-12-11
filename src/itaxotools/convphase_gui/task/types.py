# -----------------------------------------------------------------------------
# TaxiGui - GUI for Taxi2
# Copyright (C) 2022-2023  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

from dataclasses import dataclass
from enum import Enum, auto

from itaxotools.taxi_gui.types import FileInfo


@dataclass
class Results:
    output_info: FileInfo
    ambiguous: bool
    warning: str
    seconds_taken: float


class Parameter(Enum):
    PhaseThreshold = (
        "Phase threshold (-p)",
        "Minimum phase certainty from 0 to 1.",
        "phase_threshold",
        float,
        0.9,
    )
    AlleleThreshold = (
        "Allele threshold (-q)",
        "Minimum genotype certainty from 0 to 1.",
        "allele_threshold",
        float,
        0.9,
    )
    NumberOfIterations = (
        "Number of iterations",
        "Number of MCMC iterations.",
        "number_of_iterations",
        int,
        100,
    )
    ThinningInterval = (
        "Thinning interval",
        "Thinning interval.",
        "thinning_interval",
        int,
        1,
    )
    BurnIn = "Burn in", "Burn in.", "burn_in", int, 100

    def __init__(self, label, description, key, type, default):
        self.label = label
        self.description = description
        self.key = key
        self.type = type
        self.default = default

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self._name_}>"


class OutputFormat(Enum):
    Tabfile = auto()
    Fasta = auto()
    Mimic = auto()
