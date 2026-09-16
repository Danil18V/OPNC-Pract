import socket
import threading
from protocol import send_message, recv_message

HOST = "127.0.0.1"
PORT = 5000


def listen_server(sock):
    """Второй поток: слушает входящие сообщения от сервера."""
    while True:
        try:
            result = recv_message(sock)
            if result is None:
                print("\n[Соединение с сервером потеряно]")
                break
            command, payload = result
            print(f"\n{payload.decode('utf-8')}")
        except (ConnectionResetError, ConnectionError):
            print("\n[Соединение разорвано]")
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
        return

    username = input("Введите имя: ").strip()
    if not username:
        print("Имя не может быть пустым")
        return

    send_message(sock, "JOIN", username.encode("utf-8"))

    listener = threading.Thread(target=listen_server, args=(sock,), daemon=True)
    listener.start()

    print("Команды: просто текст / LIST / QUIT")
    print("---")

    try:
        while True:
            text = input()
            if not text:
                continue
            if text.upper() == "QUIT":
                send_message(sock, "QUIT", b"")
                break
            elif text.upper() == "LIST":
                send_message(sock, "LIST", b"")
            else:
                send_message(sock, "TEXT", text.encode("utf-8"))
    except (BrokenPipeError, ConnectionResetError):
        print("\n[Соединение потеряно]")
    except KeyboardInterrupt:
        send_message(sock, "QUIT", b"")
    finally:
        sock.close()
        print("Отключились от сервера")


if __name__ == "__main__":
    main()