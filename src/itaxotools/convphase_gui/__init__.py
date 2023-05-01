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

"""GUI entry point"""


def load_resources():

    from PySide6 import QtGui, QtCore

    from itaxotools.common.resources import get_local
    from itaxotools.common.widgets import VectorPixmap
    from itaxotools.taxi_gui.app import resources, skin

    root = __package__
    resources.icons.app = lambda: QtGui.QIcon(
        get_local(root, 'logos/convphase.ico'))
    resources.pixmaps.logo_tool = lambda: VectorPixmap(
        get_local(root, 'logos/convphase.svg'),
        size=QtCore.QSize(192, 48),
        colormap=skin.colormap_icon)


def run():
    """
    Show the Taxi2 window and enter the main event loop.
    Imports are done locally to optimize multiprocessing.
    """

    from itaxotools.taxi_gui.app import Application, skin
    from itaxotools.taxi_gui.main import Main

    from . import config

    app = Application()
    app.set_config(config)
    app.set_skin(skin)

    load_resources()

    main = Main()
    main.widgets.header.toolLogo.setFixedWidth(192)
    main.show()

    app.exec()
