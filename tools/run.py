#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the ConvPhase GUI"""

import multiprocessing

from itaxotools.convphase_gui import run

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run()
