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

from time import perf_counter
from dataclasses import dataclass
from pathlib import Path

from itaxotools.common.utility import AttrDict

from itaxotools.taxi_gui.tasks.common.process import progress_handler, get_file_info
from itaxotools.taxi_gui.tasks.common.types import AlignmentMode, DistanceMetric

from itaxotools.convphase.types import PhaseWarning


@dataclass
class ScanResults:
    info: tuple
    warns: list[PhaseWarning]


@dataclass
class Results:
    output_path: Path
    seconds_taken: float


def initialize():
    import itaxotools
    itaxotools.progress_handler('Initializing...')


def scan(input_path: Path) -> list[PhaseWarning]:

    from itaxotools.convphase.scan import scan_path

    warns = scan_path(input_path)
    info = get_file_info(input_path)

    return ScanResults(info, warns)


def execute(

    work_dir: Path,
    input_path: Path,

    **kwargs

) -> tuple[Path, float]:

    from itaxotools.convphase.phase import phase_mimic_format
    from time import sleep
    from sys import stderr

    output_path = work_dir / 'out'

    print(file=stderr)
    print('Running ConvPhase with parameters:', file=stderr)
    for k, v in kwargs.items():
        print(f'> {k} = {v}', file=stderr)
    print(file=stderr)

    # no good way to flush stdout, which results in garbled error messages
    # just sleep for now
    sleep(0.1)

    ts = perf_counter()
    phase_mimic_format(input_path, output_path, **kwargs)
    tf = perf_counter()

    print('Phasing completed successfully!', file=stderr)

    return Results(output_path, tf - ts)
