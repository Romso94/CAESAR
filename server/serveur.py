import asyncio
import os
import secrets
from typing import Dict, Optional

import uvicorn
import websockets
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

security = HTTPBearer(auto_error=False)
app = FastAPI(title="Agent Control API", version="0.1.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)


# ------------------------------
# In-memory stores (minimal demo)
# ------------------------------
TOKENS: Dict[str, str] = {}
AGENTS: Dict[str, Dict[str, Optional[str]]] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class RunAgentRequest(BaseModel):
    command: str


def require_auth(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = creds.credentials
    if token not in TOKENS.values():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token


# ------------------------------
# WebSocket handler for agents
# ------------------------------
async def handler(websocket):
    print(f"Nouvel agent connecté depuis {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Rapport reçu de l'agent {websocket.remote_address}: {message}")
            await websocket.send("Rapport bien reçu.")
    except websockets.exceptions.ConnectionClosedError:
        print(f"Agent {websocket.remote_address} déconnecté.")
    except Exception as e:  # pragma: no cover - simple log
        print(f"Une erreur est survenue avec l'agent {websocket.remote_address}: {e}")


ws_server = None


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Page de login minimaliste (front).
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Faux login côté front : accepte tout et redirige vers la page d'accueil.
    La vraie API d'auth reste exposée sur /api/login.
    """
    return RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/app", response_class=HTMLResponse)
async def home_page(request: Request):
    """
    Page d'accueil avec sidebar et boutons (non-fonctionnels pour l'instant).
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/app/create", response_class=HTMLResponse)
async def create_agent_page(request: Request):
    """
    Page de création d'agent (formulaire non fonctionnel).
    """
    return templates.TemplateResponse("create_agent.html", {"request": request})


@app.get("/app/agents", response_class=HTMLResponse)
async def agents_list_page(request: Request):
    """
    Page de liste des agents (non fonctionnelle).
    """
    return templates.TemplateResponse("agents_list.html", {"request": request})


@app.get("/app/info", response_class=HTMLResponse)
async def server_info_page(request: Request):
    """
    Page d'informations sur le serveur.
    """
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


# ------------------------------
# HTTP API routes
# ------------------------------
@app.post("/api/login")
async def login(payload: LoginRequest):
    if (
        payload.username != ADMIN_USERNAME
        or payload.password != ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
        )

    token = secrets.token_hex(16)
    TOKENS[payload.username] = token
    return {"token": token}



@app.post("/agents")
async def create_agent(payload: AgentCreateRequest, token: str = Depends(require_auth)):
    agent_id = secrets.token_hex(8)
    AGENTS[agent_id] = {"name": payload.name, "description": payload.description, "last_run": None}
    return {"id": agent_id, "name": payload.name, "description": payload.description}


@app.get("/agents")
async def list_agents(token: str = Depends(require_auth)):
    return [{"id": aid, **data} for aid, data in AGENTS.items()]


@app.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, payload: RunAgentRequest, token: str = Depends(require_auth)):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent introuvable")
    # Ici vous déclencheriez l'envoi du job vers l'agent via WebSocket/API interne.
    AGENTS[agent_id]["last_run"] = payload.command
    return {"status": "scheduled", "agent_id": agent_id, "command": payload.command}


def get_uvicorn_kwargs():
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload_flag = os.getenv("API_RELOAD", "false").lower() == "true"
    return {"host": host, "port": port, "reload": reload_flag}


if __name__ == "__main__":
    uvicorn.run("server.serveur:app", **get_uvicorn_kwargs())
