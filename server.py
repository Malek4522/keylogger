import asyncio
import websockets
import os
from datetime import datetime
import re

# Fixed variables
HOST_IP = '192.168.100.15'
HOST_PORT = 8000
mac_regex = r"^([0-9A-Fa-f]{2}([-;])){5}([0-9A-Fa-f]{2})$"




# Ensure logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

async def append_to_file(log_file_path, data):
    timestamp = datetime.now().isoformat(sep=' ', timespec='milliseconds')
    with open(log_file_path, 'a') as f:
        f.write(f'[{timestamp}] {data}\n')

active_connections = {}

async def handler(websocket, path):
    try:
        
        user_id = await websocket.recv()  # Receive the first message as user ID
        if(not re.match(mac_regex, user_id)):
            await websocket.send("DUPLICATE_CONNECTION")
            print("hack attempt detected")
            return
            
        if user_id in active_connections:
            print(f"Duplicate connection from User ID: {user_id}")
            await websocket.send("DUPLICATE_CONNECTION")
            return

        await websocket.send("CONNECTED")
        active_connections[user_id] = websocket    
        log_file_path = os.path.join('logs', f'{user_id}.log')  # Use user ID for log file
        print(f"Connection established with User ID: {user_id}")

        async for message in websocket:
            await append_to_file(log_file_path, message)
    except websockets.ConnectionClosed:
        print(f"Connection closed for {user_id}.")
    except Exception as e:
        print(f"Error handling connection: {e}")
    finally:
        if user_id in active_connections and active_connections[user_id] == websocket:
            del active_connections[user_id]
            print(f"Handler for {user_id} terminated.")

async def main():
    server = await websockets.serve(handler, HOST_IP, HOST_PORT)
    await server.wait_closed()

# Run the server
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shut down.")