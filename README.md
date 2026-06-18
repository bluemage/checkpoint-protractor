# Checkpoint Protractor

A transparent, always-on-top protractor overlay for Linux. Measure angles anywhere on your screen.
“Our opponent is an alien starship packed with atomic bombs," I said. "We have a protractor.”
― Neal Stephenson, Anathem 

![Python 3](https://img.shields.io/badge/python-3-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- Semicircular protractor with degree markings (0–180°)
- Two adjustable measurement arms with live angle readout
- Drag anywhere on your desktop — works across monitors
- Click-through transparent areas so you can still use apps underneath

## Requirements

- Python 3
- PyQt5

On Ubuntu / Debian:

```bash
sudo apt install python3-pyqt5
```

Or via pip:

```bash
pip install -r requirements.txt
```

## Start 
git clone https://github.com/checkpointmusic/checkpointprotractor.git

cd checkpointprotractor

make

make install     ?

make deb         ?


to use

./run.sh


## Controls

| Action | Control |
|--------|---------|
| Move protractor | Drag any empty area around the protractor |
| Move pivot (center) | Drag the yellow center handle |
| Adjust measurement arms | Drag the red or blue arm tips |
| Rotate protractor | Drag along the semicircle arc, or scroll the mouse wheel |
| Fine-tune arm 1 | Shift + mouse wheel |
| Fine-tune arm 2 | Ctrl + mouse wheel |
| Reset | `R` |
| Hide / show | `H` |
| Quit | `Esc`, `Q`, or right-click |

## Debian package

Build a `.deb` for Ubuntu / Debian:

```bash
sudo apt install debhelper-compat devscripts build-essential
make deb
```

## Project layout

```text
checkpointprotractor/
├── protractor.py          # Main application
├── run.sh                 # Launcher (uses XWayland on Ubuntu)
├── checkpoint-protractor  # System launcher (installed by .deb)
├── requirements.txt
├── Makefile               # Build Debian package
├── debian/                # Debian packaging
└── LICENSE
```

## Notes

- Uses a full-screen transparent overlay so the protractor stays visible when moved outside another app's window.
- Transparent areas pass through mouse clicks to apps underneath.
- If you see clipping on Wayland, use `./run.sh` (forces XWayland via `QT_QPA_PLATFORM=xcb`).

## License

MIT — see [LICENSE](LICENSE).
