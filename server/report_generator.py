"""
Générateur de rapports d'audit de sécurité en PDF.
Utilise reportlab pour générer les rapports à partir des données Nmap, vulnérabilités et exploits.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


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
        self.scan_target = scan_target
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
        story.append(PageBreak())
        
        # Résultats Nmap
        story.extend(self._build_nmap_section(styles))
        story.append(Spacer(1, 0.2*inch))
        
        # Vulnérabilités détectées
        if self.vulnerabilities:
            story.append(PageBreak())
            story.extend(self._build_vulnerabilities_section(styles))
            story.append(Spacer(1, 0.2*inch))
        
        # Exploits disponibles
        if self.exploits:
            story.append(PageBreak())
            story.extend(self._build_exploits_section(styles))
            story.append(Spacer(1, 0.2*inch))
        
        # Recommandations
        story.append(PageBreak())
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
