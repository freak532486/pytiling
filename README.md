# pytiling
Dynamic, mouse-based tiling for EWMH-Compliant Window Managers (basically all of them)

# Requirements
- An EWMH-Compliant Window-Manager (you probably have one if you're on Linux)
- You're running X11 (not Wayland)
- `wmctrl` and `xwininfo`, install using your package manager
- Python 3
- `pynput` and `python-xlib`, install using `pip install pynput` and `pip install python-xlib`

# Installation
After installing all requirements, simply run using `python pytile.py`.

# Usage
Press the Hotkey `Meta+Alt` and click on a window when the crosshair cursor appears. This window will be moved into the background and go into *tiling-mode*. When adding more windows, they will be added into the slave-area of the layout (stacked on the right half of the screen). You can move tiled windows by dragging them to their intended spot. The layout will be preserved. You can also resize windows using the mouse. This will resize other windows accordingly.
To remove a window from tiling mode, press `Meta+Alt` again and click on it. It will go back into floating mode and onto the normal layer.

## Features
- Tiling (mouse-based)
- Gaps
- Multiple layouts
- Different Master-Area-Width

## Missing features
- Configuration (You can't change the hotkey, gaps or the layout)
- Command-Line arguments
- More than one layout

## Known bugs
- There is no `_NET_WM_TYPE`-Property for certain applications, e.g. `steam`. I'll probably just add a configurable whitelist later on.
- `spotify` doesn't work and I don't know why. However, spotify always causes problems with window managers.
- Certain windows (e.g. `xfce4-terminal`) cannot resize arbitrarily. Alignment may be off (or completely screwed, who knows). I might add a configurable blacklist as well, to sort out these problems.

## Contributing
You can obviously contribute to this project by doing one of the following things:
- Using my software as a daily driver and reporting any crashes, bugs etc. in the *Issues*-section of GitHub
- Adding new layouts. A layout is a subclass of `Layout` and implements the functions `calculate_regions(n)` and `on_resize(window)`
  - `calculate_regions(n)` divides the rectangle `self.screen` into a list of `n` `Rectangle`s. This will then define the layout
  - `on_resize(window)` is called when `window` is resized. This handles resizing and repositioning of other windows on a resize.
  Every other operation (including moving windows from one spot to the other) is handled by the superclass.
- Fixing bugs, writing documentation, improving code quality...
If you improve the code, please create a pull request, I will review it then.