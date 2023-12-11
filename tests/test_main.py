from unittest.mock import patch

from itaxotools.convphase_gui import task as convphase
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.main import Main


def test_main(qapp):
    with patch("itaxotools.taxi_gui.main.dashboard.DashboardLegacy.addTaskIfNew"):
        # this avoids instantiating the model, which is currently untestable
        Main()


def test_convphase(qapp):
    task = app.Task.from_module(convphase)
    # task.model()
    task.view()
