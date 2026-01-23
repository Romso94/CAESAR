import asyncio
import os
import json
from typing import Dict, Optional

import uvicorn
import websockets
from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="Agent Control API", version="0.1.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)


# In-memory stores
AGENTS: Dict[str, Dict[str, Optional[str]]] = {}
AGENT_CONNECTIONS: Dict[str, Dict[str, any]] = {}  # Pour tracker les connexions WebSocket et leurs infos


class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class RunAgentRequest(BaseModel):
    command: str


# WebSocket handler for agents
async def handler(websocket):
    agent_id = None
    scan_target = None
    print(f"Nouvel agent connecté depuis {websocket.remote_address}")
    try:
        # Enregistrer la connexion de l'agent
        agent_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        AGENT_CONNECTIONS[agent_id] = {
            "websocket": websocket,
            "scan_target": None,
            "connected_at": None,
            "last_nmap": None,
            "last_lynis": None
        }
        print(f"Agent {agent_id} enregistré")
        
        async for message in websocket:
            # Extraire scan_target du message pour l'afficher
            try:
                data = json.loads(message)
                scan_target = data.get("scan_target", "inconnue")
                message_status = data.get("status", "unknown")
                
                # Mettre à jour l'IP cible si c'est un message d'initialisation
                if message_status == "agent-init":
                    AGENT_CONNECTIONS[agent_id]["scan_target"] = scan_target
                    print(f"Agent {agent_id} initialisé avec IP cible: {scan_target}")
                
                # Stocker les résultats des scans
                elif message_status == "auto-scan":
                    output = data.get("output", {})
                    # S'assurer que c'est un dictionnaire et non une chaîne
                    if isinstance(output, str):
                        try:
                            output = json.loads(output)
                        except:
                            output = {}
                    AGENT_CONNECTIONS[agent_id]["last_nmap"] = output
                    print(f"Résultat Nmap stocké pour {agent_id}")
                
                elif message_status == "lynis-audit":
                    output = data.get("output", {})
                    # S'assurer que c'est un dictionnaire et non une chaîne
                    if isinstance(output, str):
                        try:
                            output = json.loads(output)
                        except:
                            output = {}
                    AGENT_CONNECTIONS[agent_id]["last_lynis"] = output
                    print(f"Résultat Lynis stocké pour {agent_id}")
                
                print(f"Rapport reçu de l'agent {websocket.remote_address} ({message_status}) de la machine ('{scan_target}'): {message[:100]}...")
            except (json.JSONDecodeError, ValueError):
                print(f"Rapport reçu de l'agent {websocket.remote_address}: {message[:100]}...")
            await websocket.send("Rapport bien reçu.")
    except websockets.exceptions.ConnectionClosedError:
        print(f"Agent {websocket.remote_address} déconnecté.")
    except Exception as e:
        print(f"Une erreur est survenue avec l'agent {websocket.remote_address}: {e}")
    finally:
        # Nettoyer la connexion quand l'agent se déconnecte
        if agent_id and agent_id in AGENT_CONNECTIONS:
            del AGENT_CONNECTIONS[agent_id]
            print(f"Connexion de l'agent {agent_id} supprimée")


ws_server = None


# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Page de login minimaliste"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Faux login côté front : accepte tout et redirige vers la page d'accueil"""
    return RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/app", response_class=HTMLResponse)
async def home_page(request: Request):
    """Page d'accueil avec sidebar et boutons"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/app/create", response_class=HTMLResponse)
async def create_agent_page(request: Request):
    """Page de création d'agent"""
    return templates.TemplateResponse("create_agent.html", {"request": request})


@app.get("/app/agents", response_class=HTMLResponse)
async def agents_list_page(request: Request):
    """Page de liste des agents connectés"""
    agents = [
        {
            "id": agent_id,
            "address": agent_id,
            "scan_target": info.get("scan_target", "Non configuré"),
            "status": "online"
        }
        for agent_id, info in AGENT_CONNECTIONS.items()
    ]
    return templates.TemplateResponse("agents_list.html", {
        "request": request,
        "agents": agents,
        "count": len(agents)
    })


@app.get("/app/agents/{agent_id}/details", response_class=HTMLResponse)
async def agent_details_page(request: Request, agent_id: str):
    """Page de détails d'un agent avec résultats des scans"""
    if agent_id not in AGENT_CONNECTIONS:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Agent non trouvé"
        })
    
    agent_info = AGENT_CONNECTIONS[agent_id]
    nmap_result = agent_info.get("last_nmap")
    lynis_result = agent_info.get("last_lynis")
    
    return templates.TemplateResponse("agent_details.html", {
        "request": request,
        "agent_id": agent_id,
        "agent_address": agent_id,
        "scan_target": agent_info.get("scan_target", "Non configuré"),
        "nmap_result": nmap_result,
        "lynis_result": lynis_result,
        "has_nmap": nmap_result is not None,
        "has_lynis": lynis_result is not None
    })


@app.get("/app/info", response_class=HTMLResponse)
async def server_info_page(request: Request):
    """Page d'informations sur le serveur"""
    return templates.TemplateResponse("server_info.html", {"request": request})


@app.on_event("startup")
async def start_ws_server():
    global ws_server
    host = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    port = int(os.getenv("WEBSOCKET_PORT", 8765))
    print(f"Démarrage du serveur WebSocket sur {host}:{port}...")
    ws_server = await websockets.serve(handler, host, port)


@app.on_event("shutdown")
async def stop_ws_server():
    if ws_server is not None:
        ws_server.close()
        await ws_server.wait_closed()
        print("Serveur WebSocket arrêté.")


# API Routes
@app.post("/api/agents/{agent_id}/configure")
async def configure_agent(agent_id: str, ip_interface: str):
    """
    Envoie une commande de configuration à un agent connecté.
    Exemple: POST /api/agents/127.0.0.1:12345/configure?ip_interface=10.0.0.5
    """
    if agent_id not in AGENT_CONNECTIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent non connecté")
    
    agent_info = AGENT_CONNECTIONS[agent_id]
    websocket = agent_info.get("websocket")
    
    try:
        command = {
            "type": "configure",
            "ip_interface": ip_interface
        }
        await websocket.send(json.dumps(command))
        # Mettre à jour l'IP cible en mémoire
        agent_info["scan_target"] = ip_interface
        return {"status": "command_sent", "agent_id": agent_id, "ip_interface": ip_interface}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur: {e}")


@app.get("/api/agents/connected")
async def list_connected_agents():
    """Liste tous les agents actuellement connectés"""
    return {"agents": list(AGENT_CONNECTIONS.keys()), "count": len(AGENT_CONNECTIONS)}


@app.post("/agents")
async def create_agent(payload: AgentCreateRequest):
    agent_id = "agent_" + os.urandom(4).hex()
    AGENTS[agent_id] = {"name": payload.name, "description": payload.description, "last_run": None}
    return {"id": agent_id, "name": payload.name, "description": payload.description}


@app.get("/agents")
async def list_agents():
    return [{"id": aid, **data} for aid, data in AGENTS.items()]


@app.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, payload: RunAgentRequest):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent introuvable")
    AGENTS[agent_id]["last_run"] = payload.command
    return {"status": "scheduled", "agent_id": agent_id, "command": payload.command}


def get_uvicorn_kwargs():
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload_flag = os.getenv("API_RELOAD", "false").lower() == "true"
    return {"host": host, "port": port, "reload": reload_flag}


if __name__ == "__main__":
    uvicorn.run("server.serveur:app", **get_uvicorn_kwargs())
