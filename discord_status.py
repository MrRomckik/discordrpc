import time
import psutil
import pygetwindow as gw
from pypresence import Presence

# Discord Application ID
CLIENT_ID = 1518228891406176408
RPC = Presence(CLIENT_ID)

#Добовляем жесткое подключение к Discord, чтобы не было проблем с авторизацией
RPC.connect()
time.sleep(1)  # Небольшая задержка для стабильного подключения

print ("Мониторинг среды разработки с отслеживанием файлов запущен!")

IDE_processes = {
    "idea64.exe": ("IntelliJ IDEA", "idea_logo"),
    "pycharm64.exe": ("PyCharm", "pycharm_logo"),
    "code.exe": ("Visual Studio Code", "vscode_logo"),
    "devenv.exe": ("Visual Studio", "vs_logo"),
    "eclipse.exe": ("Eclipse", "eclipse_logo"),
    "netbeans.exe": ("NetBeans", "netbeans_logo"),
    "sublime_text.exe": ("Sublime Text", "sublime_logo"),
    "atom.exe": ("Atom", "atom_logo"),
    "notepad++.exe": ("Notepad++", "notepadpp_logo"),
    "clion64.exe": ("CLion", "clion_logo"),
    "rider64.exe": ("Rider", "rider_logo"),
    "webstorm64.exe": ("WebStorm", "webstorm_logo"),
    "goland64.exe": ("GoLand", "goland_logo"),
    "ruby64.exe": ("RubyMine", "rubymine_logo"),
    "androidstudio64.exe": ("Android Studio", "androidstudio_logo"),
    "phpstorm64.exe": ("PhpStorm", "phpstorm_logo"),
    "datagrip64.exe": ("DataGrip", "datagrip_logo"),
}

def get_active_file(app_name):
    try:
        file_name = "Файл не выбран"
        all_windows = gw.getAllTitles()
        for title in all_windows:
            if not title:
                continue
            if app_name in title or (app_name == "VS Code" and "Visual Studio Code" in title):
                clean_title = title
                for junk in [f" - {app_name}", " - Visual Studio Code", "Visual Stidio",  "Administrator: "]:
                    clean_title = clean_title.replace(junk, "")
                    parts = [p.strip() for p in clean_title.split("-") if p.strip()]
                if parts:
                    file_name = parts[0].replace("[", "").replace("]", "")
                    return file_name[:30]  # Ограничиваем длину до 30 символов
    except Exception:
        pass
    return "Файл не выбран"

def check_running_ide():
    running_processes = set()
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name:

                running_processes.add(name.lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        for proc_name, info in IDE_processes.items():
            if proc_name.lower() in running_processes:
                return info
    return None

current_app = None
current_file = None

try:
    start_time = int(time.time())
    while True:
        ide_info = check_running_ide()
        if ide_info:
            app_name, img_key = ide_info
            if ide_info != current_app or file_name != current_file:
                file_name = get_active_file(app_name)
                current_app = ide_info
                current_file = file_name
                print(f"[ACTIVE] {app_name} - {file_name}")
                RPC.update(state=f"Пишет код в {app_name}", details=f"Файл: {file_name}", start=start_time, large_image=img_key, large_text=app_name)

        else:
            if current_app is not None:
                print("[IDLE] Все закрыто. Ожидание...")
                RPC.clear()
                current_app = None
                current_file = None
                start_time = time.time()
        time.sleep(15)
except KeyboardInterrupt:
    print("\n Завершение мониторинга...")
    RPC.close()
    
