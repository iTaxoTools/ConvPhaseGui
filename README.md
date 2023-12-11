# ConvPhaseGui

[![PyPI - Version](https://img.shields.io/pypi/v/itaxotools-convphase-gui?color=tomato)](
    https://pypi.org/project/itaxotools-convphase-gui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/itaxotools-convphase-gui)](
    https://pypi.org/project/itaxotools-convphase-gui)
[![GitHub - Tests](https://img.shields.io/github/actions/workflow/status/iTaxoTools/ConvPhaseGui/test.yml?label=tests)](
    https://github.com/iTaxoTools/ConvPhaseGui/actions/workflows/test.yml)
[![GitHub - Windows](https://img.shields.io/github/actions/workflow/status/iTaxoTools/ConvPhaseGui/windows.yml?label=windows)](
    https://github.com/iTaxoTools/ConvPhaseGui/actions/workflows/windows.yml)
[![GitHub - macOS](https://img.shields.io/github/actions/workflow/status/iTaxoTools/ConvPhaseGui/macos.yml?label=macos)](
    https://github.com/iTaxoTools/ConvPhaseGui/actions/workflows/macos.yml)

Reconstruct haplotypes from sequence data. Input and output can be in TSV or FASTA format.

This is a Qt GUI for [ConvPhase](https://github.com/iTaxoTools/ConvPhase), a convenient phase program that combines [PHASE](https://github.com/stephens999/phase) and [SeqPHASE](https://github.com/eeg-ebe/SeqPHASE).

![Screenshot](https://raw.githubusercontent.com/iTaxoTools/ConvPhaseGui/v0.1.0/images/screenshot.png)

## Executables

Download and run the standalone executables without installing Python.

[![Release](https://img.shields.io/badge/release-0.2.0-red?style=for-the-badge)](
    https://github.com/iTaxoTools/ConvPhaseGui/releases/v0.2.0)
[![Windows](https://img.shields.io/badge/Windows-blue.svg?style=for-the-badge&logo=windows)](
    https://github.com/iTaxoTools/ConvPhaseGui/releases/download/v0.2.0/ConvPhase-0.2.0-windows-x64.exe)
[![MacOS](https://img.shields.io/badge/macOS-slategray.svg?style=for-the-badge&logo=apple)](
    https://github.com/iTaxoTools/ConvPhaseGui/releases/download/v0.2.0/ConvPhase-0.2.0-macos-universal2.dmg)

## Installation

ConvPhaseGui is available on PyPI. You can install it through `pip`:

```
pip install itaxotools-taxi-gui
convphase-gui
```

## Usage

For information on how to use the program, please refer to the 1st section of the [Hapsolutely manual](https://itaxotools.org/Hapsolutely_manual_07Nov2023.pdf).

### Packaging

It is recommended to use PyInstaller from within a virtual environment:
```
pip install ".[dev]" -f packages.html
pyinstaller scripts/convphase.spec
```

## Citations

*ConvPhaseGui* was developed in the framework of the *iTaxoTools* project:

*Vences M. et al. (2021): iTaxoTools 0.1: Kickstarting a specimen-based software toolkit for taxonomists. - Megataxa 6: 77-92.*

Sequences are phased using *PHASE* and *SeqPHASE*:

*Stephens, M., Smith, N., and Donnelly, P. (2001). A new statistical method for haplotype reconstruction from population data. American Journal of Human Genetics, 68, 978--989.*

*Stephens, M., and Donnelly, P. (2003). A comparison of Bayesian methods for haplotype reconstruction from population genotype data. American Journal of Human Genetics, 73:1162-1169.*

*Flot, J.F. (2010) seqphase: a web tool for interconverting phase input/output files and fasta sequence alignments. Mol. Ecol. Resour., 10, 162–166.*
