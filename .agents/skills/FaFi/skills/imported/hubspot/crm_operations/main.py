"""
HubSpot CRM Operations Skill (Imported)
=======================================
Führt CRM-Operationen über den HubSpot MCP-Server durch.
"""

import subprocess
import json
from typing import Dict, Any


def execute(operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Führt eine HubSpot CRM-Operation durch.
    
    Args:
        operation: Art der Operation (create_contact, search_contacts, etc.)
        data: Daten für die Operation
        
    Returns:
        Dictionary mit result und status
    """
    # Mapping von Operationen zu MCP-Tools
    operation_mapping = {
        "create_contact": "create_contact",
        "search_contacts": "search_contacts",
        "update_contact": "update_contact",
        "create_company": "create_company",
        "search_companies": "search_companies",
        "create_deal": "create_deal",
        "search_deals": "search_deals",
        "create_ticket": "create_ticket"
    }
    
    tool_name = operation_mapping.get(operation)
    
    if not tool_name:
        return {
            "result": None,
            "status": f"Unbekannte Operation: {operation}"
        }
    
    try:
        # Führe MCP-Befehl aus
        cmd = [
            "manus-mcp-cli",
            "tool", "call", tool_name,
            "--server", "hubspot",
            "--input", json.dumps(data)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                return {
                    "result": output,
                    "status": "success"
                }
            except json.JSONDecodeError:
                return {
                    "result": result.stdout,
                    "status": "success"
                }
        else:
            return {
                "result": None,
                "status": f"Fehler: {result.stderr}"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "result": None,
            "status": "Zeitüberschreitung bei der MCP-Anfrage"
        }
    except Exception as e:
        return {
            "result": None,
            "status": f"Fehler: {str(e)}"
        }


def create_contact(email: str, firstname: str = None, lastname: str = None, **kwargs) -> Dict[str, Any]:
    """Hilfsfunktion zum Erstellen eines Kontakts."""
    data = {"email": email}
    if firstname:
        data["firstname"] = firstname
    if lastname:
        data["lastname"] = lastname
    data.update(kwargs)
    return execute("create_contact", data)


def search_contacts(query: str, limit: int = 10) -> Dict[str, Any]:
    """Hilfsfunktion zum Suchen von Kontakten."""
    return execute("search_contacts", {"query": query, "limit": limit})


def create_deal(dealname: str, amount: float = None, **kwargs) -> Dict[str, Any]:
    """Hilfsfunktion zum Erstellen eines Deals."""
    data = {"dealname": dealname}
    if amount:
        data["amount"] = amount
    data.update(kwargs)
    return execute("create_deal", data)


# Für direkten Aufruf
if __name__ == "__main__":
    # Beispiel: Kontakte suchen
    result = search_contacts("test@example.com")
    print(json.dumps(result, indent=2, ensure_ascii=False))
