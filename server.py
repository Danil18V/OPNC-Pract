import socket
import threading
from protocol import send_message, recv_message

HOST = "127.0.0.1"
PORT = 5000

clients = {}
clients_lock = threading.Lock()


def broadcast(sender_sock, command, message: str):
    with clients_lock:
        recipients = list(clients.keys())
    for sock in recipients:
        if sock == sender_sock:
            continue
        try:
            send_message(sock, command, message.encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass


def handle_client(sock, addr):
    username = None
    try:
        while True:
            result = recv_message(sock)
            if result is None:
                break

            command, payload = result
            payload_str = payload.decode("utf-8")

            if command == "JOIN":
                username = payload_str
                with clients_lock:
                    clients[sock] = username
                print(f"[{username}] присоединился из {addr}")
                broadcast(sock, "TEXT", f"*** {username} вошёл в чат ***")

            elif command == "TEXT":
                if username is None:
                    send_message(sock, "ERROR", "Сначала отправьте JOIN".encode("utf-8"))

                    continue
                full_msg = f"{username}: {payload_str}"
                print(f"Сообщение от {username}: {payload_str}")
                broadcast(sock, "TEXT", full_msg)

            elif command == "LIST":
                with clients_lock:
                    user_list = "\n".join(clients.values())
                send_message(sock, "TEXT", f"Пользователи онлайн:\n{user_list}")

            elif command == "QUIT":
                break

            else:
                send_message(sock, "ERROR", f"Неизвестная команда: {command}".encode("utf-8"))

    except (ConnectionResetError, ConnectionError, BrokenPipeError):
        print(f"Клиент {addr} отключился аварийно")
    except Exception as e:
        print(f"Ошибка с клиентом {addr}: {e}")
    finally:
        with clients_lock:
            if sock in clients:
                del clients[sock]
        if username:
            broadcast(sock, "TEXT", f"*** {username} покинул чат ***")
            print(f"[{username}] покинул чат")
        sock.close()
        print(f"Соединение с {addr} закрыто")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"Сервер запущен на {HOST}:{PORT}")

    try:
        while True:
            sock, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(sock, addr), daemon=True)
            thread.start()
            print(f"Новое подключение: {addr} (потоков активно: {threading.active_count() - 1})")
    except KeyboardInterrupt:
        print("\nСервер останавливается...")
    finally:
        server.close()


if __name__ == "__main__":
    main()