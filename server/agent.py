import asyncio
import websockets
import subprocess
import os
import json

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("WEBSOCKET_PORT", "8765")

async def run_nmap(command: str) -> str:
    """Exécute nmap et renvoie la sortie brute."""
    try:
        result = subprocess.run(
            ["nmap"] + command.split(),
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
            message = await websocket.recv()
            print(f"Commande reçue : {message}")

            try:
                data = json.loads(message)
                cmd = data.get("command")
            except:
                cmd = message

            output = await run_nmap(cmd)

            await websocket.send(json.dumps({
                "status": "done",
                "command": cmd,
                "output": output
            }))

if __name__ == "__main__":
    asyncio.run(agent_loop())
