import logging
import customtkinter as ctk
import qrcode
from PIL import Image

from mobile_server.server import IMAGE_QUEUE, MobileServerRuntime

# --- Constants ---
MOBILE_SERVER_PORT = 5050
MOBILE_QR_SIZE = 200
MOBILE_STATUS_CONNECTED_COLOR = "#2fa572"
MOBILE_STATUS_IDLE_COLOR = "gray60"
MOBILE_POLL_INTERVAL_MS = 700

logger = logging.getLogger("mobile_connexion")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class MobileConnectionWindow(ctk.CTkToplevel):
    """Toplevel window showing QR code and mobile connection status"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mobile Connect")
        self.geometry("360x480")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.server_runtime: MobileServerRuntime | None = None
        self.image_queue = IMAGE_QUEUE
        self.qr_image_tk = None

        self._build_widgets()
        self.start_server()
        self.refresh_status()

    def _build_widgets(self):
        """Create the widgets inside the mobile connection window."""
        self.lbl_qr = ctk.CTkLabel(self, text="Starting server...", font=ctk.CTkFont(size=12))
        self.lbl_qr.pack(padx=20, pady=(24, 12))

        self.lbl_hint = ctk.CTkLabel(
            self,
            text="Scan with your phone",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="gray60",
        )
        self.lbl_hint.pack(padx=20, pady=(0, 12))

        self.lbl_status = ctk.CTkLabel(
            self,
            text="Mobile idle",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=MOBILE_STATUS_IDLE_COLOR,
        )
        self.lbl_status.pack(padx=20, pady=(0, 6))

        self.lbl_device = ctk.CTkLabel(
            self,
            text="No device connected",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
        )
        self.lbl_device.pack(padx=20, pady=(0, 16))

    def start_server(self):
        """Start the mobile Flask server in a background thread."""
        try:
            self.server_runtime = MobileServerRuntime(port=MOBILE_SERVER_PORT)
            self.server_runtime.start()
            url = self.server_runtime.server_url
            self._generate_qr(url)
            logger.info("Started mobile server at %s", url)
        except Exception as e:
            logger.error("Failed to start mobile server: %s", e)
            self.lbl_qr.configure(text="Server failed to start")

    def _generate_qr(self, target_url: str) -> None:
        """Generate a QR code image and display it in the window."""
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(target_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img = img.resize((MOBILE_QR_SIZE, MOBILE_QR_SIZE), Image.LANCZOS)

        self.qr_image_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(MOBILE_QR_SIZE, MOBILE_QR_SIZE))
        self.lbl_qr.configure(image=self.qr_image_tk, text="")

    def refresh_status(self) -> None:
        """Periodically update connection labels based on runtime info."""
        if self.server_runtime:
            info = self.server_runtime.get_connection_info()
            if info.get("connected"):
                self.lbl_status.configure(text="Mobile Connected", text_color=MOBILE_STATUS_CONNECTED_COLOR)
                device = info.get("device_name") or "Unknown device"
                self.lbl_device.configure(text=f"Device: {device}")
            else:
                self.lbl_status.configure(text="Mobile idle", text_color=MOBILE_STATUS_IDLE_COLOR)
                self.lbl_device.configure(text="No device connected")
        self.after(MOBILE_POLL_INTERVAL_MS, self.refresh_status)

    def on_close(self) -> None:
        """Clean up server runtime and destroy window."""
        if self.server_runtime:
            try:
                self.server_runtime.stop()
            except Exception as e:
                logger.error("Error stopping mobile server: %s", e)
        self.destroy()