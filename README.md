# Mobile Web Previewer Portable

Aplikasi desktop *portable* berbasis Python dan PyQt6 untuk melakukan pengujian dan *live preview* tampilan website pada mode seluler (iPhone & Android) secara *realtime*.

## Fitur Utama
- **Preset Device:** Pilihan resolusi presisi untuk iPhone 15 Pro, Samsung S24, dan Tablet.
- **User-Agent Spoofing:** Mengubah identitas browser agar website menyajikan tata letak *mobile*.
- **Localhost & Live Reload Support:** Cocok untuk pengujian proyek website lokal (`localhost:3000`, `127.0.0.1`, dll).
- **Portable:** Dapat di-compile menjadi 1 file `.exe` tanpa perlu instalasi setup.

## Cara Menjalankan Source Code (Development)
1. Install dependencies:
   ```bash
   pip install PyQt6 PyQt6-WebEngine
