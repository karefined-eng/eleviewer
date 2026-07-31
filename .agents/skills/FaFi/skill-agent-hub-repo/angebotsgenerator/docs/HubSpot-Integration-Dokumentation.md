# FassadenFix - HubSpot Integration Dokumentation

## Übersicht

Diese Dokumentation beschreibt die bidirektionale Synchronisation zwischen dem FassadenFix Angebotsgenerator und HubSpot CRM.

---

## Aktueller HubSpot-Status

**Verbundenes Konto:**
- **Account ID:** 26519608
- **Benutzer:** Alexander Retzlaff (a.retzlaff@fassadenfix.de)
- **Owner ID:** 522379976
- **Region:** EU (app-eu1.hubspot.com)
- **Währung:** EUR
- **Zeitzone:** Europe/Berlin

---

## Verfügbare CRM-Objekte

Die folgenden HubSpot-Objekte sind für die Integration verfügbar:

| Objekt | Status | Verwendung |
|--------|--------|------------|
| **CONTACT** | ✅ Verfügbar | Ansprechpartner des Kunden |
| **COMPANY** | ✅ Verfügbar | Firmen-/Kundendaten |
| **DEAL** | ✅ Verfügbar | Angebote als Deals |
| **TICKET** | ✅ Verfügbar | Support-Anfragen |
| **QUOTE** | ✅ Verfügbar | Angebotsdokumente |
| **LINE_ITEM** | ✅ Verfügbar | Einzelpositionen |
| **PRODUCT** | ✅ Verfügbar | FassadenFix Leistungen |

---

## Daten-Mapping: Angebot → HubSpot

### Company (Unternehmen)

| Angebot-Feld | HubSpot Property | Typ |
|--------------|------------------|-----|
| Firmenname | `name` | Text |
| Straße | `address` | Text |
| PLZ | `zip` | Text |
| Ort | `city` | Text |
| Kundennummer | `hs_object_id` / Custom | Text |

### Contact (Kontakt)

| Angebot-Feld | HubSpot Property | Typ |
|--------------|------------------|-----|
| Ansprechpartner (Vorname) | `firstname` | Text |
| Ansprechpartner (Nachname) | `lastname` | Text |
| E-Mail | `email` | Email |
| Telefon | `phone` | Phone |

### Deal (Geschäft/Angebot)

| Angebot-Feld | HubSpot Property | Typ |
|--------------|------------------|-----|
| Angebotsnummer | `dealname` | Text |
| Gesamtsumme (Brutto) | `amount` | Currency |
| Datum | `createdate` | Date |
| Objektadresse | Custom Property | Text |
| Fläche (m²) | Custom Property | Number |
| Ansprechpartner FF | `hubspot_owner_id` | Owner |

### Line Items (Positionen)

Jede Angebotsposition wird als Line Item synchronisiert:

| Angebot-Feld | HubSpot Property | Typ |
|--------------|------------------|-----|
| Position Nr. | `name` | Text |
| Bezeichnung | `description` | Text |
| Menge | `quantity` | Number |
| Einheitspreis | `price` | Currency |
| Gesamtpreis | `amount` | Currency |
| Bedarfsposition | Custom Property | Boolean |

---

## Synchronisations-Richtungen

### Angebot → HubSpot (Export)

1. **Company erstellen/aktualisieren**
   - Suche nach existierender Company via Kundennummer
   - Erstelle neue Company oder aktualisiere bestehende

2. **Contact erstellen/verknüpfen**
   - Suche nach Contact via E-Mail
   - Erstelle neuen Contact oder verknüpfe bestehenden
   - Assoziiere Contact mit Company

3. **Deal erstellen**
   - Erstelle neuen Deal mit Angebotsnummer als Name
   - Verknüpfe mit Company und Contact
   - Setze Deal Owner basierend auf FassadenFix Ansprechpartner

4. **Line Items hinzufügen**
   - Erstelle Line Items für jede Position
   - Verknüpfe mit Deal

### HubSpot → Angebot (Import)

1. **Company-Daten laden**
   - Suche Companies via Name oder ID
   - Lade Adressdaten und Kontakte

2. **Contact-Daten laden**
   - Lade verknüpfte Contacts
   - Befülle Ansprechpartner-Felder

3. **Deal-Historie laden**
   - Zeige existierende Deals/Angebote
   - Ermögliche Wiederverwendung von Daten

---

## Implementierung

### API-Endpoints

```javascript
// HubSpot API Base URL (EU)
const HUBSPOT_API = 'https://api.hubapi.com';

// Companies
POST /crm/v3/objects/companies
GET  /crm/v3/objects/companies/{companyId}
PATCH /crm/v3/objects/companies/{companyId}

// Contacts
POST /crm/v3/objects/contacts
GET  /crm/v3/objects/contacts/{contactId}

// Deals
POST /crm/v3/objects/deals
GET  /crm/v3/objects/deals/{dealId}

// Line Items
POST /crm/v3/objects/line_items
GET  /crm/v3/objects/line_items/{lineItemId}

// Associations
PUT /crm/v3/objects/{fromObjectType}/{fromObjectId}/associations/{toObjectType}/{toObjectId}/{associationType}
```

### Authentifizierung

Die Integration verwendet OAuth 2.0 mit den folgenden Scopes:

- `crm.objects.contacts.read`
- `crm.objects.contacts.write`
- `crm.objects.companies.read`
- `crm.objects.companies.write`
- `crm.objects.deals.read`
- `crm.objects.deals.write`
- `crm.objects.line_items.read`
- `crm.objects.line_items.write`

### Beispiel: Company erstellen

```javascript
async function createCompany(data) {
  const response = await fetch(`${HUBSPOT_API}/crm/v3/objects/companies`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      properties: {
        name: data.firmenname,
        address: data.strasse,
        zip: data.plz,
        city: data.ort,
        // Custom Property für Kundennummer
        kundennummer: data.kundennummer
      }
    })
  });
  return response.json();
}
```

### Beispiel: Deal mit Line Items erstellen

```javascript
async function createDealWithLineItems(angebot) {
  // 1. Deal erstellen
  const deal = await createDeal({
    dealname: `Angebot ${angebot.angebotsnummer}`,
    amount: angebot.gesamtbrutto,
    dealstage: 'qualifiedtobuy',
    pipeline: 'default'
  });

  // 2. Line Items erstellen
  for (const position of angebot.positionen) {
    const lineItem = await createLineItem({
      name: `Pos. ${position.pos}`,
      description: position.bezeichnung,
      quantity: position.menge,
      price: position.einzelpreis,
      amount: position.gesamt
    });

    // 3. Line Item mit Deal verknüpfen
    await associateLineItemWithDeal(lineItem.id, deal.id);
  }

  return deal;
}
```

---

## Aktivierung der vollständigen Integration

### Schritt 1: Opt-in für CRM-Verwaltung

Um die vollständige bidirektionale Synchronisation zu aktivieren, muss die CRM-Verwaltung freigeschaltet werden:

1. Öffnen Sie: https://app.hubspot.com/l/product-updates/new-to-you?rollout=251918
2. Aktivieren Sie die CRM-Objekt-Verwaltung
3. Verbinden Sie den HubSpot-Connector neu

### Schritt 2: Custom Object "IMMOBILIE" erstellen

Das Custom Object "IMMOBILIE" ermöglicht die bidirektionale Synchronisation von Immobilien-Daten mit HubSpot.

**Schema-Definition:**

| Property | Label | Typ | Beschreibung |
|----------|-------|-----|--------------|
| `immobilie_strasse` | Straße | Text | Straßenname |
| `immobilie_hausnummer` | Hausnummer | Text | Hausnummer |
| `immobilie_plz` | PLZ | Text | Postleitzahl |
| `immobilie_ort` | Ort | Text | Ortsname |
| `immobilie_adresse_vollstaendig` | Vollständige Adresse | Text | Primary Display Property |
| `immobilie_gesamtflaeche` | Gesamtfläche (m²) | Number | Summe aller aktiven Seiten |
| `immobilie_status` | Status | Enumeration | neu, angeboten, beauftragt, abgeschlossen |
| `immobilie_letzte_reinigung` | Letzte Reinigung | Date | Datum der letzten Durchführung |
| `immobilie_seiten_aktiv` | Aktive Seiten | Text | z.B. "Front, Rück, Links" |
| `immobilie_front_flaeche` | Frontseite Fläche | Number | m² der Frontseite |
| `immobilie_rueck_flaeche` | Rückseite Fläche | Number | m² der Rückseite |
| `immobilie_links_flaeche` | Linker Giebel Fläche | Number | m² des linken Giebels |
| `immobilie_rechts_flaeche` | Rechter Giebel Fläche | Number | m² des rechten Giebels |
| `immobilie_link360_front` | 360° Link Frontseite | URL | Link zum 360°-Rundgang |
| `immobilie_link360_rueck` | 360° Link Rückseite | URL | Link zum 360°-Rundgang |
| `immobilie_link360_links` | 360° Link Linker Giebel | URL | Link zum 360°-Rundgang |
| `immobilie_link360_rechts` | 360° Link Rechter Giebel | URL | Link zum 360°-Rundgang |
| `immobilie_buehne_erforderlich` | Bühne erforderlich | Boolean | Ob Hubarbeitsbühne benötigt |
| `immobilie_besonderheiten` | Besonderheiten | Text | Zusätzliche Hinweise |

**Associations:**

| Von | Zu | Beschreibung |
|-----|-----|--------------|
| IMMOBILIE | COMPANY | Immobilie gehört zu Unternehmen |
| IMMOBILIE | CONTACT | Ansprechpartner für Immobilie |
| IMMOBILIE | DEAL | Immobilie ist Teil eines Angebots |

### Schritt 3: Custom Properties erstellen

Folgende zusätzliche Custom Properties sollten in HubSpot angelegt werden:

**Für Companies:**
- `kundennummer` (Text) - FassadenFix Kundennummer

**Für Deals:**
- `angebotsnummer` (Text) - Angebotsnummer (ANG-XXXX)
- `fruehbucherrabatt` (Number) - Rabatt in %
- `rabatt_gueltig_bis` (Date) - Gültigkeit Frühbucher

**Für Line Items:**
- `bedarfsposition` (Boolean) - Optionale Position
- `einheit` (Dropdown) - m², Stk, Tag(e), Pausch.
- `artikelgruppe` (Dropdown) - reinigung, rabatte, technik, nebenkosten
- `immobilie_nummer` (Number) - Zuordnung zur Immobilie

### Schritt 3: Pipeline konfigurieren

Empfohlene Deal-Stages für FassadenFix Angebote:

1. **Angebot erstellt** - Initiale Erstellung
2. **Angebot gesendet** - An Kunden versendet
3. **In Verhandlung** - Kunde hat Rückfragen
4. **Angenommen** - Auftrag erteilt
5. **Abgelehnt** - Kunde hat abgelehnt
6. **Abgeschlossen** - Arbeiten durchgeführt

---

## Webhooks für Echtzeit-Sync

### HubSpot → Anwendung

Konfigurieren Sie Webhooks in HubSpot für:

- `deal.propertyChange` - Bei Änderungen am Deal
- `company.propertyChange` - Bei Änderungen an der Company
- `contact.propertyChange` - Bei Änderungen am Contact

### Webhook Payload Beispiel

```json
{
  "eventId": 1,
  "subscriptionId": 123456,
  "portalId": 26519608,
  "occurredAt": 1704067200000,
  "subscriptionType": "deal.propertyChange",
  "attemptNumber": 0,
  "objectId": 12345,
  "propertyName": "dealstage",
  "propertyValue": "closedwon"
}
```

---

## Fehlerbehandlung

### Häufige Fehler und Lösungen

| Fehlercode | Beschreibung | Lösung |
|------------|--------------|--------|
| 401 | Unauthorized | Token erneuern |
| 403 | Missing Scopes | Connector neu verbinden |
| 404 | Object not found | ID prüfen |
| 409 | Conflict | Deduplizierung prüfen |
| 429 | Rate Limit | Retry mit Backoff |

### Rate Limiting

- **Standard:** 100 Requests/10 Sekunden
- **Burst:** 150 Requests/10 Sekunden
- **Empfehlung:** Batch-APIs für mehrere Objekte nutzen

---

## Support

Bei Fragen zur HubSpot-Integration:

- **Technisch:** a.retzlaff@fassadenfix.de
- **HubSpot Doku:** https://developers.hubspot.com/docs/api/crm
- **HubSpot Support:** https://app.hubspot.com/help

---

*Dokumentation erstellt am 19.01.2026*
*Version 1.0*
