"""
Microsoft 365 Graph API Skill (Imported)
========================================
Führt Microsoft 365 Operationen über die Graph API durch.
"""

import os
import requests
from typing import Dict, Any, Optional


def execute(operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Führt eine Microsoft Graph API Operation durch.
    
    Args:
        operation: Art der Operation
        data: Daten für die Operation
        
    Returns:
        Dictionary mit result und status
    """
    access_token = os.environ.get("MICROSOFT_GRAPH_TOKEN")
    
    if not access_token:
        return {
            "result": None,
            "status": "Fehler: MICROSOFT_GRAPH_TOKEN nicht konfiguriert"
        }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    base_url = "https://graph.microsoft.com/v1.0"
    
    try:
        if operation == "send_email":
            return _send_email(base_url, headers, data)
        elif operation == "create_event":
            return _create_event(base_url, headers, data)
        elif operation == "search_files":
            return _search_files(base_url, headers, data)
        elif operation == "send_teams_message":
            return _send_teams_message(base_url, headers, data)
        elif operation == "get_calendar":
            return _get_calendar(base_url, headers, data)
        else:
            return {
                "result": None,
                "status": f"Unbekannte Operation: {operation}"
            }
    except Exception as e:
        return {
            "result": None,
            "status": f"Fehler: {str(e)}"
        }


def _send_email(base_url: str, headers: Dict, data: Dict) -> Dict[str, Any]:
    """Sendet eine E-Mail über Outlook."""
    payload = {
        "message": {
            "subject": data.get("subject", ""),
            "body": {
                "contentType": "HTML",
                "content": data.get("body", "")
            },
            "toRecipients": [
                {"emailAddress": {"address": data.get("to", "")}}
            ]
        }
    }
    
    # Füge CC hinzu, falls vorhanden
    if data.get("cc"):
        payload["message"]["ccRecipients"] = [
            {"emailAddress": {"address": cc}} for cc in data["cc"]
        ]
    
    response = requests.post(
        f"{base_url}/me/sendMail",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 202:
        return {"result": {"message": "E-Mail gesendet"}, "status": "success"}
    else:
        return {"result": None, "status": f"Fehler: {response.status_code} - {response.text}"}


def _create_event(base_url: str, headers: Dict, data: Dict) -> Dict[str, Any]:
    """Erstellt einen Kalendereintrag."""
    payload = {
        "subject": data.get("subject", ""),
        "start": {
            "dateTime": data.get("start", ""),
            "timeZone": data.get("timezone", "Europe/Berlin")
        },
        "end": {
            "dateTime": data.get("end", ""),
            "timeZone": data.get("timezone", "Europe/Berlin")
        }
    }
    
    # Füge Teilnehmer hinzu, falls vorhanden
    if data.get("attendees"):
        payload["attendees"] = [
            {
                "emailAddress": {"address": email},
                "type": "required"
            }
            for email in data["attendees"]
        ]
    
    # Füge Beschreibung hinzu
    if data.get("body"):
        payload["body"] = {
            "contentType": "HTML",
            "content": data["body"]
        }
    
    response = requests.post(
        f"{base_url}/me/events",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 201:
        result = response.json()
        return {
            "result": {
                "event_id": result.get("id"),
                "web_link": result.get("webLink")
            },
            "status": "success"
        }
    else:
        return {"result": None, "status": f"Fehler: {response.status_code} - {response.text}"}


def _search_files(base_url: str, headers: Dict, data: Dict) -> Dict[str, Any]:
    """Durchsucht OneDrive und SharePoint."""
    query = data.get("query", "")
    
    response = requests.get(
        f"{base_url}/me/drive/root/search(q='{query}')",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        files = [
            {
                "name": item.get("name"),
                "id": item.get("id"),
                "web_url": item.get("webUrl"),
                "size": item.get("size"),
                "modified": item.get("lastModifiedDateTime")
            }
            for item in result.get("value", [])
        ]
        return {"result": {"files": files}, "status": "success"}
    else:
        return {"result": None, "status": f"Fehler: {response.status_code} - {response.text}"}


def _send_teams_message(base_url: str, headers: Dict, data: Dict) -> Dict[str, Any]:
    """Sendet eine Nachricht in einen Teams-Kanal."""
    team_id = data.get("team_id")
    channel_id = data.get("channel_id")
    message = data.get("message", "")
    
    if not team_id or not channel_id:
        return {"result": None, "status": "Fehler: team_id und channel_id erforderlich"}
    
    payload = {
        "body": {
            "content": message
        }
    }
    
    response = requests.post(
        f"{base_url}/teams/{team_id}/channels/{channel_id}/messages",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 201:
        result = response.json()
        return {
            "result": {"message_id": result.get("id")},
            "status": "success"
        }
    else:
        return {"result": None, "status": f"Fehler: {response.status_code} - {response.text}"}


def _get_calendar(base_url: str, headers: Dict, data: Dict) -> Dict[str, Any]:
    """Ruft Kalendereinträge ab."""
    start = data.get("start", "")
    end = data.get("end", "")
    
    params = {}
    if start and end:
        params["startDateTime"] = start
        params["endDateTime"] = end
    
    response = requests.get(
        f"{base_url}/me/calendarView",
        headers=headers,
        params=params,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        events = [
            {
                "subject": event.get("subject"),
                "start": event.get("start", {}).get("dateTime"),
                "end": event.get("end", {}).get("dateTime"),
                "location": event.get("location", {}).get("displayName")
            }
            for event in result.get("value", [])
        ]
        return {"result": {"events": events}, "status": "success"}
    else:
        return {"result": None, "status": f"Fehler: {response.status_code} - {response.text}"}


# Hilfsfunktionen für direkten Aufruf
def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Sendet eine E-Mail."""
    return execute("send_email", {"to": to, "subject": subject, "body": body})


def create_meeting(subject: str, start: str, end: str, attendees: list = None) -> Dict[str, Any]:
    """Erstellt einen Termin."""
    data = {"subject": subject, "start": start, "end": end}
    if attendees:
        data["attendees"] = attendees
    return execute("create_event", data)


# Für direkten Aufruf
if __name__ == "__main__":
    import json
    
    # Beispiel: Dateien suchen
    result = execute("search_files", {"query": "Präsentation"})
    print(json.dumps(result, indent=2, ensure_ascii=False))
