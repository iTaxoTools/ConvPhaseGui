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

from PySide6 import QtCore, QtGui, QtWidgets

from itaxotools.common.utility import AttrDict

from itaxotools.taxi_gui.utility import type_convert
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import TaskView
from itaxotools.taxi_gui.view.widgets import (
    GLineEdit, GSpinBox, NoWheelRadioButton, RadioButtonGroup)

from itaxotools.taxi_gui.tasks.common.types import AlignmentMode, DistanceMetric, PairwiseScore
from itaxotools.taxi_gui.tasks.common.model import ItemProxyModel
from itaxotools.taxi_gui.tasks.common.view import (
    AlignmentModeSelector, DummyResultsCard, ProgressCard, SequenceSelector,
    TitleCard)


class FastaSelector(SequenceSelector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controls.fasta.parse_organism.setVisible(False)
        self.controls.browse.setText('Open')

    def set_model(self, combo, model):
        proxy_model = ItemProxyModel()
        proxy_model.setSourceModel(model, model.files)
        combo.setModel(proxy_model)

    def setObject(self, object):
        super().setObject(object)
        self.controls.config.setVisible(False)


class View(TaskView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw()

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = TitleCard(
            'ConvPhase',
            'Use PHASE to reconstruct haplotypes from population genotype data. \n'
            'Input and output is done with FASTA files via SeqPhase.',
            self)
        self.cards.dummy_results = DummyResultsCard(self)
        self.cards.progress = ProgressCard(self)
        self.cards.input_sequences = FastaSelector('Input sequences', self)

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(layout)

    def setObject(self, object):
        self.object = object
        self.binder.unbind_all()

        self.binder.bind(object.notification, self.showNotification)
        self.binder.bind(object.progression, self.cards.progress.showProgress)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy_main, self.cards.title.setBusy)
        self.binder.bind(object.properties.busy_main, self.cards.progress.setEnabled)
        self.binder.bind(object.properties.busy_main, self.cards.progress.setVisible)
        self.binder.bind(object.properties.busy_sequence, self.cards.input_sequences.setBusy)

        self.binder.bind(self.cards.input_sequences.itemChanged, object.set_sequence_file_from_file_item)
        self.binder.bind(object.properties.input_sequences, self.cards.input_sequences.setObject)
        self.binder.bind(self.cards.input_sequences.addInputFile, object.add_sequence_file)

        self.binder.bind(object.properties.dummy_results, self.cards.dummy_results.setPath)
        self.binder.bind(object.properties.dummy_results, self.cards.dummy_results.setVisible, lambda x: x is not None)

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.cards.dummy_results.setEnabled(True)
        self.cards.progress.setEnabled(True)

    def save(self):
        path = self.getExistingDirectory('Save All')
        if path:
            self.object.save(path)
