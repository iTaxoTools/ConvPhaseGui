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

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.common.widgets import VLineSeparator

from itaxotools.taxi_gui import app

from itaxotools.taxi_gui.utility import type_convert
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import TaskView
from itaxotools.taxi_gui.view.widgets import (
    GLineEdit, GSpinBox, NoWheelRadioButton, RadioButtonGroup, CategoryButton, LongLabel)

from itaxotools.taxi_gui.tasks.common.types import AlignmentMode, DistanceMetric, PairwiseScore
from itaxotools.taxi_gui.tasks.common.model import ItemProxyModel
from itaxotools.taxi_gui.tasks.common.view import (
    AlignmentModeSelector, DummyResultsCard, ProgressCard, SequenceSelector)

from .types import Parameter
from . import strings


class TitleCard(Card):
    def __init__(self, description, citations, parent=None):
        super().__init__(parent)

        description = LongLabel(strings.description)
        authors = LongLabel(strings.authors)
        authors.setStyleSheet("LongLabel {color: Palette(Dark)}")

        contents = QtWidgets.QVBoxLayout()
        contents.addWidget(description)
        contents.addWidget(authors)
        contents.setSpacing(2)

        homepage = QtWidgets.QPushButton('Homepage')
        itaxotools = QtWidgets.QPushButton('iTaxoTools')
        citations = QtWidgets.QPushButton('Citations')
        citations.setFixedWidth(154)

        homepage.clicked.connect(self.openHomepage)
        itaxotools.clicked.connect(self.openItaxotools)
        citations.clicked.connect(self.openCitations)

        buttons = QtWidgets.QVBoxLayout()
        buttons.addWidget(homepage)
        buttons.addWidget(itaxotools)
        buttons.addWidget(citations)
        buttons.addStretch(1)
        buttons.setSpacing(8)

        separator = VLineSeparator(1)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(buttons, 0)
        layout.addWidget(separator, 0)
        layout.addLayout(contents, 1)
        layout.setSpacing(16)
        self.addLayout(layout)

    def openHomepage(self):
        QtGui.QDesktopServices.openUrl(strings.homepage_url)

    def openCitations(self):
        dialog = CitationDialog(strings.citations, self.window())
        self.window().msgShow(dialog)

    def openItaxotools(self):
        QtGui.QDesktopServices.openUrl(strings.itaxotools_url)


class CitationDialog(QtWidgets.QDialog):
    def __init__(self, text, parent):
        super().__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(app.config.title + ' - ' + 'Citations')
        self.resize(400, 280)
        self.setModal(True)

        citations = QtWidgets.QPlainTextEdit()
        citations.setReadOnly(True)
        citations.setPlainText(strings.citations)
        citations.setStyleSheet("QPlainTextEdit {color: Palette(Dark)}")

        close = QtWidgets.QPushButton('Close')
        close.clicked.connect(self.reject)
        close.setDefault(True)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(close)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(citations)
        layout.addLayout(buttons)

        self.setLayout(layout)


class ResultViewer(Card):
    view = QtCore.Signal(str, Path)
    save = QtCore.Signal(str, Path)

    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.setContentsMargins(6, 2, 6, 2)
        self.text = label_text
        self.path = None

        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet("""font-size: 16px;""")

        check = QtWidgets.QLabel('\u2714')
        check.setStyleSheet("""font-size: 16px; color: Palette(Shadow);""")

        save = QtWidgets.QPushButton('Save')
        save.clicked.connect(self.handleSave)

        view = QtWidgets.QPushButton('View')
        view.clicked.connect(self.handleView)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(label)
        layout.addSpacing(12)
        layout.addWidget(check)
        layout.addStretch(1)
        layout.addWidget(save)
        layout.addSpacing(16)
        layout.addWidget(view)
        self.addLayout(layout)

        self.controls.view = view
        self.controls.save = save

    def setPath(self, path):
        self.path = path
        self.setVisible(path is not None)

    def handleView(self):
        self.view.emit(self.text, self.path)

    def handleSave(self):
        self.save.emit(self.text, self.path)


class ResultDialog(QtWidgets.QDialog):
    save = QtCore.Signal(Path)

    def __init__(self, text, path, parent):
        super().__init__(parent)
        self.path = path

        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(app.config.title + ' - ' + text)
        self.resize(460, 680)
        self.setModal(True)

        viewer = QtWidgets.QPlainTextEdit()
        viewer.setReadOnly(True)
        font = QtGui.QFont('monospace')
        font.setStyleHint(QtGui.QFont.Monospace)
        viewer.setFont(font)

        with open(path) as file:
            viewer.setPlainText(file.read())

        save = QtWidgets.QPushButton('Save')
        save.clicked.connect(self.handleSave)

        close = QtWidgets.QPushButton('Close')
        close.clicked.connect(self.reject)
        close.setDefault(True)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(save)
        buttons.addWidget(close)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(viewer)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def handleSave(self):
        self.save.emit(self.path)


class FastaSelector(SequenceSelector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(6, 2, 6, 2)
        self.controls.label.setMinimumWidth(168)
        self.controls.fasta.parse_organism.setVisible(False)
        self.controls.browse.setText('Browse')

    def set_model(self, combo, model):
        proxy_model = ItemProxyModel()
        proxy_model.setSourceModel(model, model.files)
        combo.setModel(proxy_model)

    def setObject(self, object):
        super().setObject(object)
        self.controls.config.setVisible(False)


class ParameterCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(6, 2, 6, 2)
        self.draw_title()
        self.draw_contents()

        self.controls.title.toggled.connect(self.handleToggled)
        self.setExpanded(True)

    def draw_title(self):
        title = CategoryButton('Parameters')
        title.setStyleSheet('font-size: 16px;')
        self.addWidget(title)

        self.controls.title = title

    def draw_contents(self):

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)
        layout.setColumnStretch(2, 1)
        layout.setColumnMinimumWidth(0, 168)
        row = 0

        int_validator = QtGui.QIntValidator(self)

        double_validator = QtGui.QDoubleValidator(self)
        locale = QtCore.QLocale.c()
        locale.setNumberOptions(QtCore.QLocale.RejectGroupSeparator)
        double_validator.setLocale(locale)
        double_validator.setBottom(0)
        double_validator.setTop(1)

        entries = {}

        for param in Parameter:
            label = QtWidgets.QLabel(param.label + ':')
            description = QtWidgets.QLabel(param.description)
            description.setStyleSheet("QLabel { font-style: italic; color: Palette(Shadow);}")

            entry = GLineEdit('')
            entry.setPlaceholderText(str(param.default))
            validator = int_validator if param.type == int else double_validator
            entry.setValidator(validator)
            entries[param.key] = entry

            layout.addWidget(label, row, 0)
            layout.addWidget(entry, row, 1)
            layout.addWidget(description, row, 2)
            row += 1

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)

        self.controls.contents = widget
        self.controls.entries = entries

    def setExpanded(self, expanded):
        self.controls.title.setChecked(expanded)
        self.controls.contents.setVisible(expanded)

    def handleToggled(self, checked):
        self.controls.contents.setVisible(checked)
        QtCore.QTimer.singleShot(10, self.update)

    def setContentsEnabled(self, enabled):
        self.controls.contents.setEnabled(enabled)
        color = 'Text' if enabled else 'Dark'
        self.controls.title.setStyleSheet(
            f'font-size: 16px; color: Palette({color});')


class View(TaskView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw()

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = TitleCard(
            'Use PHASE to reconstruct haplotypes from population genotype data. \n'
            'Input and output is done with FASTA files via SeqPhase.',
            'citations here',
            self)
        self.cards.results = ResultViewer('Phased results', self)
        self.cards.progress = ProgressCard(self)
        self.cards.input_sequences = FastaSelector('Input sequences', self)
        self.cards.parameters = ParameterCard(self)

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

        self.binder.bind(object.properties.busy_main, self.cards.progress.setEnabled)
        self.binder.bind(object.properties.busy_main, self.cards.progress.setVisible)
        self.binder.bind(object.properties.busy_sequence, self.cards.input_sequences.setBusy)

        self.binder.bind(self.cards.input_sequences.itemChanged, object.set_sequence_file_from_file_item)
        self.binder.bind(object.properties.input_sequences, self.cards.input_sequences.setObject)
        self.binder.bind(self.cards.input_sequences.addInputFile, object.add_sequence_file)

        self.binder.bind(object.properties.phased_results, self.cards.results.setPath)
        self.binder.bind(object.properties.phased_results, self.cards.results.setVisible, lambda x: x is not None)
        self.binder.bind(object.properties.phased_results, self.cards.parameters.setExpanded, lambda x: x is None)

        self.binder.bind(self.cards.results.view, self.view_results)
        self.binder.bind(self.cards.results.save, self.save_results)

        for param in Parameter:
            entry = self.cards.parameters.controls.entries[param.key]
            property = object.parameters.properties[param.key]
            self.binder.bind(entry.textEditedSafe, property, lambda x: type_convert(x, param.type, None))
            self.binder.bind(property, entry.setText, lambda x: type_convert(x, str, ''))

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        self.cards.title.setEnabled(True)
        self.cards.results.setEnabled(True)
        self.cards.progress.setEnabled(True)
        self.cards.input_sequences.setEnabled(editable)
        self.cards.parameters.setContentsEnabled(editable)

    def view_results(self, text, path):
        dialog = ResultDialog(text, path, self.window())
        dialog.save.connect(self.save_results)
        self.window().msgShow(dialog)

    def save_results(self):
        path = self.getSavePath('Save phased results', str(self.object.suggested_results))
        if path:
            self.object.save(path)

    def save(self):
        self.save_results()
