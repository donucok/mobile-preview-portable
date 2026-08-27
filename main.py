import sys
from PyQt6.QtCore import QUrl, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QComboBox, 
    QLineEdit, QPushButton, QHBoxLayout, QWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# User-Agent string untuk emulasi browser HP
DESKTOP_UA = ""
IPHONE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1"
ANDROID_UA = "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.105 Mobile Safari/537.36"

class MobileSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobile Web Previewer Portable")
        
        # Inisialisasi Browser Engine
        self.browser = QWebEngineView()
        
        # Setup Toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Dropdown Pilihan Perangkat
        self.device_combo = QComboBox()
        self.device_combo.addItems([
            "iPhone 15 Pro (393x852)",
            "Samsung Galaxy S24 (360x780)",
            "iPad Mini (744x1133)"
        ])
        self.device_combo.currentIndexChanged.connect(self.change_device)
        toolbar.addWidget(self.device_combo)
        
        # Input URL
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Masukkan URL (misal: localhost:3000 atau google.com)")
        self.url_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.url_bar)
        
        # Tombol Go
        btn_go = QPushButton("Buka")
        btn_go.clicked.connect(self.load_url)
        toolbar.addWidget(btn_go)

        # Set Layout Utama
        self.setCentralWidget(self.browser)
        
        # Set Default Device & URL
        self.change_device(0)
        self.url_bar.setText("https://google.com")
        self.load_url()

    def change_device(self, index):
        # Ukuran layar & User Agent berdasarkan pilihan
        if index == 0:  # iPhone 15 Pro
            self.resize(430, 920)
            self.browser.page().profile().setHttpUserAgent(IPHONE_UA)
        elif index == 1:  # Samsung S24
            self.resize(390, 840)
            self.browser.page().profile().setHttpUserAgent(ANDROID_UA)
        elif index == 2:  # iPad Mini
            self.resize(780, 1180)
            self.browser.page().profile().setHttpUserAgent(DESKTOP_UA)

    def load_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MobileSimulator()
    window.show()
    sys.exit(app.exec())
