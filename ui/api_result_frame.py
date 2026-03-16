import threading
from io import BytesIO

import customtkinter as ctk
import requests
from PIL import Image
import concurrent.futures


class ApiResultFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, i18n=None, **kwargs):
        super().__init__(master, **kwargs)
        self.images_refs = []
        self.loading_label = None
        self.loading_bar = None
        self._image_cache: dict[str, Image.Image] = {}
        self._cache_lock = threading.Lock()
        self._columns = 3
        self._configure_grid()
        self.i18n = i18n

    def _configure_grid(self):
        for col in range(self._columns):
            self.grid_columnconfigure(col, weight=1, minsize=170)

    def display_images_async(self, images: list):
        # Clear previous content
        for widget in self.winfo_children():
            widget.destroy()

        self.images_refs.clear()

        if not images:
            ctk.CTkLabel(
                self,
                text=(
                    self.i18n.t("no_images_found")
                    if self.i18n
                    else "Pas d'images trouvées"
                ),
                font=ctk.CTkFont(slant="italic"),
            ).grid(row=0, column=0, columnspan=self._columns, padx=20, pady=20)
            return

        # Show loading text + progress bar
        loading_text = f"{self.i18n.t('loading_images') if self.i18n else 'Chargement des images…'} (0/{len(images)})"
        self.loading_label = ctk.CTkLabel(self, text=loading_text)
        self.loading_label.grid(
            row=0, column=0, columnspan=self._columns, padx=20, pady=(20, 5)
        )

        self.loading_bar = ctk.CTkProgressBar(self, width=250)
        self.loading_bar.set(0)
        self.loading_bar.grid(
            row=1, column=0, columnspan=self._columns, padx=20, pady=(0, 20)
        )

        # Force UI redraw so the loading indicators appear immediately
        self.update_idletasks()

        # Start background thread
        thread = threading.Thread(
            target=self._load_images_worker, args=(images,), daemon=True
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
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            return None

        with self._cache_lock:
            self._image_cache[url] = pil_image

        return pil_image

    def _update_loading_label(self, loaded: int, total: int):
        try:
            loading_text = f"{self.i18n.t('loading_images') if self.i18n else 'Chargement des images…'} ({loaded}/{total})"
            self.loading_label.configure(text=loading_text)
            if self.loading_bar:
                self.loading_bar.set(min(max(loaded / total, 0.0), 1.0))
        except Exception:
            # If the widget is already destroyed, ignore.
            self.loading_label = None
            self.loading_bar = None

    def _load_images_worker(self, images: list):
        # Keep results in input order to preserve the intended layout
        loaded: list[Image.Image | None] = [None] * len(images)
        total = len(images)
        loaded_count = 0

        with requests.Session() as session:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(self._fetch_image, url, session): idx
                    for idx, url in enumerate(images)
                }

                for future in concurrent.futures.as_completed(futures):
                    idx = futures[future]
                    result = future.result()
                    if result:
                        loaded[idx] = result
                        loaded_count += 1
                        # Update the loading label on the main thread
                        self.after(
                            0,
                            lambda lc=loaded_count, tot=total: self._update_loading_label(
                                lc, tot
                            ),
                        )

        # Filter out any None entries (failed downloads)
        ordered_images = [img for img in loaded if img is not None]

        # Switch back to main thread
        self.after(0, lambda: self._display_loaded_images(ordered_images))

    def _open_image_popup(self, image: Image.Image):
        popup = ctk.CTkToplevel(self)
        popup.title(self.i18n.t("image_popup_title") if self.i18n else "Image agrandie")
        popup.geometry("850x850")

        display_image = image.copy()
        display_image.thumbnail((800, 800))

        popup_image = ctk.CTkImage(
            light_image=display_image, dark_image=display_image, size=display_image.size
        )
        label = ctk.CTkLabel(popup, image=popup_image, text="")
        label.pack(expand=True, fill="both", padx=10, pady=10)
        popup._popup_image_ref = popup_image

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

        columns = self._columns
        rows = (len(pil_images) + columns - 1) // columns
        for row in range(rows):
            self.grid_rowconfigure(row, weight=1, minsize=170)

        for index, full_image in enumerate(pil_images):
            thumb = full_image.copy()
            thumb.thumbnail((150, 150))

            ctk_image = ctk.CTkImage(
                light_image=thumb, dark_image=thumb, size=thumb.size
            )

            # Use a frame to better align thumbnails because it's coooool
            cell = ctk.CTkFrame(
                self,
                fg_color=("gray92", "gray18"),
                corner_radius=10,
                border_width=1,
                border_color=("gray70", "gray25"),
            )
            row = index // columns
            col = index % columns
            cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            cell.grid_rowconfigure(0, weight=1)
            cell.grid_columnconfigure(0, weight=1)

            label = ctk.CTkLabel(cell, image=ctk_image, text="")
            label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            # Open larger view on click
            label.bind(
                "<Button-1>", lambda e, img=full_image: self._open_image_popup(img)
            )

            # Keep a reference so the image stays visible
            self.images_refs.append(ctk_image)
