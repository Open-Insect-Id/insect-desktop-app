import threading
from io import BytesIO

import customtkinter as ctk
import requests
from PIL import Image


class ApiResultFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.images_refs = []
        self.loading_label = None
        self.grid_columnconfigure((0, 1, 2), weight=1)

    def display_images_async(self, images: list):
        # Clear previous content
        for widget in self.winfo_children():
            widget.destroy()

        self.images_refs.clear()

        if not images:
            ctk.CTkLabel(self, text="Pas d'images trouvées", font=ctk.CTkFont(slant="italic")).grid(row=0, column=0, columnspan=3, padx=20, pady=20)
            return

        # Show loading text
        self.loading_label = ctk.CTkLabel(self, text="Chargement des images...")
        self.loading_label.grid(row=0, column=0, columnspan=3, padx=20, pady=20)

        # Start background thread
        thread = threading.Thread(
            target=self._load_images_worker,
            args=(images,),
            daemon=True
        )
        thread.start()

    def _load_images_worker(self, images: list):
        loaded = []
        for url in images:
            try:
                response = requests.get(url, timeout=10)
                pil_image = Image.open(BytesIO(response.content))
                pil_image.thumbnail((150, 150))
                loaded.append(pil_image)
            except Exception as e:
                print(f"Error loading image from {url}: {e}")
                continue

        # Switch back to main thread
        self.after(0, lambda: self._display_loaded_images(loaded))

    def _display_loaded_images(self, pil_images):
        # Remove loading label
        if self.loading_label:
            self.loading_label.destroy()

        columns = 3

        for index, pil_image in enumerate(pil_images):
            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=pil_image.size
            )

            label = ctk.CTkLabel(self, image=ctk_image, text="")
            row = index // columns
            col = index % columns
            label.grid(row=row, column=col, padx=5, pady=5)

            self.images_refs.append(ctk_image)