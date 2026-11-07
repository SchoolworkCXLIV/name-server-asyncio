import asyncio
import json
from datetime import datetime


class NameServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.services = { # dizionario con indirizzo/porta dei servizi
            "echo": ("127.0.0.1", 6002),
            "time": ("127.0.0.1", 6001),
        }

    async def start(self, reader, writer):
        try:
            while True:
                data = (await reader.readline()).decode()
                if not data:
                    break

                try:
                    message = json.loads(data)
                    cmd = message.get("cmd")
                    service = message.get("service")

                    if cmd == "lookup":
                        if service in self.services: # controllo se il servizio è presente
                            res = {
                                "status": "ok",
                                "service": service,
                                "host": self.services[service][0],
                                "port": self.services[service][1]
                            }
                        else:
                            res = {"status": "error", "message": "service not found"}
                    elif cmd == "list":
                        res = {"status": "ok", "services": list(self.services.keys())}
                    elif cmd == "register":
                        # sintassi = register nomeservizio ip porta
                        self.services[message.get("name")] = (message.get("ip"), message.get("port"))
                        res = {"status": "ok", "name": list(self.services)[-1], "ip": self.services[message.get("name")][0], "port": self.services[message.get("name")][1]}
                    else:
                        res = {"status": "error", "message": "unknown command"}
                except json.JSONDecodeError:
                    res = {"status": "error", "message": "invalid json"}
                except Exception as e:
                    res = {"status": "error", "message": str(e)}

                writer.write((json.dumps(res) + "\n").encode())
                await writer.drain()
        except Exception as e:
            print(f"Errore NameServer: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


class TimeServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def start(self, reader, writer):
        try:
            while True:
                data = (await reader.readline()).decode()
                if not data:
                    break

                try:
                    message = json.loads(data)
                    cmd = message.get("cmd")

                    if cmd == "time":
                        res = {
                            "status": "ok",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    else:
                        res = {"status": "error", "message": "unknown command"}
                except json.JSONDecodeError:
                    res = {"status": "error", "message": "invalid json"}
                except Exception as e:
                    res = {"status": "error", "message": str(e)}

                writer.write((json.dumps(res) + "\n").encode())
                await writer.drain()
        except Exception as e:
            print(f"Errore TimeServer: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


class EchoServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def start(self, reader, writer):
        try:
            while True:
                data = (await reader.readline()).decode()
                if not data:
                    break

                try:
                    message = json.loads(data)
                    cmd = message.get("cmd")

                    if cmd == "echo":
                        if "text" in message:
                            res = {
                                "status": "ok",
                                "text": message["text"]
                            }
                        else:
                            res = {"status": "error", "message": "missing text field"}
                    else:
                        res = {"status": "error", "message": "unknown command"}
                except json.JSONDecodeError:
                    res = {"status": "error", "message": "invalid json"}
                except Exception as e:
                    res = {"status": "error", "message": str(e)}

                writer.write((json.dumps(res) + "\n").encode())
                await writer.drain()
        except Exception as e:
            print(f"Errore EchoServer: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


async def main():
    name_server_instance = NameServer(host="127.0.0.1", port=6000)
    time_server_instance = TimeServer(host="127.0.0.1", port=6001)
    echo_server_instance = EchoServer(host="127.0.0.1", port=6002)

    server_name = await asyncio.start_server(
        name_server_instance.start,
        host=name_server_instance.host,
        port=name_server_instance.port
    )

    server_time = await asyncio.start_server(
        time_server_instance.start,
        host=time_server_instance.host,
        port=time_server_instance.port
    )

    server_echo = await asyncio.start_server(
        echo_server_instance.start,
        host=echo_server_instance.host,
        port=echo_server_instance.port
    )

    print(f"NameServer attivo su {name_server_instance.host}:{name_server_instance.port}")
    print(f"TimeServer attivo su {time_server_instance.host}:{time_server_instance.port}")
    print(f"EchoServer attivo su {echo_server_instance.host}:{echo_server_instance.port}")

    async with server_name, server_time, server_echo:
        await asyncio.gather(server_name.serve_forever(), server_time.serve_forever(), server_echo.serve_forever())


if __name__ == "__main__":
    asyncio.run(main())
