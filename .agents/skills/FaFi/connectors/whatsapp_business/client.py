"""
WhatsApp Business Cloud API Client
=====================================
Konnektor für WhatsApp Business über die Meta Cloud API.
Ermöglicht Nachrichtenversand, Template-Management und Media-Upload.

API-Dokumentation: https://developers.facebook.com/docs/whatsapp/cloud-api
Auth: Meta Business Account + System User Token

FassadenFix Corporate Design: #77bc1f (Primär), #4e5758 (Sekundär)
"""

import os
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("whatsapp_business_client")


@dataclass
class WhatsAppMessage:
    """Repräsentiert eine WhatsApp-Nachricht."""
    id: Optional[str] = None
    recipient: Optional[str] = None
    message_type: Optional[str] = None
    status: Optional[str] = None
    timestamp: Optional[str] = None


class WhatsAppBusinessClient:
    """
    Python-Client für die WhatsApp Business Cloud API (Meta).

    Verwendung:
        client = WhatsAppBusinessClient(
            access_token="YOUR_TOKEN",
            phone_number_id="YOUR_PHONE_NUMBER_ID"
        )
        client.send_text_message("+491234567890", "Hallo!")
        client.send_template_message("+491234567890", "angebot_bestaetigung")
    """

    BASE_URL = "https://graph.facebook.com/v21.0"

    def __init__(
        self,
        access_token: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        business_account_id: Optional[str] = None,
    ):
        self.access_token = access_token or os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
        self.phone_number_id = phone_number_id or os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
        self.business_account_id = business_account_id or os.environ.get("WHATSAPP_BUSINESS_ACCOUNT_ID", "")

        if not self.access_token:
            logger.warning(
                "WhatsApp Access Token nicht konfiguriert. "
                "Setze WHATSAPP_ACCESS_TOKEN als Umgebungsvariable."
            )

        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        })

    def _post(self, endpoint: str, data: Dict) -> Dict:
        """Führt einen POST-Request gegen die Meta Graph API aus."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Führt einen GET-Request gegen die Meta Graph API aus."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    # ==================== NACHRICHTEN ====================

    def send_text_message(self, to: str, body: str) -> Dict:
        """
        Sendet eine Textnachricht über WhatsApp.

        Args:
            to: Empfänger-Telefonnummer (E.164 Format, z.B. +491234567890)
            body: Nachrichtentext

        Returns:
            API-Antwort mit Message-ID
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }
        return self._post(f"{self.phone_number_id}/messages", payload)

    def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "de",
        components: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Sendet eine Template-Nachricht über WhatsApp.

        Args:
            to: Empfänger-Telefonnummer
            template_name: Name des genehmigten Templates
            language_code: Sprachcode (Standard: 'de')
            components: Template-Komponenten mit Variablen

        Returns:
            API-Antwort
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }
        if components:
            payload["template"]["components"] = components

        return self._post(f"{self.phone_number_id}/messages", payload)

    def send_document_message(
        self,
        to: str,
        document_url: str,
        filename: str,
        caption: Optional[str] = None,
    ) -> Dict:
        """Sendet ein Dokument (z.B. PDF-Angebot) über WhatsApp."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url,
                "filename": filename,
            },
        }
        if caption:
            payload["document"]["caption"] = caption

        return self._post(f"{self.phone_number_id}/messages", payload)

    def send_image_message(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None,
    ) -> Dict:
        """Sendet ein Bild (z.B. Baustellenfoto) über WhatsApp."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {"link": image_url},
        }
        if caption:
            payload["image"]["caption"] = caption

        return self._post(f"{self.phone_number_id}/messages", payload)

    # ==================== TEMPLATES ====================

    def get_templates(self) -> List[Dict]:
        """Listet alle genehmigten Nachrichtenvorlagen auf."""
        data = self._get(
            f"{self.business_account_id}/message_templates",
            params={"limit": 100},
        )
        return data.get("data", [])

    # ==================== BUSINESS PROFILE ====================

    def get_business_profile(self) -> Dict:
        """Gibt das WhatsApp Business Profil zurück."""
        return self._get(
            f"{self.phone_number_id}/whatsapp_business_profile",
            params={"fields": "about,address,description,email,profile_picture_url,websites,vertical"},
        )

    def update_business_profile(
        self,
        about: Optional[str] = None,
        address: Optional[str] = None,
        description: Optional[str] = None,
        email: Optional[str] = None,
        websites: Optional[List[str]] = None,
    ) -> Dict:
        """Aktualisiert das WhatsApp Business Profil."""
        payload = {"messaging_product": "whatsapp"}
        if about:
            payload["about"] = about
        if address:
            payload["address"] = address
        if description:
            payload["description"] = description
        if email:
            payload["email"] = email
        if websites:
            payload["websites"] = websites

        return self._post(f"{self.phone_number_id}/whatsapp_business_profile", payload)

    # ==================== MEDIA ====================

    def upload_media(self, file_path: str, mime_type: str) -> Dict:
        """Lädt eine Mediendatei hoch für den Versand."""
        url = f"{self.BASE_URL}/{self.phone_number_id}/media"
        with open(file_path, "rb") as f:
            response = self.session.post(
                url,
                files={"file": (file_path, f, mime_type)},
                data={"messaging_product": "whatsapp", "type": mime_type},
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=60,
            )
        response.raise_for_status()
        return response.json()

    # ==================== MARK AS READ ====================

    def mark_as_read(self, message_id: str) -> Dict:
        """Markiert eine empfangene Nachricht als gelesen."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return self._post(f"{self.phone_number_id}/messages", payload)


def get_whatsapp_client(
    access_token: Optional[str] = None,
    phone_number_id: Optional[str] = None,
    business_account_id: Optional[str] = None,
) -> WhatsAppBusinessClient:
    """Erstellt und gibt einen konfigurierten WhatsApp-Client zurück."""
    return WhatsAppBusinessClient(
        access_token=access_token,
        phone_number_id=phone_number_id,
        business_account_id=business_account_id,
    )
