import os
import shutil
import platform
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime

# Config file
CONFIG_PATH = Path.home() / "media_autosorter_config.json"

def load_settings():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except:
            pass
    return {}

def save_settings(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))

# File mappings
PHOTO_MAP    = {
    ".ARW":  "Photos/RAW",
    ".JPG":  "Photos/JPG",
    ".JPEG": "Photos/JPG",
    ".XMP":  "Photos/XMP",
    ".XML":  "Metadata",
    ".THM":  "Metadata"
}
VIDEO_EXTS   = {".MP4", ".MOV", ".MTS", ".MXF", ".MPG", ".AVI"}
AVCHD_FOLDERS = ["PRIVATE", "MP_ROOT"]

class MediaAutoSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sony Alpha Media AutoSorter")
        self.root.configure(bg="#2b2b2b")

        s = load_settings()
        today = datetime.now().strftime("%Y-%m-%d")
        default_dest = Path.home() / "Pictures" / f"{today}_Imports"
        default_dest.mkdir(parents=True, exist_ok=True)

        # Variables
        self.source_dir       = tk.StringVar(value=s.get("last_src", ""))
        self.dest_dir         = tk.StringVar(value=s.get("last_dest", str(default_dest)))
        self.preserve_all     = tk.BooleanVar(value=s.get("preserve_all", False))
        self.include_xmp      = tk.BooleanVar(value=s.get("include_xmp", False))
        self.include_metadata = tk.BooleanVar(value=s.get("include_metadata", False))
        self.include_avchd    = tk.BooleanVar(value=s.get("include_avchd", True))
        self.video_mode       = tk.StringVar(value=s.get("video_mode", "merge"))
        self.video_dir_name   = tk.StringVar(value=s.get("video_dir_name", "Video"))
        self.show_folder      = tk.BooleanVar(value=s.get("show_folder", True))
        self.checksum_verify  = tk.BooleanVar(value=s.get("checksum_verify", False))
        self.threads          = tk.IntVar(value=s.get("threads", 1))

        self.build_ui()
        self.auto_detect_drive()

    def build_ui(self):
        L = lambda txt, r: tk.Label(self.root, text=txt, fg="white", bg="#2b2b2b")\
                             .grid(row=r, column=0, sticky="w", padx=10, pady=5)

        # Source
        L("Source Drive:", 0)
        tk.Entry(self.root, textvariable=self.source_dir, width=40)\
          .grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_source)\
          .grid(row=0, column=2, padx=5)

        # Destination
        L("Destination:", 1)
        tk.Entry(self.root, textvariable=self.dest_dir, width=40)\
          .grid(row=1, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_dest)\
          .grid(row=1, column=2, padx=5)

        # Video folder name
        L("Video folder name:", 2)
        tk.Entry(self.root, textvariable=self.video_dir_name, width=20)\
          .grid(row=2, column=1, sticky="w")

        # Mirror mode
        tk.Checkbutton(self.root,
            text="Preserve all folders exactly as‑is",
            variable=self.preserve_all,
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b",
            command=self.toggle_mirror
        ).grid(row=3, column=0, columnspan=3, sticky="w", padx=10)

        # Video behavior
        L("Video behavior:", 4)
        tk.Radiobutton(self.root,
            text="Preserve structure",
            variable=self.video_mode, value="preserve",
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b"
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=20)
        tk.Radiobutton(self.root,
            text="Merge all into one folder",
            variable=self.video_mode, value="merge",
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b"
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=20)

        # Sidecars & metadata
        tk.Checkbutton(self.root,
            text="Include .XMP sidecars", variable=self.include_xmp,
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b"
        ).grid(row=7, column=0, columnspan=2, sticky="w", padx=20)
        tk.Checkbutton(self.root,
            text="Include .XML/.THM metadata", variable=self.include_metadata,
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b"
        ).grid(row=8, column=0, columnspan=2, sticky="w", padx=20)
        tk.Checkbutton(self.root,
            text="Copy AVCHD/XAVC folders", variable=self.include_avchd,
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b"
        ).grid(row=9, column=0, columnspan=2, sticky="w", padx=20)

        # Open after import
        tk.Checkbutton(self.root,
            text="Open destination after import", variable=self.show_folder,
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b"
        ).grid(row=10, column=0, columnspan=2, sticky="w", padx=20)

        # Preferences & Start
        tk.Button(self.root, text="Preferences…", command=self.open_preferences)\
          .grid(row=11, column=0, pady=15)
        tk.Button(self.root, text="Start Sorting", command=self.sort_files,
            bg="#1e9b37", fg="white", width=15
        ).grid(row=11, column=1)

        self.toggle_mirror()

    def toggle_mirror(self):
        state = "disabled" if self.preserve_all.get() else "normal"
        for w in self.root.grid_slaves():
            r = w.grid_info()["row"]
            if 5 <= r <= 10:
                w.configure(state=state)

    def browse_source(self):
        d = filedialog.askdirectory(title="Select card root")
        if d:
            # normalize path separators
            self.source_dir.set(str(Path(d)))

    def browse_dest(self):
        d = filedialog.askdirectory(title="Select destination")
        if d:
            self.dest_dir.set(str(Path(d)))

    def auto_detect_drive(self):
        candidates = []
        if platform.system() == "Windows":
            from string import ascii_uppercase
            candidates = [f"{d}:/" for d in ascii_uppercase if os.path.exists(f"{d}:/")]
        else:
            vols = Path("/Volumes")
            candidates = [str(vols / v) for v in vols.iterdir()]

        for d in candidates:
            if Path(d, "DCIM").exists():
                self.source_dir.set(str(Path(d)))
                return

    def open_preferences(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Preferences")
        dlg.configure(bg="#2b2b2b")

        tk.Checkbutton(dlg,
            text="Verify checksum after copy", variable=self.checksum_verify,
            fg="white", bg="#2b2b2b", selectcolor="#2b2b2b"
        ).pack(anchor="w", padx=20, pady=5)

        tk.Label(dlg, text="Parallel copy threads:",
                 fg="white", bg="#2b2b2b").pack(anchor="w", padx=20)
        tk.Spinbox(dlg, from_=1, to=8, textvariable=self.threads,
                   width=5).pack(anchor="w", padx=40)

        tk.Button(dlg, text="OK", command=dlg.destroy).pack(pady=10)

    def sort_files(self):
        src = Path(self.source_dir.get().strip())
        dst = Path(self.dest_dir.get().strip())
        if not src.exists() or not dst.exists():
            messagebox.showerror("Error", "Select both source and destination.")
            return

        cnt = 0

        if self.preserve_all.get():
            # Mirror the entire card
            for item in src.rglob("*"):
                if item.name.startswith("."):
                    continue
                rel = item.relative_to(src)
                out = dst / rel
                if item.is_dir():
                    out.mkdir(parents=True, exist_ok=True)
                else:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, out)
                cnt += 1

        else:
            # Flatten DCIM folder
            dcim = src / "DCIM"
            for f in dcim.rglob("*"):
                if not f.is_file():
                    continue
                ext = f.suffix.upper()

                if ext in VIDEO_EXTS:
                    # All video clips go here
                    out = dst / self.video_dir_name.get()
                elif ext in PHOTO_MAP:
                    # Photos & sidecars
                    if ext == ".XMP" and not self.include_xmp.get():
                        continue
                    if ext in {".XML", ".THM"} and not self.include_metadata.get():
                        continue
                    out = dst / PHOTO_MAP[ext]
                else:
                    continue

                out.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, out / f.name)
                cnt += 1

            # Handle AVCHD/XAVC folders
            if self.include_avchd.get():
                for sub in AVCHD_FOLDERS:
                    folder = src / sub
                    if not folder.is_dir():
                        continue

                    if self.video_mode.get() == "merge":
                        # Flatten all clips under this folder
                        for f in folder.rglob("*"):
                            if not f.is_file():
                                continue
                            if f.suffix.upper() in VIDEO_EXTS:
                                out = dst / self.video_dir_name.get()
                                out.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(f, out / f.name)
                                cnt += 1
                    else:
                        # Preserve the full folder tree
                        dest_sub = dst / self.video_dir_name.get() / sub
                        if not dest_sub.exists():
                            shutil.copytree(folder, dest_sub)
                            cnt += sum(1 for _ in dest_sub.rglob("*") if _.is_file())

        # Save settings
        cfg = {
            "last_src":       self.source_dir.get(),
            "last_dest":      self.dest_dir.get(),
            "preserve_all":   self.preserve_all.get(),
            "include_xmp":    self.include_xmp.get(),
            "include_metadata": self.include_metadata.get(),
            "include_avchd":  self.include_avchd.get(),
            "video_mode":     self.video_mode.get(),
            "video_dir_name": self.video_dir_name.get(),
            "show_folder":    self.show_folder.get(),
            "checksum_verify": self.checksum_verify.get(),
            "threads":         self.threads.get()
        }
        save_settings(cfg)

        # Optionally open destination
        if self.show_folder.get():
            p = str(dst)
            if platform.system() == "Windows":
                os.startfile(p)
            elif platform.system() == "Darwin":
                subprocess.run(["open", p])
            else:
                subprocess.run(["xdg-open", p])

        messagebox.showinfo("Done", f"✅ Copied {cnt} files.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaAutoSorterApp(root)
    root.mainloop()
