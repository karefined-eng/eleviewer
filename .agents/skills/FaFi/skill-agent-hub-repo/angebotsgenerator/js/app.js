// ============================================
// FASSADENFIX ANGEBOTSGENERATOR - APP.JS
// Hauptlogik und Datenstrukturen
// ============================================

// ============================================
// DATEN UND KONSTANTEN
// ============================================
let positions = [];
let immobilien = [];
let hubspotCompanies = [];
let hubspotContacts = [];
let selectedCompany = null;
let selectedContact = null;
let selectedOwner = null;
let artikelKatalog = null;

// Artikelgruppen-Definition
const ARTIKELGRUPPEN = {
    reinigung: { range: [1, 9], label: 'Reinigung', prefix: '0' },
    rabatte: { range: [10, 19], label: 'Rabatte', prefix: '1' },
    technik: { range: [20, 29], label: 'Technik', prefix: '2' },
    nebenkosten: { range: [30, 39], label: 'Nebenkosten', prefix: '3' }
};

// Seiten-Definitionen
const SEITEN_TYPEN = {
    frontseite: { label: 'Frontseite', icon: '🏠', beschreibung: 'Die Seite mit den Hauseingängen.' },
    rueckseite: { label: 'Rückseite', icon: '🔙', beschreibung: 'Die gegenüberliegende Seite.' },
    linkerGiebel: { label: 'Linker Giebel', icon: '◀️', beschreibung: 'Linke Seitenwand.' },
    rechterGiebel: { label: 'Rechter Giebel', icon: '▶️', beschreibung: 'Rechte Seitenwand.' }
};

const MASSNAHMEN_OPTIONEN = [
    { id: 'gruenschnitt', label: 'Grünschnitt erforderlich' },
    { id: 'parkplatz', label: 'Parkplatzsperrung' },
    { id: 'gehweg', label: 'Gehwegsperrung' },
    { id: 'strasse', label: 'Straßensperrung' },
    { id: 'sonstiges', label: 'Sonstiges' }
];

const BUEHNEN_OPTIONEN = [
    { id: 'keine', label: 'Keine Bühne notwendig' },
    { id: 'scherenbuhne', label: 'Scherenbühne (bis 15m)' },
    { id: 'gelenkbuhne_klein', label: 'Gelenkbühne (bis 26m)' },
    { id: 'gelenkbuhne_gross', label: 'Gelenkbühne (bis 45m)' },
    { id: 'lkw_buhne', label: 'LKW-Bühne (bis 60m)' },
    { id: 'kletterer', label: 'Industriekletterer' },
    { id: 'geruest', label: 'Gerüst erforderlich' },
    { id: 'sonstige', label: 'Sonstige Anforderung' }
];

const UNTERGRUND_OPTIONEN = [
    { id: 'asphalt', label: 'Asphalt/Beton' },
    { id: 'pflaster', label: 'Pflastersteine' },
    { id: 'schotter', label: 'Schotter/Kies' },
    { id: 'rasen', label: 'Rasen/Wiese' },
    { id: 'erde', label: 'Unbefestigt/Erde' },
    { id: 'gemischt', label: 'Gemischt' }
];

const ZUGAENGLICHKEIT_OPTIONEN = [
    { id: 'gut', label: '✓ Gut zugänglich' },
    { id: 'parkplatz', label: 'Über Parkplatz' },
    { id: 'gehweg', label: 'Über Gehweg' },
    { id: 'einfahrt', label: 'Über Einfahrt' },
    { id: 'strasse', label: 'Straßensperrung nötig' },
    { id: 'hinterhof', label: 'Hinterhof (eng)' },
    { id: 'eingeschraenkt', label: '⚠ Eingeschränkt' }
];

const HINDERNISSE_OPTIONEN = [
    { id: 'keine', label: 'Keine Hindernisse' },
    { id: 'baeume', label: 'Bäume/Sträucher' },
    { id: 'leitungen', label: 'Oberleitungen' },
    { id: 'balkone', label: 'Viele Balkone' },
    { id: 'vordaecher', label: 'Vordächer/Markisen' },
    { id: 'spielgeraete', label: 'Spielgeräte' },
    { id: 'parkende_autos', label: 'Parkende Autos' },
    { id: 'sonstiges', label: 'Sonstiges' }
];

// Bühnen-Preislogik (NEU - gemäß Spezifikation)
const BUEHNEN_PREISE = {
    'keine': { preis: 0, label: 'Keine Bühne', einheit: '' },
    'standard': { preis: 390, label: 'FassadenFix Standard', einheit: 'Tag' },
    'sonder': { preis: 'anfrage', label: 'Sonderbühne', einheit: '' },
    // Detail-Typen für Sonderbühnen (alle "Auf Anfrage")
    'gelenkbuehne': { preis: 'anfrage', label: 'Gelenkbühne', einheit: 'Tag' },
    'teleskopbuehne': { preis: 'anfrage', label: 'Teleskopbühne', einheit: 'Tag' },
    'lkwbuehne': { preis: 'anfrage', label: 'LKW-Bühne', einheit: 'Tag' },
    'kletterer': { preis: 'anfrage', label: 'Industriekletterer', einheit: 'Tag' },
    'geruest': { preis: 'anfrage', label: 'Gerüst', einheit: 'Pausch.' },
    'sonstiges': { preis: 'anfrage', label: 'Sonstiges', einheit: '' }
};

// Standard Bühne (390€)
const FF_STANDARD_BUEHNE_PREIS = 390;

// Reinigungsprodukte (NEU)
const REINIGUNGSPRODUKTE = {
    standard: [
        { id: 'ffc', label: 'FFC (Standard)', selected: true },
        { id: 'ffc_plus', label: 'FFC Plus', selected: true }
    ],
    zusaetzlich: [
        { id: 'icarly_stone', label: 'iCarly Stone' },
        { id: 's1_steinaner', label: 'S.1/Steinaner' },
        { id: 'm1', label: 'M1' },
        { id: 'sonstiges', label: 'Sonstiges' }
    ]
};

// Schaden-Typen (NEU)
const SCHADEN_TYPEN = [
    { id: 'graffiti', label: 'Graffiti', icon: '🎨' },
    { id: 'loecher', label: 'Specht-Löcher/Löcher', icon: '🕳️' },
    { id: 'risse', label: 'Risse/substanzielle Schäden', icon: '⚡' }
];

// HubSpot Owner Mapping (auch für FF-Mitarbeiter Dropdown)
const hubspotOwners = {
    '753843912': { name: 'Sebastian Siebenhühner', email: 's.siebenhuehner@fassadenfix.de', phone: '+4915792646863' },
    '522379976': { name: 'Alexander Retzlaff', email: 'a.retzlaff@fassadenfix.de', phone: '0345 218392 35' },
    '1178553498': { name: 'Rocco Seitz', email: 'r.seitz@fassadenfix.de', phone: '' },
    '753849449': { name: 'Matthias Breier', email: 'm.breier@fassadenfix.de', phone: '' },
    '1258292442': { name: 'Fabian Czewerda', email: 'f.czewerda@fassadenfix.de', phone: '' },
    '1126851218': { name: 'Sven Zorn', email: 's.zorn@fassadenfix.de', phone: '' },
    '978174667': { name: 'Ronny Ries', email: 'r.ries@fassadenfix.de', phone: '' }
};

// ============================================
// HILFSFUNKTIONEN
// ============================================
function formatCurrency(value) {
    return value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function calculateTotals() {
    let netto = 0, bedarfs = 0;
    positions.forEach(p => {
        const sum = p.menge * p.einzelpreis;
        if (p.bedarfsposition) bedarfs += sum;
        else netto += sum;
    });
    return { netto, bedarfs, mwst: netto * 0.19, brutto: netto * 1.19 };
}

function getImmobilieGesamtflaeche(immo) {
    return Object.values(immo.seiten)
        .filter(s => s.aktiv)
        .reduce((sum, s) => sum + (s.flaeche || 0), 0);
}

function getFormattedAdresse(immo) {
    const a = immo.adresse;
    return `${a.strasse} ${a.hausnummer}, ${a.plz} ${a.ort}`.trim();
}

// Preisstufen-Daten (wird aus JSON geladen)
let preisstufen = null;

// Preisstufen laden
async function loadPreisstufen() {
    try {
        const response = await fetch('data/preisstufen.json');
        preisstufen = await response.json();
        console.log('Preisstufen geladen');
        return preisstufen;
    } catch (e) {
        console.error('Fehler beim Laden der Preisstufen:', e);
        return null;
    }
}

// Preis für Fläche aus Preisstufen ermitteln
function getPreisForFlaeche(qm) {
    if (!preisstufen) return { preis: 9.75, artikelId: 'R003', bezeichnung: 'FassadenFix Systemreinigung' };

    const stufen = preisstufen.preisstufen.reinigung.stufen;
    for (const stufe of stufen) {
        if (qm >= stufe.von_m2 && qm <= stufe.bis_m2) {
            return {
                preis: stufe.preis,
                artikelId: stufe.artikelId,
                bezeichnung: stufe.bezeichnung
            };
        }
    }
    // Fallback: Größte Stufe
    const letzteStufe = stufen[stufen.length - 1];
    return {
        preis: letzteStufe.preis,
        artikelId: letzteStufe.artikelId,
        bezeichnung: letzteStufe.bezeichnung
    };
}

// ============================================
// AUTOMATISCHE POSITIONS-GENERIERUNG
// ============================================
function generatePositionsFromImmobilien() {
    // Neue Positionen erstellen
    const neuePositionen = [];

    // =========================================
    // Position 0.0.0 - PREISSTAFFEL-ÜBERSICHT
    // (Stets als Grundinformation im Angebot)
    // =========================================
    const preisstaffelText = `FassadenFix Systemreinigung - Preisstaffel:

500 - 999 m²: 10,50 €/m²
1.000 - 2.499 m²: 9,75 €/m²
2.500 - 4.999 m²: 9,25 €/m²
ab 5.000 m²: 8,75 €/m²`;

    neuePositionen.push({
        pos: '0.0.0',
        immoNummer: 0, // Global, nicht immobilienspezifisch
        artikelgruppe: 'reinigung',
        menge: 1,
        einheit: '-',
        bezeichnung: preisstaffelText,
        einzelpreis: 0,
        bedarfsposition: false,
        istEckdatenPosition: true, // Keine Menge/Preis anzeigen
        beschreibung: ''
    });

    // Pro Immobilie Positionen generieren
    immobilien.forEach((immo) => {
        const immoNr = immo.nummer;

        // Sammle aktive Seiten mit Flächen für diese Immobilie
        let immoFlaeche = 0;
        const seitenDetails = [];
        let hatStandardBuehne = false;
        let hatSonderBuehne = false;
        let sonderBuehneTyp = '';
        const zugaenglichkeitsEinschraenkungen = [];
        const zusaetzlicheReinigungsmittel = [];
        let hatSchaeden = false;
        const schaedenListe = [];

        Object.entries(immo.seiten).forEach(([seiteKey, seite]) => {
            if (seite.zuReinigen === true && seite.flaeche > 0) {
                immoFlaeche += seite.flaeche;
                seitenDetails.push({
                    seiteKey: seiteKey,
                    seiteLabel: SEITEN_TYPEN[seiteKey].label,
                    flaeche: seite.flaeche,
                    buehne: seite.buehne
                });

                // Bühnen prüfen
                if (seite.buehne?.typ === 'standard') {
                    hatStandardBuehne = true;
                } else if (seite.buehne?.typ === 'sonder') {
                    hatSonderBuehne = true;
                    sonderBuehneTyp = seite.buehne?.sonderTyp || 'Sonderbühne';
                }

                // Zugänglichkeits-Einschränkungen sammeln
                if (seite.zugaenglichkeit?.typ === 'eingeschraenkt' && seite.zugaenglichkeit?.einschraenkungen?.length > 0) {
                    seite.zugaenglichkeit.einschraenkungen.forEach(e => {
                        const labels = {
                            'gehweg': 'Gehweg-Sperrung',
                            'parkplatz': 'Parkplatz-Sperrung',
                            'strasse': 'Straßensperrung',
                            'gruenschnitt': 'Grünschnitt',
                            'sonstiges': seite.zugaenglichkeit?.sonstigesBeschreibung || 'Sonstiges'
                        };
                        if (!zugaenglichkeitsEinschraenkungen.includes(labels[e])) {
                            zugaenglichkeitsEinschraenkungen.push(labels[e]);
                        }
                    });
                }

                // Zusätzliche Reinigungsmittel sammeln
                if (seite.reinigungsprodukt?.zusaetzlichErforderlich && seite.reinigungsprodukt?.zusaetzlichProdukte?.length > 0) {
                    seite.reinigungsprodukt.zusaetzlichProdukte.forEach(p => {
                        const labels = {
                            'icarly_stone': 'iCarly Stone',
                            's1_steinaner': 'S.1/Steinaner',
                            'm1': 'M1',
                            'sonstiges': 'Sonstiges'
                        };
                        if (!zusaetzlicheReinigungsmittel.includes(labels[p])) {
                            zusaetzlicheReinigungsmittel.push(labels[p]);
                        }
                    });
                }

                // Schäden sammeln
                if (seite.schaeden?.vorhanden) {
                    hatSchaeden = true;
                    SCHADEN_TYPEN.forEach(schaden => {
                        if (seite.schaeden?.[schaden.id]?.aktiv) {
                            schaedenListe.push(schaden.label);
                        }
                    });
                }
            }
        });

        // Wenn keine Fläche, keine Positionen für diese Immobilie
        if (immoFlaeche === 0) return;

        // Preis für Fläche dieser Immobilie ermitteln
        const preisInfo = getPreisForFlaeche(immoFlaeche);

        // Adresse formatieren
        const adresse = `${immo.adresse.strasse} ${immo.adresse.hausnummer}, ${immo.adresse.plz} ${immo.adresse.ort}`.trim();

        // Seiten-Details mit Flächen formatieren
        const seitenMitFlaechen = seitenDetails.map(s =>
            `${s.seiteLabel}: ${s.flaeche.toLocaleString('de-DE')} m²`
        ).join(' | ');

        // =========================================
        // Position X.0.0 - IMMOBILIEN-ECKDATEN (Erweitert)
        // =========================================
        let eckdatenText = `📍 ${adresse || 'Adresse noch nicht erfasst'}\n`;
        eckdatenText += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        eckdatenText += `Flächen: ${seitenMitFlaechen}\n`;
        eckdatenText += `Gesamtfläche: ${immoFlaeche.toLocaleString('de-DE')} m²\n`;

        // Zugänglichkeit
        if (zugaenglichkeitsEinschraenkungen.length > 0) {
            eckdatenText += `\n⚠️ Zugänglichkeit: ${zugaenglichkeitsEinschraenkungen.join(', ')}`;
        }

        // Reinigungsmittel
        if (zusaetzlicheReinigungsmittel.length > 0) {
            eckdatenText += `\n🧪 Zusätzliche Reinigung: ${zusaetzlicheReinigungsmittel.join(', ')}`;
        }

        // Schäden
        if (hatSchaeden && schaedenListe.length > 0) {
            eckdatenText += `\n⚡ Schäden: ${[...new Set(schaedenListe)].join(', ')}`;
        }

        // Bühnen-Info
        if (hatStandardBuehne) {
            const buehnenTage = Math.ceil(immoFlaeche / 500);
            eckdatenText += `\n🏗️ Bühne: Standard (${buehnenTage} Tag${buehnenTage > 1 ? 'e' : ''})`;
        }
        if (hatSonderBuehne) {
            eckdatenText += `\n🏗️ Sonderbühne: Auf Anfrage`;
        }

        neuePositionen.push({
            pos: `${immoNr}.0.0`,
            immoNummer: immoNr,
            artikelgruppe: 'reinigung',
            menge: 1,
            einheit: '-',
            bezeichnung: `Immobilie ${immoNr} - Eckdaten`,
            einzelpreis: 0,
            bedarfsposition: false,
            istEckdatenPosition: true,
            beschreibung: eckdatenText
        });

        // =========================================
        // Position X.0.1 - FassadenFix Systemreinigung
        // (Kein Einzelpreis hier - wird über alle Immobilien kumuliert berechnet)
        // =========================================
        neuePositionen.push({
            pos: `${immoNr}.0.1`,
            immoNummer: immoNr,
            artikelgruppe: 'reinigung',
            menge: immoFlaeche,
            einheit: 'm²',
            bezeichnung: 'FassadenFix Systemreinigung - zertifizierte Eigenprodukte (exklusiv nur bei FassadenFix)',
            einzelpreis: 0, // Preis wird kumuliert in Preisstaffel berechnet
            bedarfsposition: false,
            preisInKumulierung: true, // Flag für kumulierte Preisberechnung
            beschreibung: 'Leistungen: Auftragen der FassadenFix Reinigungslösung FFC Plus, Auffangen und Aufbereiten von Schmutz- und Abwasser (gesetzlich vorgeschrieben), Auftragen des hochwertigen Langzeitschutzes FFP - **bundesamtlich zertifiziert** nach BauA.'
        });

        // =========================================
        // Position X.0.2 - Bühnen (automatisch berechnet)
        // =========================================
        if (hatStandardBuehne) {
            // Berechnung: 500 m²/Tag, aufrunden
            const buehnenTage = Math.ceil(immoFlaeche / 500);
            const buehnenPreis = 390; // €/Tag

            neuePositionen.push({
                pos: `${immoNr}.0.2`,
                immoNummer: immoNr,
                artikelgruppe: 'technik',
                menge: buehnenTage,
                einheit: 'Tag(e)',
                bezeichnung: 'Hubarbeitsbühne Standard (FassadenFix)',
                einzelpreis: buehnenPreis,
                bedarfsposition: false,
                beschreibung: `Berechnung: ${immoFlaeche.toLocaleString('de-DE')} m² ÷ 500 m²/Tag = ${buehnenTage} Tag(e)`
            });
        }

        // =========================================
        // Position X.0.3 - Baustelleneinrichtung (IMMER, 100€ pauschal)
        // =========================================
        neuePositionen.push({
            pos: `${immoNr}.0.3`,
            immoNummer: immoNr,
            artikelgruppe: 'nebenkosten',
            menge: 1,
            einheit: 'Pausch.',
            bezeichnung: 'Baustelleneinrichtung',
            einzelpreis: 100, // 100€ pauschal je Immobilie
            bedarfsposition: false,
            beschreibung: 'Pauschale für Baustelleneinrichtung, -absicherung und -räumung.'
        });

        let zusatzPosNr = 4; // Weitere Positionen beginnen bei X.0.4

        // =========================================
        // Auf-Anfrage-Positionen
        // =========================================

        // Sonderbühne
        if (hatSonderBuehne) {
            const sonderLabel = {
                'gelenkbuehne': 'Gelenkbühne',
                'teleskopbuehne': 'Teleskopbühne',
                'lkwbuehne': 'LKW-Bühne',
                'kletterer': 'Industriekletterer',
                'geruest': 'Gerüst',
                'sonstiges': 'Sonderbühne'
            };
            neuePositionen.push({
                pos: `${immoNr}.0.${zusatzPosNr}`,
                immoNummer: immoNr,
                artikelgruppe: 'technik',
                menge: 1,
                einheit: 'Pausch.',
                bezeichnung: `${sonderLabel[sonderBuehneTyp] || 'Sonderbühne'} — Auf Anfrage`,
                einzelpreis: 0,
                bedarfsposition: true,
                beschreibung: 'Preis wird nach Klärung der Anforderungen separat kalkuliert'
            });
            zusatzPosNr++;
        }

        // Zugänglichkeits-Maßnahmen
        if (zugaenglichkeitsEinschraenkungen.length > 0) {
            neuePositionen.push({
                pos: `${immoNr}.0.${zusatzPosNr}`,
                immoNummer: immoNr,
                artikelgruppe: 'nebenkosten',
                menge: 1,
                einheit: 'Pausch.',
                bezeichnung: `Zugänglichkeits-Maßnahmen — Auf Anfrage`,
                einzelpreis: 0,
                bedarfsposition: true,
                beschreibung: `Erforderlich: ${zugaenglichkeitsEinschraenkungen.join(', ')}. Preis wird separat kalkuliert.`
            });
            zusatzPosNr++;
        }

        // Zusätzliche Reinigungsmittel
        if (zusaetzlicheReinigungsmittel.length > 0) {
            neuePositionen.push({
                pos: `${immoNr}.0.${zusatzPosNr}`,
                immoNummer: immoNr,
                artikelgruppe: 'nebenkosten',
                menge: 1,
                einheit: 'Pausch.',
                bezeichnung: `Zusätzliche Reinigungsmittel — Auf Anfrage`,
                einzelpreis: 0,
                bedarfsposition: true,
                beschreibung: `Erforderlich: ${zusaetzlicheReinigungsmittel.join(', ')}. Preis wird separat kalkuliert.`
            });
            zusatzPosNr++;
        }
    });

    // Positionen aktualisieren
    positions = neuePositionen;

    // UI aktualisieren - nur renderImmobilien, da Positionen jetzt dort integriert sind
    if (typeof renderImmobilien === 'function') renderImmobilien();
    if (typeof updatePreview === 'function') updatePreview();

    console.log('Positionen automatisch generiert:', positions.length, 'für', immobilien.length, 'Immobilien');
}


// ============================================
// IMMOBILIEN-FACTORY
// ============================================
function createEmptySeite(typ) {
    return {
        typ: typ,
        // NEU: Pflichtfeld "Zu reinigen?"
        zuReinigen: null, // null = nicht entschieden, true = ja, false = nein
        aktiv: false,
        breite: 0,
        hoehe: 0,
        flaeche: 0,
        // Optionale Felder
        letzteSanierung: '', // Jahr
        farbwerte: '', // Freitext
        balkone: false,
        link360: '',
        // Bühnen-Daten mit Preislogik
        buehne: {
            typ: 'keine',
            tage: 1,
            preis: 0, // 0, 390 oder 'anfrage'
            beschreibung: ''
        },
        // Reinigungsprodukt
        reinigungsprodukt: {
            standard: true, // FFC/FFC Plus
            zusaetzlichErforderlich: false,
            zusaetzlichProdukte: [], // ['icarly_stone', 'm1', ...]
            anwendung: 'zusaetzlich', // 'zusaetzlich' oder 'stattdessen'
            begruendung: ''
        },
        // Zugänglichkeit mit Untermenü
        zugaenglichkeit: {
            typ: 'ungehindert', // 'ungehindert' oder 'eingeschraenkt'
            einschraenkungen: [], // ['gehweg', 'parkplatz', ...]
            sonstigesBeschreibung: ''
        },
        // Schäden/Besonderheiten
        schaeden: {
            vorhanden: false,
            graffiti: { aktiv: false, beschreibung: '', fotos: [] },
            loecher: { aktiv: false, beschreibung: '', fotos: [] },
            risse: { aktiv: false, beschreibung: '', fotos: [] },
            weitereBesonderheiten: ''
        },
        // Legacy-Felder
        massnahmen: { gruenschnitt: false, parkplatz: false, gehweg: false, strasse: false, sonstiges: false, sonstigesBeschreibung: '' },
        hindernisse: [],
        untergrund: 'asphalt'
    };
}

function createEmptyImmobilie(nummer) {
    return {
        id: Date.now(),
        nummer: nummer,
        hubspotImmobilieId: null,
        hubspotAssociations: { companyId: null, contactId: null, dealId: null },
        // Adresse
        adresse: { strasse: '', hausnummer: '', plz: '', ort: '' },
        // NEU: Kopfdaten
        datumObjektaufnahme: '', // Datum (YYYY-MM-DD)
        ffMitarbeiter: '', // HubSpot Owner ID
        agMitarbeiter: {
            name: '',
            email: '',
            telefon: '',
            position: '', // z.B. Hausmeister, Verwalter
            hubspotContactId: null // für Sync
        },
        // PFLICHTABFRAGEN
        reinigungMoeglich: null, // null = noch nicht beantwortet, true/false
        marketingGeeignet: null, // null = noch nicht beantwortet, true/false
        marketingAufgabeErstellt: false, // Flag ob HubSpot-Aufgabe bereits erstellt
        // Status
        gesamtflaeche: 0,
        status: 'neu',
        historie: { angebote: [], auftraege: [], termine: [], letzteReinigung: null },
        alleSeiten: false,
        // Seiten
        seiten: {
            frontseite: createEmptySeite('frontseite'),
            rueckseite: createEmptySeite('rueckseite'),
            linkerGiebel: createEmptySeite('linkerGiebel'),
            rechterGiebel: createEmptySeite('rechterGiebel')
        }
    };
}

// ============================================
// ARTIKELKATALOG LADEN
// ============================================
async function loadArtikelKatalog() {
    try {
        const response = await fetch('data/artikel.json');
        artikelKatalog = await response.json();
        console.log('Artikelkatalog geladen:', Object.keys(artikelKatalog.artikelgruppen).length, 'Gruppen');
        return artikelKatalog;
    } catch (e) {
        console.error('Fehler beim Laden des Artikelkatalogs:', e);
        return null;
    }
}

function renderArtikelDropdown(gruppenFilter = null) {
    if (!artikelKatalog) return '<option value="">Katalog lädt...</option>';

    let html = '<option value="">-- Artikel wählen --</option>';

    Object.entries(artikelKatalog.artikelgruppen).forEach(([gruppeKey, gruppe]) => {
        if (gruppenFilter && gruppenFilter !== gruppeKey) return;

        html += `<optgroup label="${gruppe.label}" style="color:${gruppe.farbe}">`;
        gruppe.artikel.filter(a => a.aktiv).forEach(artikel => {
            html += `<option value="${artikel.artikelId}" data-preis="${artikel.preis}" data-einheit="${artikel.einheit}">${artikel.bezeichnung} (${artikel.preis}€/${artikel.einheit})</option>`;
        });
        html += '</optgroup>';
    });

    return html;
}

function selectArtikelFromKatalog(posIndex, artikelId) {
    if (!artikelKatalog) return;

    for (const gruppe of Object.values(artikelKatalog.artikelgruppen)) {
        const artikel = gruppe.artikel.find(a => a.artikelId === artikelId);
        if (artikel) {
            positions[posIndex].bezeichnung = artikel.bezeichnung;
            positions[posIndex].beschreibung = artikel.beschreibung || '';
            positions[posIndex].einzelpreis = artikel.preis;
            positions[posIndex].einheit = artikel.einheit;
            renderPositions();
            updatePreview();
            break;
        }
    }
}

// ============================================
// INITIALISIERUNG
// ============================================
async function initApp() {
    // Artikelkatalog und Preisstufen laden
    await loadArtikelKatalog();
    await loadPreisstufen();

    // Initiale Daten laden
    loadInitialData();

    // Datum setzen
    document.getElementById('angebotsdatum').value = new Date().toISOString().split('T')[0];

    // UI rendern
    renderImmobilien();
    renderPositions();
    updatePreview();

    // Event-Listener
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.search-container')) {
            document.getElementById('companyResults').classList.remove('active');
        }
    });

    console.log('FassadenFix Angebotsgenerator initialisiert');
}

function loadInitialData() {
    // Formular startet LEER - keine vorausgefüllten Daten
    // Eine leere Immobilie als Startpunkt
    immobilien = [createEmptyImmobilie(1)];

    // Standard-Positionen 0.0.x (Grundinformationen, immer im Angebot)
    const preisstaffelBeschreibung = `500 - 999 m²: 10,50 €/m²
1.000 - 2.499 m²: 9,75 €/m²
2.500 - 4.999 m²: 9,25 €/m²
ab 5.000 m²: 8,75 €/m²`;

    positions = [
        // 0.0.0 - Preisstaffel
        {
            pos: '0.0.0',
            immoNummer: 0,
            artikelgruppe: 'reinigung',
            menge: 1,
            einheit: '-',
            bezeichnung: 'FassadenFix Systemreinigung - Preisstaffel:',
            einzelpreis: 0,
            bedarfsposition: false,
            istEckdatenPosition: true,
            beschreibung: preisstaffelBeschreibung
        },
        // 0.0.1 - Jährliche Inspektion (Inklusivleistung) ✅
        {
            pos: '0.0.1',
            immoNummer: 0,
            artikelgruppe: 'reinigung',
            menge: 1,
            einheit: '-',
            bezeichnung: '✅ Jährliche Inspektion (Inklusivleistung)',
            einzelpreis: 0,
            bedarfsposition: false,
            istEckdatenPosition: true,
            beschreibung: 'Im Leistungsumfang enthalten: Jährliche Sichtprüfung der gereinigten Fassadenflächen während der Garantiezeit.'
        },
        // 0.0.2 - Ergebnisgarantie - 5 Jahre Algenfreiheit (Inklusivleistung) ✅
        {
            pos: '0.0.2',
            immoNummer: 0,
            artikelgruppe: 'reinigung',
            menge: 1,
            einheit: '-',
            bezeichnung: '✅ Ergebnisgarantie - 5 Jahre Algenfreiheit (Inklusivleistung)',
            einzelpreis: 0,
            bedarfsposition: false,
            istEckdatenPosition: true,
            beschreibung: 'Wir garantieren Ihnen 5 Jahre Algenfreiheit. Bei erneutem Befall innerhalb der Garantiezeit erfolgt kostenlose Nachbehandlung.'
        },
        // 0.0.3 - Pauschalfestpreisgarantie - Nachträge ausgeschlossen! (Inklusivleistung) ✅
        {
            pos: '0.0.3',
            immoNummer: 0,
            artikelgruppe: 'reinigung',
            menge: 1,
            einheit: '-',
            bezeichnung: '✅ Pauschalfestpreisgarantie - Nachträge ausgeschlossen! (Inklusivleistung)',
            einzelpreis: 0,
            bedarfsposition: false,
            istEckdatenPosition: true,
            beschreibung: 'Der Angebotspreis ist ein garantierter Pauschalfestpreis. Nachträge sind ausgeschlossen! Die Rechnung wird niemals höher als die Auftragsbestätigung.'
        }
    ];
}

// DOM Ready
document.addEventListener('DOMContentLoaded', initApp);
