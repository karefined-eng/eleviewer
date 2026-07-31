"""
Ricoh360 Tours Cloud API Client
=================================
Konnektor für Ricoh360 Tours (https://www.ricoh360.com/tours/)
Ermöglicht Verwaltung von 360-Grad-Touren, Bildern und Projekten.

API-Dokumentation: https://docs.ricoh360.com/
Auth: API Key (vom Team-Admin über Ricoh360 Dashboard)

FassadenFix Corporate Design: #77bc1f (Primär), #4e5758 (Sekundär)
"""

import os
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("ricoh360_client")


@dataclass
class Ricoh360Tour:
    """Repräsentiert eine 360-Grad-Tour."""
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    share_url: Optional[str] = None
    created_at: Optional[str] = None
    image_count: int = 0


@dataclass
class Ricoh360Image:
    """Repräsentiert ein 360-Grad-Bild."""
    id: str
    tour_id: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: Optional[str] = None


class Ricoh360Client:
    """
    Python-Client für die Ricoh360 Cloud API.

    Verwendung:
        client = Ricoh360Client(api_key="YOUR_API_KEY")
        tours = client.get_tours()
        images = client.get_tour_images(tour_id="...")
    """

    BASE_URL = "https://api.ricoh360.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("RICOH360_API_KEY", "")
        if not self.api_key:
            logger.warning(
                "Ricoh360 API-Key nicht konfiguriert. "
                "Setze RICOH360_API_KEY als Umgebungsvariable."
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Führt einen GET-Request gegen die Ricoh360 API aus."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Führt einen POST-Request gegen die Ricoh360 API aus."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint: str) -> Dict:
        """Führt einen DELETE-Request gegen die Ricoh360 API aus."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.delete(url, timeout=30)
        response.raise_for_status()
        if response.content:
            return response.json()
        return {"status": "deleted"}

    # ==================== TOUREN ====================

    def get_tours(self, limit: int = 50, offset: int = 0) -> List[Ricoh360Tour]:
        """Listet alle 360-Grad-Touren auf."""
        data = self._get("tours", params={"limit": limit, "offset": offset})
        tours = []
        for t in data.get("tours", data.get("data", [])):
            tours.append(Ricoh360Tour(
                id=t.get("id", ""),
                title=t.get("title"),
                description=t.get("description"),
                status=t.get("status"),
                share_url=t.get("share_url"),
                created_at=t.get("created_at"),
                image_count=t.get("image_count", 0),
            ))
        return tours

    def get_tour(self, tour_id: str) -> Ricoh360Tour:
        """Gibt Details einer einzelnen Tour zurück."""
        data = self._get(f"tours/{tour_id}")
        t = data.get("tour", data)
        return Ricoh360Tour(
            id=t.get("id", tour_id),
            title=t.get("title"),
            description=t.get("description"),
            status=t.get("status"),
            share_url=t.get("share_url"),
            created_at=t.get("created_at"),
            image_count=t.get("image_count", 0),
        )

    def create_tour(
        self,
        title: str,
        description: Optional[str] = None,
    ) -> Dict:
        """Erstellt eine neue 360-Grad-Tour."""
        payload = {"title": title}
        if description:
            payload["description"] = description
        return self._post("tours", data=payload)

    def delete_tour(self, tour_id: str) -> Dict:
        """Löscht eine Tour."""
        return self._delete(f"tours/{tour_id}")

    # ==================== BILDER ====================

    def get_tour_images(self, tour_id: str) -> List[Ricoh360Image]:
        """Listet alle Bilder einer Tour auf."""
        data = self._get(f"tours/{tour_id}/images")
        images = []
        for img in data.get("images", data.get("data", [])):
            images.append(Ricoh360Image(
                id=img.get("id", ""),
                tour_id=tour_id,
                url=img.get("url"),
                thumbnail_url=img.get("thumbnail_url"),
                created_at=img.get("created_at"),
            ))
        return images

    def upload_image(self, tour_id: str, file_path: str) -> Dict:
        """Lädt ein 360-Grad-Bild zu einer Tour hoch."""
        url = f"{self.BASE_URL}/tours/{tour_id}/images"
        with open(file_path, "rb") as f:
            response = self.session.post(
                url,
                files={"file": f},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=120,
            )
        response.raise_for_status()
        return response.json()

    # ==================== SHARING ====================

    def get_share_link(self, tour_id: str) -> str:
        """Gibt den öffentlichen Share-Link einer Tour zurück."""
        tour = self.get_tour(tour_id)
        return tour.share_url or ""


def get_ricoh360_client(api_key: Optional[str] = None) -> Ricoh360Client:
    """Erstellt und gibt einen konfigurierten Ricoh360-Client zurück."""
    return Ricoh360Client(api_key=api_key)
