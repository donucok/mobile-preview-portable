import sys
import os
import resources_rc  # Load resource Qt di awal agar icon & QR code terbaca sempurna
import json
import urllib.request
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QComboBox, 
                             QLabel, QFrame, QDialog, QDialogButtonBox, QMessageBox)
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QSize, Qt, QUrl, QEvent, QPointF
from PyQt6.QtGui import QIcon, QAction, QPixmap, QDesktopServices

APP_VERSION = "2.0.0"
GITHUB_REPO = "donucok/mobile-preview-portable"

DEVICE_PRESETS = {
    "iPhone 15 Pro": {"width": 393, "height": 852, "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"},
    "Samsung Galaxy S23": {"width": 360, "height": 780, "ua": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"},
    "Pixel 7 Pro": {"width": 412, "height": 892, "ua": "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"},
    "iPad Air (Tablet)": {"width": 820, "height": 1180, "ua": "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"}
}

# JS Injection untuk mengubah Mouse Drag menjadi Touch Swipe
TOUCH_EMULATION_JS = """
(function() {
    var isDragging = false;
    var startY = 0;
    var startScrollTop = 0;

    window.addEventListener('mousedown', function(e) {
        isDragging = true;
        startY = e.pageY;
        startScrollTop = window.scrollY || document.documentElement.scrollTop;
    });

    window.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        var deltaY = startY - e.pageY;
        window.scrollTo(0, startScrollTop + deltaY);
    });

    window.addEventListener('mouseup', function() {
        isDragging = false;
    });
})();
"""

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Mobile Web Previewer")
        self.setFixedSize(360, 480)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Mobile Web Previewer")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setStyleSheet("color: gray;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        author_label = QLabel("Created by donucok")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label)
        
        layout.addSpacing(15)
        
        qr_label = QLabel()
        qr_pixmap = QPixmap(":/donate_qr.png")
        if not qr_pixmap.isNull():
            qr_label.setPixmap(qr_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            qr_label.setText("[QR Code Not Found]")
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(qr_label)
        
        donate_text = QLabel("Scan QR Code to Support / Donate")
        donate_text.setStyleSheet("font-style: italic; font-size: 11px; color: #888;")
        donate_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(donate_text)
        
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Mobile Web Previewer v{APP_VERSION}")
        self.setMinimumSize(600, 800)
        self.setWindowIcon(QIcon(":/app_icon.png"))
        
        self.current_device = "iPhone 15 Pro"
        self.is_landscape = False
        self.touch_mode_enabled = True

        self.web_view = QWebEngineView()
        self.web_view.page().loadFinished.connect(self.on_page_loaded)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        # Address Bar
        top_bar = QHBoxLayout()
        self.url_input = QLineEdit("https://techrunner.id")
        self.url_input.returnPressed.connect(self.load_url)
        btn_load = QPushButton("Go")
        btn_load.clicked.connect(self.load_url)
        top_bar.addWidget(self.url_input)
        top_bar.addWidget(btn_load)
        self.main_layout.addLayout(top_bar)
        
        # Frame Mockup HP
        self.phone_frame = QFrame()
        self.phone_frame.setStyleSheet("""
            QFrame {
                background-color: #111;
                border: 12px solid #222;
                border-radius: 36px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.phone_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self.web_view)
        
        center_container = QHBoxLayout()
        center_container.addStretch()
        center_container.addWidget(self.phone_frame)
        center_container.addStretch()
        
        self.main_layout.addLayout(center_container)
        
        self.setup_menu_bar()
        self.update_simulation_mode()
        self.load_url()

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        
        # --- MENU FILE ---
        file_menu = menu_bar.addMenu("File")
        
        reload_action = QAction("Reload Page", self)
        reload_action.triggered.connect(self.web_view.reload)
        file_menu.addAction(reload_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # --- MENU VIEW ---
        view_menu = menu_bar.addMenu("View")
        
        device_menu = view_menu.addMenu("Select Device")
        for dev_name in DEVICE_PRESETS.keys():
            action = QAction(dev_name, self)
            action.triggered.connect(lambda checked, d=dev_name: self.change_device(d))
            device_menu.addAction(action)
            
        view_menu.addSeparator()
        
        rotate_action = QAction("Rotate Orientation", self)
        rotate_action.triggered.connect(self.toggle_rotate)
        view_menu.addAction(rotate_action)
        
        self.touch_action = QAction("Enable Touch Swipe Scroll", self, checkable=True)
        self.touch_action.setChecked(True)
        self.touch_action.triggered.connect(self.toggle_touch_mode)
        view_menu.addAction(self.touch_action)

        # --- MENU HELP ---
        help_menu = menu_bar.addMenu("Help")
        
        update_action = QAction("Check for Updates...", self)
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def change_device(self, dev_name):
        self.current_device = dev_name
        self.update_simulation_mode()

    def toggle_rotate(self):
        self.is_landscape = not self.is_landscape
        self.update_simulation_mode()

    def toggle_touch_mode(self, enabled):
        self.touch_mode_enabled = enabled
        if enabled:
            self.inject_touch_js()

    def update_simulation_mode(self):
        data = DEVICE_PRESETS[self.current_device]
        w, h = (data["height"], data["width"]) if self.is_landscape else (data["width"], data["height"])
        
        self.phone_frame.setFixedSize(w, h)
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(data["ua"])

    def load_url(self):
        url = self.url_input.text()
        if not url.startswith("http"):
            url = "https://" + url
            self.url_input.setText(url)
        self.web_view.load(QUrl(url))

    def on_page_loaded(self, success):
        if success and self.touch_mode_enabled:
            self.inject_touch_js()

    def inject_touch_js(self):
        self.web_view.page().runJavaScript(TOUCH_EMULATION_JS)

    def check_for_updates(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "").replace("v", "")
                
                if latest_tag and latest_tag > APP_VERSION:
                    reply = QMessageBox.information(
                        self, "Update Available",
                        f"A new version (v{latest_tag}) is available!\nDo you want to open the download page?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        QDesktopServices.openUrl(QUrl(data.get("html_url", "")))
                else:
                    QMessageBox.information(self, "No Update", f"You are using the latest version (v{APP_VERSION}).")
        except Exception as e:
            QMessageBox.warning(self, "Check Update Failed", f"Could not connect to update server.\nError: {e}")

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())