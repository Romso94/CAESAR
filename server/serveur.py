import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

import uvicorn
import websockets
from fastapi import FastAPI, Form, HTTPException, Request, status, Depends, Cookie, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configuration MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "caesar")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "admin123")

MONGO_SCANS_HOST = os.getenv("MONGO_SCANS_HOST", "localhost")
MONGO_SCANS_PORT = int(os.getenv("MONGO_SCANS_PORT", 27018))
MONGO_SCANS_DATABASE = os.getenv("MONGO_SCANS_DATABASE", "caesar_scans")
MONGO_SCANS_USERNAME = os.getenv("MONGO_SCANS_USERNAME", "scans")
MONGO_SCANS_PASSWORD = os.getenv("MONGO_SCANS_PASSWORD", "scans123")

# Configuration JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Connexions MongoDB
mongo_client = None
mongo_db = None
mongo_scans_client = None
mongo_scans_db = None

# Cryptographie pour les mots de passe
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

app = FastAPI(title="Agent Control API", version="0.1.0")

# Configuration CORS pour permettre les requêtes depuis le frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)

# Fonctions d'authentification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Optional[str] = Cookie(None)):
    if not token or mongo_db is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    try:
        user = await mongo_db.users.find_one({"username": username})
        if user:
            # Retirer le mot de passe hashé du résultat
            user.pop("hashed_password", None)
        return user
    except Exception:
        return None


async def get_current_user_from_header(authorization: Optional[str] = Header(None)):
    """Récupère l'utilisateur depuis le header Authorization"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    return await get_current_user(token=token)


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
    scan_target = "inconnue"
    print(f"Nouvel agent connecté depuis {websocket.remote_address}")
    try:
        # Enregistrer la connexion de l'agent
        agent_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        AGENT_CONNECTIONS[agent_id] = {
            "websocket": websocket,
            "ip_interface": None,
            "connected_at": None,
            "last_nmap": None,
        }
        print(f"Agent {agent_id} enregistré")
        
        async for message in websocket:
            # Extraire scan_target du message pour l'afficher
            try:
                data = json.loads(message)
                message_status = data.get("status", "unknown")
                message_scan_target = data.get("ip_interface")
                
                # Mettre à jour l'IP cible si fournie
                if message_scan_target:
                    scan_target = message_scan_target
                    AGENT_CONNECTIONS[agent_id]["ip_interface"] = scan_target
                
                # Traiter le message d'initialisation
                if message_status == "agent-init":
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
                    
                    # Sauvegarder les scans dans MongoDB (optionnel)
                    if mongo_scans_db is not None:
                        try:
                            scan_doc = {
                                "agent_id": agent_id,
                                "scan_target": data.get("scan_target", "unknown"),
                                "timestamp": datetime.utcnow(),
                                "nmap_result": output,
                                "vulnerabilities": output.get("vulnerabilities", []),
                                "exploits": output.get("exploits", [])
                            }
                            await mongo_scans_db.scans.insert_one(scan_doc)
                        except Exception as e:
                            print(f"Erreur lors de la sauvegarde du scan dans MongoDB: {e}")
            except (json.JSONDecodeError, ValueError):
                print(f"Rapport reçu de l'agent {agent_id}: {message}")
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
    """Page de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Page d'inscription"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    """Inscription d'un nouvel utilisateur"""
    # Vérifier que les mots de passe correspondent
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Les mots de passe ne correspondent pas"
        })
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = await mongo_db.users.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Un utilisateur avec ce nom ou cet email existe déjà"
        })
    
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(password)
    user = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await mongo_db.users.insert_one(user)
    
    # Rediriger vers la page de connexion avec un message de succès
    return RedirectResponse(url="/?registered=1", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Connexion d'un utilisateur"""
    # Chercher l'utilisateur dans la base de données
    user = await mongo_db.users.find_one({"username": username})
    
    if not user or not verify_password(password, user.get("hashed_password", "")):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Nom d'utilisateur ou mot de passe incorrect"
        })
    
    if not user.get("is_active", True):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Ce compte est désactivé"
        })
    
    # Créer un token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Rediriger vers l'application avec le token en cookie
    response = RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response


@app.get("/logout")
async def logout():
    """Déconnexion"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="token")
    return response


# API Routes pour authentification JSON
@app.post("/api/auth/login", response_model=TokenResponse)
async def api_login(login_data: LoginRequest):
    """API de connexion pour le frontend React"""
    if not mongo_db:
        raise HTTPException(status_code=500, detail="Base de données non disponible")
    
    # Chercher l'utilisateur dans la base de données
    user = await mongo_db.users.find_one({"username": login_data.username})
    
    if not user or not verify_password(login_data.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est désactivé"
        )
    
    # Créer un token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Retirer le mot de passe hashé du résultat
    user.pop("hashed_password", None)
    
    return TokenResponse(
        access_token=access_token,
        user=user
    )


@app.post("/api/auth/register", response_model=TokenResponse)
async def api_register(register_data: RegisterRequest):
    """API d'inscription pour le frontend React"""
    if not mongo_db:
        raise HTTPException(status_code=500, detail="Base de données non disponible")
    
    # Vérifier que les mots de passe correspondent
    if register_data.password != register_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les mots de passe ne correspondent pas"
        )
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = await mongo_db.users.find_one({
        "$or": [
            {"username": register_data.username},
            {"email": register_data.email}
        ]
    })
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec ce nom ou cet email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(register_data.password)
    user = {
        "username": register_data.username,
        "email": register_data.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await mongo_db.users.insert_one(user)
    
    # Créer un token JWT pour connecter automatiquement l'utilisateur
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Retirer le mot de passe hashé du résultat
    user.pop("hashed_password", None)
    
    return TokenResponse(
        access_token=access_token,
        user=user
    )


@app.post("/api/auth/logout")
async def api_logout():
    """API de déconnexion pour le frontend React"""
    return {"message": "Déconnexion réussie"}


async def get_current_user_from_header(authorization: Optional[str] = Header(None)):
    """Récupère l'utilisateur depuis le header Authorization"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    return await get_current_user(token=token)


@app.get("/api/auth/me")
async def api_get_current_user(user: Optional[dict] = Depends(get_current_user_from_header)):
    """API pour obtenir les informations de l'utilisateur actuel"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant, invalide ou expiré"
        )
    
    return {"user": user}


@app.get("/app", response_class=HTMLResponse)
async def home_page(request: Request, current_user: Optional[dict] = Depends(get_current_user)):
    """Page d'accueil avec sidebar et boutons"""
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})


@app.get("/app/create", response_class=HTMLResponse)
async def create_agent_page(request: Request, current_user: Optional[dict] = Depends(get_current_user)):
    """Page de création d'agent"""
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("create_agent.html", {"request": request, "user": current_user})


@app.get("/app/agents", response_class=HTMLResponse)
async def agents_list_page(request: Request, current_user: Optional[dict] = Depends(get_current_user)):
    """Page de liste des agents connectés"""
    agents = [
        {
            "id": agent_id,
            "address": agent_id,
            "scan_target": info.get("ip_interface", "Non configuré"),
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
async def agent_details_page(request: Request, agent_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """Page de détails d'un agent avec résultats des scans"""
    if agent_id not in AGENT_CONNECTIONS:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Agent non trouvé"
        })
    
    agent_info = AGENT_CONNECTIONS[agent_id]
    nmap_result = agent_info.get("last_nmap")
    
    # Extraire les vulnérabilités et exploits du résultat
    vulnerabilities = []
    exploits = []
    if nmap_result and isinstance(nmap_result, dict):
        vulnerabilities = nmap_result.get("vulnerabilities", [])
        exploits = nmap_result.get("exploits", [])
    
    return templates.TemplateResponse("agent_details.html", {
        "request": request,
        "agent_id": agent_id,
        "agent_address": agent_id,
        "scan_target": agent_info.get("ip_interface", "Non configuré"),
        "nmap_result": nmap_result,
        "has_nmap": nmap_result is not None,
        "vulnerabilities": vulnerabilities,
        "vulnerabilities_count": len(vulnerabilities),
        "exploits": exploits,
        "exploits_count": len(exploits)
    })


@app.get("/app/info", response_class=HTMLResponse)
async def server_info_page(request: Request, current_user: Optional[dict] = Depends(get_current_user)):
    """Page d'informations sur le serveur"""
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("server_info.html", {"request": request, "user": current_user})

@app.on_event("startup")
async def startup_event():
    """Initialisation des connexions MongoDB et WebSocket au démarrage"""
    global mongo_client, mongo_db, mongo_scans_client, mongo_scans_db, ws_server
    
    # Connexion MongoDB principale (utilisateurs)
    mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource=admin"
    mongo_client = AsyncIOMotorClient(mongo_uri)
    mongo_db = mongo_client[MONGO_DATABASE]
    
    # Connexion MongoDB scans
    mongo_scans_uri = f"mongodb://{MONGO_SCANS_USERNAME}:{MONGO_SCANS_PASSWORD}@{MONGO_SCANS_HOST}:{MONGO_SCANS_PORT}/{MONGO_SCANS_DATABASE}?authSource=admin"
    mongo_scans_client = AsyncIOMotorClient(mongo_scans_uri)
    mongo_scans_db = mongo_scans_client[MONGO_SCANS_DATABASE]
    
    # Créer les index pour les collections
    await mongo_db.users.create_index("username", unique=True)
    await mongo_db.users.create_index("email", unique=True)
    
    print(f"Connecté à MongoDB: {MONGO_DATABASE} sur {MONGO_HOST}:{MONGO_PORT}")
    print(f"Connecté à MongoDB Scans: {MONGO_SCANS_DATABASE} sur {MONGO_SCANS_HOST}:{MONGO_SCANS_PORT}")
    
    # Démarrer le serveur WebSocket
    host = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    port = int(os.getenv("WEBSOCKET_PORT", 8765))
    print(f"Démarrage du serveur WebSocket sur {host}:{port}...")
    ws_server = await websockets.serve(
        handler, 
        host, 
        port, 
        max_size=10 * 1024 * 1024  # 10 MB
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Fermeture des connexions MongoDB et WebSocket à l'arrêt"""
    global mongo_client, mongo_scans_client, ws_server
    
    if mongo_client:
        mongo_client.close()
    if mongo_scans_client:
        mongo_scans_client.close()
    
    if ws_server is not None:
        ws_server.close()
        await ws_server.wait_closed()
        print("Serveur WebSocket arrêté.")

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
