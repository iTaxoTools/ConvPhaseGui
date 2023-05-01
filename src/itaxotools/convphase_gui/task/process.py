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

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from itaxotools.common.utility import AttrDict

from itaxotools.taxi_gui.tasks.common.process import progress_handler, sequences_from_model
from itaxotools.taxi_gui.tasks.common.types import AlignmentMode, DistanceMetric


@dataclass
class DereplicateResults:
    pass


def initialize():
    import itaxotools
    itaxotools.progress_handler('Initializing...')


def execute(

    work_dir: Path,

    input_sequences: AttrDict,

    alignment_mode: AlignmentMode,
    alignment_write_pairs: bool,
    alignment_pairwise_scores: dict,

    distance_metric: DistanceMetric,
    distance_metric_bbc_k: int,
    distance_linear: bool,
    distance_matricial: bool,
    distance_percentile: bool,
    distance_precision: int,
    distance_missing: str,

    similarity_threshold: float,
    length_threshold: int,

    **kwargs

) -> tuple[Path, float]:

    print('INSERT CONVPHASE HERE')
    return 42
