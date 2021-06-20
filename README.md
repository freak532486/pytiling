# pytiling
Dynamic, mouse-based tiling for EWMH-Compliant Window Managers (basically all of them)

## What is this?
*pytiling* is a small script that, when run, tiles all windows on the current workspace into a "master-slave"-type layout.
In this type of layout, there's a single window on the left taking up half the screen. All other windows stacked on the right half of the screen.
Windows are assigned to their positions based on how far they would move. In order to organize your tiled layout, just move the windows *very roughly* to the position where they shall end up, and then run the script. The script will then properly align the windows.

## Features
- Tiling (mouse-based)
- Gaps
- Multiple layouts
- Different Master-Area-Width

## Missing features
- Command-Line Arguments (you basically can't switch tiling mode and can't change gaps)
- Code quality (The whole thing was written in a long evening)

## Known bugs
- There is no `_NET_WM_TYPE`-Property for `spotify`. Spotify has one too many quirks with window managers. I'll probably just add a configurable whitelist later on.
- Certain windows (e.g. `xfce4-terminal`) cannot resize arbitrarily. Alignment may be off (or completely screwed, who knows). I might add a configurable blacklist as well, to sort out those problematic problems.

## Installation
The whole thing runs on Python 3 (who even uses Python 2 nowadays?). You'll need `python-xlib`, install it with `pip install python-xlib`.
To run, simply run `python pytile.py`. Your windows should be reordered.