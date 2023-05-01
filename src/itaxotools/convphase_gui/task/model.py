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

from datetime import datetime
from pathlib import Path
from shutil import copytree

from itaxotools.common.bindings import Binder, EnumObject, Instance, Property

from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.model.common import ItemModel
from itaxotools.taxi_gui.model.input_file import InputFileModel
from itaxotools.taxi_gui.model.partition import PartitionModel
from itaxotools.taxi_gui.model.sequence import SequenceModel
from itaxotools.taxi_gui.model.tasks import TaskModel
from itaxotools.taxi_gui.types import InputFile, Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from itaxotools.taxi_gui.tasks.common.process import get_file_info
from itaxotools.taxi_gui.tasks.common.types import AlignmentMode, DistanceMetric, PairwiseScore

from . import process
from .types import Subtask, Parameter


def get_effective(property):
    if property.value is None:
        return property.default
    return property.value


class Parameters(EnumObject):
    enum = Parameter


class Model(TaskModel):
    task_name = 'ConvPhase'

    input_sequences = Property(SequenceModel, None)
    parameters = Property(Parameters, Instance)

    busy_main = Property(bool, False)
    busy_sequence = Property(bool, False)

    dummy_results = Property(Path, None)
    dummy_time = Property(float, None)

    def __init__(self, name=None):
        super().__init__(name)
        self.exec(Subtask.Initialize, process.initialize)

    def readyTriggers(self):
        return [
            self.properties.input_sequences,
        ]

    def isReady(self):
        if self.input_sequences is None:
            return False
        if not isinstance(self.input_sequences, SequenceModel):
            return False
        if not self.input_sequences.file_item:
            return False
        return True

    def start(self):
        super().start()
        self.busy_main = True
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        params = self.parameters.properties

        self.exec(
            Subtask.Main,
            process.execute,

            work_dir=work_dir,
            input_sequences=self.input_sequences.as_dict(),

            number_of_iterations=get_effective(params.number_of_iterations),
            thinning_interval=get_effective(params.thinning_interval),
            burn_in=get_effective(params.burn_in),
            phase_threshold=get_effective(params.phase_threshold),
            allele_threshold=get_effective(params.allele_threshold),

        )

    def add_sequence_file(self, path):
        self.busy = True
        self.busy_sequence = True
        self.exec(Subtask.AddSequenceFile, get_file_info, path)

    def add_file_item_from_info(self, info):
        if info.type == InputFile.Fasta:
            index = app.model.items.add_file(InputFileModel.Fasta(info), focus=False)
            return index.data(ItemModel.ItemRole)
        else:
            self.notification.emit(Notification.Warn(f'Unsupported sequence-file format: {info.type.__name__}'))
            return None

    def get_model_from_file_item(self, file_item, model_parent, *args, **kwargs):
        if file_item is None:
            return None
        try:
            model_type = {
                InputFileModel.Tabfile: {
                    SequenceModel: SequenceModel.Tabfile,
                    PartitionModel: PartitionModel.Tabfile,
                },
                InputFileModel.Fasta: {
                    SequenceModel: SequenceModel.Fasta,
                },
            }[type(file_item.object)][model_parent]
        except Exception:
            self.notification.emit(Notification.Warn('Unexpected file type.'))
            return None
        return model_type(file_item, *args, **kwargs)

    def set_sequence_file_from_file_item(self, file_item):
        self.input_sequences = self.get_model_from_file_item(file_item, SequenceModel)

    def onDone(self, report):
        if report.id == Subtask.Initialize:
            return
        if report.id == Subtask.Main:
            time_taken = human_readable_seconds(report.result.seconds_taken)
            self.notification.emit(Notification.Info(f'{self.name} completed successfully!\nTime taken: {time_taken}.'))
            self.dummy_results = report.result.output_path
            self.dummy_time = report.result.seconds_taken
            self.busy_main = False
            self.done = True
        if report.id == Subtask.AddSequenceFile:
            file_item = self.add_file_item_from_info(report.result)
            self.set_sequence_file_from_file_item(file_item)
            self.busy_sequence = False
        self.busy = False

    def onStop(self, report):
        super().onStop(report)
        self.busy_main = False
        self.busy_sequence = False

    def onFail(self, report):
        super().onFail(report)
        self.busy_main = False
        self.busy_sequence = False

    def onError(self, report):
        super().onError(report)
        self.busy_main = False
        self.busy_sequence = False

    def clear(self):
        self.dummy_results = None
        self.dummy_time = None
        self.done = False

    def save(self, destination: Path):
        copytree(self.dummy_results, destination, dirs_exist_ok=True)
        self.notification.emit(Notification.Info('Saved files successfully!'))
