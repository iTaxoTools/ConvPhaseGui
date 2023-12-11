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
from itaxotools.taxi_gui.tasks.common.view import InputSelector, ProgressCard
from itaxotools.taxi_gui.types import FileFormat
from itaxotools.taxi_gui.utility import human_readable_size
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import ScrollTaskView
from itaxotools.taxi_gui.view.widgets import (
    CategoryButton,
    LongLabel,
    MinimumStackedWidget,
    NoWheelComboBox,
    RadioButtonGroup,
    UnscrollableDoubleSpinBox,
    UnscrollableSpinBox,
)

from . import strings
from .types import OutputFormat, Parameter


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

        homepage = QtWidgets.QPushButton("Homepage")
        itaxotools = QtWidgets.QPushButton("iTaxoTools")
        citations = QtWidgets.QPushButton("Citations")
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
        self.setWindowTitle(app.config.title + " - " + "Citations")
        self.resize(400, 280)
        self.setModal(True)

        citations = QtWidgets.QPlainTextEdit()
        citations.setReadOnly(True)
        citations.setPlainText(strings.citations)
        citations.setStyleSheet("QPlainTextEdit {color: Palette(Shadow)}")

        close = QtWidgets.QPushButton("Close")
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

        check = QtWidgets.QLabel("\u2714")
        check.setStyleSheet("""font-size: 16px; color: Palette(Shadow);""")
        font = check.font()
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        check.setFont(font)

        cross = QtWidgets.QLabel("\u2718")
        cross.setStyleSheet("""font-size: 16px; color: Palette(Shadow);""")
        font = cross.font()
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        cross.setFont(font)

        save = QtWidgets.QPushButton("Save")
        save.clicked.connect(self.handleSave)

        view = QtWidgets.QPushButton("View")
        view.clicked.connect(self.handleView)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(label)
        layout.addSpacing(12)
        layout.addWidget(check)
        layout.addWidget(cross)
        layout.addStretch(1)
        layout.addWidget(save)
        layout.addSpacing(16)
        layout.addWidget(view)
        self.addLayout(layout)

        self.controls.view = view
        self.controls.save = save
        self.controls.check = check
        self.controls.cross = cross

    def setPath(self, path):
        self.path = path
        self.setVisible(path is not None)

    def handleView(self):
        self.view.emit(self.text, self.path)

    def handleSave(self):
        self.save.emit(self.text, self.path)


class WarningViewer(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(6, 2, 6, 2)

        arrow = QtWidgets.QLabel("\u2937")
        arrow.setStyleSheet("padding-bottom: 4px;")
        font = arrow.font()
        font.setBold(True)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        arrow.setFont(font)

        arrow_layout = QtWidgets.QVBoxLayout()
        arrow_layout.addWidget(arrow)
        arrow_layout.addStretch(1)

        warning = LongLabel("WARNING GOES HERE")
        explanation = LongLabel(strings.ambiguity)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.setSpacing(4)
        title_layout.addLayout(arrow_layout)
        title_layout.addWidget(warning, 1)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(12)
        layout.addLayout(title_layout)
        layout.addWidget(explanation)

        self.addLayout(layout)

        self.warning = warning


class ResultDialog(QtWidgets.QDialog):
    save = QtCore.Signal(Path)

    def __init__(self, text, path, parent):
        super().__init__(parent)
        self.path = path

        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(app.config.title + " - " + text)
        self.resize(520, 680)
        self.setModal(True)

        viewer = QtWidgets.QPlainTextEdit()
        viewer.setReadOnly(True)
        font = QtGui.QFont("monospace")
        font.setStyleHint(QtGui.QFont.Monospace)
        viewer.setFont(font)

        with open(path) as file:
            viewer.setPlainText(file.read())

        save = QtWidgets.QPushButton("Save")
        save.clicked.connect(self.handleSave)

        close = QtWidgets.QPushButton("Close")
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


class InputSequencesSelector(InputSelector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(6, 2, 6, 2)
        self.controls.label.setMinimumWidth(168)
        self.controls.browse.setText("Browse")

    def draw_config(self):
        self.controls.config = MinimumStackedWidget()
        self.addWidget(self.controls.config)
        self.draw_config_tabfile()
        self.draw_config_fasta()

    def draw_config_tabfile(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        column = 0

        type_label = QtWidgets.QLabel("File format:")
        size_label = QtWidgets.QLabel("File size:")

        layout.addWidget(type_label, 0, column)
        layout.addWidget(size_label, 1, column)
        layout.setColumnMinimumWidth(column, 70)
        column += 1

        layout.setColumnMinimumWidth(column, 8)
        column += 1

        type_label_value = QtWidgets.QLabel("Tabfile")
        size_label_value = QtWidgets.QLabel("42 MB")

        layout.addWidget(type_label_value, 0, column)
        layout.addWidget(size_label_value, 1, column)
        layout.setColumnMinimumWidth(column, 60)
        column += 1

        layout.setColumnMinimumWidth(column, 32)
        column += 1

        index_label = QtWidgets.QLabel("Indices:")
        sequence_label = QtWidgets.QLabel("Sequences:")
        subset_label = QtWidgets.QLabel("Subset:")

        layout.addWidget(index_label, 0, column)
        layout.addWidget(sequence_label, 1, column)
        layout.addWidget(subset_label, 2, column)
        column += 1

        layout.setColumnMinimumWidth(column, 8)
        column += 1

        index_combo = NoWheelComboBox()
        sequence_combo = NoWheelComboBox()
        subset_combo = NoWheelComboBox()

        layout.addWidget(index_combo, 0, column)
        layout.addWidget(sequence_combo, 1, column)
        layout.addWidget(subset_combo, 2, column)
        layout.setColumnStretch(column, 1)
        column += 1

        layout.setColumnMinimumWidth(column, 16)
        column += 1

        view = QtWidgets.QPushButton("View")
        view.setVisible(False)

        layout.addWidget(view, 0, column)
        layout.setColumnMinimumWidth(column, 80)
        column += 1

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.controls.tabfile = AttrDict()
        self.controls.tabfile.widget = widget
        self.controls.tabfile.index_combo = index_combo
        self.controls.tabfile.sequence_combo = sequence_combo
        self.controls.tabfile.subset_combo = subset_combo
        self.controls.tabfile.file_size = size_label_value
        self.controls.config.addWidget(widget)

    def draw_config_fasta(self):
        type_label = QtWidgets.QLabel("File format:")
        size_label = QtWidgets.QLabel("File size:")

        type_label_value = QtWidgets.QLabel("Fasta")
        size_label_value = QtWidgets.QLabel("42 MB")

        parse_organism = QtWidgets.QCheckBox(
            'Parse identifiers as "individual|organism"'
        )

        view = QtWidgets.QPushButton("View")
        view.setVisible(False)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(type_label)
        layout.addWidget(type_label_value)
        layout.addSpacing(48)
        layout.addWidget(size_label)
        layout.addWidget(size_label_value)
        layout.addSpacing(48)
        layout.addWidget(parse_organism)
        layout.addStretch(1)
        layout.addWidget(view)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.controls.fasta = AttrDict()
        self.controls.fasta.widget = widget
        self.controls.fasta.file_size = size_label_value
        self.controls.fasta.parse_organism = parse_organism
        self.controls.config.addWidget(widget)

    def bind_object(self, object):
        self.binder.unbind_all()
        format = object.info.format if object else None
        {
            FileFormat.Tabfile: self._bind_tabfile,
            FileFormat.Fasta: self._bind_fasta,
            None: self._bind_none,
        }[format](object)
        self.update()

    def _bind_tabfile(self, object):
        self._populate_headers(object.info.headers)
        self.binder.bind(
            object.properties.index_column,
            self.controls.tabfile.index_combo.setCurrentIndex,
        )
        self.binder.bind(
            self.controls.tabfile.index_combo.currentIndexChanged,
            object.properties.index_column,
        )
        self.binder.bind(
            object.properties.sequence_column,
            self.controls.tabfile.sequence_combo.setCurrentIndex,
        )
        self.binder.bind(
            self.controls.tabfile.sequence_combo.currentIndexChanged,
            object.properties.sequence_column,
        )
        self.binder.bind(
            object.properties.subset_column,
            self.controls.tabfile.subset_combo.setCurrentIndex,
            lambda index: index + 1,
        )
        self.binder.bind(
            self.controls.tabfile.subset_combo.currentIndexChanged,
            object.properties.subset_column,
            lambda index: index - 1,
        )
        self.binder.bind(
            object.properties.info,
            self.controls.tabfile.file_size.setText,
            lambda info: human_readable_size(info.size),
        )
        self.controls.config.setCurrentWidget(self.controls.tabfile.widget)
        self.controls.config.setVisible(True)

    def _bind_fasta(self, object):
        self.binder.bind(
            object.properties.file_has_subsets,
            self.controls.fasta.parse_organism.setVisible,
        )
        self.binder.bind(
            object.properties.parse_organism,
            self.controls.fasta.parse_organism.setChecked,
        )
        self.binder.bind(
            self.controls.fasta.parse_organism.toggled, object.properties.parse_organism
        )
        self.binder.bind(
            object.properties.subset_separator,
            self.controls.fasta.parse_organism.setText,
            lambda x: f'Parse identifiers as "individual{x or "/"}organism"',
        )
        self.binder.bind(
            object.properties.info,
            self.controls.fasta.file_size.setText,
            lambda info: human_readable_size(info.size),
        )
        self.controls.config.setCurrentWidget(self.controls.fasta.widget)
        self.controls.config.setVisible(True)

    def _bind_none(self, object):
        self.controls.config.setVisible(False)

    def _populate_headers(self, headers):
        self.controls.tabfile.index_combo.clear()
        self.controls.tabfile.sequence_combo.clear()
        self.controls.tabfile.subset_combo.clear()
        self.controls.tabfile.subset_combo.addItem("---", None)
        for header in headers:
            self.controls.tabfile.index_combo.addItem(header)
            self.controls.tabfile.sequence_combo.addItem(header)
            self.controls.tabfile.subset_combo.addItem(header, header)


class OutputFormatCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(6, 2, 6, 2)
        self.draw_title()
        self.draw_fasta_config()

    def draw_title(self):
        title = QtWidgets.QLabel("Output format:")
        title.setStyleSheet("font-size: 16px;")
        title.setFixedWidth(160)

        radio_tabfile = QtWidgets.QRadioButton("Tabfile")
        radio_fasta = QtWidgets.QRadioButton("Fasta")
        radio_mimic = QtWidgets.QRadioButton("Same as input")

        group = RadioButtonGroup()
        group.add(radio_tabfile, OutputFormat.Tabfile)
        group.add(radio_fasta, OutputFormat.Fasta)
        group.add(radio_mimic, OutputFormat.Mimic)

        radios = QtWidgets.QHBoxLayout()
        radios.addWidget(radio_tabfile, 1)
        radios.addWidget(radio_fasta, 1)
        radios.addWidget(radio_mimic, 1)
        radios.addStretch(1)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 4)
        layout.addWidget(title)
        layout.addLayout(radios, 1)
        layout.addSpacing(100)

        self.controls.format = group

        self.addLayout(layout)

    def draw_fasta_config(self):
        radio_label = QtWidgets.QLabel("Subset separator:")
        radio_label.setFixedWidth(178)

        radio_pipe = QtWidgets.QRadioButton("Pipe: individual|subset")
        radio_period = QtWidgets.QRadioButton("Period: individual.subset")

        group = RadioButtonGroup()
        group.add(radio_pipe, "|")
        group.add(radio_period, ".")

        radios = QtWidgets.QHBoxLayout()
        radios.setContentsMargins(0, 0, 0, 0)
        radios.addWidget(radio_label)
        radios.addWidget(radio_pipe, 1)
        radios.addWidget(radio_period, 1)
        radios.addStretch(0.66)
        radios.addSpacing(60)

        radio_widget = QtWidgets.QWidget()
        radio_widget.setLayout(radios)
        radio_widget.roll = VerticalRollAnimation(radio_widget)

        check_concatenate_extras = QtWidgets.QCheckBox(
            "  Concatenate all extra fields into fasta identifier"
        )
        check_concatenate_extras.roll = VerticalRollAnimation(check_concatenate_extras)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(radio_widget)
        layout.addWidget(check_concatenate_extras)
        layout.setSpacing(10)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)

        self.controls.separator = group
        self.controls.separators = radio_widget
        self.controls.concatenate = check_concatenate_extras
        self.controls.fasta = widget

        self.addWidget(widget)


class ParameterCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(6, 2, 6, 2)
        self.draw_title()
        self.draw_contents()

        self.controls.title.toggled.connect(self.handleToggled)
        self.setExpanded(True)

    def draw_title(self):
        title = CategoryButton("Parameters")
        title.setStyleSheet("font-size: 16px;")
        self.addWidget(title)

        self.controls.title = title

    def draw_contents(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 3)
        layout.setColumnMinimumWidth(0, 168)
        row = 0

        entries = {}

        for param in Parameter:
            label = QtWidgets.QLabel(param.label + ":")
            description = QtWidgets.QLabel(param.description)
            description.setStyleSheet(
                "QLabel { font-style: italic; color: Palette(Shadow);}"
            )

            entry = (
                self.get_int_entry() if param.type is int else self.get_float_entry()
            )
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

    def get_int_entry(self):
        entry = UnscrollableSpinBox()
        entry.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        entry.setMinimumWidth(100)
        entry.setMinimum(0)
        entry.setMaximum(999999)
        entry.setSingleStep(1)
        return entry

    def get_float_entry(self):
        entry = UnscrollableDoubleSpinBox()
        entry.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        entry.setMinimumWidth(100)
        entry.setMinimum(0.0)
        entry.setMaximum(1.0)
        entry.setSingleStep(0.05)
        return entry

    def setExpanded(self, expanded):
        self.controls.title.setChecked(expanded)
        self.controls.contents.setVisible(expanded)

    def handleToggled(self, checked):
        self.controls.contents.setVisible(checked)
        self.update()

    def setContentsEnabled(self, enabled):
        self.controls.contents.setEnabled(enabled)
        color = "Text" if enabled else "Dark"
        self.controls.title.setStyleSheet(f"font-size: 16px; color: Palette({color});")


class View(ScrollTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw()

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = TitleCard(
            "Use PHASE to reconstruct haplotypes from population genotype data. \n"
            "Input and output is done with FASTA files via SeqPhase.",
            "citations here",
            self,
        )
        self.cards.results = ResultViewer("Phased sequences", self)
        self.cards.warnings = WarningViewer(self)
        self.cards.progress_matrix = ProgressCard(self)
        self.cards.progress_mcmc = ProgressCard(self)
        self.cards.input_sequences = InputSequencesSelector("Input sequences", self)
        self.cards.output_format = OutputFormatCard(self)
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
        self.binder.bind(object.request_confirmation, self.requestConfirmation)
        self.binder.bind(
            object.progression,
            self.cards.progress_matrix.showProgress,
            condition=lambda x: "matrix" in x.text,
        )
        self.binder.bind(
            object.progression,
            self.cards.progress_mcmc.showProgress,
            condition=lambda x: "MCMC" in x.text,
        )
        self.binder.bind(object.properties.busy, self.cards.progress_matrix.setEnabled)
        self.binder.bind(object.properties.busy, self.cards.progress_matrix.setVisible)
        self.binder.bind(object.properties.busy, self.cards.progress_mcmc.setEnabled)
        self.binder.bind(object.properties.busy, self.cards.progress_mcmc.setVisible)

        self.binder.bind(
            object.subtask_sequences.properties.busy,
            self.cards.input_sequences.set_busy,
        )

        self._bind_input_selector(
            self.cards.input_sequences, object.input_sequences, object.subtask_sequences
        )

        self.binder.bind(object.properties.phased_path, self.cards.results.setPath)
        self.binder.bind(
            object.properties.phased_path,
            self.cards.results.setVisible,
            lambda x: x is not None,
        )
        self.binder.bind(
            object.properties.phased_path,
            self.cards.parameters.setExpanded,
            lambda x: x is None,
        )
        self.binder.bind(
            object.properties.phased_ambiguous,
            self.cards.results.controls.check.setVisible,
            lambda x: not x,
        )
        self.binder.bind(
            object.properties.phased_ambiguous,
            self.cards.results.controls.cross.setVisible,
        )
        self.binder.bind(
            object.properties.phased_ambiguous, self.cards.warnings.setVisible
        )
        self.binder.bind(
            object.properties.phased_warning, self.cards.warnings.warning.setText
        )

        self.binder.bind(
            object.output_options.properties.format,
            self.cards.output_format.controls.format.setValue,
        )
        self.binder.bind(
            self.cards.output_format.controls.format.valueChanged,
            object.output_options.properties.format,
        )
        self.binder.bind(
            object.output_options.properties.fasta_separator,
            self.cards.output_format.controls.separator.setValue,
        )
        self.binder.bind(
            self.cards.output_format.controls.separator.valueChanged,
            object.output_options.properties.fasta_separator,
        )
        self.binder.bind(
            object.output_options.properties.fasta_concatenate,
            self.cards.output_format.controls.concatenate.setChecked,
        )
        self.binder.bind(
            self.cards.output_format.controls.concatenate.toggled,
            object.output_options.properties.fasta_concatenate,
        )

        self.binder.bind(
            object.output_options.properties.fasta_separator_visible,
            self.cards.output_format.controls.separators.roll.setAnimatedVisible,
        )
        self.binder.bind(
            object.output_options.properties.fasta_concatenate_visible,
            self.cards.output_format.controls.concatenate.roll.setAnimatedVisible,
        )
        self.binder.bind(
            object.output_options.properties.fasta_config_visible,
            self.cards.output_format.controls.fasta.roll.setAnimatedVisible,
        )

        self.binder.bind(self.cards.results.view, self.view_results)
        self.binder.bind(self.cards.results.save, self.save_results)

        for param in Parameter:
            self._bind_param_field(param, object)

        # defined last to override `set_busy` calls
        self.binder.bind(object.properties.editable, self.setEditable)

    def _bind_input_selector(self, card, object, subtask):
        self.binder.bind(card.addInputFile, subtask.start)
        self.binder.bind(card.indexChanged, object.set_index)
        self.binder.bind(object.properties.model, card.set_model)
        self.binder.bind(object.properties.index, card.set_index)
        self.binder.bind(object.properties.object, card.bind_object)

    def _bind_param_field(self, param, object):
        entry = self.cards.parameters.controls.entries[param.key]
        property = object.parameters.properties[param.key]
        self.binder.bind(entry.valueChanged, property)
        self.binder.bind(property, entry.setValue)

    def requestConfirmation(self, warns, callback, abort):
        msgBox = QtWidgets.QMessageBox(self.window())
        msgBox.setWindowTitle(f"{app.config.title} - Warning")
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)

        text = (
            "Problems detected with input file: \n\n"
            + "\n".join("- " + str(warn) for warn in warns)
            + "\n\n"
            "The program may crash or produce false results. \n"
            "Proceed anyway?"
        )
        msgBox.setText(text)

        result = self.window().msgShow(msgBox)
        if result == QtWidgets.QMessageBox.Ok:
            callback()
        else:
            abort()

    def setEditable(self, editable: bool):
        self.cards.title.setEnabled(True)
        self.cards.results.setEnabled(True)
        self.cards.progress_matrix.setEnabled(True)
        self.cards.progress_mcmc.setEnabled(True)
        self.cards.input_sequences.setEnabled(editable)
        self.cards.output_format.setEnabled(editable)
        self.cards.parameters.setContentsEnabled(editable)

    def view_results(self, text, path):
        dialog = ResultDialog(text, path, self.window())
        dialog.save.connect(self.save_results)
        self.window().msgShow(dialog)

    def save_results(self):
        dir = str(self.object.suggested_results)
        format = self.object.get_output_format()
        filter = f"{format.label} (*{format.extension})"
        path = self.getSavePath("Save phased sequences", dir=dir, filter=filter)
        if path:
            self.object.save(path)

    def save(self):
        self.save_results()
