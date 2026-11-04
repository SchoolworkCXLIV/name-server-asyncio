import asyncio
import random

# reader: oggetto usato per ricevere byte dal client. asincrono perche deve aspettare i dati
# writer: inviare byte al client, usa un buffer


class ClassDevice:
    def __init__(self):
        self.lista_comandi = ["TEMP", "UMIDITA", "LED ON", "LED OFF", "STATO", "QUIT"] # lista comandi per controllo
        # stato condiviso del sensore
        self.comandi = {
            "TEMP": 25,
            "UMIDITA": 45,
            "LED": "OFF"
        }

    async def device(self, reader, writer):
        addr = writer.get_extra_info('peername') # ottiene nome client
        print(f"Nuova connessione da {addr}")

        try:
            while True:
                data = await reader.readline()
                # dati vuoti --> disconnessione
                if not data:
                    print(f"Client {addr} si è disconnesso improvvisamente.")
                    break

                comm = (data.decode().strip()).upper() # ricava il comando dai dati ricevuti: decodifica, toglie blanks inutili, trasforma in maiuscolo

                if comm not in self.lista_comandi:
                    writer.write("ERR Comando non riconosciuto\n".encode()) # mette i dati da mandare in un buffer
                    await writer.drain() # manda il buffer di writer.write, ferma il programma per dare il tempo al sistema di mandare i dati
                    continue # non break, altrimenti a ogni errore fermerebbe il programma

                if comm == "LED ON":
                    self.comandi["LED"] = "ON"
                    writer.write(f"OK LED impostato a {self.comandi['LED']}\n".encode())

                elif comm == "LED OFF":
                    self.comandi["LED"] = "OFF"
                    writer.write(f"OK LED impostato a {self.comandi['LED']}\n".encode())

                elif comm == "STATO":
                    r = f"OK temp {self.comandi['TEMP']} C - umidita {self.comandi['UMIDITA']}% - LED {self.comandi['LED']}\n"
                    writer.write(r.encode())

                elif comm == "UMIDITA":
                    self.comandi["UMIDITA"] = random.randint(30, 80)
                    writer.write(f"OK {self.comandi['UMIDITA']}%\n".encode())

                elif comm == "TEMP":
                    self.comandi["TEMP"] = round(random.uniform(18.0, 28.0), 1)
                    writer.write(f"OK {self.comandi['TEMP']} C\n".encode())

                elif comm == "QUIT":
                    writer.write("OK Connessione in chiusura\n".encode())
                    await writer.drain()
                    break

                # unico drain alla fine dell'elaborazione del comando invece che in ogni comando
                await writer.drain()

        except Exception as e:
            print(f"Errore per il client {addr}: {e}")
        finally:
            print(f"Chiusura connessione con {addr}") # chiusura con QUIT
            writer.close() # dichiara che la connessione deve finire
            await writer.wait_closed() # attende la chiusura effettiva della connessione
            # evita che il programma faccia altre cose dopo aver chiuso la connessione o che la connessione rimanga

async def main():
    dev = ClassDevice() # istanza la classe
    server = await asyncio.start_server(dev.device, "127.0.0.1", 8000)
    print("Server in ascolto sulla porta 8000...")

    async with server: # ciclo del server, quando si esce dal ciclo chiude tutto
        await server.serve_forever() # accettare connessioni all'infinito

if __name__ == "__main__":
    asyncio.run(main()) # avvia il programma principale