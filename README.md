# Open Insect Id desktop app

This is the desktop app for our AI model, made in python using Tkinter and CustomTkinter

## Troubleshooting

### ModuleNotFoundError: No module named 'tkinter'

If you encounter this error when running the app, it means tkinter is not installed or not available in your Python environment.

Tkinter is part of the standard Python library, but on some systems (especially Linux distributions), it may not be included by default.

#### Solutions:

1. **Install tkinter system-wide (Linux):**
   - On Ubuntu/Debian: `sudo apt-get install python3-tk`
   - On Fedora: `sudo dnf install python3-tkinter`
   - On Arch: `sudo pacman -S tk`

2. **Run outside of Flatpak VS Code:**
   If you're using VS Code installed via Flatpak, tkinter may not be available due to sandboxing. The Flatpak version of VS Code uses a sandboxed Python environment that doesn't include tkinter. Try one of the following:
   - Install VS Code natively (not via Flatpak) to access the system Python with tkinter.
   - Run the app directly from a host terminal outside of VS Code.

3. **Use system Python:**
   Ensure you're using the system Python that has tkinter. You can check with `python3 -c "import tkinter"`.

After installing, recreate the virtual environment if necessary.

