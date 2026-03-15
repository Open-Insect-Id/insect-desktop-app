import os
import platform
import webbrowser

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
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            self,
            text="Historique des analyses",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", padx=16, pady=(16, 8))

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

    def refresh(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        observations = fetch_observations()
        if not observations:
            empty = ctk.CTkLabel(
                self.scroll,
                text="Aucun enregistrement pour le moment.",
                font=ctk.CTkFont(size=14),
                text_color="gray60",
            )
            empty.grid(row=0, column=0, pady=20, padx=20)
            return

        for idx, obs in enumerate(observations):
            frame = ctk.CTkFrame(self.scroll, corner_radius=10)
            frame.grid(row=idx, column=0, sticky="ew", padx=10, pady=6)
            frame.grid_columnconfigure(1, weight=1)

            # Left: timestamp + species
            info_text = f"{obs.get('timestamp', '')}  |  {obs.get('species', 'N/A')}"
            label = ctk.CTkLabel(frame, text=info_text, anchor="w")
            label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 4))

            confidence = obs.get('confidence')
            reliable = obs.get('reliable')
            reliable_text = "Oui" if reliable else "Non"
            confidence_text = f"Confiance: {confidence:.1f}%" if confidence is not None else "Confiance: -"

            sublabel = ctk.CTkLabel(
                frame,
                text=f"{confidence_text}  |  Fiable: {reliable_text}",
                font=ctk.CTkFont(size=11),
                text_color="gray60",
                anchor="w",
            )
            sublabel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))

            # Buttons
            btn_open = ctk.CTkButton(
                frame,
                text="Ouvrir l'image",
                width=140,
                command=lambda p=obs.get('image_path'): _open_file(p) if p else None,
            )
            btn_open.grid(row=0, column=2, rowspan=2, padx=(0, 12), pady=10)
