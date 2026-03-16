import customtkinter as ctk
from PIL import Image

from config import THEME
from ui.Theme import Theme


def show_box_popup(parent, img_boxes, theme: Theme, i18n=None):
    """
    Affiche une popup avec l'image annotée (box) et propose le choix de recadrer ou non.
    parent : fenêtre principale (CTk)
    img_boxes : PIL.Image (image avec box)
    i18n : I18N instance (optional)
    Retourne True (recadrer), False (garder), ou None (fermé)
    """
    popup = ctk.CTkToplevel(parent)
    popup.title(i18n.t("crop_image") if i18n else "Recadrer l'image ?")
    popup.geometry("600x500")
    popup.grab_set()
    theme.apply_bg_to(popup)


    ratio = min(550 / img_boxes.width, 400 / img_boxes.height)
    new_size = (int(img_boxes.width * ratio), int(img_boxes.height * ratio))
    resample = Image.Resampling.LANCZOS
    img_resized = img_boxes.resize(new_size, resample)
    img_tk = ctk.CTkImage(
        light_image=img_resized, dark_image=img_resized, size=new_size
    )

    label = ctk.CTkLabel(popup, image=img_tk, text="")
    label.pack(pady=20)

    result = {"crop": None}

    def on_crop():
        result["crop"] = True
        popup.destroy()

    def on_no_crop():
        result["crop"] = False
        popup.destroy()

    btn_frame = ctk.CTkFrame(popup)
    theme.apply_bg_to(btn_frame)
    btn_frame.pack(pady=10)
    crop_btn = ctk.CTkButton(
        btn_frame,
        text=i18n.t("crop_yes") if i18n else "Recadrer autour de l'objet",
        command=on_crop,
    )
    crop_btn.pack(side="left", padx=10)
    no_crop_btn = ctk.CTkButton(
        btn_frame,
        text=i18n.t("crop_no") if i18n else "Garder l'image entière",
        command=on_no_crop,
    )
    no_crop_btn.pack(side="left", padx=10)

    popup.wait_window()
    return result["crop"]
