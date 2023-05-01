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
from itaxotools.taxi_gui.tasks.common.view import (
    AlignmentModeSelector, DummyResultsCard, ProgressCard, SequenceSelector,
    TitleCard)


class DistanceMetricSelector(Card):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_main()
        self.draw_file_type()
        self.draw_format()

    def draw_main(self):
        label = QtWidgets.QLabel('Distance metric')
        label.setStyleSheet("""font-size: 16px;""")

        description = QtWidgets.QLabel(
            'Select the type of distances that should be calculated for each pair of sequences:')
        description.setWordWrap(True)

        metrics = QtWidgets.QGridLayout()
        metrics.setContentsMargins(0, 0, 0, 0)
        metrics.setSpacing(8)

        metric_p = NoWheelRadioButton('Uncorrected (p-distance)')
        metric_pg = NoWheelRadioButton('Uncorrected with gaps')
        metric_jc = NoWheelRadioButton('Jukes Cantor (jc)')
        metric_k2p = NoWheelRadioButton('Kimura 2-Parameter (k2p)')
        metrics.addWidget(metric_p, 0, 0)
        metrics.addWidget(metric_pg, 1, 0)
        metrics.setColumnStretch(0, 2)
        metrics.setColumnMinimumWidth(1, 16)
        metrics.setColumnStretch(1, 0)
        metrics.addWidget(metric_jc, 0, 2)
        metrics.addWidget(metric_k2p, 1, 2)
        metrics.setColumnStretch(2, 2)

        metric_ncd = NoWheelRadioButton('Normalized Compression Distance (NCD)')
        metric_bbc = NoWheelRadioButton('Base-Base Correlation (BBC)')

        metric_bbc_k_label = QtWidgets.QLabel('BBC k parameter:')
        metric_bbc_k_field = GLineEdit('10')

        metric_bbc_k = QtWidgets.QHBoxLayout()
        metric_bbc_k.setContentsMargins(0, 0, 0, 0)
        metric_bbc_k.setSpacing(8)
        metric_bbc_k.addWidget(metric_bbc_k_label)
        metric_bbc_k.addSpacing(16)
        metric_bbc_k.addWidget(metric_bbc_k_field, 1)

        metrics_free = QtWidgets.QGridLayout()
        metrics_free.setContentsMargins(0, 0, 0, 0)
        metrics_free.setSpacing(8)

        metrics_free.addWidget(metric_ncd, 0, 0)
        metrics_free.addWidget(metric_bbc, 1, 0)
        metrics_free.setColumnStretch(0, 2)
        metrics_free.setColumnMinimumWidth(1, 16)
        metrics_free.setColumnStretch(1, 0)
        metrics_free.addLayout(metric_bbc_k, 1, 2)
        metrics_free.setColumnStretch(2, 2)

        metrics_all = QtWidgets.QVBoxLayout()
        metrics_all.addLayout(metrics)
        metrics_all.addLayout(metrics_free)
        metrics_all.setContentsMargins(0, 0, 0, 0)
        metrics_all.setSpacing(8)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(description)
        layout.addLayout(metrics_all)
        layout.setSpacing(16)

        group = RadioButtonGroup()
        group.add(metric_p, DistanceMetric.Uncorrected)
        group.add(metric_pg, DistanceMetric.UncorrectedWithGaps)
        group.add(metric_jc, DistanceMetric.JukesCantor)
        group.add(metric_k2p, DistanceMetric.Kimura2Parameter)
        group.add(metric_ncd, DistanceMetric.NCD)
        group.add(metric_bbc, DistanceMetric.BBC)

        self.controls.group = group
        self.controls.metrics = AttrDict()
        self.controls.metrics.p = metric_p
        self.controls.metrics.pg = metric_pg
        self.controls.metrics.jc = metric_jc
        self.controls.metrics.k2p = metric_k2p
        self.controls.metrics.ncd = metric_ncd
        self.controls.metrics.bbc = metric_bbc

        self.controls.bbc_k = metric_bbc_k_field
        self.controls.bbc_k_label = metric_bbc_k_label

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)

    def draw_file_type(self):
        write_linear = QtWidgets.QCheckBox('Write distances in linear format (all metrics in the same file)')
        write_matricial = QtWidgets.QCheckBox('Write distances in matricial format (one metric per matrix file)')

        self.controls.write_linear = write_linear
        self.controls.write_matricial = write_matricial

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(write_linear)
        layout.addWidget(write_matricial)
        layout.setSpacing(8)
        self.addLayout(layout)

    def draw_format(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        unit_radio = QtWidgets.QRadioButton('Distances from 0.0 to 1.0')
        percent_radio = QtWidgets.QRadioButton('Distances as percentages (%)')

        percentile = RadioButtonGroup()
        percentile.add(unit_radio, False)
        percentile.add(percent_radio, True)

        layout.addWidget(unit_radio, 0, 0)
        layout.addWidget(percent_radio, 1, 0)
        layout.setColumnStretch(0, 2)

        layout.setColumnMinimumWidth(1, 16)
        layout.setColumnStretch(1, 0)

        precision_label = QtWidgets.QLabel('Decimal precision:')
        missing_label = QtWidgets.QLabel('Not-Available symbol:')

        layout.addWidget(precision_label, 0, 2)
        layout.addWidget(missing_label, 1, 2)

        layout.setColumnMinimumWidth(3, 16)

        precision = GLineEdit('4')
        missing = GLineEdit('NA')

        self.controls.percentile = percentile
        self.controls.precision = precision
        self.controls.missing = missing

        layout.addWidget(precision, 0, 4)
        layout.addWidget(missing, 1, 4)
        layout.setColumnStretch(4, 2)

        self.addLayout(layout)

    def setAlignmentMode(self, mode):
        pairwise = bool(mode == AlignmentMode.PairwiseAlignment)
        self.controls.metrics.ncd.setVisible(not pairwise)
        self.controls.metrics.bbc.setVisible(not pairwise)
        self.controls.bbc_k.setVisible(not pairwise)
        self.controls.bbc_k_label.setVisible(not pairwise)
        free = bool(mode == AlignmentMode.AlignmentFree)
        self.controls.metrics.p.setVisible(not free)
        self.controls.metrics.pg.setVisible(not free)
        self.controls.metrics.jc.setVisible(not free)
        self.controls.metrics.k2p.setVisible(not free)


class SimilarityThresholdCard(Card):

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel('Similarity Threshold')
        label.setStyleSheet("""font-size: 16px;""")

        threshold = GLineEdit()
        threshold.setFixedWidth(80)

        validator = QtGui.QDoubleValidator(threshold)
        locale = QtCore.QLocale.c()
        locale.setNumberOptions(QtCore.QLocale.RejectGroupSeparator)
        validator.setLocale(locale)
        validator.setBottom(0)
        validator.setTop(1)
        validator.setDecimals(2)
        threshold.setValidator(validator)

        description = QtWidgets.QLabel(
            'Sequence pairs for which the computed distance is below '
            'this threshold will be considered similar and will be truncated.')
        description.setWordWrap(True)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(threshold, 0, 1)
        layout.addWidget(description, 1, 0)
        layout.setColumnStretch(0, 1)
        layout.setHorizontalSpacing(20)
        layout.setSpacing(8)
        self.addLayout(layout)

        self.controls.similarityThreshold = threshold


class IdentityThresholdCard(Card):

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel('Identity Threshold')
        label.setStyleSheet("""font-size: 16px;""")

        threshold = GSpinBox()
        threshold.setMinimum(0)
        threshold.setMaximum(100)
        threshold.setSingleStep(1)
        threshold.setSuffix('%')
        threshold.setValue(97)
        threshold.setFixedWidth(80)

        description = QtWidgets.QLabel(
            'Sequence pairs with an identity above '
            'this threshold will be considered similar and will be truncated.')
        description.setWordWrap(True)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(threshold, 0, 1)
        layout.addWidget(description, 1, 0)
        layout.setColumnStretch(0, 1)
        layout.setHorizontalSpacing(20)
        layout.setSpacing(8)
        self.addLayout(layout)

        self.controls.identityThreshold = threshold


class LengthThresholdCard(Card):

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel('Length Threshold')
        label.setStyleSheet("""font-size: 16px;""")

        threshold = GLineEdit('0')
        threshold.setFixedWidth(80)

        validator = QtGui.QIntValidator(threshold)
        validator.setBottom(0)
        threshold.setValidator(validator)

        description = QtWidgets.QLabel('Sequences with length below this threshold will be ignored.')
        description.setWordWrap(True)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(threshold, 0, 1)
        layout.addWidget(description, 1, 0)
        layout.setColumnStretch(0, 1)
        layout.setHorizontalSpacing(20)
        layout.setSpacing(8)
        self.addLayout(layout)

        self.controls.lengthThreshold = threshold


class View(TaskView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw()

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = TitleCard(
            'ConvPhase',
            'Use PHASE to reconstruct haplotypes from population genotype data. '
            'Input and output is done with FASTA files via SeqPhase. ',
            self)
        self.cards.dummy_results = DummyResultsCard(self)
        self.cards.progress = ProgressCard(self)
        self.cards.input_sequences = SequenceSelector('Input sequences', self)

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
