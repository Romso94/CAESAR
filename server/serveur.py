import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from contextlib import asynccontextmanager
from io import BytesIO

import uvicorn
import websockets
from fastapi import FastAPI, Form, HTTPException, Request, status, Depends, Cookie, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


# ==================== SECURITY AUDIT REPORT GENERATOR ====================
class SecurityAuditReportGenerator:
    """Générateur de rapports d'audit de sécurité en PDF."""
    
    def __init__(self, agent_id: str, scan_target: str, nmap_result: Dict[str, Any]):
        """
        Initialise le générateur de rapport.
        
        Args:
            agent_id: ID de l'agent
            scan_target: IP/cible du scan
            nmap_result: Résultats complets du scan Nmap (contient nmap, vulnérabilités, exploits)
        """
        self.agent_id = agent_id
        # Évite d'afficher "None" dans le PDF si la cible n'a pas été configurée
        self.scan_target = scan_target or "Non configuré"
        self.nmap_result = nmap_result
        self.vulnerabilities = nmap_result.get("vulnerabilities", [])
        self.exploits = nmap_result.get("exploits", [])
        self.timestamp = datetime.now()
        
    def generate(self) -> BytesIO:
        """
        Génère le rapport PDF complet.
        
        Returns:
            BytesIO: Le contenu du PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            title="Rapport d'Audit de Sécurité"
        )
        
        # Construire les éléments du document
        story = self._build_story()
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _build_story(self) -> List:
        """Construit la liste des éléments du rapport."""
        styles = getSampleStyleSheet()
        story = []
        
        # Titre principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0078d4'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("RAPPORT D'AUDIT DE SÉCURITÉ", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Informations générales
        story.extend(self._build_header_info(styles))
        story.append(Spacer(1, 0.3*inch))
        
        # Résumé exécutif
        story.extend(self._build_executive_summary(styles))
        # Laisser ReportLab paginer naturellement pour éviter de grosses zones blanches
        story.append(Spacer(1, 0.25*inch))
        
        # Résultats Nmap
        story.extend(self._build_nmap_section(styles))
        story.append(Spacer(1, 0.2*inch))
        
        # Vulnérabilités détectées
        story.extend(self._build_vulnerabilities_section(styles))
        story.append(Spacer(1, 0.2*inch))
        
        # Exploits disponibles
        story.extend(self._build_exploits_section(styles))
        story.append(Spacer(1, 0.2*inch))
        
        # Recommandations
        # Pas de saut de page forcé: évite une page quasi vide quand les résultats sont courts
        story.extend(self._build_recommendations_section(styles))
        
        return story
    
    def _build_header_info(self, styles) -> List:
        """Construit la section d'informations générales."""
        elements = []
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6
        )
        
        elements.append(Paragraph(f"<b>Agent ID:</b> {self.agent_id}", header_style))
        elements.append(Paragraph(f"<b>Cible du scan:</b> {self.scan_target}", header_style))
        elements.append(Paragraph(f"<b>Date du rapport:</b> {self.timestamp.strftime('%d/%m/%Y à %H:%M:%S')}", header_style))
        elements.append(Paragraph(f"<b>Système:</b> CAESAR Security Audit", header_style))
        
        return elements
    
    def _build_executive_summary(self, styles) -> List:
        """Construit le résumé exécutif."""
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0078d4'),
            spaceAfter=12,
            spaceBefore=6,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#0078d4'),
            borderWidth=2,
            borderPadding=6
        )
        
        elements.append(Paragraph("RÉSUMÉ EXÉCUTIF", title_style))
        
        # Statistiques
        open_ports = self.nmap_result.get("summary", {}).get("open_ports", 0)
        vuln_count = len(self.vulnerabilities)
        exploit_count = len(self.exploits)
        
        summary_text = f"""
        <b>Résultats de l'audit:</b><br/>
        • Ports ouverts détectés: <b>{open_ports}</b><br/>
        • Vulnérabilités trouvées: <b>{vuln_count}</b><br/>
        • Exploits disponibles: <b>{exploit_count}</b><br/>
        <br/>
        Ce rapport détaille les résultats complets du scan de sécurité réalisé sur la cible {self.scan_target}.
        Il inclut une analyse des ports ouverts, des vulnérabilités détectées et des exploits potentiellement applicables.
        """
        
        summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            textColor=colors.HexColor('#374151')
        )
        
        elements.append(Paragraph(summary_text, summary_style))
        
        return elements
    
    def _build_nmap_section(self, styles) -> List:
        """Construit la section des résultats Nmap."""
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0078d4'),
            spaceAfter=12,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("RÉSULTATS NMAP", title_style))
        
        # Tableau de résumé
        summary = self.nmap_result.get("summary", {})
        summary_data = [
            ["Métrique", "Valeur"],
            ["Ports scannés", str(summary.get("total_ports_scanned", 0))],
            ["Ports ouverts", str(summary.get("open_ports", 0))],
            ["Ports fermés", str(summary.get("closed_ports", 0))],
            ["Ports filtrés", str(summary.get("filtered_ports", 0))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078d4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Détail des ports ouverts
        ports = self.nmap_result.get("ports", [])
        if ports:
            elements.append(Paragraph("Ports ouverts détectés:", styles['Heading3']))
            
            ports_data = [["Port", "Protocole", "État", "Service", "Version"]]
            for port in ports[:20]:  # Limiter à 20 ports pour éviter un tableau trop volumineux
                ports_data.append([
                    str(port.get("port", "N/A")),
                    port.get("protocol", "N/A"),
                    port.get("state", "N/A"),
                    port.get("service", "N/A"),
                    port.get("version", "N/A")[:30]  # Limiter la longueur de la version
                ])
            
            ports_table = Table(ports_data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.4*inch])
            ports_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078d4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(ports_table)
            
            if len(ports) > 20:
                elements.append(Spacer(1, 0.1*inch))
                more_style = ParagraphStyle(
                    'MoreStyle',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#6b7280')
                )
                elements.append(Paragraph(f"... et {len(ports) - 20} autres ports", more_style))
        
        return elements
    
    def _build_vulnerabilities_section(self, styles) -> List:
        """Construit la section des vulnérabilités."""
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#d83b01'),
            spaceAfter=12,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph(f"VULNÉRABILITÉS DÉTECTÉES ({len(self.vulnerabilities)})", title_style))
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        )

        # Si aucune vulnérabilité n'est fournie par l'agent, afficher une section explicite
        if not self.vulnerabilities:
            elements.append(Paragraph(
                "Aucune vulnérabilité n'a été remontée par l'analyse automatique pour cette exécution. "
                "Cela ne signifie pas nécessairement que la cible est exempte de failles : "
                "les résultats dépendent des scripts/outils exécutés par l'agent et du niveau de profondeur du scan.",
                normal_style
            ))
            return elements
        
        for i, vuln in enumerate(self.vulnerabilities[:15], 1):  # Limiter à 15 vulnérabilités
            severity = vuln.get("severity", "UNKNOWN").upper()
            severity_color = self._get_severity_color(severity)
            
            vuln_text = f"""
            <b>{i}. {vuln.get('title', 'Vulnérabilité inconnue')}</b>
            <font color="{severity_color}"><b>[{severity}]</b></font><br/>
            """
            
            if vuln.get("description"):
                vuln_text += f"Description: {vuln['description']}<br/>"
            
            if vuln.get("port"):
                vuln_text += f"Port affecté: {vuln['port']}<br/>"
            
            if vuln.get("cve"):
                cve_str = ", ".join(vuln['cve']) if isinstance(vuln['cve'], list) else vuln['cve']
                vuln_text += f"CVE: <font color=\"#0066cc\"><u>{cve_str}</u></font><br/>"
            
            elements.append(Paragraph(vuln_text, normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        if len(self.vulnerabilities) > 15:
            more_style = ParagraphStyle(
                'MoreStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#6b7280')
            )
            elements.append(Paragraph(f"... et {len(self.vulnerabilities) - 15} autres vulnérabilités", more_style))
        
        return elements
    
    def _build_exploits_section(self, styles) -> List:
        """Construit la section des exploits."""
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#dc2626'),
            spaceAfter=12,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph(f"EXPLOITS DISPONIBLES ({len(self.exploits)})", title_style))
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        )

        # Si aucun exploit n'est associé, afficher une section explicite (au lieu de laisser un "trou")
        if not self.exploits:
            elements.append(Paragraph(
                "Aucun exploit n'a été identifié automatiquement (par ex. via corrélation service/version/CVE). "
                "Pour aller plus loin : enrichir l'inventaire des versions (bannières), vérifier les CVE associées, "
                "et croiser avec des bases de données (Exploit-DB, Metasploit, etc.).",
                normal_style
            ))
            return elements
        
        for i, exploit in enumerate(self.exploits[:15], 1):  # Limiter à 15 exploits
            exploit_text = f"""
            <b>{i}. {exploit.get('title', 'Exploit inconnu')}</b><br/>
            """
            
            if exploit.get("service"):
                exploit_text += f"Service: {exploit['service']}<br/>"
            
            if exploit.get("version"):
                exploit_text += f"Version: {exploit['version']}<br/>"
            
            if exploit.get("port"):
                exploit_text += f"Port: {exploit['port']}<br/>"
            
            if exploit.get("cve"):
                exploit_text += f"CVE: <font color=\"#0066cc\"><u>{exploit['cve']}</u></font><br/>"
            
            if exploit.get("edb_id"):
                exploit_text += f"EDB ID: {exploit['edb_id']}<br/>"
            
            if exploit.get("type"):
                exploit_text += f"Type: {exploit['type']}<br/>"
            
            elements.append(Paragraph(exploit_text, normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        if len(self.exploits) > 15:
            more_style = ParagraphStyle(
                'MoreStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#6b7280')
            )
            elements.append(Paragraph(f"... et {len(self.exploits) - 15} autres exploits", more_style))
        
        return elements
    
    def _build_recommendations_section(self, styles) -> List:
        """Construit la section des recommandations."""
        elements = []
        
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#107c10'),
            spaceAfter=12,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("RECOMMANDATIONS", title_style))
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        )
        
        recommendations = [
            "1. <b>Mise à jour des services:</b> Mettre à jour tous les services identifiés avec leurs dernières versions de sécurité.",
            "2. <b>Fermeture des ports inutiles:</b> Fermer ou filtrer tous les ports ouverts qui ne sont pas essentiels à votre infrastructure.",
            "3. <b>Filtrage réseau:</b> Implémenter des pare-feu et des listes de contrôle d'accès pour limiter l'accès aux services.",
            "4. <b>Correctifs de sécurité:</b> Appliquer immédiatement tous les correctifs de sécurité disponibles pour les CVE détectées.",
            "5. <b>Surveillance continue:</b> Mettre en place une surveillance continue et des scans réguliers de sécurité.",
            "6. <b>Gestion des identifiants:</b> Renforcer la politique de gestion des mots de passe et implémenter l'authentification multi-facteurs.",
            "7. <b>Audit de sécurité:</b> Réaliser des audits de sécurité réguliers et des tests de pénétration.",
        ]
        
        for rec in recommendations:
            elements.append(Paragraph(rec, normal_style))
        
        elements.append(Spacer(1, 0.2*inch))
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph(
            f"Rapport généré par CAESAR Security Audit le {self.timestamp.strftime('%d/%m/%Y à %H:%M:%S')}",
            footer_style
        ))
        
        return elements
    
    @staticmethod
    def _get_severity_color(severity: str) -> str:
        """Retourne la couleur associée à un niveau de sévérité."""
        severity_colors = {
            "CRITICAL": "#dc2626",
            "HIGH": "#f97316",
            "MEDIUM": "#eab308",
            "LOW": "#3b82f6",
            "INFO": "#6b7280",
            "UNKNOWN": "#9ca3af"
        }
        return severity_colors.get(severity.upper(), "#9ca3af")


# ==================== END SECURITY AUDIT REPORT GENERATOR ====================

# Configuration MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27019))
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler to initialize and tear down resources."""
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

    try:
        yield
    finally:
        if mongo_client:
            mongo_client.close()
        if mongo_scans_client:
            mongo_scans_client.close()

        if ws_server is not None:
            ws_server.close()
            await ws_server.wait_closed()
            print("Serveur WebSocket arrêté.")


app = FastAPI(title="Agent Control API", version="0.1.0", lifespan=lifespan)

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


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict


# WebSocket handler for agents
async def handler(websocket):
    agent_id = None
    temp_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    print(f"Nouvel agent connecté depuis {websocket.remote_address}")
    try:
        # Enregistrer la connexion temporaire de l'agent
        agent_id = temp_id
        AGENT_CONNECTIONS[agent_id] = {
            "websocket": websocket,
            "ip_interface": None,
            "agent_address": websocket.remote_address[0],
            "agent_port": websocket.remote_address[1],
            "connected_at": datetime.utcnow(),
            "last_seen": datetime.utcnow(),
            "last_nmap": None,
            "status": "online",
        }
        print(f"Agent {agent_id} enregistré temporairement")
        
        async for message in websocket:
            # Extraire scan_target du message pour l'afficher
            try:
                data = json.loads(message)
                message_status = data.get("status", "unknown")
                message_ip_interface = data.get("ip_interface")
                
                print(f"[{agent_id}] Message reçu - Status: {message_status}, IP: {message_ip_interface}")
                
                # Mettre à jour l'IP cible si fournie dans n'importe quel message
                if message_ip_interface:
                    # Chercher un agent existant avec cette IP Machine
                    existing_agent = None
                    for aid, info in list(AGENT_CONNECTIONS.items()):
                        if info.get("ip_interface") == message_ip_interface and aid != agent_id:
                            existing_agent = aid
                            break
                    
                    # Si un agent existe déjà avec cette IP Machine, le mettre à jour
                    if existing_agent:
                        print(f"✓ Agent existant trouvé ({existing_agent}), mise à jour avec nouvelle connexion {agent_id}")
                        # Copier les données dans l'ancien agent
                        AGENT_CONNECTIONS[existing_agent]["websocket"] = websocket
                        AGENT_CONNECTIONS[existing_agent]["agent_address"] = websocket.remote_address[0]
                        AGENT_CONNECTIONS[existing_agent]["agent_port"] = websocket.remote_address[1]
                        AGENT_CONNECTIONS[existing_agent]["status"] = "online"
                        AGENT_CONNECTIONS[existing_agent]["last_seen"] = datetime.utcnow()
                        # Supprimer la connexion temporaire
                        if agent_id in AGENT_CONNECTIONS and agent_id != existing_agent:
                            del AGENT_CONNECTIONS[agent_id]
                        # Utiliser l'ID existant
                        agent_id = existing_agent
                    else:
                        # Nouveau agent : utiliser l'IP Machine comme ID unique
                        new_agent_id = message_ip_interface
                        if new_agent_id != agent_id:
                            # Transférer les données vers le nouvel ID
                            AGENT_CONNECTIONS[new_agent_id] = AGENT_CONNECTIONS[agent_id]
                            del AGENT_CONNECTIONS[agent_id]
                            agent_id = new_agent_id
                            print(f"✓ Agent réidentifié avec IP Machine: {agent_id}")
                    
                    AGENT_CONNECTIONS[agent_id]["ip_interface"] = message_ip_interface
                    print(f"✓ Agent {agent_id} - IP Interface mise à jour: {message_ip_interface}")

                # Mettre à jour le statut et le dernier contact
                AGENT_CONNECTIONS[agent_id]["status"] = "online"
                AGENT_CONNECTIONS[agent_id]["last_seen"] = datetime.utcnow()
                
                # Traiter le message d'initialisation
                if message_status == "agent-init":
                    print(f"✓ Agent {agent_id} initialisé avec IP: {message_ip_interface}")
                
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
                    
                    # Sauvegarder les scans dans MongoDB
                    if mongo_scans_db is not None:
                        try:
                            vulnerabilities = output.get("vulnerabilities", [])
                            exploits = output.get("exploits", [])
                            print(f"📊 Données du scan: {len(vulnerabilities)} vulns, {len(exploits)} exploits")
                            
                            scan_doc = {
                                "agent_id": agent_id,
                                "ip_interface": message_ip_interface or "unknown",
                                "scan_target": message_ip_interface or "unknown",
                                "timestamp": datetime.utcnow(),
                                "nmap_result": output,
                                "vulnerabilities": vulnerabilities,
                                "exploits": exploits
                            }
                            result = await mongo_scans_db.scans.insert_one(scan_doc)
                            print(f"✓ Scan sauvegardé pour {agent_id} (ID: {result.inserted_id})")
                            print(f"  Vulnérabilités: {len(vulnerabilities)}, Exploits: {len(exploits)}")
                        except Exception as e:
                            print(f"✗ Erreur lors de la sauvegarde du scan: {e}")
            
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Erreur JSON du message: {e}")
            
            # Envoyer une réponse de confirmation
            try:
                await websocket.send(json.dumps({"status": "ok", "message": "Rapport bien reçu."}))
            except Exception as e:
                print(f"Erreur lors de l'envoi de la réponse: {e}")
                
    except websockets.exceptions.ConnectionClosedError:
        print(f"Agent {websocket.remote_address} déconnecté.")
    except Exception as e:
        print(f"Une erreur est survenue avec l'agent {websocket.remote_address}: {e}")
    finally:
        # Marquer l'agent comme offline au lieu de le supprimer
        if agent_id and agent_id in AGENT_CONNECTIONS:
            AGENT_CONNECTIONS[agent_id]["status"] = "offline"
            AGENT_CONNECTIONS[agent_id]["websocket"] = None
            AGENT_CONNECTIONS[agent_id]["last_seen"] = datetime.utcnow()
            print(f"Agent {agent_id} marqué offline")


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
    recent_vulns = []
    try:
        if mongo_scans_db is not None:
            async for scan in mongo_scans_db.scans.find().sort("timestamp", -1).limit(30):
                scan_target = scan.get("ip_interface") or scan.get("scan_target", "Unknown")
                agent_id = scan.get("agent_id", "Unknown")
                timestamp = scan.get("timestamp", datetime.utcnow())
                for vuln in scan.get("vulnerabilities", []):
                    recent_vulns.append({
                        "title": vuln.get("title", "Vulnérabilité inconnue"),
                        "severity": vuln.get("severity", "unknown"),
                        "port": vuln.get("port"),
                        "cve": vuln.get("cve"),
                        "scan_target": scan_target,
                        "agent_id": agent_id,
                        "timestamp": timestamp,
                    })
                    if len(recent_vulns) >= 10:
                        break
                if len(recent_vulns) >= 10:
                    break
    except Exception as e:
        print(f"Erreur lors de la récupération des vulnérabilités: {e}")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
        "recent_vulns": recent_vulns,
        "recent_vulns_count": len(recent_vulns)
    })


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
            "address": f"{info.get('agent_address', agent_id)}:{info.get('agent_port', '')}" if info.get('agent_port') else info.get("agent_address", agent_id),
            "scan_target": info.get("ip_interface") or "Non configuré",
            "status": info.get("status", "online")
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
        "agent_address": f"{agent_info.get('agent_address', agent_id)}:{agent_info.get('agent_port', '')}" if agent_info.get('agent_port') else agent_info.get("agent_address", agent_id),
        "scan_target": agent_info.get("ip_interface") or "Non configuré",
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


@app.get("/app/history", response_class=HTMLResponse)
async def history_page(request: Request, current_user: Optional[dict] = Depends(get_current_user)):
    """Page d'historique des scans"""
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    # Récupérer les derniers scans depuis MongoDB et grouper par IP
    scans_by_ip = {}
    all_vulns_by_ip = {}
    
    try:
        if mongo_scans_db is not None:
            # Récupérer les 100 derniers scans triés par timestamp décroissant
            async for scan in mongo_scans_db.scans.find().sort("timestamp", -1).limit(100):
                scan_target = scan.get("ip_interface") or scan.get("scan_target", "Unknown")
                
                # Initialiser le groupe IP si nécessaire
                if scan_target not in scans_by_ip:
                    scans_by_ip[scan_target] = []
                    all_vulns_by_ip[scan_target] = []
                
                # Ajouter le scan
                scans_by_ip[scan_target].append({
                    "agent_id": scan.get("agent_id", "Unknown"),
                    "scan_target": scan_target,
                    "timestamp": scan.get("timestamp", datetime.utcnow()),
                    "vulnerabilities_count": len(scan.get("vulnerabilities", [])),
                    "exploits_count": len(scan.get("exploits", [])),
                    "open_ports": scan.get("nmap_result", {}).get("summary", {}).get("open_ports", 0),
                    "vulnerabilities": scan.get("vulnerabilities", [])[:5]  # Top 5 vulnérabilités
                })
                
                # Collecter toutes les vulnérabilités pour cette IP
                for vuln in scan.get("vulnerabilities", []):
                    # Éviter les doublons
                    vuln_key = f"{vuln.get('title')}:{vuln.get('cve')}"
                    if not any(v.get('title') == vuln.get('title') and v.get('cve') == vuln.get('cve') 
                              for v in all_vulns_by_ip[scan_target]):
                        all_vulns_by_ip[scan_target].append(vuln)
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique: {e}")
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "user": current_user,
        "scans_by_ip": scans_by_ip,
        "all_vulns_by_ip": all_vulns_by_ip,
        "count": sum(len(scans) for scans in scans_by_ip.values())
    })




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
        agent_info["ip_interface"] = ip_interface
        return {"status": "command_sent", "agent_id": agent_id, "ip_interface": ip_interface}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur: {e}")


@app.get("/api/agents/connected")
async def list_connected_agents():
    """Liste tous les agents actuellement connectés"""
    return {"agents": list(AGENT_CONNECTIONS.keys()), "count": len(AGENT_CONNECTIONS)}


@app.get("/api/debug/scans")
async def debug_scans(current_user: Optional[dict] = Depends(get_current_user)):
    """Debug: Affiche tous les scans dans la base de données"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    scans = []
    try:
        if mongo_scans_db is not None:
            async for scan in mongo_scans_db.scans.find().limit(10):
                # Convertir ObjectId en string
                scan["_id"] = str(scan["_id"])
                scans.append(scan)
        return {"scans": scans, "count": len(scans)}
    except Exception as e:
        return {"error": str(e), "scans": []}


@app.post("/api/agents/{agent_id}/generate-report")
async def generate_security_report(agent_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """
    Génère un rapport d'audit de sécurité en PDF.
    Combine les données Nmap, vulnérabilités et exploits.
    """
    if agent_id not in AGENT_CONNECTIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent non trouvé")
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non autorisé")
    
    agent_info = AGENT_CONNECTIONS[agent_id]
    nmap_result = agent_info.get("last_nmap")
    
    if not nmap_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun résultat de scan disponible")
    
    try:
        # .get(...) ne renvoie pas le fallback si la valeur existe mais vaut None
        scan_target = agent_info.get("ip_interface") or "Non configuré"
        
        # Générer le rapport PDF
        report_generator = SecurityAuditReportGenerator(
            agent_id=agent_id,
            scan_target=scan_target,
            nmap_result=nmap_result
        )
        
        pdf_buffer = report_generator.generate()
        
        # Retourner le PDF en téléchargement
        filename = f"rapport_audit_{agent_id}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du rapport: {str(e)}"
        )


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
