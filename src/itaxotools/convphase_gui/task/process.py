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

from pathlib import Path
from sys import stderr
from time import perf_counter, sleep

from itaxotools.common.utility import AttrDict

from .types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    from . import work  # noqa


def execute(
    work_dir: Path,
    input_sequences: AttrDict,
    output_options: AttrDict,
    parameters: AttrDict,
) -> tuple[Path, float]:
    from itaxotools import abort, get_feedback

    from .work import (
        configure_progress_callbacks,
        get_file_info,
        get_input_sequence_warnings,
        get_output_file_handler,
        get_output_file_name,
        get_output_sequence_ambiguity,
        get_phased_sequences,
        get_sequences_from_model,
    )

    ts = perf_counter()

    configure_progress_callbacks()

    output_path = work_dir / "out"

    print(file=stderr)
    print("Running ConvPhase with parameters:", file=stderr)
    for k, v in parameters.items():
        print(f"> {k} = {v}", file=stderr)
    print(file=stderr)

    # no good way to flush stdout for both python and convphase extension,
    # which results in garbled error messages. just sleep for now...
    sleep(0.1)

    sequences = get_sequences_from_model(input_sequences)
    warns = get_input_sequence_warnings(sequences)

    tm = perf_counter()

    if warns:
        answer = get_feedback(warns)
        if not answer:
            abort()

    tx = perf_counter()

    phased_sequences = get_phased_sequences(sequences, parameters)

    ambiguous, warning = get_output_sequence_ambiguity(phased_sequences)

    output_path = work_dir / get_output_file_name(output_options, input_sequences)

    write_handler = get_output_file_handler(
        output_path, output_options, input_sequences
    )

    with write_handler as file:
        for sequence in phased_sequences:
            file.write(sequence)

    output_info = get_file_info(output_path)

    tf = perf_counter()

    print("Phasing completed successfully!", file=stderr)

    return Results(output_info, ambiguous, warning, tm - ts + tf - tx)
