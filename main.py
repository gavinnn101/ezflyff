import os
import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile, QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow

from loguru import logger

import configparser


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("ezFlyff")
        self.flyff_url = "https://universe.flyff.com/play"
        self.ezflyff_dir = sys.path[0]  # Full path to directory where the script is launched from.

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
        profile.setCachePath(f"{self.ezflyff_dir}\\profiles\\{profile_name}\\cache")
        profile.setPersistentStoragePath(f"{self.ezflyff_dir}\\profiles\\{profile_name}\\storage")
        page = QWebEnginePage(profile, browser)

        browser.setPage(page)
        browser.load(QUrl(url))
        browser.show()
        return browser


def create_settings_dir(profile_name):
    logger.info("create_settings_dir called")
    dir_path = f"{sys.path[0]}\\profiles\\{profile_name}"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Created directory {dir_path}")
    else:
        logger.info(f"Directory {dir_path} already exists")


def get_profile_settings(profile_name):
    logger.info("get_profile_settings called")
    config = configparser.ConfigParser()
    settings_path = f"{sys.path[0]}\\profiles\\{profile_name}\\settings.ini"
    if not os.path.isfile(settings_path):
        logger.info(f"Creating settings.ini for profile {profile_name}")
        config.add_section("window")
        config.set("window", "window_width", "800")
        config.set("window", "window_height", "600")
        config.set("window", "window_x_pos", "0")
        config.set("window", "window_y_pos", "0")
        with open(settings_path, "w") as config_file:
            config.write(config_file)
    config.read(settings_path)
    return config

views = []
profiles = ['main', 'fullsupport']

app = QApplication(sys.argv)
app.setApplicationName("ezFlyff")

window = MainWindow()
for acc in profiles:
    logger.info(f"Launching {acc}")
    create_settings_dir(acc)
    settings = get_profile_settings(acc)
    view = window.create_new_window(window.flyff_url, acc, settings)
    views.append(view)  # Keep reference to window to prevent it from closing
sys.exit(app.exec_())


# Auto assist notes
### Find window handle by title possibly (could use "alt" tag to find it, etc)
### Send key event(s) down / up to window handle
### Key event may block window... If so we probably multithread the keypresses (pyflyff is using multithreading)
###
### Add slight randomization to timers below
### Heal every x seconds
### Buff every x seconds ( action chain hotkey could likely be used for this )
### "follow target" hotkey every x seconds
###