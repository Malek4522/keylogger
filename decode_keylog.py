import tkinter as tk
from tkinter import filedialog, scrolledtext

def decode_keylog():
    # Create a GUI window
    root = tk.Tk()
    root.title("Keylog Decoder")

    def load_file():
        log_file_path = filedialog.askopenfilename(title="Select Log File")
        if log_file_path:
            with open(log_file_path, "r") as f:
                lines = f.readlines()
            decoded_text = decode_lines(lines)
            text_area.delete(1.0, tk.END)  # Clear the text area
            text_area.insert(tk.END, decoded_text)  # Insert decoded text

    def decode_lines(lines):
        decoded_text = ""
        current_line = ""
        cursor_pos = 0
        for line in lines:
            parts = line.strip().split("] ", 1)
            if len(parts) != 2:
                continue
            timestamp, content = parts
            # Handle special keys in brackets
            if content.startswith("[") and content.endswith("]"):
                key = content[1:-1]  # Remove brackets
                # Handle special keys logic
                if key == "SPACE":
                    current_line = current_line[:cursor_pos] + " " + current_line[cursor_pos:]
                    cursor_pos += 1
                elif key == "ENTER":
                    decoded_text += current_line + "\n"
                    current_line = ""
                    cursor_pos = 0
                elif key == "BACKSPACE":
                    if cursor_pos > 0:
                        current_line = current_line[:cursor_pos-1] + current_line[cursor_pos:]
                        cursor_pos -= 1
                elif key == "DELETE":
                    if cursor_pos < len(current_line):
                        current_line = current_line[:cursor_pos] + current_line[cursor_pos+1:]
                elif key.startswith("CAPS_LOCK:"):
                    caps_lock = key.endswith("ON")
                elif key == "LEFT" and cursor_pos > 0:
                    cursor_pos -= 1
                elif key == "RIGHT" and cursor_pos < len(current_line):
                    cursor_pos += 1
                elif key == "HOME":
                    cursor_pos = 0
                elif key == "END":
                    cursor_pos = len(current_line)
                elif key.startswith("COPIED:"):
                    pass  # Skip logging copied text
                elif key.startswith("PASTED:"):
                    pasted_text = key[7:].strip()  # Remove "PASTED: "
                    current_line = current_line[:cursor_pos] + pasted_text + current_line[cursor_pos:]
                    cursor_pos += len(pasted_text)
                elif key in ["UP", "DOWN", "PAGE_UP", "PAGE_DOWN"]:
                    pass  # These don't affect the text content
            # Handle regular characters
            else:
                current_line = current_line[:cursor_pos] + content + current_line[cursor_pos:]
                cursor_pos += len(content)
        if current_line:
            decoded_text += current_line
        return decoded_text

    # Create UI components
    load_button = tk.Button(root, text="Load Log File", command=load_file)
    load_button.pack(pady=10)

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
    text_area.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    decode_keylog()
