import threading
from io import BytesIO

import customtkinter as ctk
import requests
from PIL import Image
import concurrent.futures


class ApiResultFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.images_refs = []
        self.loading_label = None
        self.loading_bar = None
        self._image_cache: dict[str, Image.Image] = {}
        self._cache_lock = threading.Lock()
        self.grid_columnconfigure((0, 1, 2), weight=1)

    def display_images_async(self, images: list):
        # Clear previous content
        for widget in self.winfo_children():
            widget.destroy()

        self.images_refs.clear()

        if not images:
            ctk.CTkLabel(self, text="Pas d'images trouvées", font=ctk.CTkFont(slant="italic")).grid(row=0, column=0, columnspan=3, padx=20, pady=20)
            return

        # Show loading text + progress bar
        self.loading_label = ctk.CTkLabel(self, text="Chargement des images… (0/{})".format(len(images)))
        self.loading_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 5))

        self.loading_bar = ctk.CTkProgressBar(self, width=250)
        self.loading_bar.set(0)
        self.loading_bar.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20))

        # Force UI redraw so the loading indicators appear immediately
        self.update_idletasks()

        # Start background thread
        thread = threading.Thread(
            target=self._load_images_worker,
            args=(images,),
            daemon=True
        )
        thread.start()

    def _fetch_image(self, url: str, session: requests.Session) -> Image.Image | None:
        # Reuse cached images when possible
        with self._cache_lock:
            cached = self._image_cache.get(url)
        if cached is not None:
            return cached

        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            pil_image = Image.open(BytesIO(response.content))
            pil_image.thumbnail((150, 150))
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            return None

        with self._cache_lock:
            self._image_cache[url] = pil_image

        return pil_image

    def _update_loading_label(self, loaded: int, total: int):

        try:
            self.loading_label.configure(text=f"Chargement des images… ({loaded}/{total})")
            if self.loading_bar:
                self.loading_bar.set(min(max(loaded / total, 0.0), 1.0))
        except Exception:
            # If the widget is already destroyed, ignore.
            self.loading_label = None
            self.loading_bar = None

    def _load_images_worker(self, images: list):
        loaded: list[Image.Image] = []
        total = len(images)
        loaded_count = 0

        with requests.Session() as session:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self._fetch_image, url, session) for url in images]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        loaded.append(result)
                        loaded_count += 1
                        # Update the loading label on the main thread
                        self.after(0, lambda lc=loaded_count, tot=total: self._update_loading_label(lc, tot))

        # Switch back to main thread
        self.after(0, lambda: self._display_loaded_images(loaded))

    def _display_loaded_images(self, pil_images):
        # Remove loading widgets
        if self.loading_label:
            try:
                self.loading_label.destroy()
            except Exception:
                pass
            self.loading_label = None

        if self.loading_bar:
            try:
                self.loading_bar.destroy()
            except Exception:
                pass
            self.loading_bar = None

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