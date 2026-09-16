import struct
print(f"--- ЗАГРУЖЕН ПРОТОКОЛ ИЗ: {__file__}")


COMMAND_SIZE = 4
MAX_MESSAGE_SIZE = 10 * 1024 * 1024


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Соединение закрыто")
        data += chunk
    return data


def send_message(sock, command: str, payload: bytes) -> None:
    cmd_bytes = command.encode("utf-8")[:COMMAND_SIZE]
    cmd_bytes = cmd_bytes.ljust(COMMAND_SIZE, b"\x00")

    length = len(payload)
    if length > MAX_MESSAGE_SIZE:
        raise ValueError("Сообщение слишком большое")

    header = cmd_bytes + struct.pack("!I", length)
    sock.sendall(header + payload)


def recv_message(sock):
    try:
        header = recv_exact(sock, COMMAND_SIZE + 4)
    except ConnectionError:
        return None

    command = header[:COMMAND_SIZE].rstrip(b"\x00").decode("utf-8")

    # !!! ИСПРАВЛЕНИЕ: добавляем, чтобы получить число из кортежа
    length = struct.unpack("!I", header[COMMAND_SIZE:])

    if length > MAX_MESSAGE_SIZE:
        raise ValueError("Получено слишком большое сообщение")

    if length == 0:
        return command, b""

    payload = recv_exact(sock, length)
    return command, payload