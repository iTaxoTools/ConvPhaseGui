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

from PySide6 import QtCore

from datetime import datetime
from pathlib import Path
from shutil import copyfile

from itaxotools.common.bindings import (
    Binder, EnumObject, Instance, Property, PropertyObject)
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel
from itaxotools.taxi_gui.tasks.common.model import ImportedInputModel
from itaxotools.taxi_gui.threading import ReportDone
from itaxotools.taxi_gui.types import FileFormat, FileInfo, Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from . import process
from .input import InputModel
from .process import scan_file
from .types import OutputFormat, Parameter, ScanResults


def get_effective(property):
    if property.value is None:
        return property.default
    return property.value


class Parameters(EnumObject):
    enum = Parameter


class SequenceScanSubtaskModel(SubtaskModel):
    task_name = 'FileScanSubtask'

    done = QtCore.Signal(FileInfo)

    def start(self, path: Path):
        super().start(scan_file, path)

    def onDone(self, report: ReportDone):
        self.done.emit(report.result)
        self.busy = False


class OutputModel(PropertyObject):
    format = Property(OutputFormat, OutputFormat.Mimic)

    fasta_separator = Property(str, '|')
    fasta_concatenate = Property(bool, False)

    fasta_config_visible = Property(bool, False)
    fasta_separator_visible = Property(bool, False)
    fasta_concatenate_visible = Property(bool, False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.binder = Binder()

        self.set_input_object(None)

    def set_input_object(self, object):
        self.binder.unbind_all()
        self.object = object

        self.binder.bind(self.properties.format, self._update_fasta_config_visible)

        if object is None:
            return

        if object.info.format == FileFormat.Fasta and object.info.subset_separator in ['|', '.']:
            self.fasta_separator = object.info.subset_separator

        self.binder.bind(object.properties.has_subsets, self.properties.fasta_separator_visible)
        self.binder.bind(object.properties.has_extras, self.properties.fasta_concatenate_visible)

        self.binder.bind(object.properties.has_subsets, self._update_fasta_config_visible)
        self.binder.bind(object.properties.has_extras, self._update_fasta_config_visible)

    def _check_fasta_config_visible(self):
        if self.format != OutputFormat.Fasta:
            return False
        if any((
            self.fasta_separator_visible,
            self.fasta_concatenate_visible,
        )):
            return True
        return False

    def _update_fasta_config_visible(self):
        visible = self._check_fasta_config_visible()
        self.fasta_config_visible = visible


class Model(TaskModel):
    task_name = 'ConvPhase'

    request_confirmation = QtCore.Signal(object, object)

    input_sequences = Property(ImportedInputModel, ImportedInputModel(InputModel))
    parameters = Property(Parameters, Instance)

    output = Property(OutputModel, Instance)

    busy_main = Property(bool, False)
    busy_sequence = Property(bool, False)

    phased_results = Property(Path, None)
    phased_time = Property(float, None)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = True

        self.subtask_init = SubtaskModel(self, bind_busy=False)
        self.subtask_init.start(process.initialize)

        self.subtask_sequences = SequenceScanSubtaskModel(self)
        self.binder.bind(self.subtask_sequences.done, self.onDoneScanSequences)

        self.binder.bind(self.input_sequences.properties.object, self.output.set_input_object)

        self.binder.bind(self.input_sequences.updated, self.checkReady)
        self.checkReady()

    def isReady(self):
        if not self.input_sequences.is_valid():
            return False
        return True

    def start(self):
        super().start()
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        params = self.parameters.properties

        self.exec(
            process.execute,
            work_dir=work_dir,

            input_sequences=self.input_sequences.as_dict(),

            number_of_iterations=get_effective(params.number_of_iterations),
            thinning_interval=get_effective(params.thinning_interval),
            burn_in=get_effective(params.burn_in),
            phase_threshold=get_effective(params.phase_threshold),
            allele_threshold=get_effective(params.allele_threshold),
        )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f'{self.name} completed successfully!\nTime taken: {time_taken}.'))
        self.phased_results = report.result.output_path
        self.phased_time = report.result.seconds_taken
        self.busy_main = False
        self.busy = False
        self.done = True

    def onDoneScanSequences(self, result: ScanResults):
        info = result.info
        warns = result.warns

        if not warns:
            self.input_sequences.add_info(info)
        else:
            self.request_confirmation.emit(
                warns,
                lambda: self.input_sequences.add_info(info)
            )
        self.busy_sequence = False

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
        self.phased_results = None
        self.phased_time = None
        self.done = False

    def open(self, path):
        self.clear()
        self.subtask_sequences.start(path)

    def save(self, destination: Path):
        copyfile(self.phased_results, destination)
        self.notification.emit(Notification.Info('Saved file successfully!'))

    @property
    def suggested_results(self):
        info = self.input_sequences.object.info
        path = info.path
        extension = info.format.extension
        return path.parent / f'{path.stem}.phased{extension}'
