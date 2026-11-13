"""Windows GUI application for Discord Rich Presence IDE detection."""

import ctypes
import queue
import threading
import time
import tkinter as tk
from ctypes import wintypes
from tkinter import messagebox, ttk

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
        return "", ""

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
    """Return (app name, image key, window title) for a supported foreground IDE."""
    process_name, title = get_foreground_window()
    ide_info = IDE_PROCESSES.get(process_name)
    if ide_info is None:
        return None

    app_name, image_key = ide_info
    clean_title = title.replace("Administrator: ", "").strip()
    for suffix in (
        " - Visual Studio Code",
        " - Visual Studio",
        f" - {app_name}",
        f" — {app_name}",
    ):
        clean_title = clean_title.replace(suffix, "")

    parts = [part.strip() for part in clean_title.replace(" — ", " - ").split(" - ") if part.strip()]
    window_title = parts[0].replace("[", "").replace("]", "") if parts else ""
    return app_name, image_key, window_title[:30] or "Файл не выбран"


class DiscordRPCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DiscordRPC")
        self.root.geometry("460x340")
        self.root.minsize(420, 300)

        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None
        self.closing = False

        self.status_var = tk.StringVar(value="Остановлено")
        self.hide_title_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(100, self._process_events)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="DiscordRPC", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            main,
            text="Показывает активную IDE в Discord Rich Presence.",
            wraplength=410,
        ).pack(anchor="w", pady=(4, 14))

        status_frame = ttk.LabelFrame(main, text="Состояние", padding=10)
        status_frame.pack(fill="x")
        ttk.Label(status_frame, textvariable=self.status_var, wraplength=390).pack(anchor="w")

        ttk.Checkbutton(
            main,
            text="Не показывать название файла/окна в Discord",
            variable=self.hide_title_var,
        ).pack(anchor="w", pady=(12, 8))

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(4, 12))
        self.start_button = ttk.Button(buttons, text="Запустить", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(buttons, text="Остановить", command=self.stop, state="disabled")
        self.stop_button.pack(side="left", padx=(8, 0))

        ttk.Label(main, text="Журнал").pack(anchor="w")
        self.log = tk.Text(main, height=6, wrap="word", state="disabled", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, pady=(4, 0))

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        self.stop_event.clear()
        hide_title = self.hide_title_var.get()
        self.worker = threading.Thread(target=self._monitor, args=(hide_title,), daemon=True)
        self.worker.start()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_var.set("Подключение к Discord...")
        self._append_log("Запуск мониторинга...")

    def stop(self):
        if self.worker and self.worker.is_alive():
            self.stop_event.set()
            self.stop_button.configure(state="disabled")
            self.status_var.set("Остановка...")

    def _monitor(self, hide_title):
        rpc = Presence(CLIENT_ID)
        connected = False
        current_status = None
        start_time = int(time.time())

        try:
            rpc.connect()
            connected = True
            self.events.put(("status", "Подключено к Discord. Ожидание активной IDE..."))
            self.events.put(("log", "Подключено к Discord."))

            while not self.stop_event.is_set():
                active = get_active_ide()
                if active is None:
                    if current_status is not None:
                        rpc.clear()
                        current_status = None
                        start_time = int(time.time())
                        self.events.put(("status", "Активная IDE не найдена; статус очищен."))
                        self.events.put(("log", "Активное окно IDE не найдено."))
                else:
                    app_name, image_key, window_title = active
                    displayed_title = "Работает над проектом" if hide_title else window_title
                    new_status = (app_name, displayed_title)
                    if new_status != current_status:
                        rpc.update(
                            state=f"Пишет код в {app_name}",
                            details=displayed_title,
                            start=start_time,
                            large_image=image_key,
                            large_text=app_name,
                        )
                        current_status = new_status
                        self.events.put(("status", f"Активно: {app_name} — {displayed_title}"))
                        self.events.put(("log", f"[ACTIVE] {app_name} — {displayed_title}"))

                self.stop_event.wait(POLL_INTERVAL)
        except Exception as exc:
            self.events.put(("error", f"Не удалось подключиться или обновить статус: {exc}"))
        finally:
            if connected:
                try:
                    rpc.clear()
                except Exception:
                    pass
                try:
                    rpc.close()
                except Exception:
                    pass
            self.events.put(("stopped", None))

    def _process_events(self):
        if self.closing:
            if self.worker and self.worker.is_alive():
                self.root.after(100, self._process_events)
            else:
                self.root.destroy()
            return

        while True:
            try:
                event, value = self.events.get_nowait()
            except queue.Empty:
                break

            if event == "status":
                self.status_var.set(value)
            elif event == "log":
                self._append_log(value)
            elif event == "error":
                self.status_var.set("Ошибка подключения")
                self._append_log(value)
                messagebox.showerror("DiscordRPC", value, parent=self.root)
            elif event == "stopped":
                self.status_var.set("Остановлено")
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
                self._append_log("Мониторинг остановлен.")

        self.root.after(100, self._process_events)

    def _on_close(self):
        self.closing = True
        self.stop_event.set()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        if self.worker and self.worker.is_alive():
            self.status_var.set("Завершение...")
            self.root.after(100, self._process_events)
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    DiscordRPCApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
