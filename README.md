# DiscordRPC

A small Windows desktop app that shows your active development environment in Discord Rich Presence.

## Features

- Simple graphical interface: start and stop monitoring without using a terminal
- Detects the foreground window for supported IDEs
- Updates Discord when the active IDE or window changes
- Optional privacy mode to avoid publishing the window/file title

## Supported IDEs on Windows

IntelliJ IDEA, PyCharm, Visual Studio Code, Visual Studio, Eclipse, NetBeans, Sublime Text, Atom, Notepad++, CLion, Rider, WebStorm, GoLand, RubyMine, Android Studio, PhpStorm, and DataGrip.

## Requirements

- Windows 10 or later
- Discord desktop application running
- Python 3.10 or later, if running from source

## Run from source

```powershell
git clone https://github.com/MrRomckik/discordrpc.git
cd discordrpc
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python discord_status.py
```

The app opens a window. Click **Запустить** to connect to Discord and begin monitoring. Enable the privacy checkbox before starting if you do not want the active window title sent to Discord. Click **Остановить** to clear the presence and stop monitoring.

## Build a standalone Windows executable

Build on Windows with Python installed:

```powershell
python -m pip install pyinstaller
pyinstaller --onefile --windowed --name DiscordRPC discord_status.py
```

The executable will be at `dist\DiscordRPC.exe`. The `--windowed` option prevents a console window from appearing, so it launches as a normal GUI application. You can copy the executable somewhere convenient or create a shortcut to it.

## Privacy

Without privacy mode, the app may send the active IDE window title to Discord. Window titles can include project or file names. With privacy mode enabled, it sends a generic activity label instead. The setting applies for that monitoring session and is not saved.

## Known limitations

- This GUI app and `discord_status.py` are Windows-specific.
- `discord_status_macos.py` is a separate experimental script and is not covered by this GUI or Windows build instructions; it has not been verified on a physical Mac.
- IDE window-title formats can differ, so the displayed title may not always be the current file name.
- Windows may show a security warning for an unsigned executable. Do not download binaries from unofficial sources.

## Contributing

Bug reports and suggestions are welcome. Include your Windows version, Python version, IDE, and relevant error output. Please avoid posting private project or file names.
