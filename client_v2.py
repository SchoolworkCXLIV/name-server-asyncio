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


async def ainput(prompt):
    """input asincrono per non bloccare asyncio"""
    return await asyncio.to_thread(input, prompt)


async def usa_servizio(service_name, host, port):
    """apre connessione al servizio trovato e manda richieste"""
    print(f"\n[Client] Connessione a {service_name} ({host}:{port})...")
    reader, writer = await asyncio.open_connection(host, int(port))

    try:
        while True:
            if service_name == "time":
                req = {"cmd": "time"}
            elif service_name == "echo":
                testo = await ainput("Scrivi testo da mandare (oppure 'esci'): ")
                if testo == "esci":
                    break
                req = {"cmd": "echo", "text": testo}
            else:
                cmd = await ainput(f"Comando per {service_name} (oppure 'esci'): ")
                if cmd == "esci":
                    break
                req = {"cmd": cmd}

            print(f"[Client -> {service_name}]: {req}")
            await send_json(writer, req)

            res = await receive_json(reader)
            print(f"[{service_name} -> Client]: {res}\n")

            # per time basta una volta, poi chiedo se rifare
            if service_name == "time":
                ancora = await ainput("Chiedere di nuovo l'ora? (s/n): ")
                if ancora.lower() != "s":
                    break
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"[Client] Disconnesso da {service_name}\n")


async def main():
    print(f"[Client] Connessione al NameServer ({NAME_SERVER_HOST}:{NAME_SERVER_PORT})...")
    reader, writer = await asyncio.open_connection(NAME_SERVER_HOST, NAME_SERVER_PORT)

    try:
        while True:
            print("--- MENU ---")
            print("1 - lookup (cerca e usa servizio)")
            print("2 - register (registra nuovo servizio)")
            print("3 - list (lista servizi)")
            print("0 - esci")

            scelta = (await ainput("Scegli: ")).strip()

            if scelta == "0":
                print("Ciao!")
                break

            elif scelta == "1":
                servizio = (await ainput("Nome servizio (es. time, echo): ")).strip()
                req = {"cmd": "lookup", "service": servizio}
                print(f"[Client -> NameServer]: {req}")
                await send_json(writer, req)

                res = await receive_json(reader)
                print(f"[NameServer -> Client]: {res}\n")

                # se lo trova, chiedo se vuole connettersi subito
                if res and res.get("status") == "ok":
                    vai = (await ainput("Vuoi usarlo ora? (s/n): ")).strip().lower()
                    if vai == "s":
                        await usa_servizio(servizio, res["host"], res["port"])

            elif scelta == "2":
                nome = (await ainput("Nome servizio: ")).strip()
                ip = (await ainput("IP (es. 127.0.0.1): ")).strip()
                porta = (await ainput("Porta: ")).strip()

                # nota: converto porta in int così è coerente col dizionario del server
                req = {"cmd": "register", "name": nome, "ip": ip, "port": int(porta)}
                print(f"[Client -> NameServer]: {req}")
                await send_json(writer, req)

                res = await receive_json(reader)
                print(f"[NameServer -> Client]: {res}\n")

            elif scelta == "3":
                req = {"cmd": "list"}
                print(f"[Client -> NameServer]: {req}")
                await send_json(writer, req)

                res = await receive_json(reader)
                print(f"[NameServer -> Client]: {res}\n")


    finally:
        writer.close()
        await writer.wait_closed()
        print("[Client] Connessione chiusa.")


if __name__ == "__main__":
    asyncio.run(main())
