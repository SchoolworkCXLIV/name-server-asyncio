import asyncio
import json
from datetime import datetime


class NameServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.diz = {
            "echo": ("127.0.0.1", 6002),
            "time": ("127.0.0.1", 6001),
        }

    async def start(self, reader, writer):
        try:
            data = (await reader.readline()).decode()
            if not data:
                return

            message = json.loads(data)
            cmd = message.get("cmd")
            service = message.get("service")
            res = {}

            if cmd == "lookup":
                if service in self.diz:
                    res = {
                        "status": "ok",
                        "service": service,
                        "host": self.diz[service][0],
                        "port": self.diz[service][1]
                    }
                else:
                    res = {"status": "error", "message": "service not found"}
            else:
                res = {"status": "error", "message": "unknown command"}

            writer.write((json.dumps(res) + "\n").encode())
            await writer.drain()  # Aggiunto await
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
            data = (await reader.readline()).decode()
            if not data:
                return

            message = json.loads(data)
            cmd = message.get("cmd")

            if cmd == "time":
                res = {
                    "status": "ok",
                    "time": datetime.now().isoformat()
                }
            else:
                res = {"status": "error", "message": "unknown command"}

            writer.write((json.dumps(res) + "\n").encode())
            await writer.drain()
        except Exception as e:
            print(f"Errore TimeServer: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


async def main():
    name_server_instance = NameServer(host="127.0.0.1", port=6000)
    time_server_instance = TimeServer(host="127.0.0.1", port=6001)

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

    print(f"NameServer attivo su {name_server_instance.host}:{name_server_instance.port}")
    print(f"TimeServer attivo su {time_server_instance.host}:{time_server_instance.port}")

    # Avvia entrambi i server contemporaneamente
    async with server_name, server_time:
        await asyncio.gather(server_name.serve_forever(), server_time.serve_forever())


if __name__ == "__main__":
    asyncio.run(main())
