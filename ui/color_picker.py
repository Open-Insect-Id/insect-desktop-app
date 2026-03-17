import tkinter as tk

from ui.theme import Theme
from utils.logger import setup_logger
from utils.settings_db import get_theme

logger = setup_logger(__name__)

import customtkinter as ctk

# ──────────────────────────────────────────────────────────────────────────────
# Embedded HSV color-picker widget (pure tkinter/customtkinter, no extra deps)
# Used AI to write that, as it is horrible to draw it in python and tkinter
# ──────────────────────────────────────────────────────────────────────────────


class ColorPickerDialog(ctk.CTkToplevel):
    """
    A modal HSV color picker.
    On confirm it sets self.result to the chosen hex color (#rrggbb),
    on cancel self.result stays None.
    """

    SQ = 220  # size of the hue/saturation square
    BAR_W = 24  # width of the hue & value bars

    def __init__(self, parent, initial_color: str, title: str = "Pick a color"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)

        self.theme = get_theme()
        self.result: str | None = None

        # Parse initial color → h, s, v
        self._h, self._s, self._v = self._hex_to_hsv(initial_color)

        self._build_ui()
        self._draw_all()
        self._update_preview()

        # grab_set() requires the window to be visible first
        self.after(100, self._safe_grab)

    def _safe_grab(self):
        """Called after the window is rendered — grab_set() is safe here."""
        try:
            self.grab_set()
        except Exception:
            pass  # window was closed before becoming visible

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        pad = dict(padx=10, pady=6)

        # ── top row: SV square + hue bar + value bar ──
        canvas_frame = ctk.CTkFrame(self, fg_color="transparent")
        canvas_frame.grid(row=0, column=0, columnspan=2, **pad)

        SQ, BW = self.SQ, self.BAR_W

        self._sv_canvas = tk.Canvas(
            canvas_frame, width=SQ, height=SQ, highlightthickness=1, cursor="crosshair"
        )
        self._sv_canvas.grid(row=0, column=0, padx=(0, 8))
        self._sv_canvas.bind("<Button-1>", self._on_sv_click)
        self._sv_canvas.bind("<B1-Motion>", self._on_sv_click)

        self._hue_canvas = tk.Canvas(
            canvas_frame,
            width=BW,
            height=SQ,
            highlightthickness=1,
            cursor="sb_v_double_arrow",
        )
        self._hue_canvas.grid(row=0, column=1, padx=(0, 8))
        self._hue_canvas.bind("<Button-1>", self._on_hue_click)
        self._hue_canvas.bind("<B1-Motion>", self._on_hue_click)

        # ── preview swatch ──
        self._preview = tk.Canvas(
            canvas_frame, width=BW * 2, height=SQ, highlightthickness=1
        )
        self._preview.grid(row=0, column=2)

        # ── hex entry ──
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.grid(row=1, column=0, columnspan=2, pady=(0, 4))

        ctk.CTkLabel(entry_frame, text="Hex:").pack(side="left", padx=(0, 6))
        self._hex_var = tk.StringVar(value=self._hsv_to_hex(self._h, self._s, self._v))
        self._hex_entry = ctk.CTkEntry(
            entry_frame, textvariable=self._hex_var, width=100
        )
        self._hex_entry.pack(side="left")
        self._hex_entry.bind("<Return>", self._on_hex_enter)
        self._hex_entry.bind("<FocusOut>", self._on_hex_enter)

        # ── buttons ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(4, 10))

        pc = self.theme.primary_color
        hc = self.theme.hover_color
        tc = self.theme.text

        ctk.CTkButton(
            btn_frame,
            text="OK",
            width=90,
            fg_color=pc,
            hover_color=hc,
            text_color=tc,
            command=self._on_ok,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btn_frame,
            text="Annuler",
            width=90,
            fg_color=pc,
            hover_color=hc,
            text_color=tc,
            command=self.destroy,
        ).pack(side="left", padx=8)

    # ── drawing ───────────────────────────────────────────────────────────────

    def _draw_all(self):
        self._draw_sv_square()
        self._draw_hue_bar()
        self._draw_sv_cursor()
        self._draw_hue_cursor()

    def _draw_sv_square(self):
        """Draw the saturation-value square for the current hue."""
        SQ = self.SQ
        canvas = self._sv_canvas
        canvas.delete("sv")
        img = tk.PhotoImage(width=SQ, height=SQ)
        # Build pixel data row by row
        rows = []
        for y in range(SQ):
            v = 1.0 - y / (SQ - 1)
            row_pixels = []
            for x in range(SQ):
                s = x / (SQ - 1)
                r, g, b = self._hsv_to_rgb(self._h, s, v)
                row_pixels.append(f"#{r:02x}{g:02x}{b:02x}")
            rows.append("{" + " ".join(row_pixels) + "}")
        img.put(" ".join(rows))
        canvas.create_image(0, 0, anchor="nw", image=img, tags="sv")
        canvas._sv_img = img  # keep a reference

    def _draw_hue_bar(self):
        """Draw a vertical rainbow hue bar."""
        SQ, BW = self.SQ, self.BAR_W
        canvas = self._hue_canvas
        canvas.delete("hue")
        img = tk.PhotoImage(width=BW, height=SQ)
        rows = []
        for y in range(SQ):
            h = y / (SQ - 1)
            r, g, b = self._hsv_to_rgb(h, 1.0, 1.0)
            color = f"#{r:02x}{g:02x}{b:02x}"
            rows.append("{" + " ".join([color] * BW) + "}")
        img.put(" ".join(rows))
        canvas.create_image(0, 0, anchor="nw", image=img, tags="hue")
        canvas._hue_img = img

    def _draw_sv_cursor(self):
        self._sv_canvas.delete("cursor")
        SQ = self.SQ
        cx = int(self._s * (SQ - 1))
        cy = int((1.0 - self._v) * (SQ - 1))
        r = 6
        self._sv_canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r, outline="white", width=2, tags="cursor"
        )
        self._sv_canvas.create_oval(
            cx - r + 1,
            cy - r + 1,
            cx + r - 1,
            cy + r - 1,
            outline="black",
            width=1,
            tags="cursor",
        )

    def _draw_hue_cursor(self):
        self._hue_canvas.delete("hcursor")
        SQ, BW = self.SQ, self.BAR_W
        cy = int(self._h * (SQ - 1))
        self._hue_canvas.create_line(
            0, cy, BW, cy, fill="white", width=2, tags="hcursor"
        )
        self._hue_canvas.create_line(
            0, cy + 1, BW, cy + 1, fill="black", width=1, tags="hcursor"
        )

    def _update_preview(self):
        color = self._hsv_to_hex(self._h, self._s, self._v)
        self._preview.configure(bg=color)
        self._hex_var.set(color)

    # ── event handlers ────────────────────────────────────────────────────────

    def _on_sv_click(self, event):
        SQ = self.SQ
        self._s = max(0.0, min(1.0, event.x / (SQ - 1)))
        self._v = max(0.0, min(1.0, 1.0 - event.y / (SQ - 1)))
        self._draw_sv_cursor()
        self._update_preview()

    def _on_hue_click(self, event):
        SQ = self.SQ
        self._h = max(0.0, min(1.0, event.y / (SQ - 1)))
        self._draw_sv_square()
        self._draw_hue_cursor()
        self._draw_sv_cursor()
        self._update_preview()

    def _on_hex_enter(self, event=None):
        raw = self._hex_var.get().strip().lstrip("#")
        if len(raw) == 6:
            try:
                int(raw, 16)
                self._h, self._s, self._v = self._hex_to_hsv("#" + raw)
                self._draw_all()
                self._update_preview()
            except ValueError:
                pass

    def _on_ok(self):
        self.result = self._hsv_to_hex(self._h, self._s, self._v)
        self.destroy()

    # ── color math ───────────────────────────────────────────────────────────

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    def _hsv_to_hex(self, h, s, v):
        r, g, b = self._hsv_to_rgb(h, s, v)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _hex_to_hsv(hex_color: str):
        import colorsys

        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))
        return colorsys.rgb_to_hsv(r, g, b)
