import socket
import threading

# Server settings
host = '0.0.0.0'
port = 55555

# List of connected clients
clients = []

# Create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

print("Server is running...")

def broadcast(message):
    for client in clients[:]:  # Use a shallow copy
        try:
            client.send(message)
        except BrokenPipeError:
            clients.remove(client)
            client.close()
        except Exception as e:
            print("Broadcast error:", e)

def handle(client):
    try:
        username = client.recv(1024).decode('utf-8').strip()

        # Ignore HTTP health checks or bots
        if username.startswith("GET") or username.startswith("HEAD") or "HTTP" in username:
            print("Ignored HTTP client:", username)
            client.close()
            return

        clients.append(client)
        print(f"{username} connected.")
        broadcast(f"{username} joined the chat!".encode('utf-8'))

        while True:
            message = client.recv(1024)
            if not message:
                break
            broadcast(message)

    except Exception as e:
        print("Error in handle():", e)
    finally:
        if client in clients:
            clients.remove(client)
        client.close()
        broadcast(f"{username} has left the chat.".encode('utf-8'))
        print(f"{username} disconnected.")

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        client.send("Connected to the server.".encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
