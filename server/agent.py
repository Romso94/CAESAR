import asyncio
import websockets
import subprocess
import os
import json

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("WEBSOCKET_PORT", "8765")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))

async def run_nmap(command: str) -> str:
    try:
        result = subprocess.run(
            ["nmap", "-sV", "-sC"] + command.split(),
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except Exception as e:
        return f"Erreur lors du scan : {e}"

async def agent_loop():
    uri = f"ws://{SERVER_HOST}:{SERVER_PORT}"
    print(f"Connexion à {uri}...")

    async with websockets.connect(uri) as websocket:
        print("Connecté au serveur.")

        while True:
            print(f"Scan automatique : 127.0.0.1")
            output = await run_nmap("127.0.0.1")

            await websocket.send(json.dumps({
                "status": "auto-scan",
                "target": "127.0.0.1",
                "output": output
            }))

            await asyncio.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    asyncio.run(agent_loop())