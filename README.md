# TaxiGui

A convenient phase program, combining _phase_ and _SeqPhase_.

This is a Qt GUI for [ConvPhase](https://github.com/iTaxoTools/ConvPhase).


### Windows and macOS Executables
Download and run the standalone executables without installing Python.</br>
[See the latest release here.](https://github.com/iTaxoTools/ConvPhaseGui/releases/latest)


### Installing from source
Clone and install the latest version (requires Python 3.10.2 or later):
```
git clone https://github.com/iTaxoTools/ConvPhaseGui.git
cd TaxIGui
pip install . -f packages.html
```


## Usage
To launch the GUI, please use:
```
convphase-gui
```


### Packaging

It is recommended to use PyInstaller from within a virtual environment:
```
pip install ".[dev]" -f packages.html
pyinstaller scripts/convphase.spec
```
