import io
import os
import platform
import webbrowser

from PIL import Image
import customtkinter as ctk

from utils.observation_db import fetch_observations


def _open_file(path: str) -> None:
    """Open a file with the system's default application."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            # macOS
            os.system(f"open {path!r}")
        else:
            # Linux / others
            os.system(f"xdg-open {path!r}")
    except Exception:
        # Fallback to opening in the default browser
        try:
            webbrowser.open(f"file://{os.path.abspath(path)}")
        except Exception:
            pass


def _load_placeholder_image(size=(86, 86)) -> ctk.CTkImage:
    """Load the SVG placeholder"""
    base = os.path.dirname(__file__)
    svg_path = os.path.join(base, "icons", "No-Image-Placeholder.svg")

    # Try to load the SVG using cairosvg if installed
    try:
        import cairosvg

        png_bytes = cairosvg.svg2png(url=svg_path, output_width=size[0], output_height=size[1])
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        # Fallback: simple gray box
        img = Image.new("RGBA", size, (60, 60, 60, 255))
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)


class ObservationJournalWindow(ctk.CTkToplevel):
    """Window displaying the observation history."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Journal d'observation")
        self.geometry("760x520")
        self.resizable(True, True)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        top_bar.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            top_bar,
            text="Historique des analyses",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        self.btn_refresh = ctk.CTkButton(
            btn_frame,
            text="Rafraîchir",
            width=120,
            command=self.refresh,
        )
        self.btn_refresh.pack(side="right", padx=(0, 6))

        self.btn_close = ctk.CTkButton(
            btn_frame,
            text="Fermer",
            width=120,
            command=self.destroy,
        )
        self.btn_close.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.scroll.grid_columnconfigure(0, weight=1)

        self._thumb_images: list[ctk.CTkImage] = []
        self._placeholder_image = _load_placeholder_image()

    def refresh(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        observations = fetch_observations()
        if not observations:
            empty = ctk.CTkLabel(
                self.scroll,
                text="📭 Aucun enregistrement pour le moment.",
                font=ctk.CTkFont(size=14),
                text_color="gray60",
            )
            empty.grid(row=0, column=0, pady=20, padx=20)
            return

        for idx, obs in enumerate(observations):
            frame = ctk.CTkFrame(
                self.scroll,
                corner_radius=12,
                border_width=1,
                border_color=("gray40", "gray30"),
                fg_color=("#1e1e1e", "#1a1a1a"),
            )
            frame.grid(row=idx, column=0, sticky="ew", padx=10, pady=6)
            frame.grid_columnconfigure(0, weight=0)
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(2, weight=0)

            # Thumbnail (optimised, if available)
            thumb = None
            path = obs.get("image_path")
            if path and os.path.exists(path):
                try:
                    img = Image.open(path)
                    img.thumbnail((86, 86), Image.LANCZOS)
                    thumb = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                    self._thumb_images.append(thumb)
                except Exception:
                    thumb = None

            if thumb:
                thumb_label = ctk.CTkLabel(frame, image=thumb, text="")
            else:
                thumb_label = ctk.CTkLabel(frame, image=self._placeholder_image, text="")
            thumb_label.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=12, pady=10)

            # Info principal (espèce + date)
            species = obs.get("species") or "N/A"
            timestamp = obs.get("timestamp", "")
            species_label = ctk.CTkLabel(
                frame,
                text=species,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            )
            species_label.grid(row=0, column=1, sticky="w", padx=(12, 6), pady=(10, 4))

            timestamp_label = ctk.CTkLabel(
                frame,
                text=timestamp,
                font=ctk.CTkFont(size=10),
                text_color="gray60",
                anchor="w",
            )
            timestamp_label.grid(row=1, column=1, sticky="w", padx=(12, 6), pady=(0, 10))

            # Statuts
            confidence = obs.get("confidence")
            reliable = obs.get("reliable")
            reliable_text = "✅ Fiable" if reliable else "⚠️ Incertain"
            confidence_text = f"Confiance: {confidence:.1f}%" if confidence is not None else "Confiance: -"
            status_label = ctk.CTkLabel(
                frame,
                text=f"{confidence_text}  •  {reliable_text}",
                font=ctk.CTkFont(size=11),
                text_color="gray70",
                anchor="w",
            )
            status_label.grid(row=2, column=1, sticky="w", padx=(12, 6), pady=(0, 12))

            # Action buttons
            if path and os.path.exists(path):
                btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                btn_frame.grid(row=0, column=2, rowspan=3, sticky="e", padx=(0, 12), pady=10)

                btn_open = ctk.CTkButton(
                    btn_frame,
                    text="Ouvrir l'image",
                    width=140,
                    command=lambda p=path: _open_file(p) if p else None,
                )
                btn_open.pack(side="top", pady=(0, 8))
