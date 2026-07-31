"""
Google Ads MCP Server - Setup & Konfiguration
================================================
Konfiguriert den offiziellen Google Ads MCP Server für die Manus-Integration.
Ermöglicht KI-gestützte Analyse und Verwaltung von Google Ads Kampagnen.

MCP Server: https://github.com/google-marketing-solutions/google_ads_mcp
Dokumentation: https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server

Voraussetzungen:
    1. Google Ads Developer Token
    2. OAuth2 Client ID + Secret (Google Cloud Console)
    3. Refresh Token (über OAuth2 Flow)
    4. Google Ads Customer ID

FassadenFix Corporate Design: #77bc1f (Primär), #4e5758 (Sekundär)
"""

import os
import json
import subprocess
import logging
from typing import Optional, Dict

logger = logging.getLogger("google_ads_mcp_setup")

# ==================== MCP SERVER KONFIGURATION ====================

MCP_SERVER_CONFIG = {
    "name": "google-ads",
    "description": "Google Ads MCP Server für FassadenFix Kampagnenmanagement",
    "repository": "https://github.com/google-marketing-solutions/google_ads_mcp",
    "transport": "stdio",
    "command": "python",
    "args": ["-m", "google_ads_mcp"],
    "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "${GOOGLE_ADS_DEVELOPER_TOKEN}",
        "GOOGLE_ADS_CLIENT_ID": "${GOOGLE_ADS_CLIENT_ID}",
        "GOOGLE_ADS_CLIENT_SECRET": "${GOOGLE_ADS_CLIENT_SECRET}",
        "GOOGLE_ADS_REFRESH_TOKEN": "${GOOGLE_ADS_REFRESH_TOKEN}",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "${GOOGLE_ADS_LOGIN_CUSTOMER_ID}",
    },
    "available_tools": [
        "search_campaigns",
        "get_campaign_performance",
        "get_ad_group_performance",
        "get_keyword_performance",
        "get_search_terms_report",
        "get_account_budget",
        "get_change_history",
        "execute_gaql_query",
    ],
}


def generate_manus_mcp_config() -> Dict:
    """
    Generiert die MCP-Konfiguration für Manus.
    Diese Konfiguration wird in den Manus MCP-Einstellungen hinterlegt.
    """
    return {
        "mcpServers": {
            "google-ads": {
                "command": "npx",
                "args": [
                    "-y",
                    "@anthropic-ai/mcp-server-google-ads"
                ],
                "env": {
                    "GOOGLE_ADS_DEVELOPER_TOKEN": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
                    "GOOGLE_ADS_CLIENT_ID": os.environ.get("GOOGLE_ADS_CLIENT_ID", ""),
                    "GOOGLE_ADS_CLIENT_SECRET": os.environ.get("GOOGLE_ADS_CLIENT_SECRET", ""),
                    "GOOGLE_ADS_REFRESH_TOKEN": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", ""),
                    "GOOGLE_ADS_LOGIN_CUSTOMER_ID": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", ""),
                },
            }
        }
    }


def generate_env_template() -> str:
    """Generiert ein .env Template für die Google Ads Konfiguration."""
    return """# Google Ads MCP Server - Umgebungsvariablen
# =============================================
# Anleitung: https://developers.google.com/google-ads/api/docs/get-started/introduction

# Developer Token (aus Google Ads API Center)
GOOGLE_ADS_DEVELOPER_TOKEN=

# OAuth2 Credentials (aus Google Cloud Console)
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=

# FassadenFix Google Ads Kunden-ID (ohne Bindestriche)
GOOGLE_ADS_LOGIN_CUSTOMER_ID=
"""


def install_mcp_server() -> bool:
    """Installiert den Google Ads MCP Server."""
    try:
        result = subprocess.run(
            ["pip3", "install", "google-ads-mcp"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            logger.info("Google Ads MCP Server erfolgreich installiert.")
            return True
        else:
            logger.warning(f"Installation fehlgeschlagen: {result.stderr}")
            # Fallback: Direkt von GitHub
            result2 = subprocess.run(
                ["pip3", "install", "git+https://github.com/google-marketing-solutions/google_ads_mcp.git"],
                capture_output=True,
                text=True,
                timeout=180,
            )
            return result2.returncode == 0
    except Exception as e:
        logger.error(f"Fehler bei Installation: {e}")
        return False


def verify_credentials() -> Dict[str, bool]:
    """Prüft, ob alle erforderlichen Umgebungsvariablen gesetzt sind."""
    required_vars = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    ]
    return {var: bool(os.environ.get(var)) for var in required_vars}


# ==================== ALTERNATIVE: Python API Client ====================

class GoogleAdsClient:
    """
    Fallback Python-Client für Google Ads API (ohne MCP).
    Nutzt die offizielle google-ads Python Library.

    Verwendung:
        client = GoogleAdsClient()
        campaigns = client.get_campaigns()
    """

    def __init__(self):
        self.developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")
        self.client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
        self.client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")
        self.refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", "")
        self.customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
        self._client = None

    def _get_client(self):
        """Initialisiert den Google Ads Client."""
        if self._client is None:
            try:
                from google.ads.googleads.client import GoogleAdsClient as GAClient
                credentials = {
                    "developer_token": self.developer_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "login_customer_id": self.customer_id,
                    "use_proto_plus": True,
                }
                self._client = GAClient.load_from_dict(credentials)
            except ImportError:
                raise ImportError(
                    "google-ads Paket nicht installiert. "
                    "Installiere mit: pip install google-ads"
                )
        return self._client

    def execute_gaql(self, query: str) -> list:
        """Führt eine Google Ads Query Language (GAQL) Abfrage aus."""
        client = self._get_client()
        ga_service = client.get_service("GoogleAdsService")
        response = ga_service.search(
            customer_id=self.customer_id,
            query=query,
        )
        return list(response)

    def get_campaigns(self) -> list:
        """Listet alle Kampagnen auf."""
        query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign_budget.amount_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name
        """
        return self.execute_gaql(query)

    def get_campaign_performance(self, campaign_id: str, date_range: str = "LAST_30_DAYS") -> list:
        """Gibt Performance-Daten einer Kampagne zurück."""
        query = f"""
        SELECT
            campaign.name,
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.average_cpc
        FROM campaign
        WHERE campaign.id = {campaign_id}
            AND segments.date DURING {date_range}
        ORDER BY segments.date DESC
        """
        return self.execute_gaql(query)


if __name__ == "__main__":
    print("=== Google Ads MCP Server Konfiguration ===")
    print()
    print("Credential-Status:")
    status = verify_credentials()
    for var, is_set in status.items():
        icon = "✓" if is_set else "✗"
        print(f"  {icon} {var}")
    print()
    print("MCP Konfiguration:")
    print(json.dumps(generate_manus_mcp_config(), indent=2))
    print()
    print(".env Template:")
    print(generate_env_template())
