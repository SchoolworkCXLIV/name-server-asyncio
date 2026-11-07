import asyncio
import json

NAME_SERVER_HOST = "127.0.0.1"
NAME_SERVER_PORT = 6000


async def send_json(writer, msg_dict):
    """invia json"""
    payload = (json.dumps(msg_dict) + "\n").encode()
    writer.write(payload)
    await writer.drain()


async def receive_json(reader):
    """legge e decodifica il json del server"""
    data = await reader.readline()
    if not data:
        return None
    return json.loads(data.decode())


async def request_service_address(service_name):
    """si connette al nameserver e richiede un servizio"""
    print(
        f"[Client] Connessione al NameServer ({NAME_SERVER_HOST}:{NAME_SERVER_PORT})..."
    )
    reader, writer = await asyncio.open_connection(
        NAME_SERVER_HOST, NAME_SERVER_PORT
    )

    try:
        # lookup
        req = {"cmd": "lookup", "service": service_name}
        print(f"[Client -> NameServer]: {req}")
        await send_json(writer, req)

        # risposta lookup
        res = await receive_json(reader)
        print(f"[NameServer -> Client]: {res}\n")
        return res
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    # test time server
    print("TEST TIME SERVER")
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

    # test echo server
    print("TEST ECHO SERVER")
    lookup_echo = await request_service_address("echo")

    if lookup_echo and lookup_echo.get("status") == "ok":
        host = lookup_echo["host"]
        port = lookup_echo["port"]

        print(f"[Client] Connessione al Echo Server ({host}:{port})...")
        reader, writer = await asyncio.open_connection(host, port)
        try:
            req = {"cmd": "echo", "text": "ciaociaociaociaociaociaociaociaociao"}
            print(f"[Client -> EchoServer]: {req}")
            await send_json(writer, req)

            res = await receive_json(reader)
            print(f"[EchoServer -> Client]: {res}\n")
        finally:
            writer.close()
            await writer.wait_closed()

    # test errori
    print("TEST ERRORI")
    # servizio inesistente
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

    # json non valido
    print("[Client] Invio json non valido")
    reader, writer = await asyncio.open_connection(
        NAME_SERVER_HOST, NAME_SERVER_PORT
    )
    try:
        stringa_invalida = "FAKEASS_JSON\n"
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
