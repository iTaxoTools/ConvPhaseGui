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

from PySide6 import QtCore

from typing import Generic, TypeVar

from itaxotools.common.utility import AttrDict, DecoratorDict

from itaxotools.taxi_gui.types import ColumnFilter, FileFormat, FileInfo
from itaxotools.taxi_gui.model.common import Object, Property, TreeItem
from itaxotools.taxi_gui.model.input_file import InputFileModel

FileInfoType = TypeVar('FileInfoType', bound=FileInfo)

models = DecoratorDict[FileInfo, Object]()


class InputModel(Object, Generic[FileInfoType]):
    info = Property(FileInfo, None)

    def __init__(self, info: FileInfo):
        super().__init__()
        self.info = info
        self.name = f'Sequences from {info.path.name}'

    def __repr__(self):
        return f'{".".join(self._get_name_chain())}({repr(self.name)})'

    def is_valid(self):
        return True

    def as_dict(self):
        return AttrDict({p.key: p.value for p in self.properties})

    @classmethod
    def from_file_info(cls, info: FileInfoType) -> InputModel[FileInfoType]:
        if not type(info) in models:
            raise Exception(f'No suitable {cls.__name__} for info: {info}')
        return models[type(info)](info)


@models(FileInfo.Fasta)
class Fasta(InputModel):
    has_subsets = Property(bool, False)
    parse_organism = Property(bool, False)
    subset_separator = Property(str, '|')

    def __init__(self, info: FileInfo.Fasta):
        super().__init__(info)
        self.has_subsets = info.has_subsets
        self.parse_organism = info.has_subsets
        self.subset_separator = info.subset_separator


@models(FileInfo.Tabfile)
class Tabfile(InputModel):
    index_column = Property(int, -1)
    sequence_column = Property(int, -1)
    subset_column = Property(int, -1)

    def __init__(self, info: FileInfo.Tabfile):
        super().__init__(info)
        self.index_column = self._header_get(info.headers, info.header_individuals)
        self.sequence_column = self._header_get(info.headers, info.header_sequences)
        species_column = self._header_get(info.headers, 'species')
        genera_column = self._header_get(info.headers, 'genera')
        self.subset_column = species_column if species_column >= 0 else genera_column

    @staticmethod
    def _header_get(headers: list[str], field: str):
        try:
            return headers.index(field)
        except ValueError:
            return -1

    def is_valid(self):
        if self.index_column < 0:
            return False
        if self.sequence_column < 0:
            return False
        if len(set([self.index_column, self.sequence_column, self.subset_column])) < 3:
            return False
        return True
