import asyncio
import websockets
import subprocess
import os
import json
import socket

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("WEBSOCKET_PORT", "8765")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))
SCAN_TARGET = os.getenv("SCAN_TARGET", None)  # Permet de forcer une IP cible

def get_host_ip():
    """
    Détecte l'IP de l'hôte Windows depuis le conteneur Docker.
    Sur Docker Desktop Windows, utilise host.docker.internal ou la gateway par défaut.
    """
    if SCAN_TARGET:
        return SCAN_TARGET
    
    # Essayer d'abord host.docker.internal (fonctionne sur Docker Desktop)
    try:
        host_ip = socket.gethostbyname("host.docker.internal")
        print(f"IP hôte détectée via host.docker.internal: {host_ip}")
        return host_ip
    except socket.gaierror:
        pass
    
    # Sinon, utiliser la gateway par défaut du conteneur (généralement l'hôte)
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Extraire l'IP de la gateway (premier champ après "default via")
            parts = result.stdout.strip().split()
            if "via" in parts:
                idx = parts.index("via")
                if idx + 1 < len(parts):
                    gateway_ip = parts[idx + 1]
                    print(f"IP hôte détectée via gateway: {gateway_ip}")
                    return gateway_ip
    except Exception as e:
        print(f"Erreur lors de la détection de la gateway: {e}")
    
    # Fallback: utiliser host.docker.internal même si la résolution DNS échoue
    # Sur Windows Docker Desktop, cela devrait fonctionner
    print("Utilisation de host.docker.internal comme fallback")
    return "host.docker.internal"

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
    
    # Détecter l'IP de l'hôte une fois au démarrage
    host_ip = get_host_ip()
    print(f"IP cible pour les scans: {host_ip}")

    async with websockets.connect(uri) as websocket:
        print("Connecté au serveur.")

        while True:
            print(f"Scan automatique : {host_ip}")
            output = await run_nmap(host_ip)

            await websocket.send(json.dumps({
                "status": "auto-scan",
                "target": host_ip,
                "output": output
            }))

            await asyncio.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    asyncio.run(agent_loop())