import asyncio
import websockets
import subprocess
import os
import json
import socket
import re

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("WEBSOCKET_PORT", "8765")
WEBSOCKET_SCHEME = os.getenv("WEBSOCKET_SCHEME", "ws")  # ws ou wss
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

def parse_vuln_output(output: str) -> list:
    """
    Parse la sortie des scripts NSE vuln de Nmap pour extraire les vulnérabilités.
    """
    vulnerabilities = []
    lines = output.split('\n')
    current_vuln = None
    current_port = None
    in_vuln_section = False
    in_port_section = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_orig = line
        
        # Détecter les ports dans la section PORT
        if "PORT" in line and "STATE" in line and "SERVICE" in line:
            in_port_section = True
            continue
        
        if in_port_section and line_stripped and not line_stripped.startswith("-") and "/" in line_stripped:
            # Parser le port
            parts = line_stripped.split()
            if len(parts) >= 2:
                port_info = parts[0].split('/')
                if len(port_info) == 2:
                    try:
                        current_port = int(port_info[0])
                    except:
                        pass
        
        # Détecter le début d'une section de script vuln
        if "|" in line and ("vuln" in line.lower() or "cve" in line.lower() or "VULNERABLE" in line):
            in_vuln_section = True
            
            # Extraire le nom du script (format: | vuln-script-name:)
            if ":" in line:
                script_name = line.split(":")[0].replace("|", "").replace("_", "").strip()
                vuln_desc = line.split(":", 1)[1].strip() if ":" in line else ""
            else:
                script_name = line.replace("|", "").replace("_", "").strip()
                vuln_desc = ""
            
            # Extraire les CVE de la ligne
            cves = re.findall(r'CVE-\d{4}-\d+', line, re.IGNORECASE)
            
            # Déterminer la sévérité basée sur les mots-clés
            severity = "unknown"
            if any(word in line.lower() for word in ["critical", "critique"]):
                severity = "critical"
            elif any(word in line.lower() for word in ["high", "élevé"]):
                severity = "high"
            elif any(word in line.lower() for word in ["medium", "moyen"]):
                severity = "medium"
            elif any(word in line.lower() for word in ["low", "faible"]):
                severity = "low"
            
            current_vuln = {
                "title": script_name or "Vulnérabilité détectée",
                "description": vuln_desc or line_stripped.replace("|", "").replace("_", "").strip(),
                "cve": cves,
                "severity": severity,
                "port": current_port,
                "raw_line": line_stripped
            }
        
        # Continuer à parser les détails de la vulnérabilité
        elif current_vuln and line.startswith("|") and in_vuln_section:
            line_content = line.replace("|", "").replace("_", "").strip()
            
            # Extraire plus de CVE
            cves = re.findall(r'CVE-\d{4}-\d+', line, re.IGNORECASE)
            if cves:
                current_vuln["cve"].extend(cves)
            
            # Extraire des informations supplémentaires
            if ":" in line_content:
                key, value = line_content.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ["state", "id", "published", "disclosure"]:
                    current_vuln[key] = value
                elif "severity" in key or "risk" in key:
                    current_vuln["severity"] = value.lower()
                elif "description" in key or "summary" in key:
                    if not current_vuln.get("description") or len(value) > len(current_vuln.get("description", "")):
                        current_vuln["description"] = value
        
        # Détecter la fin d'une section de vulnérabilité
        elif in_vuln_section and (not line.startswith("|") or "Nmap scan report" in line or "Host script results" in line):
            if current_vuln:
                # Nettoyer les CVE en double
                current_vuln["cve"] = list(set(current_vuln["cve"]))
                vulnerabilities.append(current_vuln)
                current_vuln = None
            in_vuln_section = False
        
        # Détecter la fin de la section des ports
        if "Service detection performed" in line or "Nmap done:" in line:
            in_port_section = False
    
    # Ajouter la dernière vulnérabilité si elle existe
    if current_vuln:
        current_vuln["cve"] = list(set(current_vuln["cve"]))
        vulnerabilities.append(current_vuln)
    
    return vulnerabilities

async def run_nmap_vuln(target: str, ports: list = None) -> dict:
    """
    Exécute un scan Nmap avec les scripts NSE vuln pour détecter les vulnérabilités.
    """
    try:
        # Construire la commande Nmap avec les scripts vuln
        cmd = ["nmap", "--script", "vuln", "-sV", target]
        
        # Si des ports spécifiques sont fournis, les scanner uniquement
        if ports:
            port_list = ",".join(str(p) for p in ports)
            cmd.extend(["-p", port_list])
        
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Plus de temps pour les scans vuln
            )
        except subprocess.TimeoutExpired:
            return {
                "error": True,
                "message": "Timeout lors du scan de vulnérabilités (dépassement de 120 secondes)",
                "vulnerabilities": [],
                "count": 0
            }
        
        stdout_output = result.stdout if result.stdout else ""
        stderr_output = result.stderr if result.stderr else ""
        
        if result.returncode != 0:
            return {
                "error": True,
                "message": f"Erreur lors du scan de vulnérabilités (code {result.returncode})",
                "stderr": stderr_output
            }
        
        # Parser les vulnérabilités
        vulnerabilities = parse_vuln_output(stdout_output)
        
        return {
            "error": False,
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "raw_output": stdout_output
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": True,
            "message": "Timeout lors du scan de vulnérabilités (dépassement de 120 secondes)",
            "vulnerabilities": [],
            "count": 0
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Erreur lors du scan de vulnérabilités : {e}",
            "vulnerabilities": [],
            "count": 0
        }

async def run_searchsploit(nmap_result: dict) -> dict:
    """
    Utilise searchsploit pour chercher des exploits basés sur les services/versions détectés par Nmap.
    """
    exploits = []
    
    try:
        # Extraire les services et versions des ports ouverts
        for port_data in nmap_result.get("ports", []):
            service = port_data.get("service", "")
            version = port_data.get("version", "")
            
            if not service or service == "unknown":
                continue
            
            # Construire la requête searchsploit
            search_term = f"{service} {version}".strip()
            
            try:
                try:
                    result = await asyncio.to_thread(
                        subprocess.run,
                        ["searchsploit", "-j", "--nocolor", search_term],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    # searchsploit non disponible ou timeout
                    continue
                
                if result.returncode == 0 and result.stdout:
                    try:
                        # Parser le JSON de searchsploit
                        exploit_data = json.loads(result.stdout)
                        if "RESULTS_EXPLOIT" in exploit_data and exploit_data["RESULTS_EXPLOIT"]:
                            for exploit in exploit_data["RESULTS_EXPLOIT"]:
                                exploits.append({
                                    "title": exploit.get("Title", ""),
                                    "edb_id": exploit.get("EDB-ID", ""),
                                    "cve": exploit.get("Codes", ""),
                                    "platform": exploit.get("Platform", ""),
                                    "type": exploit.get("Type", ""),
                                    "port": port_data.get("port"),
                                    "service": service,
                                    "version": version
                                })
                    except json.JSONDecodeError:
                        # Si le parsing JSON échoue, ignorer
                        pass
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # searchsploit non disponible ou timeout
                pass
            except Exception:
                pass
        
        return {
            "error": False,
            "exploits": exploits,
            "count": len(exploits)
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Erreur lors de la recherche d'exploits : {e}",
            "exploits": [],
            "count": 0
        }

async def run_nmap(target: str) -> dict:
    """
    Exécute un scan Nmap et retourne les résultats structurés en JSON.
    Parse la sortie texte de Nmap pour créer une structure JSON.
    """
    try:
        # Exécuter Nmap avec sortie texte standard
        # -sV : détection de version
        # -sC : exécution des scripts par défaut
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["nmap", "-sV", "-sC", target],
                capture_output=True,
                text=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            return {
                "error": True,
                "message": "Timeout lors du scan Nmap (dépassement de 60 secondes)",
                "target": target,
                "scan_target": target,
                "format": "error"
            }
        
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
  
async def agent_loop():
    uri = f"{WEBSOCKET_SCHEME}://{SERVER_HOST}:{SERVER_PORT}"
    
    # Détecter l'IP de l'hôte une fois au démarrage
    host_ip = get_host_ip()
    print(f"Configuration de connexion:")
    print(f"  - Serveur WebSocket: {uri}")
    print(f"  - IP cible pour les scans: {host_ip}")

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
            # 1. Scan Nmap initial
            output_nmap = await run_nmap(host_ip)
            
            # 2. Scan de vulnérabilités avec NSE vuln si le scan Nmap a réussi
            vulnerabilities_result = {"error": True, "vulnerabilities": [], "count": 0}
            if not output_nmap.get("error") and output_nmap.get("ports"):
                print("Exécution du scan de vulnérabilités NSE...")
                # Extraire les ports ouverts pour le scan vuln
                open_ports = [p["port"] for p in output_nmap.get("ports", []) if p.get("state") == "open"]
                vulnerabilities_result = await run_nmap_vuln(host_ip, open_ports if open_ports else None)
            
            # 3. Recherche d'exploits avec searchsploit (optionnel)
            exploits_result = {"error": True, "exploits": [], "count": 0}
            if not output_nmap.get("error"):
                print("Recherche d'exploits avec searchsploit...")
                exploits_result = await run_searchsploit(output_nmap)
            
            # 4. Combiner tous les résultats
            combined_output = output_nmap.copy()
            combined_output["vulnerabilities"] = vulnerabilities_result.get("vulnerabilities", [])
            combined_output["vulnerabilities_count"] = vulnerabilities_result.get("count", 0)
            combined_output["exploits"] = exploits_result.get("exploits", [])
            combined_output["exploits_count"] = exploits_result.get("count", 0)

            await websocket.send(json.dumps({
                "status": "auto-scan",
                "target": host_ip,
                "scan_target": host_ip,
                "output": combined_output
            }))

            print(f"Scan terminé. Vulnérabilités: {combined_output['vulnerabilities_count']}, Exploits: {combined_output['exploits_count']}")
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