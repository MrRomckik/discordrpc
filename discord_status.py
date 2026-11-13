"""Windows entry point for Discord Rich Presence IDE detection."""

import ctypes
import time
from ctypes import wintypes

import psutil
from pypresence import Presence

CLIENT_ID = 1518228891406176408
POLL_INTERVAL = 5

IDE_PROCESSES = {
    "idea64.exe": ("IntelliJ IDEA", "idea_logo"),
    "pycharm64.exe": ("PyCharm", "pycharm_logo"),
    "code.exe": ("Visual Studio Code", "vscode_logo"),
    "devenv.exe": ("Visual Studio", "vs_logo"),
    "eclipse.exe": ("Eclipse", "eclipse_logo"),
    "netbeans64.exe": ("NetBeans", "netbeans_logo"),
    "netbeans.exe": ("NetBeans", "netbeans_logo"),
    "sublime_text.exe": ("Sublime Text", "sublime_logo"),
    "atom.exe": ("Atom", "atom_logo"),
    "notepad++.exe": ("Notepad++", "notepadpp_logo"),
    "clion64.exe": ("CLion", "clion_logo"),
    "rider64.exe": ("Rider", "rider_logo"),
    "webstorm64.exe": ("WebStorm", "webstorm_logo"),
    "goland64.exe": ("GoLand", "goland_logo"),
    "ruby64.exe": ("RubyMine", "rubymine_logo"),
    "studio64.exe": ("Android Studio", "androidstudio_logo"),
    "androidstudio64.exe": ("Android Studio", "androidstudio_logo"),
    "phpstorm64.exe": ("PhpStorm", "phpstorm_logo"),
    "datagrip64.exe": ("DataGrip", "datagrip_logo"),
}


def get_foreground_window():
    """Return the foreground window's process name and title on Windows."""
    user32 = ctypes.windll.user32
    user32.GetForegroundWindow.restype = wintypes.HWND
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None, ""

    process_id = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

    title_length = user32.GetWindowTextLengthW(hwnd)
    title_buffer = ctypes.create_unicode_buffer(title_length + 1)
    user32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))

    try:
        process_name = psutil.Process(process_id.value).name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        process_name = ""

    return process_name, title_buffer.value.strip()


def get_active_ide():
    """Return (IDE info, display title) for the foreground IDE, if supported."""
    process_name, title = get_foreground_window()
    ide_info = IDE_PROCESSES.get(process_name)
    if ide_info is None:
        return None

    app_name, _ = ide_info
    clean_title = title.replace("Administrator: ", "").strip()
    for suffix in (
        " - Visual Studio Code",
        " - Visual Studio",
        f" - {app_name}",
        f" — {app_name}",
    ):
        clean_title = clean_title.replace(suffix, "")

    # IDE window titles commonly put the file before the project/editor name.
    parts = [part.strip() for part in clean_title.replace(" — ", " - ").split(" - ") if part.strip()]
    file_name = parts[0].replace("[", "").replace("]", "") if parts else ""
    file_name = file_name[:30] or "Файл не выбран"
    return ide_info, file_name


def main():
    rpc = Presence(CLIENT_ID)
    connected = False
    current_status = None
    start_time = int(time.time())

    try:
        rpc.connect()
        connected = True
        print("Мониторинг активного окна IDE запущен. Для выхода нажмите Ctrl+C.")

        while True:
            active = get_active_ide()
            if active is None:
                if current_status is not None:
                    print("[IDLE] Активное окно IDE не найдено.")
                    rpc.clear()
                    current_status = None
                    start_time = int(time.time())
            else:
                ide_info, file_name = active
                status = (ide_info, file_name)
                if status != current_status:
                    app_name, image_key = ide_info
                    print(f"[ACTIVE] {app_name} — {file_name}")
                    rpc.update(
                        state=f"Пишет код в {app_name}",
                        details=f"Файл: {file_name}",
                        start=start_time,
                        large_image=image_key,
                        large_text=app_name,
                    )
                    current_status = status

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nЗавершение мониторинга...")
    finally:
        if connected:
            rpc.close()


if __name__ == "__main__":
    main()
