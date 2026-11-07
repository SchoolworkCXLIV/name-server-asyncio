import asyncio
import json

NAME_SERVER_HOST = "127.0.0.1"
NAME_SERVER_PORT = 6000


async def send_json(writer, msg_dict):
    """Invia un messaggio JSON terminato da newline."""
    payload = (json.dumps(msg_dict) + "\n").encode()
    writer.write(payload)
    await writer.drain()


async def receive_json(reader):
    """Legge una riga dal server e la decodifica come JSON."""
    data = await reader.readline()
    if not data:
        return None
    return json.loads(data.decode())


async def request_service_address(service_name):
    """Fase 1 e 2: Interroga il Name Server per ottenere host e porta di un servizio."""
    print(
        f"[Client] Connessione al Name Server ({NAME_SERVER_HOST}:{NAME_SERVER_PORT})..."
    )
    reader, writer = await asyncio.open_connection(
        NAME_SERVER_HOST, NAME_SERVER_PORT
    )

    try:
        # Richiesta lookup
        req = {"cmd": "lookup", "service": service_name}
        print(f"[Client -> NameServer]: {req}")
        await send_json(writer, req)

        # Risposta lookup
        res = await receive_json(reader)
        print(f"[NameServer -> Client]: {res}\n")
        return res
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    # -----------------------------------------------------------------
    # TEST 1: Richiesta e utilizzo del TIME SERVER
    # -----------------------------------------------------------------
    print("--- TEST TIME SERVER ---")
    lookup_time = await request_service_address("time")

    if lookup_time and lookup_time.get("status") == "ok":
        host = lookup_time["host"]
        port = lookup_time["port"]

        print(f"[Client] Connessione al Time Server ({host}:{port})...")
        reader, writer = await asyncio.open_connection(host, port)
        try:
            req = {"cmd": "time"}
            print(f"[Client -> TimeServer]: {req}")
            await send_json(writer, req)

            res = await receive_json(reader)
            print(f"[TimeServer -> Client]: {res}\n")
        finally:
            writer.close()
            await writer.wait_closed()

    # -----------------------------------------------------------------
    # TEST 2: Richiesta e utilizzo del ECHO SERVER
    # -----------------------------------------------------------------
    print("--- TEST ECHO SERVER ---")
    lookup_echo = await request_service_address("echo")

    if lookup_echo and lookup_echo.get("status") == "ok":
        host = lookup_echo["host"]
        port = lookup_echo["port"]

        print(f"[Client] Connessione al Echo Server ({host}:{port})...")
        reader, writer = await asyncio.open_connection(host, port)
        try:
            req = {"cmd": "echo", "text": "ciao a tutti dal laboratorio!"}
            print(f"[Client -> EchoServer]: {req}")
            await send_json(writer, req)

            res = await receive_json(reader)
            print(f"[EchoServer -> Client]: {res}\n")
        finally:
            writer.close()
            await writer.wait_closed()

    # -----------------------------------------------------------------
    # TEST 3: Gestione degli errori (Servizio inesistente e JSON invalido)
    # -----------------------------------------------------------------
    print("--- TEST GESTIONE ERRORI ---")
    # A. Servizio inesistente
    print("[Client] Test servizio inesistente sul Name Server...")
    reader, writer = await asyncio.open_connection(
        NAME_SERVER_HOST, NAME_SERVER_PORT
    )
    try:
        req = {"cmd": "lookup", "service": "xyz"}
        print(f"[Client -> NameServer]: {req}")
        await send_json(writer, req)
        res = await receive_json(reader)
        print(f"[NameServer -> Client]: {res}\n")
    finally:
        writer.close()
        await writer.wait_closed()

    # B. Stringa JSON non valida (Verifica che il server risponda e rimanga attivo)
    print("[Client] Invio di una stringa malformata (JSON non valido)...")
    reader, writer = await asyncio.open_connection(
        NAME_SERVER_HOST, NAME_SERVER_PORT
    )
    try:
        stringa_invalida = "QUESTO_NON_E_UN_JSON\n"
        print(f"[Client -> NameServer]: {stringa_invalida.strip()}")
        writer.write(stringa_invalida.encode())
        await writer.drain()

        res = await receive_json(reader)
        print(f"[NameServer -> Client]: {res}\n")
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
