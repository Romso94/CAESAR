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

def parse_nmap_output(output: str, target: str) -> dict:
    """
    Parse la sortie texte de Nmap et la structure en JSON.
    """
    result = {
        "target": target,
        "host_status": "unknown",
        "latency": None,
        "ports": [],
        "os_info": {},
        "scripts": [],
        "summary": {
            "total_ports_scanned": 0,
            "open_ports": 0,
            "closed_ports": 0,
            "filtered_ports": 0
        }
    }
    
    lines = output.split('\n')
    current_port = None
    in_port_section = False
    in_script_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Détecter le statut de l'hôte
        if "Host is up" in line:
            result["host_status"] = "up"
            # Extraire la latence si présente
            if "latency" in line:
                try:
                    latency_str = line.split("latency")[1].split()[0]
                    result["latency"] = latency_str
                except:
                    pass
        elif "Host is down" in line:
            result["host_status"] = "down"
        
        # Détecter le rapport de scan
        if "Nmap scan report for" in line:
            # Extraire l'IP ou le hostname
            host_info = line.replace("Nmap scan report for", "").strip()
            result["hostname"] = host_info
        
        # Détecter les ports fermés (résumé)
        if "closed" in line.lower() and "ports" in line.lower():
            try:
                closed_count = int(line.split()[0])
                result["summary"]["closed_ports"] = closed_count
            except:
                pass
        
        # Détecter la section des ports
        if "PORT" in line and "STATE" in line and "SERVICE" in line:
            in_port_section = True
            continue
        
        # Parser les ports ouverts
        if in_port_section and line and not line.startswith("-"):
            # Format: PORT/STATE SERVICE VERSION
            parts = line.split()
            if len(parts) >= 3:
                port_info = parts[0].split('/')
                if len(port_info) == 2:
                    port = port_info[0]
                    protocol = port_info[1]
                    state = parts[1]
                    service = parts[2] if len(parts) > 2 else "unknown"
                    version = " ".join(parts[3:]) if len(parts) > 3 else ""
                    
                    port_data = {
                        "port": int(port),
                        "protocol": protocol,
                        "state": state,
                        "service": service,
                        "version": version,
                        "scripts": []
                    }
                    
                    if state == "open":
                        result["summary"]["open_ports"] += 1
                        # Ajouter seulement les ports ouverts (et filtrés si nécessaire)
                        result["ports"].append(port_data)
                        current_port = port_data
                    elif state == "closed":
                        result["summary"]["closed_ports"] += 1
                        # Ne pas ajouter les ports fermés à la liste
                        current_port = None
                    elif state == "filtered":
                        result["summary"]["filtered_ports"] += 1
                        # Ajouter les ports filtrés aussi
                        result["ports"].append(port_data)
                        current_port = port_data
        
        # Parser les informations de version/service détaillées
        if current_port and line.startswith("|_"):
            script_output = line.replace("|_", "").strip()
            current_port["scripts"].append(script_output)
        
        # Parser les scripts hôtes
        if "Host script results:" in line:
            in_script_section = True
            continue
        
        if in_script_section and line.startswith("|"):
            script_line = line.replace("|", "").strip()
            if script_line:
                result["scripts"].append(script_line)
        
        # Parser les informations OS
        if "Service Info:" in line:
            os_info = line.replace("Service Info:", "").strip()
            result["os_info"]["service_info"] = os_info
        if "OS:" in line and "CPE:" in line:
            if "os_info" not in result:
                result["os_info"] = {}
            result["os_info"]["detected_os"] = line
        
        # Parser l'adresse MAC
        if "MAC Address:" in line:
            mac_info = line.replace("MAC Address:", "").strip()
            result["mac_address"] = mac_info.split()[0] if mac_info else None
        
        # Détecter la fin de la section des ports
        if "Service detection performed" in line or "Nmap done:" in line:
            in_port_section = False
            in_script_section = False
    
    result["summary"]["total_ports_scanned"] = (
        result["summary"]["open_ports"] + 
        result["summary"]["closed_ports"] + 
        result["summary"]["filtered_ports"]
    )
    
    return result


async def run_nmap(target: str) -> dict:
    """
    Exécute un scan Nmap et retourne les résultats structurés en JSON.
    Parse la sortie texte de Nmap pour créer une structure JSON.
    """
    try:
        # Exécuter Nmap avec sortie texte standard
        # -sV : détection de version
        # -sC : exécution des scripts par défaut
        result = subprocess.run(
            ["nmap", "-sV", "-sC", target],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        stdout_output = result.stdout if result.stdout else ""
        stderr_output = result.stderr if result.stderr else ""
        
        if result.returncode != 0:
            return {
                "error": True,
                "message": f"Erreur lors de l'exécution de Nmap (code {result.returncode})",
                "stderr": stderr_output,
                "target": target
            }
        
        # Parser la sortie texte et la structurer
        parsed_data = parse_nmap_output(stdout_output, target)
        parsed_data["error"] = False
        parsed_data["format"] = "structured"
        
        return parsed_data
            
    except subprocess.TimeoutExpired:
        return {
            "error": True,
            "message": "Timeout lors du scan Nmap (dépassement de 60 secondes)",
            "target": target,
            "format": "error"
        }
    except FileNotFoundError:
        return {
            "error": True,
            "message": "Nmap n'est pas installé sur le système",
            "target": target,
            "format": "error"
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Erreur lors du scan : {e}",
            "target": target,
            "format": "error"
        }
    
async def run_lynis() -> str:
    """
    Exécute un audit de sécurité avec Lynis.
    Lynis analyse la configuration de sécurité de l'HÔTE via volumes montés.
    L'hôte doit être monté sur /host dans le conteneur.
    Nécessite des droits root pour un audit complet.
    """
    try:
        # Commande Lynis avec options :
        # --rootdir=/host : audite l'hôte monté sur /host
        # --quiet : mode silencieux
        # --quick : audit rapide
        result = subprocess.run(
            ["lynis", "audit", "system", "--quick", "--quiet", "--rootdir=/host"],
            capture_output=True,
            text=True,
            timeout=120  # Lynis peut être plus lent que nmap
        )
        return result.stdout if result.stdout else result.stderr
    except FileNotFoundError:
        return "Erreur : Lynis n'est pas installé sur le système"
    except Exception as e:
        return f"Erreur lors de l'audit Lynis : {e}"


async def agent_loop():
    uri = f"ws://{SERVER_HOST}:{SERVER_PORT}"
    
    # Détecter l'IP de l'hôte une fois au démarrage
    host_ip = get_host_ip()
    print(f"IP cible pour les scans: {host_ip}")

    while True:
        try:
            print(f"Connexion à {uri}...")
            async with websockets.connect(uri) as websocket:
                print("Connecté au serveur.")

                while True:
                    print(f"Scan automatique : {host_ip}")
                    output_nmap = await run_nmap(host_ip)

                    await websocket.send(json.dumps({
                        "status": "auto-scan",
                        "target": host_ip,
                        "output": output_nmap  # Déjà au format dict, sera sérialisé en JSON
                    }))

                    # Lire la réponse du serveur pour éviter de surcharger le buffer
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        print(f"Réponse serveur: {response}")
                    except asyncio.TimeoutError:
                        # Pas de réponse, continuer
                        pass

                    # ===== AUDIT LYNIS =====
                    print("Exécution de l'audit de sécurité Lynis...")
                    output_lynis = await run_lynis()

                    # Envoyer le résultat de l'audit Lynis au serveur
                    await websocket.send(json.dumps({
                        "status": "lynis-audit",
                        "target": "localhost",  # Lynis audite le système local
                        "output": output_lynis
                    }))
                    print("Résultat Lynis envoyé au serveur.")

                    # Lire la réponse du serveur pour éviter de surcharger le buffer
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        print(f"Réponse serveur: {response}")
                    except asyncio.TimeoutError:
                        # Pas de réponse, continuer
                        pass

                    print(f"Attente de {SCAN_INTERVAL} secondes avant le prochain scan...")
                    await asyncio.sleep(SCAN_INTERVAL)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connexion fermée: {e}. Reconnexion dans 5 secondes...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Erreur de connexion: {e}. Reconnexion dans 5 secondes...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(agent_loop())