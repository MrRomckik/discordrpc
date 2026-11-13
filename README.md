# DiscordRPC

Show your coding activity in Discord Rich Presence. DiscordRPC detects a supported IDE running on your computer and displays its name and the active window title as your Discord status.

> **Platform note:** The original `discord_status.py` uses Windows process names and `pygetwindow`. The macOS implementation is separate and has not yet been verified on a Mac. See [Known limitations](#known-limitations).

## Features

- Discord Rich Presence for supported development environments
- Displays the IDE and a shortened active-window title
- Checks for activity periodically and clears the status when no supported IDE is detected
- Separate entry points for Windows and macOS

## Supported IDEs

The Windows script includes process detection for IntelliJ IDEA, PyCharm, Visual Studio Code, Visual Studio, Eclipse, NetBeans, Sublime Text, Atom, Notepad++, CLion, Rider, WebStorm, GoLand, RubyMine, Android Studio, PhpStorm, and DataGrip.

The macOS script uses application bundle identifiers. Its supported-app list may need adjustments for specific IDE versions or installations.

## Requirements

- Python 3
- Discord desktop application running
- A Discord application configured for Rich Presence, with the image assets used by this project uploaded to it

## Setup

Clone the repository and install the dependencies:

```bash
git clone https://github.com/MrRomckik/discordrpc.git
cd discordrpc
python -m venv .venv
```

Activate the virtual environment, then install the packages required by the Windows version:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install psutil pygetwindow pypresence
```

On macOS, install the packages for its separate implementation:

```bash
source .venv/bin/activate
python -m pip install pypresence pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

## Run

On Windows:

```bash
python discord_status.py
```

On macOS:

```bash
python discord_status_macos.py
```

Press `Ctrl+C` in the terminal to stop the script.

## Privacy

The status can include text taken from the IDE's window title. Review what your IDE displays in its title bar before running the app, especially if it may contain private project or file names. The macOS script shortens the title to its final path component, but window-title detection may vary by application.

## Known limitations

- IDE and window detection depends on operating-system APIs and application window titles; results can vary between versions.
- The macOS implementation has not been tested on a physical Mac. Permissions, bundle identifiers, and window-title availability may affect detection.
- A standalone executable or macOS disk image is not currently provided by this README; build and test instructions will be added after platform-specific packaging is verified.
- This project is provided as a Python script and may require troubleshooting on your system.

## Contributing

Bug reports and suggestions are welcome. When reporting an issue, include your operating system, Python version, IDE, and the relevant error output. Please avoid posting private project or file names.
