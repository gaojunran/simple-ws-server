import asyncio
import websockets
import argparse
import sys

# Store all connected clients
connected_clients = set()
def msg(msg_str: str):
    print(f"\033[34m{msg_str}\033[0m")

async def handle_client(websocket):
    # When a client connects, add to the set and print a notification message
    connected_clients.add(websocket)
    msg(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            # When a message is received from the client, print it to the console
            msg(f"Message received from client {websocket.remote_address}: {message}")
    except websockets.ConnectionClosed:
        pass
    finally:
        # When the client disconnects, remove from the set and print a notification message
        connected_clients.remove(websocket)
        msg(f"Client disconnected: {websocket.remote_address}")

async def broadcast_message(message):
    # Broadcast the message to all connected clients
    if connected_clients:  # Ensure there are connected clients
        # Use asyncio.gather instead of asyncio.wait
        await asyncio.gather(*(client.send(message) for client in connected_clients))

async def main(port):
    # Start the WebSocket server
    server = await websockets.serve(handle_client, "localhost", port)
    msg(f"WebSocket server started, listening on port {port}.")

    # Continuously receive user input and broadcast messages
    loop = asyncio.get_event_loop()
    while True:
        try:
            # Use a thread pool to read standard input to avoid blocking the event loop
            message = await loop.run_in_executor(None, sys.stdin.readline)
            message = message.strip()
            if message:  # Avoid broadcasting empty messages
                await broadcast_message(message)
        except KeyboardInterrupt:
            msg("\nServer is shutting down...")
            server.close()
            await server.wait_closed()
            break

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="WebSocket server")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port to listen on, default is 8080")
    args = parser.parse_args()

    # Start the event loop
    try:
        asyncio.run(main(args.port))
    except KeyboardInterrupt:
        msg("\nServer has been closed")
