"""
HERO Software GraphQL API Client
=================================
Konnektor für die HERO Handwerkersoftware (https://hero-software.de)
Ermöglicht Zugriff auf Kontakte, Projekte, Dokumente, Termine und Artikel.

API-Dokumentation: https://hero-software.de/api-doku/graphql-guide
Endpoint: https://login.hero-software.de/api/external/v7/graphql
Auth: Bearer Token (API-Key vom HERO Support anfordern)

FassadenFix Corporate Design: #77bc1f (Primär), #4e5758 (Sekundär)
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("hero_software_client")


@dataclass
class HeroContact:
    """Repräsentiert einen HERO-Kontakt."""
    id: int
    nr: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone_home: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    zipcode: Optional[str] = None


@dataclass
class HeroProject:
    """Repräsentiert ein HERO-Projekt."""
    id: int
    project_nr: Optional[str] = None
    measure_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_zipcode: Optional[str] = None
    status_code: Optional[str] = None
    status_name: Optional[str] = None


@dataclass
class HeroDocument:
    """Repräsentiert ein HERO-Dokument."""
    id: int
    nr: Optional[str] = None
    value: Optional[float] = None
    status_code: Optional[str] = None
    document_type: Optional[str] = None
    file_url: Optional[str] = None
    created: Optional[str] = None


class HeroSoftwareClient:
    """
    Python-Client für die HERO Software GraphQL API.

    Verwendung:
        client = HeroSoftwareClient(api_key="YOUR_API_KEY")
        contacts = client.get_contacts()
        projects = client.get_projects()
    """

    BASE_URL = "https://login.hero-software.de/api/external/v7/graphql"
    LEAD_API_URL = "https://login.hero-software.de/api/external/v1/leads"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("HERO_API_KEY", "")
        if not self.api_key:
            logger.warning("Kein HERO API-Key konfiguriert. Setze HERO_API_KEY als Umgebungsvariable.")

        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })

    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Führt eine GraphQL-Abfrage gegen die HERO API aus."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = self.session.post(self.BASE_URL, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if "errors" in result:
                error_msgs = [e.get("message", "Unbekannter Fehler") for e in result["errors"]]
                raise Exception(f"HERO GraphQL Fehler: {'; '.join(error_msgs)}")

            return result.get("data", {})

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP-Fehler bei HERO API: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Verbindungsfehler zur HERO API: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout bei HERO API: {e}")
            raise

    # ==================== KONTAKTE ====================

    def get_contacts(
        self,
        category: Optional[str] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[HeroContact]:
        """
        Listet Kontakte aus HERO auf.

        Args:
            category: Filtert nach Kategorie (z.B. 'customer', 'supplier')
            offset: Startposition für Paginierung
            limit: Maximale Anzahl (Standard: 50)

        Returns:
            Liste von HeroContact-Objekten
        """
        query = """
        query ($category: CustomerCategoryEnum, $offset: Int) {
            contacts(category: $category, orderBy: "id", offset: $offset) {
                id
                nr
                first_name
                last_name
                company_name
                email
                phone_home
                address {
                    street
                    city
                    zipcode
                }
            }
        }
        """
        variables = {"offset": offset}
        if category:
            variables["category"] = category

        data = self._execute_query(query, variables)
        contacts = []
        for c in data.get("contacts", []):
            addr = c.get("address", {}) or {}
            contacts.append(HeroContact(
                id=c["id"],
                nr=c.get("nr"),
                first_name=c.get("first_name"),
                last_name=c.get("last_name"),
                company_name=c.get("company_name"),
                email=c.get("email"),
                phone_home=c.get("phone_home"),
                street=addr.get("street"),
                city=addr.get("city"),
                zipcode=addr.get("zipcode"),
            ))
        return contacts

    def create_contact(
        self,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        company_name: Optional[str] = None,
        phone: Optional[str] = None,
        street: Optional[str] = None,
        city: Optional[str] = None,
        zipcode: Optional[str] = None,
    ) -> Dict:
        """Erstellt einen neuen Kontakt in HERO."""
        query = """
        mutation ($input: CreateContactInput!) {
            create_contact(input: $input) {
                id
                nr
                first_name
                last_name
            }
        }
        """
        input_data = {
            "first_name": first_name,
            "last_name": last_name,
        }
        if email:
            input_data["email"] = email
        if company_name:
            input_data["company_name"] = company_name
        if phone:
            input_data["phone_home"] = phone
        if street or city or zipcode:
            input_data["address"] = {}
            if street:
                input_data["address"]["street"] = street
            if city:
                input_data["address"]["city"] = city
            if zipcode:
                input_data["address"]["zipcode"] = zipcode

        return self._execute_query(query, {"input": input_data})

    # ==================== PROJEKTE ====================

    def get_projects(
        self,
        ids: Optional[List[int]] = None,
        offset: int = 0
    ) -> List[HeroProject]:
        """
        Listet Projekte aus HERO auf.

        Args:
            ids: Optional - Filtert nach bestimmten Projekt-IDs
            offset: Startposition für Paginierung

        Returns:
            Liste von HeroProject-Objekten
        """
        if ids:
            query = """
            query ($ids: [Int!]) {
                project_matches(ids: $ids) {
                    id
                    project_nr
                    measure { short name }
                    customer { id first_name last_name email }
                    contact { id first_name last_name email }
                    address { street city zipcode }
                    current_project_match_status { status_code name }
                }
            }
            """
            variables = {"ids": ids}
        else:
            query = """
            query ($offset: Int) {
                project_matches(offset: $offset) {
                    id
                    project_nr
                    measure { short name }
                    customer { id first_name last_name email }
                    address { street city zipcode }
                    current_project_match_status { status_code name }
                }
            }
            """
            variables = {"offset": offset}

        data = self._execute_query(query, variables)
        projects = []
        for p in data.get("project_matches", []):
            customer = p.get("customer", {}) or {}
            addr = p.get("address", {}) or {}
            status = p.get("current_project_match_status", {}) or {}
            measure = p.get("measure", {}) or {}
            projects.append(HeroProject(
                id=p["id"],
                project_nr=p.get("project_nr"),
                measure_name=measure.get("name"),
                customer_name=f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                customer_email=customer.get("email"),
                address_street=addr.get("street"),
                address_city=addr.get("city"),
                address_zipcode=addr.get("zipcode"),
                status_code=status.get("status_code"),
                status_name=status.get("name"),
            ))
        return projects

    def create_project(
        self,
        customer_id: int,
        description: Optional[str] = None,
        measure_id: Optional[int] = None,
    ) -> Dict:
        """Erstellt ein neues Projekt in HERO."""
        query = """
        mutation ($input: CreateProjectMatchInput!) {
            create_project_match(input: $input) {
                id
                project_nr
            }
        }
        """
        input_data = {"customer_id": customer_id}
        if description:
            input_data["description"] = description
        if measure_id:
            input_data["measure_id"] = measure_id

        return self._execute_query(query, {"input": input_data})

    # ==================== DOKUMENTE ====================

    def get_documents(
        self,
        project_id: Optional[int] = None,
        offset: int = 0
    ) -> List[HeroDocument]:
        """Listet Dokumente aus HERO auf."""
        if project_id:
            query = """
            query ($ids: [Int!]) {
                project_matches(ids: $ids) {
                    customer_documents {
                        id
                        type
                        nr
                        value
                        created
                        status_code
                        document_type { base_type name }
                        file_upload { url }
                    }
                }
            }
            """
            variables = {"ids": [project_id]}
        else:
            query = """
            query ($offset: Int) {
                customer_documents(offset: $offset) {
                    id
                    nr
                    value
                    created
                    status_code
                    document_type { base_type name }
                    file_upload { url }
                }
            }
            """
            variables = {"offset": offset}

        data = self._execute_query(query, variables)

        docs = []
        if project_id:
            for pm in data.get("project_matches", []):
                for d in pm.get("customer_documents", []):
                    doc_type = d.get("document_type", {}) or {}
                    file_upload = d.get("file_upload", {}) or {}
                    docs.append(HeroDocument(
                        id=d.get("id", 0),
                        nr=d.get("nr"),
                        value=d.get("value"),
                        status_code=d.get("status_code"),
                        document_type=doc_type.get("name"),
                        file_url=file_upload.get("url"),
                        created=d.get("created"),
                    ))
        else:
            for d in data.get("customer_documents", []):
                doc_type = d.get("document_type", {}) or {}
                file_upload = d.get("file_upload", {}) or {}
                docs.append(HeroDocument(
                    id=d.get("id", 0),
                    nr=d.get("nr"),
                    value=d.get("value"),
                    status_code=d.get("status_code"),
                    document_type=doc_type.get("name"),
                    file_url=file_upload.get("url"),
                    created=d.get("created"),
                ))
        return docs

    # ==================== TERMINE ====================

    def get_calendar_events(self, offset: int = 0) -> List[Dict]:
        """Listet Kalendereinträge aus HERO auf."""
        query = """
        query ($offset: Int) {
            calendar_events(offset: $offset) {
                id
                title
                start
                end
                all_day
                description
            }
        }
        """
        data = self._execute_query(query, {"offset": offset})
        return data.get("calendar_events", [])

    # ==================== LOGBUCH ====================

    def add_logbook_entry(
        self,
        project_id: int,
        title: str,
        text: str,
    ) -> Dict:
        """Fügt einen Logbucheintrag zu einem Projekt hinzu."""
        query = """
        mutation ($input: AddLogbookEntryInput!) {
            add_logbook_entry(input: $input) {
                id
                custom_title
                custom_text
                created
            }
        }
        """
        return self._execute_query(query, {
            "input": {
                "project_match_id": project_id,
                "custom_title": title,
                "custom_text": text,
            }
        })

    # ==================== LEAD API (REST) ====================

    def create_lead(
        self,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        message: Optional[str] = None,
        source: str = "Manus/FaFi",
    ) -> Dict:
        """
        Erstellt einen neuen Lead über die HERO Lead API (REST).
        Ideal für Kontaktformulare und automatisierte Lead-Imports.
        """
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "source": source,
        }
        if email:
            payload["email"] = email
        if phone:
            payload["phone"] = phone
        if message:
            payload["message"] = message

        response = self.session.post(
            self.LEAD_API_URL,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    # ==================== CUSTOM QUERY ====================

    def execute_custom_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """
        Führt eine benutzerdefinierte GraphQL-Abfrage aus.
        Nützlich für erweiterte Abfragen, die nicht durch die Standard-Methoden abgedeckt sind.
        """
        return self._execute_query(query, variables)


# Convenience-Funktion für schnellen Zugriff
def get_hero_client(api_key: Optional[str] = None) -> HeroSoftwareClient:
    """Erstellt und gibt einen konfigurierten HERO-Client zurück."""
    return HeroSoftwareClient(api_key=api_key)
