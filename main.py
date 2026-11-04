import asyncio
import json
from datetime import datetime

class NameServer:
    # 127.0.0.1 - 6000 - Restituisce host e porta del servizio richiesto
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.diz = {
            "echo": ("127.0.0.1", 6002),
            "time": ("127.0.0.1", 6001),
        }

    async def start(self, reader, writer):
        # cmd_list = ["lookup", "echo"]
        while True:
            data = await reader.readline().decode()
            message = json.loads(data)
            cmd = message["cmd"]
            service = message["service"]
            res = {}
            if cmd == "lookup":
                if service in self.diz.keys():
                    res = {
                        "status": "ok",
                        "service": service,
                        "host": self.diz[service][0],
                        "port": self.diz[service][1]
                    }
                else:
                    res = {
                        "status": "error",
                        "message": "service not found"
                    }
            else:
                res = {
                    "status": "error",
                    "message": "unknown command"
                }
            writer.write(json.dumps(res).encode())
            writer.drain()
            writer.close()
            await writer.wait_closed()

class TimeServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def start(self, reader, writer):
        while True:
            data = await reader.readline().decode()
            message = json.loads(data)
            cmd = message["cmd"]
            if cmd == "time":
                res = {
                    "status": "ok",
                    "time": datetime.now()
                }
            else:
                res = {
                    "status": "error",
                    "message": "unknown command"
                }

            writer.write(json.dumps(res).encode())
            writer.drain()
            writer.close()
            await writer.wait_closed()


async def main():
    nameServer = NameServer(host="127.0.0.1", port=6000)
    server = await asyncio.start_server(nameServer.start())

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())




