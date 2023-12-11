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
    Binder,
    EnumObject,
    Instance,
    Property,
    PropertyObject,
)
from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui.loop import DataQuery
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel
from itaxotools.taxi_gui.tasks.common.model import (
    FileInfoSubtaskModel,
    ImportedInputModel,
)
from itaxotools.taxi_gui.types import FileFormat, FileInfo, Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from . import process
from .input import InputModel
from .types import OutputFormat, Parameter


class Parameters(EnumObject):
    enum = Parameter

    def as_dict(self):
        return AttrDict({p.key: self._get_effective(p) for p in self.properties})

    @staticmethod
    def _get_effective(property):
        if property.value is None:
            return property.default
        return property.value


class OutputOptionsModel(PropertyObject):
    format = Property(OutputFormat, OutputFormat.Mimic)

    fasta_separator = Property(str, "|")
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

        if object.info.format == FileFormat.Fasta and object.info.subset_separator in [
            "|",
            ".",
        ]:
            self.fasta_separator = object.info.subset_separator

        self.binder.bind(
            object.properties.has_subsets, self.properties.fasta_separator_visible
        )
        self.binder.bind(
            object.properties.has_extras, self.properties.fasta_concatenate_visible
        )

        self.binder.bind(
            object.properties.has_subsets, self._update_fasta_config_visible
        )
        self.binder.bind(
            object.properties.has_extras, self._update_fasta_config_visible
        )

    def _check_fasta_config_visible(self):
        if self.format != OutputFormat.Fasta:
            return False
        if any(
            (
                self.fasta_separator_visible,
                self.fasta_concatenate_visible,
            )
        ):
            return True
        return False

    def _update_fasta_config_visible(self):
        visible = self._check_fasta_config_visible()
        self.fasta_config_visible = visible

    def as_dict(self):
        return AttrDict({p.key: p.value for p in self.properties})


class Model(TaskModel):
    task_name = "ConvPhase"

    request_confirmation = QtCore.Signal(object, object, object)

    input_sequences = Property(ImportedInputModel, ImportedInputModel(InputModel))
    parameters = Property(Parameters, Instance)

    output_options = Property(OutputOptionsModel, Instance)

    phased_path = Property(Path, None)
    phased_info = Property(FileInfo, None)
    phased_time = Property(float, None)

    phased_ambiguous = Property(bool, False)
    phased_warning = Property(str, "")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = True

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        self.subtask_sequences = FileInfoSubtaskModel(self)
        self.binder.bind(self.subtask_sequences.done, self.input_sequences.add_info)

        self.binder.bind(
            self.input_sequences.properties.object, self.output_options.set_input_object
        )
        self.binder.bind(self.input_sequences.notification, self.notification)

        self.binder.bind(self.query, self.on_query)

        self.binder.bind(self.input_sequences.updated, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input_sequences.is_valid():
            return False
        return True

    def start(self):
        super().start()
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,
            input_sequences=self.input_sequences.as_dict(),
            output_options=self.output_options.as_dict(),
            parameters=self.parameters.as_dict(),
        )

    def on_query(self, query: DataQuery):
        warns = query.data
        if not warns:
            self.answer(True)
        else:
            self.request_confirmation.emit(
                warns,
                lambda: self.answer(True),
                lambda: self.answer(False),
            )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        if report.result.ambiguous:
            self.notification.emit(
                Notification.Warn(
                    f"{self.name} completed with warnings!\nTime taken: {time_taken}."
                )
            )
        else:
            self.notification.emit(
                Notification.Info(
                    f"{self.name} completed sucessfully!\nTime taken: {time_taken}."
                )
            )
        self.phased_info = report.result.output_info
        self.phased_path = report.result.output_info.path
        self.phased_time = report.result.seconds_taken
        self.phased_ambiguous = report.result.ambiguous
        self.phased_warning = report.result.warning
        self.busy = False
        self.done = True

    def clear(self):
        self.phased_info = None
        self.phased_path = None
        self.phased_time = None
        self.phased_ambiguous = False
        self.phased_warning = ""
        self.done = False

    def open(self, path):
        self.clear()
        self.subtask_sequences.start(path)

    def save(self, destination: Path):
        copyfile(self.phased_path, destination)
        self.notification.emit(Notification.Info("Saved file successfully!"))

    def get_output_format(self):
        match self.output_options.format:
            case OutputFormat.Mimic:
                return self.input_sequences.object.info.format
            case OutputFormat.Fasta:
                return FileFormat.Fasta
            case OutputFormat.Tabfile:
                return FileFormat.Tabfile

    @property
    def suggested_results(self):
        format = self.get_output_format()
        path = self.input_sequences.object.info.path
        return path.parent / f"{path.stem}_phased{format.extension}"
