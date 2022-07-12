import configparser
import os
import random
import sys
import traceback
import time
import win32api
from PyQt5.QtCore import QUrl, Qt, pyqtSlot, QThreadPool, QRunnable
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile, QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow

from loguru import logger

import win32con
from win32gui import FindWindow, SendMessage
from key_codes import KEY_MAP

ezflyff_dir = sys.path[0]  # Full path to directory where the script is launched from.

class Worker(QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.logger.info_exc()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("ezFlyff")
        self.flyff_url = "https://universe.flyff.com/play"

        self.threadpool = QThreadPool.globalInstance()


    def create_new_window(self, url, profile_name, profile_settings):
        logger.info("create_new_window called")
        browser = QWebEngineView()
        browser.setAttribute(Qt.WA_DeleteOnClose)
        browser.setWindowTitle(f"ezFlyff - {profile_name}")

        # Apply user settings from profile_settings.ini
        browser.resize(int(profile_settings["window"]["window_width"]), int(profile_settings["window"]["window_height"]))
        browser.move(int(profile_settings["window"]["window_x_pos"]), int(profile_settings["window"]["window_y_pos"]))

        profile = QWebEngineProfile(profile_name, browser)
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
        )
        profile.setCachePath(f"{ezflyff_dir}\\profiles\\{profile_name}\\cache")
        profile.setPersistentStoragePath(f"{ezflyff_dir}\\profiles\\{profile_name}\\storage")
        page = QWebEnginePage(profile, browser)

        browser.setPage(page)
        browser.load(QUrl(url))
        browser.show()
        return browser


    def start_assist_loop(self, profile_name, profile_settings):
        worker = Worker(assist_loop, profile_name, profile_settings)
        self.threadpool.start(worker)


def create_settings_dir(profile_name):
    logger.info("create_settings_dir called")
    dir_path = f"{ezflyff_dir}\\profiles\\{profile_name}"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Created directory {dir_path}")
    else:
        logger.info(f"Directory {dir_path} already exists")


def get_profile_settings(profile_name):
    logger.info("get_profile_settings called")
    config = configparser.ConfigParser()
    settings_path = f"{ezflyff_dir}\\profiles\\{profile_name}\\settings.ini"
    if not os.path.isfile(settings_path):
        logger.info(f"Creating settings.ini for profile {profile_name}")
        # Add window settings to settings.ini
        config.add_section("window")
        config.set("window", "window_width", "800")
        config.set("window", "window_height", "600")
        config.set("window", "window_x_pos", "0")
        config.set("window", "window_y_pos", "0")
        # Add assist settings to settings.ini
        config.add_section("assist")
        config.set("assist", "toggle_key", "-")
        config.set("assist", "heal_hotkey", "3")
        config.set("assist", "heal_interval", "2")
        config.set("assist", "buff_hotkey", "4")
        config.set("assist", "buff_interval", "300")
        with open(settings_path, "w") as config_file:
            config.write(config_file)
    config.read(settings_path)
    return config


def press_key(handle, hotkey):
    hotkey = KEY_MAP[hotkey]
    SendMessage(handle, win32con.WM_KEYDOWN, hotkey, 0)
    time.sleep(0.5 + random.random())
    SendMessage(handle, win32con.WM_KEYUP, hotkey, 0)


def get_game_handle(profile_name):
    logger.debug("get_game_handle called")
    game_window_name = f"ezFlyff - {profile_name}"
    game_window_class = "Qt5152QWindowIcon"
    return FindWindow(game_window_class, game_window_name)


def assist_loop(profile_name, profile_settings):
    logger.debug("assist_loop called")
    # map hotkeys to key codes
    toggle_key = profile_settings["assist"]["toggle_key"]
    heal_hotkey = profile_settings["assist"]["heal_hotkey"]
    heal_interval = int(profile_settings["assist"]["heal_interval"])
    buff_hotkey = profile_settings["assist"]["buff_hotkey"]
    buff_interval = int(profile_settings["assist"]["buff_interval"])
    # Get game handle
    game_handle = get_game_handle(profile_name)

    def buff_character():
        logger.info("pressing buff hotkey")
        press_key(game_handle, buff_hotkey)
        logger.info("Sleeping 5 seconds while character buffs")
        time.sleep(5 + random.random())  # To make sure buffs arent interrupted by a heal
        buff_timer = time.perf_counter()  # Reset buff timer
        return buff_timer

    def heal_character():
        logger.info(f"Sleeping {heal_interval} seconds...")
        time.sleep(heal_interval + random.random())
        logger.info(f"pressing heal hotkey")
        press_key(game_handle, heal_hotkey)

    assist_mode = False

    # Wait for user to toggle assist mode
    while True:
        if win32api.GetAsyncKeyState(KEY_MAP[toggle_key]):
            assist_mode = True
            break
        else:
            assist_mode = False

    if assist_mode:
        logger.info(f"{profile_name} - Assist mode enabled")
        buff_timer = buff_character()
        while assist_mode:
            heal_character()
            buff_timer_check = time.perf_counter()
            if buff_timer_check - buff_timer > buff_interval:
                buff_timer = buff_character()
            if win32api.GetAsyncKeyState(KEY_MAP[toggle_key]):
                logger.info(f"{profile_name} - Assist mode disabled")
                assist_mode = False
                break
            else:
                continue


if __name__ == "__main__":
    views = []
    profiles = ['fullsupport']

    app = QApplication(sys.argv)
    app.setApplicationName("ezFlyff")

    window = MainWindow()
    for acc in profiles:
        logger.info(f"Launching {acc}")
        create_settings_dir(acc)
        settings = get_profile_settings(acc)
        view = window.create_new_window(window.flyff_url, acc, settings)
        views.append(view)  # Keep reference to window to prevent it from closing
        window.start_assist_loop(acc, settings)
    sys.exit(app.exec_())

# Auto assist notes
### "follow target" hotkey every x seconds
