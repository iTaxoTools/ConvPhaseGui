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

from itaxotools.common.utility import AttrDict
from itaxotools.convphase.phase import iter_phase, set_progress_callback
from itaxotools.convphase.scan import scan_input_sequences, scan_output_sequences
from itaxotools.convphase.types import PhasedSequence, PhaseWarning, UnphasedSequence
from itaxotools.taxi2.file_types import FileFormat
from itaxotools.taxi2.files import get_info
from itaxotools.taxi2.sequences import Sequence, SequenceHandler, Sequences
from itaxotools.taxi_gui.tasks.common.process import progress_handler

from .types import OutputFormat


def configure_progress_callbacks() -> None:
    set_progress_callback(lambda v, m, t: progress_handler(t, v, m))
    progress_handler("Computing matrix Q", 0, 1)
    progress_handler("MCMC resolution", 0, 1)


def get_input_sequence_warnings(sequences: Sequences) -> list[str]:
    return [str(w) for w in scan_input_sequences(sequences)]


def get_sequences_from_model(input: AttrDict):
    match input.info.format:
        case FileFormat.Tabfile:
            return Sequences.fromPath(
                input.info.path,
                SequenceHandler.Tabfile,
                hasHeader=True,
                idColumn=input.index_column,
                seqColumn=input.sequence_column,
            )
        case FileFormat.Fasta:
            return Sequences.fromPath(
                input.info.path,
                SequenceHandler.Fasta,
                parse_organism=input.parse_organism,
                organism_separator=input.subset_separator,
                organism_tag="organism",
            )
    raise Exception(f"Cannot create sequences from input: {input}")


def _get_sequences_from_phased_data(
    sequences: Sequences,
    phased: iter[PhasedSequence],
) -> iter[Sequence]:
    phased_dict = {line.id: line for line in phased}

    for sequence in sequences:
        try:
            # SeqPhase automatically replaces spaces...
            phased_id = sequence.id.replace(" ", "_")
            # and cuts everything after a bar...
            phased_id = sequence.id.split("|")[0]
            line = phased_dict[phased_id]
        except KeyError:
            raise Exception(
                f'Sequence identifier not found in phased data: "{sequence.id}"'
            )

        for extra, value in sequence.extras.items():
            if value is None:
                sequence.extras[extra] = ""

        yield Sequence(sequence.id, line.data_a, sequence.extras | {"allele": "a"})
        yield Sequence(sequence.id, line.data_b, sequence.extras | {"allele": "b"})


def get_phased_sequences(
    sequences: Sequences, parameters: dict[str, int | float]
) -> Sequences:
    unphased = (UnphasedSequence(sequence.id, sequence.seq) for sequence in sequences)
    phased = iter_phase(unphased, **parameters)

    return Sequences(list(_get_sequences_from_phased_data(sequences, phased)))


def get_output_file_handler(
    output_path: Path,
    output_options: dict,
    input_sequences: AttrDict,
) -> SequenceHandler:
    match output_options.format:
        case OutputFormat.Mimic:
            match input_sequences.info.format:
                case FileFormat.Fasta:
                    return SequenceHandler.Fasta(
                        output_path,
                        "w",
                        write_organism=input_sequences.info.has_subsets,
                        concatenate_extras=["allele"],
                        organism_separator=input_sequences.info.subset_separator,
                        organism_tag="organism",
                    )

                case FileFormat.Tabfile:
                    headers = input_sequences.info.headers
                    return SequenceHandler.Tabfile(
                        output_path,
                        "w",
                        idHeader=headers[input_sequences.index_column],
                        seqHeader=headers[input_sequences.sequence_column],
                    )

                case _:
                    raise ValueError(f"Unknown format: {input_sequences.info}")

        case OutputFormat.Fasta:
            info = input_sequences.info

            organism_tag = "organism"
            write_organism = input_sequences.has_subsets
            concatenate_extras = ["allele"]

            if info.format == FileFormat.Tabfile:
                if write_organism:
                    organism_tag = info.headers[input_sequences.subset_column]
                if input_sequences.has_extras and output_options.fasta_concatenate:
                    keys = [
                        info.headers[input_sequences.index_column],
                        info.headers[input_sequences.sequence_column],
                        organism_tag,
                        "allele",
                    ]
                    concatenate_extras = [x for x in info.headers if x not in keys]
                    concatenate_extras += ["allele"]

            return SequenceHandler.Fasta(
                output_path,
                "w",
                write_organism=write_organism,
                concatenate_extras=concatenate_extras,
                organism_separator=output_options.fasta_separator,
                organism_tag=organism_tag,
            )

        case OutputFormat.Tabfile:
            return SequenceHandler.Tabfile(
                output_path,
                "w",
                idHeader="seqid",
                seqHeader="sequence",
            )


def _get_output_format(
    output_options: dict,
    input_sequences: AttrDict,
) -> str:
    match output_options.format:
        case OutputFormat.Mimic:
            return input_sequences.info.format

        case OutputFormat.Fasta:
            return FileFormat.Fasta

        case OutputFormat.Tabfile:
            return FileFormat.Tabfile


def get_output_file_name(
    output_options: dict,
    input_sequences: AttrDict,
) -> str:
    format = _get_output_format(output_options, input_sequences)
    path = input_sequences.info.path
    return f"{path.stem}_phased{format.extension}"


def get_file_info(path: Path):
    return get_info(path)


def get_output_sequence_ambiguity(sequences: Sequences) -> tuple[bool, str]:
    ambiguous = False
    warning = ""
    for warning in scan_output_sequences(sequences):
        if isinstance(warning, PhaseWarning.Ambiguity):
            ambiguous = True
            warning = "WARNING: " + str(warning)
    return ambiguous, warning
