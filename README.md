<img width="324" height="292" alt="image" src="https://github.com/user-attachments/assets/b9d7e8d9-d2c2-477d-8d97-095a2f120b2c" />


# 🎞️ Sony Alpha Media AutoSorter

**Sony Alpha Media AutoSorter** is a cross-platform Python tool that auto-detects your Sony camera SD and/or CF cards, sorts your media files into a clean folder structure, and supports full AVCHD/XAVC backups. Designed for photographers and videographers using Sony Alpha, FX, ZV, and RX series cameras, it speeds up your workflow: separating JPG and RAW files into `Photos/JPG` and `Photos/RAW` folders lets you instantly hand off client-ready images and deploy them to the cloud, and consolidating all clips into a single `Video/` folder makes your footage easy to locate and upload—no more digging through nested directories.

---

## 🚀 Features

- ✅ **Auto-detects removable drives** (SD, CF, etc.) with a `DCIM` folder  
- ✅ **Mirror mode**: exact copy of your source drive—preserves every folder and file as-is (ideal when full backups are required)  
- ✅ **Sort mode**: organize media into:  
  - `Video/` for all clips  
  - `Photos/RAW`, `Photos/JPG`, `Photos/XMP` (optional sidecars)  
  - `Metadata/` for `.XML`/`.THM` files (optional)  
  - `AVCHD/PRIVATE` or `MP_ROOT` (optional full folder backup)  
- ✅ **Dark mode GUI** built with `tkinter`  
- ✅ **Checksum verification** and thread count options  
- ✅ **No deletions**—only safe copies  

---

## 📁 Example Folder Structure

<img width="430" height="223" alt="image" src="https://github.com/user-attachments/assets/e26d4e08-da32-4649-a114-cf2b1aacf8da" />


---

## 🧩 How to Use

1. Insert your SD/CF card (or connect your camera).  
2. Launch the app:  
   - **With Python**: `python Media_AutoSorter.py`  
   - **Standalone**: run the packaged `.exe`/`.app`  
3. The **Source** field should auto-fill. Otherwise, click **Browse**.  
4. Choose a **Destination** folder (defaults to `~/Pictures/YYYY-MM-DD_Imports`).  
5. Select options:  
   - `.XMP` sidecars  
   - `.XML`/`.THM` metadata  
   - AVCHD/XAVC folder backup  
   - **Mirror** vs. **Sort** mode  
6. **Start Sorting** and wait for the completion popup.  

---

## 🛠️ Requirements

- **OS**: Windows, macOS, or Linux  
- **Python**: 3.9+  
- **Libraries**: standard Python libs (`tkinter`, `os`, `shutil`, `pathlib`, `subprocess`, `platform`, `datetime`)  

---

## ⚙️ Installation & Packaging

### 1. Clone & Run

```bash
git clone https://github.com/yourusername/media-autosorter.git
cd media-autosorter
python Media_AutoSorter.py

2. Build Standalone Executable (Windows)
Install PyInstaller: pip install pyinstaller

Run PyInstaller to create the EXE in the same folder:
pyinstaller --onefile --windowed --distpath . Media_AutoSorter.py
After running, you’ll find Media_AutoSorter.exe right alongside your script.

3. Packaging for macOS & Linux
On macOS or Linux, you can also use PyInstaller:
pyinstaller --onefile --windowed --name "SonyAlphaMediaAutoSorter" Media_AutoSorter.py
The bundled app will be in dist/SonyAlphaMediaAutoSorter

4. Advanced Customization
Spec file: After the first build, edit the generated .spec (e.g., SonyAlphaMediaAutoSorter.spec) to add or tweak:
Additional data files (datas=[('media_autosorter_config.json', '.') ])
Hidden imports if you add new dependencies
Rebuild using the spec:
pyinstaller SonyAlphaMediaAutoSorter.spec

---

📷 Compatible Sony Cameras
It SHOULD Work with any model that uses standard folder layouts (DCIM, PRIVATE, MP_ROOT), including:
Alpha Series: A7 II/III/IV, A7C, A7CR, A9, A1
FX Series: FX3, FX30, FX6
ZV Series: ZV-E1, ZV-E10
RX Series: RX100, RX10, RX1R
APS-C Alpha: A6000 through A6600

---

📝 Changelog
v1.1.0
Renamed to Sony Alpha Media AutoSorter
Added checksum verification & thread count
Improved dark‑mode UI
v1.0.0
Initial release as A7C2 Media AutoSorter

Created by R2OH1

---

📜 License
This project is licensed under the MIT License – see the LICENSE file for details.
