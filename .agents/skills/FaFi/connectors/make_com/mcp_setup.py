"""
Make.com MCP Server - Setup & Konfiguration
=============================================
Konfiguriert den Make.com MCP Server für die Manus-Integration.
Ermöglicht Automatisierung von 3000+ Apps inkl. HERO Software.

MCP Server: https://developers.make.com/mcp-server
Dokumentation: https://developers.make.com/

Voraussetzungen:
    1. Make.com Account (Team oder Enterprise)
    2. API Token (aus Make.com Profil-Einstellungen)

FassadenFix Corporate Design: #77bc1f (Primär), #4e5758 (Sekundär)
"""

import os
import json
import logging
from typing import Optional, Dict, List

logger = logging.getLogger("make_com_mcp_setup")

# ==================== MCP SERVER KONFIGURATION ====================

MCP_SERVER_CONFIG = {
    "name": "make",
    "description": "Make.com Automatisierung für FassadenFix Workflows",
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@anthropic-ai/mcp-server-make"],
    "env": {
        "MAKE_API_TOKEN": "${MAKE_API_TOKEN}",
        "MAKE_TEAM_ID": "${MAKE_TEAM_ID}",
        "MAKE_ZONE": "eu1",
    },
    "available_tools": [
        "list_scenarios",
        "run_scenario",
        "get_scenario_details",
        "list_connections",
        "list_data_stores",
        "search_data_store",
    ],
}


def generate_manus_mcp_config() -> Dict:
    """
    Generiert die MCP-Konfiguration für Manus.
    """
    return {
        "mcpServers": {
            "make": {
                "url": "https://eu1.make.com/api/mcp/sse",
                "headers": {
                    "Authorization": f"Token {os.environ.get('MAKE_API_TOKEN', '')}",
                },
            }
        }
    }


def generate_env_template() -> str:
    """Generiert ein .env Template für die Make.com Konfiguration."""
    return """# Make.com MCP Server - Umgebungsvariablen
# ==========================================
# API Token: Make.com > Profil > API

# Make.com API Token
MAKE_API_TOKEN=

# Team ID (aus Make.com URL)
MAKE_TEAM_ID=

# Zone (eu1 für Europa, us1 für USA)
MAKE_ZONE=eu1
"""


# ==================== EMPFOHLENE SZENARIEN ====================

RECOMMENDED_SCENARIOS = [
    {
        "name": "HERO → HubSpot Kontakt-Sync",
        "description": "Synchronisiert neue Kontakte aus HERO automatisch nach HubSpot CRM",
        "trigger": "HERO Software - Watch Contacts",
        "actions": ["HubSpot - Create/Update Contact"],
        "priority": "hoch",
    },
    {
        "name": "HubSpot Deal → HERO Projekt",
        "description": "Erstellt automatisch ein HERO-Projekt wenn ein HubSpot Deal gewonnen wird",
        "trigger": "HubSpot - Watch Deals (Status: Won)",
        "actions": ["HERO Software - Create Project"],
        "priority": "hoch",
    },
    {
        "name": "HERO Angebot → WhatsApp Benachrichtigung",
        "description": "Sendet eine WhatsApp-Nachricht wenn ein Angebot in HERO erstellt wird",
        "trigger": "HERO Software - Watch Documents",
        "actions": ["WhatsApp Business - Send Template Message"],
        "priority": "mittel",
    },
    {
        "name": "Sipgate Anruf → HubSpot Aktivität",
        "description": "Loggt eingehende Sipgate-Anrufe als Aktivität in HubSpot",
        "trigger": "Sipgate - Watch Calls",
        "actions": ["HubSpot - Create Engagement (Call)"],
        "priority": "mittel",
    },
    {
        "name": "Google Ads Lead → HERO Projekt",
        "description": "Importiert Google Ads Leads automatisch als HERO-Projekte",
        "trigger": "Google Ads - Watch Lead Form Submissions",
        "actions": ["HERO Software - Create Lead"],
        "priority": "hoch",
    },
    {
        "name": "Notion Update → Outlook Benachrichtigung",
        "description": "Sendet E-Mail-Benachrichtigungen bei wichtigen Notion-Updates",
        "trigger": "Notion - Watch Database Items",
        "actions": ["Outlook - Send Email"],
        "priority": "niedrig",
    },
]


def get_recommended_scenarios() -> List[Dict]:
    """Gibt die empfohlenen Automatisierungsszenarien zurück."""
    return RECOMMENDED_SCENARIOS


def verify_credentials() -> Dict[str, bool]:
    """Prüft, ob alle erforderlichen Umgebungsvariablen gesetzt sind."""
    required_vars = [
        "MAKE_API_TOKEN",
        "MAKE_TEAM_ID",
    ]
    return {var: bool(os.environ.get(var)) for var in required_vars}


# ==================== PYTHON API CLIENT (FALLBACK) ====================

class MakeClient:
    """
    Python-Client für die Make.com REST API.
    Fallback wenn MCP Server nicht verfügbar.
    """

    BASE_URL = "https://eu1.make.com/api/v2"

    def __init__(self, api_token: Optional[str] = None, team_id: Optional[str] = None):
        import requests
        self.api_token = api_token or os.environ.get("MAKE_API_TOKEN", "")
        self.team_id = team_id or os.environ.get("MAKE_TEAM_ID", "")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
        })

    def list_scenarios(self) -> List[Dict]:
        """Listet alle Szenarien auf."""
        response = self.session.get(
            f"{self.BASE_URL}/scenarios",
            params={"teamId": self.team_id},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("scenarios", [])

    def run_scenario(self, scenario_id: int, data: Optional[Dict] = None) -> Dict:
        """Führt ein Szenario aus."""
        response = self.session.post(
            f"{self.BASE_URL}/scenarios/{scenario_id}/run",
            json=data or {},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def get_scenario_details(self, scenario_id: int) -> Dict:
        """Gibt Details eines Szenarios zurück."""
        response = self.session.get(
            f"{self.BASE_URL}/scenarios/{scenario_id}",
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    print("=== Make.com MCP Server Konfiguration ===")
    print()
    print("Credential-Status:")
    status = verify_credentials()
    for var, is_set in status.items():
        icon = "✓" if is_set else "✗"
        print(f"  {icon} {var}")
    print()
    print("Empfohlene Szenarien:")
    for s in RECOMMENDED_SCENARIOS:
        print(f"  [{s['priority'].upper()}] {s['name']}")
        print(f"         {s['description']}")
    print()
    print("MCP Konfiguration:")
    print(json.dumps(generate_manus_mcp_config(), indent=2))
