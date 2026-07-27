"""
Sipgate VoIP REST API Client
==============================
Konnektor für Sipgate Telefonie (https://sipgate.de)
Ermöglicht Zugriff auf Anrufhistorie, SMS-Versand, Kontakte und Voicemails.

API-Dokumentation: https://api.sipgate.com/v2/doc
Auth: Personal Access Token (PAT) oder OAuth2
Developer Hub: https://en.sipgate.io

FassadenFix Corporate Design: #77bc1f (Primär), #4e5758 (Sekundär)
"""

import os
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("sipgate_client")


@dataclass
class SipgateCall:
    """Repräsentiert einen Sipgate-Anruf."""
    id: str
    source: str
    target: str
    direction: str  # 'incoming' oder 'outgoing'
    created: str
    duration: Optional[int] = None
    status: Optional[str] = None


@dataclass
class SipgateSMS:
    """Repräsentiert eine SMS-Nachricht."""
    id: Optional[str] = None
    recipient: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None


class SipgateClient:
    """
    Python-Client für die Sipgate REST API v2.

    Verwendung:
        client = SipgateClient(token_id="your_token_id", token="your_token")
        history = client.get_call_history()
        client.send_sms("+491234567890", "Nachricht")
    """

    BASE_URL = "https://api.sipgate.com/v2"

    def __init__(
        self,
        token_id: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.token_id = token_id or os.environ.get("SIPGATE_TOKEN_ID", "")
        self.token = token or os.environ.get("SIPGATE_TOKEN", "")

        if not self.token_id or not self.token:
            logger.warning(
                "Sipgate-Credentials nicht konfiguriert. "
                "Setze SIPGATE_TOKEN_ID und SIPGATE_TOKEN als Umgebungsvariablen."
            )

        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.auth = (self.token_id, self.token)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Führt einen GET-Request gegen die Sipgate API aus."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Führt einen POST-Request gegen die Sipgate API aus."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        if response.content:
            return response.json()
        return {"status": "ok"}

    # ==================== ACCOUNT ====================

    def get_account_info(self) -> Dict:
        """Gibt Account-Informationen zurück."""
        return self._get("account")

    def get_users(self) -> List[Dict]:
        """Listet alle Benutzer des Accounts auf."""
        data = self._get("users")
        return data.get("items", [])

    # ==================== ANRUFHISTORIE ====================

    def get_call_history(
        self,
        limit: int = 50,
        offset: int = 0,
        direction: Optional[str] = None,
    ) -> List[SipgateCall]:
        """
        Gibt die Anrufhistorie zurück.

        Args:
            limit: Maximale Anzahl der Einträge
            offset: Startposition
            direction: 'incoming' oder 'outgoing' (optional)

        Returns:
            Liste von SipgateCall-Objekten
        """
        params = {"limit": limit, "offset": offset}
        if direction:
            params["direction"] = direction

        data = self._get("history", params=params)
        calls = []
        for item in data.get("items", []):
            calls.append(SipgateCall(
                id=item.get("id", ""),
                source=item.get("source", ""),
                target=item.get("target", ""),
                direction=item.get("direction", ""),
                created=item.get("created", ""),
                duration=item.get("duration"),
                status=item.get("status"),
            ))
        return calls

    # ==================== SMS ====================

    def send_sms(
        self,
        recipient: str,
        message: str,
        sms_id: Optional[str] = None,
    ) -> Dict:
        """
        Sendet eine SMS über Sipgate.

        Args:
            recipient: Telefonnummer des Empfängers (E.164 Format, z.B. +491234567890)
            message: Nachrichtentext
            sms_id: SMS-Extension ID (z.B. 's0', optional)

        Returns:
            API-Antwort
        """
        payload = {
            "recipient": recipient,
            "message": message,
        }
        if sms_id:
            payload["smsId"] = sms_id

        return self._post("sessions/sms", data=payload)

    # ==================== VOICEMAIL ====================

    def get_voicemails(self) -> List[Dict]:
        """Listet alle Voicemails auf."""
        data = self._get("voicemails")
        return data.get("items", [])

    # ==================== KONTAKTE ====================

    def get_contacts(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Listet Sipgate-Kontakte auf."""
        params = {"limit": limit, "offset": offset}
        data = self._get("contacts", params=params)
        return data.get("items", [])

    def create_contact(
        self,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> Dict:
        """Erstellt einen neuen Kontakt."""
        payload = {
            "name": {"firstName": first_name, "lastName": last_name},
        }
        if phone:
            payload["phones"] = [{"number": phone, "type": ["CELL"]}]
        if email:
            payload["emails"] = [{"email": email, "type": ["WORK"]}]
        if organization:
            payload["organization"] = [[organization]]

        return self._post("contacts", data=payload)

    # ==================== NUMMERN ====================

    def get_numbers(self) -> List[Dict]:
        """Listet alle verfügbaren Telefonnummern auf."""
        data = self._get("numbers")
        return data.get("items", [])

    # ==================== DEVICES ====================

    def get_devices(self, user_id: str) -> List[Dict]:
        """Listet Geräte eines Benutzers auf."""
        data = self._get(f"{user_id}/devices")
        return data.get("items", [])


def get_sipgate_client(
    token_id: Optional[str] = None,
    token: Optional[str] = None,
) -> SipgateClient:
    """Erstellt und gibt einen konfigurierten Sipgate-Client zurück."""
    return SipgateClient(token_id=token_id, token=token)
