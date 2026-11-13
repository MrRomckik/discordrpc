"""macOS entry point for Discord Rich Presence IDE detection.

Install on macOS with:
    python -m pip install pypresence psutil pyobjc-framework-Cocoa pyobjc-framework-Quartz

The active application is detected with NSWorkspace and its frontmost window
with Quartz. The Windows-only pygetwindow module is intentionally not used.
"""

import time

from AppKit import NSWorkspace
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGNullWindowID,
    kCGWindowListExcludeDesktopElements,
    kCGWindowListOptionOnScreenOnly,
    kCGWindowOwnerName,
    kCGWindowOwnerPID,
    kCGWindowName,
)
from pypresence import Presence

CLIENT_ID = 1518228891406176408
POLL_INTERVAL = 5

# Bundle identifiers are more stable than process names on macOS.
IDE_BUNDLE_IDS = {
    "com.microsoft.VSCode": ("Visual Studio Code", "vscode_logo"),
    "com.jetbrains.intellij": ("IntelliJ IDEA", "idea_logo"),
    "com.jetbrains.pycharm": ("PyCharm", "pycharm_logo"),
    "com.jetbrains.pycharm.ce": ("PyCharm Community Edition", "pycharm_logo"),
    "com.jetbrains.WebStorm": ("WebStorm", "webstorm_logo"),
    "com.jetbrains.CLion": ("CLion", "clion_logo"),
    "com.jetbrains.rider": ("Rider", "rider_logo"),
    "com.jetbrains.goland": ("GoLand", "goland_logo"),
    "com.jetbrains.phpstorm": ("PhpStorm", "phpstorm_logo"),
    "com.jetbrains.intellij.ce": ("IntelliJ IDEA Community Edition", "idea_logo"),
    "com.apple.dt.Xcode": ("Xcode", "xcode_logo"),
    "org.eclipse.eclipse": ("Eclipse", "eclipse_logo"),
    "com.sublimetext.4": ("Sublime Text", "sublime_logo"),
}


def get_frontmost_ide():
    """Return (display name, image key, window title), or None if not an IDE."""
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    if app is None:
        return None

    bundle_id = app.bundleIdentifier()
    ide_info = IDE_BUNDLE_IDS.get(bundle_id)
    if ide_info is None:
        return None

    app_name, image_key = ide_info
    pid = app.processIdentifier()
    title = "Файл не выбран"

    # Window list is ordered front-to-back; select this app's first titled window.
    windows = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
        kCGNullWindowID,
    ) or []
    for window in windows:
        if window.get(kCGWindowOwnerPID) != pid:
            continue
        window_title = window.get(kCGWindowName)
        if window_title:
            title = str(window_title).strip()
            break

    # Do not publish a full project path or an excessively long title.
    title = title.rsplit("/", 1)[-1][:30] or "Файл не выбран"
    return app_name, image_key, title


def main():
    rpc = Presence(CLIENT_ID)
    try:
        rpc.connect()
        print("Мониторинг IDE запущен. Для выхода нажмите Ctrl+C.")
        current_status = None
        start_time = int(time.time())

        while True:
            active_ide = get_frontmost_ide()
            if active_ide is None:
                if current_status is not None:
                    rpc.clear()
                    current_status = None
                    start_time = int(time.time())
            elif active_ide != current_status:
                app_name, image_key, window_title = active_ide
                rpc.update(
                    state=f"Пишет код в {app_name}",
                    details=f"Окно: {window_title}",
                    start=start_time,
                    large_image=image_key,
                    large_text=app_name,
                )
                print(f"[ACTIVE] {app_name} — {window_title}")
                current_status = active_ide

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nЗавершение мониторинга...")
    finally:
        rpc.close()


if __name__ == "__main__":
    main()
