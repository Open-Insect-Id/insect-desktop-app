# Open Insect Id desktop app

This is the desktop app for our AI model, made in python using Tkinter and CustomTkinter

<details>
<summary>Troubleshooting</summary>

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
   - Run the app directly from a host terminal outside of VS Code (see detailed tutorial below).

3. **Use system Python:**
   Ensure you're using the system Python that has tkinter. You can check with `python3 -c "import tkinter"`.

After installing, recreate the virtual environment if necessary.

#### Detailed Tutorial: Running from an External Terminal on Linux

Since the terminal inside VS Code Flatpak is sandboxed and doesn't have access to tkinter, you need to run the app from your system's native terminal. Follow these steps:

1. **Open a system terminal:**
   - Press `Ctrl + Alt + T` on your keyboard (this works on most Linux distributions like Ubuntu, Fedora, etc.).
   - Alternatively, search for "Terminal" or "Konsole" in your applications menu and open it.

2. **Navigate to the project directory:**
   - Use the `cd` command to change to the directory where the project is located. Replace the path with your actual path:
     ```
     cd /insect-desktop-app
     ```
   - You can confirm you're in the right place by running `ls` and checking for files like `main.py` and `requirements.txt`.

3. **Activate the virtual environment (if you created one):**
   - If you have a `.venv` folder from earlier setup, activate it:
     ```
     source .venv/bin/activate
     ```
   - Your prompt should change to show `(.venv)` at the beginning, indicating the virtual environment is active.

4. **Install dependencies (if not already done):**
   - If the virtual environment is new or you recreated it, install the required packages:
     ```
     pip install -r requirements.txt
     ```

5. **Run the application:**
   - Execute the main script:
     ```
     python main.py
     ```
   - The GUI window should open. If you get the tkinter error again, proceed to the next step.

6. **If tkinter is still missing:**
   - Exit the virtual environment with `deactivate`.
   - Install tkinter on your system (see Solution 1 above).
   - Recreate the virtual environment to include tkinter:
     ```
     rm -rf .venv
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
   - Then run `python main.py` again.

This method runs the app in your host system's environment, where tkinter and GUI libraries are properly accessible.

</details>

