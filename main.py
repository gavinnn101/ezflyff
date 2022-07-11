import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile, QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow

from loguru import logger


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("ezFlyff")
        self.flyff_url = "https://universe.flyff.com/play"
        self.ezflyff_dir = "C:\\Users\\Gavin\\Desktop\\ezflyff"

    def create_new_window(self, url, profile_name):
        logger.info("create_new_window called")
        browser = QWebEngineView()
        browser.setAttribute(Qt.WA_DeleteOnClose)
        browser.setWindowTitle(f"ezFlyff - {profile_name}")
        browser.resize(1000, 720)

        profile = QWebEngineProfile(profile_name, browser)
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
        )
        profile.setCachePath(f"{self.ezflyff_dir}\\profiles\\{profile_name}\\cache")
        profile.setPersistentStoragePath(f"{self.ezflyff_dir}\\profiles\\{profile_name}")
        page = QWebEnginePage(profile, browser)

        browser.setPage(page)
        browser.load(QUrl(url))
        browser.show()
        return browser
    
views = []
profiles = ['main', 'alt']

app = QApplication(sys.argv)
app.setApplicationName("ezFlyff")

window = MainWindow()
for acc in profiles:
    logger.info(f"Launching {acc}")
    view = window.create_new_window(window.flyff_url, acc)
    views.append(view)  # Keep reference to window to prevent it from closing
sys.exit(app.exec_())
