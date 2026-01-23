import asyncio
import websockets
import subprocess
import os
import json
import socket

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("WEBSOCKET_PORT", "8765")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))
IP_INTERFACE = os.getenv("IP_INTERFACE", None)  # Permet de forcer une IP cible

def get_host_ip():
    """
    Retourne l'IP cible configurée via la variable d'environnement IP_INTERFACE.
    """
    if not IP_INTERFACE:
        raise ValueError("IP_INTERFACE doit être définie. Exemple: IP_INTERFACE=192.168.1.132")
    return IP_INTERFACE

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


def clean_ansi_codes(text: str) -> str:
    """
    Supprime les codes ANSI (couleurs, formatage) de la sortie.
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def parse_lynis_output(output: str) -> dict:
    """
    Parse la sortie texte de Lynis et la structure en JSON.
    Extrait les informations de sécurité de manière structurée.
    """
    result = {
        "target": "localhost",
        "audit_type": "system-security",
        "tests": [],
        "warnings": [],
        "suggestions": [],
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "warning": 0,
            "failed": 0
        },
        "sections": {}
    }
    
    lines = output.split('\n')
    current_section = None
    
    for line in lines:
        line_stripped = line.strip()
        
        # Parser les sections (ex: "System tools")
        if line.startswith('[') and ']' in line:
            section_match = line.split(']')
            if len(section_match) >= 2:
                current_section = section_match[1].strip()
                if current_section:
                    result["sections"][current_section] = {
                        "tests": [],
                        "warnings": [],
                        "suggestions": []
                    }
        
        # Parser les tests avec résultats
        if " [ " in line and " ] " in line:
            # Format: [TEST-ID] Description [ PASSED/WARNING/FAILED ]
            try:
                # Extraire l'ID du test
                test_id_start = line.find('[')
                test_id_end = line.find(']', test_id_start)
                if test_id_start != -1 and test_id_end != -1:
                    test_id = line[test_id_start + 1:test_id_end].strip()
                    
                    # Extraire le résultat du test
                    result_start = line.rfind('[')
                    result_end = line.rfind(']')
                    if result_start != -1 and result_end != -1:
                        test_result = line[result_start + 1:result_end].strip()
                        
                        # Extraire la description
                        description = line[test_id_end + 1:result_start].strip()
                        
                        test_data = {
                            "id": test_id,
                            "description": description,
                            "result": test_result
                        }
                        
                        # Ajouter aux résultats globaux
                        result["tests"].append(test_data)
                        
                        # Mettre à jour les statistiques
                        result["summary"]["total_tests"] += 1
                        if test_result == "PASSED":
                            result["summary"]["passed"] += 1
                        elif test_result == "WARNING":
                            result["summary"]["warning"] += 1
                            result["warnings"].append(test_data)
                        elif test_result == "FAILED":
                            result["summary"]["failed"] += 1
                        
                        # Ajouter à la section courante
                        if current_section and current_section in result["sections"]:
                            result["sections"][current_section]["tests"].append(test_data)
            except:
                pass
        
        # Parser les avertissements et suggestions
        if "Warning:" in line or "WARNING:" in line:
            warning_text = line.replace("Warning:", "").replace("WARNING:", "").strip()
            if warning_text:
                result["warnings"].append({
                    "message": warning_text,
                    "section": current_section
                })
        
        if "Suggestion:" in line or "SUGGESTION:" in line:
            suggestion_text = line.replace("Suggestion:", "").replace("SUGGESTION:", "").strip()
            if suggestion_text:
                result["suggestions"].append({
                    "message": suggestion_text,
                    "section": current_section
                })
        
        # Parser les informations générales du système
        if "Hostname:" in line or "OS name:" in line or "OS version:" in line:
            if "system_info" not in result:
                result["system_info"] = {}
            
            if "Hostname:" in line:
                result["system_info"]["hostname"] = line.split(":", 1)[1].strip()
            elif "OS name:" in line:
                result["system_info"]["os_name"] = line.split(":", 1)[1].strip()
            elif "OS version:" in line:
                result["system_info"]["os_version"] = line.split(":", 1)[1].strip()
    
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
                "target": target,
                "scan_target": target
            }
        
        # Parser la sortie texte et la structurer
        parsed_data = parse_nmap_output(stdout_output, target)
        parsed_data["error"] = False
        parsed_data["format"] = "structured"
        parsed_data["scan_target"] = target  # Ajouter l'IP de la machine cible
        
        return parsed_data
            
    except subprocess.TimeoutExpired:
        return {
            "error": True,
            "message": "Timeout lors du scan Nmap (dépassement de 60 secondes)",
            "target": target,
            "scan_target": target,
            "format": "error"
        }
    except FileNotFoundError:
        return {
            "error": True,
            "message": "Nmap n'est pas installé sur le système",
            "target": target,
            "scan_target": target,
            "format": "error"
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Erreur lors du scan : {e}",
            "target": target,
            "scan_target": target,
            "format": "error"
        }
    
async def run_lynis(scan_target: str) -> dict:
    """
    Exécute un audit de sécurité avec Lynis.
    Analyse la configuration de sécurité du système.
    Retourne les résultats structurés en JSON.
    """
    try:
        # Commande Lynis avec options :
        # --no-colors : pas de codes de couleur ANSI
        # --quiet : mode silencieux
        # --quick : audit rapide
        result = subprocess.run(
            ["lynis", "audit", "system", "--quick", "--no-colors"],
            capture_output=True,
            text=True,
            timeout=120  # Lynis peut être plus lent que nmap
        )
        
        stdout_output = result.stdout if result.stdout else ""
        stderr_output = result.stderr if result.stderr else ""
        
        # Nettoyer les codes ANSI même si --no-colors est fourni
        stdout_output = clean_ansi_codes(stdout_output)
        stderr_output = clean_ansi_codes(stderr_output)
        
        if result.returncode != 0:
            return {
                "error": True,
                "message": f"Erreur lors de l'exécution de Lynis (code {result.returncode})",
                "stderr": stderr_output,
                "format": "error",
                "scan_target": scan_target
            }
        
        # Parser la sortie texte et la structurer
        parsed_data = parse_lynis_output(stdout_output)
        parsed_data["error"] = False
        parsed_data["format"] = "structured"
        parsed_data["scan_target"] = scan_target  # Ajouter l'IP de la machine cible
        parsed_data["raw_output"] = stdout_output  # Ajouter aussi la sortie brute pour référence
        
        return parsed_data
        
    except subprocess.TimeoutExpired:
        return {
            "error": True,
            "message": "Timeout lors de l'audit Lynis (dépassement de 120 secondes)",
            "format": "error",
            "scan_target": scan_target
        }
    except FileNotFoundError:
        return {
            "error": True,
            "message": "Lynis n'est pas installé sur le système",
            "format": "error",
            "scan_target": scan_target
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Erreur lors de l'audit : {e}",
            "format": "error",
            "scan_target": scan_target
        }
    
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
                
                # Envoyer un message d'initialisation avec l'IP cible
                await websocket.send(json.dumps({
                    "status": "agent-init",
                    "scan_target": host_ip
                }))
                print(f"Message d'initialisation envoyé avec IP cible: {host_ip}")
                
                # Créer une tâche de scan en arrière-plan
                scan_task = asyncio.create_task(scan_loop(websocket, host_ip))
                
                # Boucle pour recevoir les commandes du serveur
                try:
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            if data.get("type") == "configure":
                                # Mettre à jour l'IP cible
                                new_ip = data.get("ip_interface")
                                if new_ip:
                                    host_ip = new_ip
                                    print(f"Configuration mise à jour. Nouvelle IP cible: {host_ip}")
                                    await websocket.send(json.dumps({
                                        "status": "configured",
                                        "new_ip": host_ip
                                    }))
                        except json.JSONDecodeError:
                            print(f"Message non-JSON reçu: {message}")
                except asyncio.CancelledError:
                    scan_task.cancel()
                    raise

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connexion fermée: {e}. Reconnexion dans 5 secondes...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Erreur de connexion: {e}. Reconnexion dans 5 secondes...")
            await asyncio.sleep(5)


async def scan_loop(websocket, host_ip):
    """
    Boucle de scan en arrière-plan. Elle s'exécute indépendamment.
    """
    while True:
        try:
            print(f"Scan automatique : {host_ip}")
            output_nmap = await run_nmap(host_ip)

            await websocket.send(json.dumps({
                "status": "auto-scan",
                "target": host_ip,
                "scan_target": host_ip,
                "output": output_nmap
            }))

            # ===== AUDIT LYNIS =====
            print("Exécution de l'audit de sécurité Lynis...")
            output_lynis = await run_lynis(host_ip)

            # Envoyer le résultat de l'audit Lynis au serveur
            await websocket.send(json.dumps({
                "status": "lynis-audit",
                "target": "localhost",
                "scan_target": host_ip,
                "output": output_lynis
            }))
            print("Résultat Lynis envoyé au serveur.")

            print(f"Attente de {SCAN_INTERVAL} secondes avant le prochain scan...")
            await asyncio.sleep(SCAN_INTERVAL)
            
        except asyncio.CancelledError:
            print("Scan loop annulée.")
            break
        except Exception as e:
            print(f"Erreur lors du scan: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(agent_loop())