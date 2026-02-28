import logging
import os
import queue
import socket
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from venv import logger

from flask import Flask, jsonify, render_template, request
from PIL import Image
from werkzeug.serving import make_server

APP_NAME = "Open Insect Orga - Mobile Upload"
DEFAULT_PORT = 3630
UPLOAD_PREFIX = "mobile_upload_"
CONNECTION_TIMEOUT_SECONDS = 120
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}

MODULE_DIRECTORY = Path(__file__).resolve().parent
TEMPLATES_DIRECTORY = MODULE_DIRECTORY / "templates"
# static folder removed; CSS now inlined in HTML
UPLOAD_DIRECTORY = MODULE_DIRECTORY / "uploads"
# Queue partagée avec le desktop
IMAGE_QUEUE: queue.Queue[str] = queue.Queue()

LOGGER = logging.getLogger("mobile_server")
if not LOGGER.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    LOGGER.addHandler(stream_handler)
LOGGER.setLevel(logging.INFO)


# --- Utility Functions ---
def detect_lan_ip_address() -> str:
    """Detect the best LAN IP address for local network access if detected, otherwise 127.0.0.1"""
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        test_socket.connect(("8.8.8.8", 80))
        detected_ip = test_socket.getsockname()[0]
        return detected_ip
    except OSError:
        return "127.0.0.1"
    finally:
        test_socket.close()


def extract_device_name_from_request() -> str:
    """Extract a readable client device name from HTTP headers"""
    explicit_name = request.headers.get("X-Device-Name", "").strip()
    if explicit_name:
        return explicit_name

    user_agent = request.headers.get("User-Agent", "Unknown device")
    truncated_agent = user_agent[:120]
    return truncated_agent


def validate_uploaded_image(uploaded_file_path: str) -> None:
    """Validate uploaded image content by opening it with Pillow"""
    file_extension = Path(uploaded_file_path).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported image extension: {file_extension}")
    with Image.open(uploaded_file_path) as image:
        image.verify()


# --- Mobile Server Runtime ---
class MobileServerRuntime:
    """Manage Flask web server"""

    def __init__(self, port: int = DEFAULT_PORT):
        """Initialize runtime state and Flask application"""
        self.port = port
        self.lan_ip_address = detect_lan_ip_address()
        self.host_device_name = socket.gethostname()

        self._server = None
        self._server_thread = None
        self._is_running = False
        self._connection_lock = threading.Lock()

        self._last_connection_time: Optional[datetime] = None
        self._last_device_name: Optional[str] = None

        self._flask_app = self._build_flask_app()

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def server_url(self) -> str:
        return f"http://{self.lan_ip_address}:{self.port}"

    def _build_flask_app(self) -> Flask:
        """Create and configure the Flask app instance
        """
        flask_app = Flask(
            __name__,
            template_folder=str(TEMPLATES_DIRECTORY),
        )

        @flask_app.before_request
        def log_request_details() -> None:
            """Log incoming connections with timestamp and remote address."""
            LOGGER.info(
                "Incoming request | method=%s path=%s from=%s",
                request.method,
                request.path,
                request.remote_addr,
            )

        @flask_app.route("/", methods=["GET"])
        def index():
            self._mark_connection(extract_device_name_from_request())
            return render_template("index.html")

        @flask_app.route("/upload", methods=["POST"])
        def upload():
            saved_file_path = None
            try:
                if "photo" not in request.files:
                    return jsonify({"status": "error", "message": "Missing file field: photo"}), 400

                uploaded_file = request.files["photo"]
                if uploaded_file.filename is None or uploaded_file.filename.strip() == "":
                    return jsonify({"status": "error", "message": "Empty filename"}), 400

                UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
                suffix = Path(uploaded_file.filename).suffix.lower() or ".jpg"

                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    prefix=UPLOAD_PREFIX,
                    suffix=suffix,
                    dir=str(UPLOAD_DIRECTORY),
                    delete=False,
                ) as temporary_file:
                    uploaded_file.save(temporary_file)
                    saved_file_path = temporary_file.name

                validate_uploaded_image(saved_file_path)
                IMAGE_QUEUE.put(saved_file_path)

                detected_device_name = extract_device_name_from_request()
                self._mark_connection(detected_device_name)

                LOGGER.info("Upload accepted | saved_path=%s", saved_file_path)
                return jsonify({"status": "received", "saved_path": saved_file_path}), 200

            except ValueError as validation_error:
                if saved_file_path and os.path.exists(saved_file_path):
                    os.remove(saved_file_path)
                LOGGER.warning("Upload rejected | reason=%s", validation_error)
                return jsonify({"status": "error", "message": str(validation_error)}), 415
            except Exception as upload_error:
                if saved_file_path and os.path.exists(saved_file_path):
                    os.remove(saved_file_path)
                LOGGER.exception("Upload processing failed: %s", upload_error)
                return jsonify({"status": "error", "message": "Server processing error"}), 500

        @flask_app.route("/status", methods=["GET"])
        def status():
            return jsonify({"app_name": APP_NAME, "device_name": self.host_device_name}), 200

        return flask_app

    def _mark_connection(self, device_name: str) -> None:
        with self._connection_lock:
            self._last_connection_time = datetime.utcnow()
            self._last_device_name = device_name

    def get_connection_info(self) -> Dict[str, Optional[str]]:
        """Return current connection for desktop status, returns connected flag and latest client device name."""
        with self._connection_lock:
            has_recent_connection = False
            if self._last_connection_time is not None:
                elapsed = (datetime.now() - self._last_connection_time).total_seconds()
                has_recent_connection = elapsed <= CONNECTION_TIMEOUT_SECONDS

            return {
                "connected": has_recent_connection,
                "device_name": self._last_device_name,
            }

    def start(self) -> None:
        """Start Flask server"""
        if self._is_running:
            raise RuntimeError("Mobile server is already running")

        self._server = make_server(self.lan_ip_address, self.port, self._flask_app, threaded=True)
        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()
        self._is_running = True

        LOGGER.info("Mobile server started at %s", self.server_url)

    def stop(self) -> None:
        """Shutdown Flask server and wait for thread completion."""
        if not self._is_running:
            return

        try:
            if self._server is not None:
                self._server.shutdown()
        finally:
            if self._server_thread is not None and self._server_thread.is_alive():
                self._server_thread.join(timeout=2)

            self._is_running = False
            self._server = None
            self._server_thread = None

        LOGGER.info("Mobile server stopped")


if __name__ == "__main__":
    runtime = MobileServerRuntime(port=DEFAULT_PORT)
    runtime.start()
