---
name: api-client-builder
description: Ein Skill, der eine schrittweise Anleitung zur Erstellung eines API-Clients bietet und dabei das Prinzip der Progressive Disclosure anwendet.
---

# API Client Builder

Dieser Skill führt dich durch den Prozess der Erstellung eines robusten API-Clients in Python. Der Prozess ist in Phasen unterteilt, um Komplexität schrittweise aufzudecken (Progressive Disclosure).

## Phase 1: API-Typ identifizieren

Bestimme zunächst den Typ der API, mit der du interagieren möchtest. Die gängigsten Typen sind REST, GraphQL und WebSocket.

- **REST (Representational State Transfer):** Nutzt Standard-HTTP-Methoden (GET, POST, PUT, DELETE) und ist ideal für ressourcenorientierte Architekturen.
- **GraphQL:** Eine Abfragesprache für APIs, die es Clients ermöglicht, genau die Daten anzufordern, die sie benötigen.
- **WebSocket:** Ermöglicht eine bidirektionale Echtzeit-Kommunikation zwischen Client und Server.

Wenn du den API-Typ identifiziert hast, lies die entsprechende Referenz für spezifische Implementierungsmuster:

- Für REST-APIs, siehe: `references/rest.md`
- Für GraphQL-APIs, siehe: `references/graphql.md`
- Für WebSocket-APIs, siehe: `references/websocket.md`

## Phase 2: Basis-Client implementieren

Erstelle eine grundlegende Client-Klasse in Python, die für die Authentifizierung und das Senden von Anfragen zuständig ist. Verwende die `requests`-Bibliothek für REST und GraphQL oder `websockets` für WebSockets.

## Phase 3: Fehlerbehandlung und Wiederholungslogik

Implementiere eine robuste Fehlerbehandlung, um auf verschiedene HTTP-Statuscodes oder API-spezifische Fehler zu reagieren. Füge eine Wiederholungslogik (z.B. mit exponentiellem Backoff) hinzu, um temporäre Netzwerkprobleme zu bewältigen.

## Phase 4: Datenmodellierung und Serialisierung

Definiere Python-Klassen, die die API-Ressourcen repräsentieren. Dies verbessert die Typsicherheit und die Lesbarkeit des Codes. Verwende Bibliotheken wie `pydantic`, um die Datenvalidierung und -serialisierung zu automatisieren.

## Phase 5: Testen und Dokumentieren

Schreibe Unit- und Integrationstests für deinen API-Client. Dokumentiere die öffentliche Schnittstelle deines Clients mit Docstrings und erstelle eine `README.md`-Datei mit Anwendungsbeispielen.
