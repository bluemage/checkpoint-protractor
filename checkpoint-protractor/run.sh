#!/usr/bin/env bash
# Launch protractor as an independent overlay.
# Uses X11 (XWayland) by default on Ubuntu — avoids Wayland clipping when
# the app is started from inside another window (e.g. Cursor's terminal).
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
exec python3 "$(dirname "$(readlink -f "$0")")/protractor.py" "$@"
