// ============================================
// FASSADENFIX ANGEBOTSGENERATOR - PREVIEW.JS
// Preview-Rendering und PDF-Export
// ============================================

// ============================================
// PREVIEW UPDATE
// ============================================
function updatePreview() {
    updateDealAmount();
    updateFruehbucherErsparnis();
    updatePreviewStatus();

    const street = document.getElementById('companyStreet').value;
    const streetNum = document.getElementById('companyStreetNumber').value;
    const fullStreet = streetNum ? `${street} ${streetNum}` : street;

    const salutation = document.getElementById('contactSalutation').value;
    const firstname = document.getElementById('contactFirstname').value;
    const lastname = document.getElementById('contactLastname').value;
    const fullContact = `${salutation} ${firstname} ${lastname}`.trim();

    const ownerParts = document.getElementById('hubspotOwnerId').value.split('|');

    const data = {
        firma: document.getElementById('companyName').value,
        strasse: fullStreet,
        plz: document.getElementById('companyZip').value,
        ort: document.getElementById('companyCity').value,
        ansprechpartner: fullContact,
        angNr: document.getElementById('angebotsnummer').value,
        kundNr: document.getElementById('kundennummer').value,
        datum: document.getElementById('angebotsdatum').value,
        immobilien: immobilien
    };

    const ff = [ownerParts[1] || '', ownerParts[2] || '', ownerParts[3] || ''];
    const totals = calculateTotals();

    let posHTML = positions.map(p => {
        const ges = p.menge * p.einzelpreis;
        const cls = p.bedarfsposition ? 'bedarfs' : (p.istEckdatenPosition ? 'eckdaten' : '');
        const gesStr = p.bedarfsposition ? `(${formatCurrency(ges)})` : formatCurrency(ges);
        const bzLabel = p.bedarfsposition ? `${p.bezeichnung} (Bedarfsposition)` : p.bezeichnung;

        // Bei Eckdaten-Position keine Menge anzeigen
        const mengeStr = p.istEckdatenPosition ? '' : `${p.menge.toLocaleString('de-DE')} ${p.einheit}`;

        let beschrHTML = '';
        if (p.beschreibung) {
            beschrHTML = `<div class="beschreibung">${p.beschreibung.split('\n').join('<br>')}</div>`;
        }

        // Bezeichnung mit Zeilenumbrüchen formatieren
        const bzFormatted = bzLabel.split('\n').join('<br>');

        return `<tr class="${cls}">
            <td class="pos-col">${p.pos}</td>
            <td>${mengeStr}</td>
            <td><span class="bezeichnung">${bzFormatted}</span>${beschrHTML}</td>
            <td class="price-col">${p.einzelpreis > 0 ? formatCurrency(p.einzelpreis) : ''}</td>
            <td class="total-col">${ges > 0 ? gesStr : ''}</td>
        </tr>`;
    }).join('');

    document.getElementById('pdfPreview').innerHTML = generatePreviewHTML(data, ff, totals, posHTML);
}

function generatePreviewHTML(data, ff, totals, posHTML) {
    return `
        <div class="pdf-header">
            <img src="assets/logo.png" alt="FassadenFix" style="height: 20mm; width: auto;">
        </div>
        <div class="pdf-header-line"></div>
        
        <div class="pdf-sender-line">
            FASSADENFIX • Immobiliengruppe Retzlaff OHG • An der Saalebahn 8a • 06118 Halle
        </div>
        
        <div class="pdf-address-meta">
            <div class="pdf-address">
                <div class="pdf-address-company">${data.firma}</div>
                <div>${data.ansprechpartner}</div>
                <div>${data.strasse}</div>
                <div>${data.plz} ${data.ort}</div>
            </div>
            <div class="pdf-meta">
                <div class="pdf-meta-row"><span class="pdf-meta-label">Angebotsnummer</span><span class="pdf-meta-value">${data.angNr}</span></div>
                <div class="pdf-meta-row"><span class="pdf-meta-label">Kundennummer</span><span class="pdf-meta-value">${data.kundNr}</span></div>
                <div class="pdf-meta-row"><span class="pdf-meta-label">Datum</span><span class="pdf-meta-value">${formatDate(data.datum)}</span></div>
                <div class="pdf-meta-row"><span class="pdf-meta-label">Ansprechpartner</span><span class="pdf-meta-value">${ff[0]}</span></div>
                <div class="pdf-meta-row"><span class="pdf-meta-label">Mobil</span><span class="pdf-meta-value">${ff[2]}</span></div>
                <div class="pdf-meta-row"><span class="pdf-meta-label">E-Mail</span><span class="pdf-meta-value">${ff[1]}</span></div>
            </div>
        </div>
        
        <div class="pdf-title">Angebot Nr. ${data.angNr}</div>
        
        <div class="pdf-intro">
            Wir freuen uns über Ihr Interesse an unserer FassadenFix - Systemreinigung.<br>
            Gerne erstellen wir Ihnen wunschgemäß ein Angebot.
        </div>
        
        <table class="pdf-table">
            <thead>
                <tr>
                    <th>Pos</th>
                    <th>Menge</th>
                    <th>Bezeichnung</th>
                    <th>Einheitspreis</th>
                    <th>Gesamt</th>
                </tr>
            </thead>
            <tbody>${posHTML}</tbody>
        </table>
        
        <div class="pdf-totals">
            ${totals.bedarfs !== 0 ? `<div class="pdf-total-row bedarfs"><span>Bedarfspositionen</span><span>(${formatCurrency(totals.bedarfs)})</span></div>` : ''}
            <div class="pdf-total-row"><span>Nettobetrag</span><span>${formatCurrency(totals.netto)}</span></div>
            <div class="pdf-total-row"><span>zzgl. 19% MwSt.</span><span>${formatCurrency(totals.mwst)}</span></div>
            <div class="pdf-total-row final"><span>Gesamtsumme</span><span>${formatCurrency(totals.brutto)}</span></div>
        </div>
        
        <div class="pdf-footer-content">
            <div class="pdf-footer-col">
                <strong>FASSADENFIX</strong>
                <div>Immobiliengruppe Retzlaff oHG</div>
                <div>An der Saalebahn 8a</div>
                <div>06118 Halle (Saale)</div>
            </div>
            <div class="pdf-footer-col">
                <div>T  0345 218392 35</div>
                <div>E  info@fassadenfix.de</div>
                <div>W www.fassadenfix.de</div>
            </div>
            <div class="pdf-footer-col">
                <div>Commerzbank</div>
                <div>IBAN: DE49 8004 0000 0325 0123 00</div>
                <div>BIC: COBADEFFXXX</div>
            </div>
            <div class="pdf-footer-col">
                <div>Geschäftsführer:</div>
                <div>Alexander Retzlaff</div>
                <div>HRA 4244</div>
            </div>
        </div>
        <div class="pdf-footer"></div>
    `;
}

function updateDealAmount() {
    const totals = calculateTotals();
    document.getElementById('dealAmount').value = formatCurrency(totals.brutto);
}

function updateFruehbucherErsparnis() {
    const aktiv = document.getElementById('fruehbucherAktiv').checked;
    const prozent = parseFloat(document.getElementById('fruehbucherProzent').value) || 0;

    let nettoOhneRabatt = 0;
    positions.forEach(p => {
        if (!p.bedarfsposition && p.einzelpreis > 0) {
            nettoOhneRabatt += p.menge * p.einzelpreis;
        }
    });

    const ersparnis = aktiv ? (nettoOhneRabatt * prozent / 100) : 0;
    document.getElementById('fruehbucherErsparnis').textContent = formatCurrency(ersparnis);
    return { aktiv, prozent, ersparnis };
}

function updatePreviewStatus() {
    const statusEl = document.getElementById('previewStatus');
    const issues = [];

    if (!document.getElementById('companyName').value) issues.push('Unternehmen');
    if (!document.getElementById('contactLastname').value) issues.push('Ansprechpartner');
    if (!document.getElementById('angebotsnummer').value) issues.push('Angebotsnummer');
    if (immobilien.length === 0) issues.push('Immobilie');
    if (positions.length === 0) issues.push('Positionen');

    if (issues.length > 0) {
        statusEl.innerHTML = `<span style="color:#f57c00;">⚠️ Fehlend: ${issues.join(', ')}</span>`;
    } else {
        statusEl.innerHTML = `<span style="color:#7AB800;">✓ Vollständig</span>`;
    }
}

// ============================================
// RABATTE UND AKTIONEN
// ============================================
function toggleRabatt(typ, aktiv) {
    const detailsMap = {
        'fruehbucher': 'fruehbucherDetails',
        'wohnungsunternehmen': 'wohnungsunternehmenDetails',
        'sonder': 'sonderrabattDetails'
    };

    const detailsId = detailsMap[typ];
    if (detailsId) {
        const details = document.getElementById(detailsId);
        if (details) {
            details.style.display = aktiv ? 'block' : 'none';
        }
    }

    updateRabatte();
    updatePreview();
}

// Frühbucher-Optionen basierend auf Aktionsjahr aktualisieren
function updateFruehbucherOptionen() {
    const aktionSelect = document.getElementById('fruehbucherAktion');
    const prozentSelect = document.getElementById('fruehbucherProzent');
    if (!aktionSelect || !prozentSelect) return;

    const jahr = aktionSelect.value;
    const vorjahr = parseInt(jahr) - 1;

    // Optionen aktualisieren (Jahr in data-bis anpassen)
    const optionen = [
        { value: '6', bis: `${vorjahr}-12-31`, label: `6% (bis 31.12.${vorjahr})` },
        { value: '4.5', bis: `${jahr}-01-31`, label: `4,5% (bis 31.01.${jahr})` },
        { value: '3', bis: `${jahr}-02-28`, label: `3% (bis 28.02.${jahr})` },
        { value: '1.5', bis: `${jahr}-03-31`, label: `1,5% (bis 31.03.${jahr})` }
    ];

    prozentSelect.innerHTML = optionen.map(opt =>
        `<option value="${opt.value}" data-bis="${opt.bis}">${opt.label}</option>`
    ).join('');

    updateRabatte();
}

function updateRabatte() {
    const totals = calculateTotals ? calculateTotals() : { netto: 0 };
    const netto = totals.netto || 0;

    let rabattProzent = 0;
    let ersparnis = 0;

    // Frühbucherrabatt
    const fruehbucherAktiv = document.getElementById('fruehbucherAktiv')?.checked;
    if (fruehbucherAktiv) {
        const fruehbucherProzent = parseFloat(document.getElementById('fruehbucherProzent')?.value) || 0;
        rabattProzent += fruehbucherProzent;

        // Badge aktualisieren
        const badge = document.getElementById('fruehbucherAktuell');
        if (badge) badge.textContent = fruehbucherProzent + '%';
    }

    // Sonderrabatt
    const sonderAktiv = document.getElementById('sonderrabattAktiv')?.checked;
    if (sonderAktiv) {
        const sonderProzent = parseFloat(document.getElementById('sonderrabattProzent')?.value) || 0;
        rabattProzent += sonderProzent;
    }

    // Ersparnis berechnen
    ersparnis = netto * (rabattProzent / 100);

    // Anzeige aktualisieren
    const ersparnisEl = document.getElementById('gesamtErsparnis');
    const rabattEl = document.getElementById('rabattGesamt');

    if (ersparnisEl) ersparnisEl.textContent = formatCurrency(ersparnis);
    if (rabattEl) rabattEl.textContent = rabattProzent.toLocaleString('de-DE') + '%';

    // Alte Elemente für Kompatibilität
    const altErsparnis = document.getElementById('fruehbucherErsparnis');
    if (altErsparnis) altErsparnis.textContent = formatCurrency(ersparnis);
}

function getRabattData() {
    return {
        fruehbucher: {
            aktiv: document.getElementById('fruehbucherAktiv')?.checked || false,
            prozent: parseFloat(document.getElementById('fruehbucherProzent')?.value) || 0,
            gueltigBis: document.getElementById('fruehbucherBis')?.value || ''
        },
        wohnungsunternehmen: {
            aktiv: document.getElementById('wohnungsunternehmenAktiv')?.checked || false,
            preisProM2: parseFloat(document.getElementById('wohnungsunternehmenPreis')?.value) || 7.99
        },
        sonder: {
            aktiv: document.getElementById('sonderrabattAktiv')?.checked || false,
            prozent: parseFloat(document.getElementById('sonderrabattProzent')?.value) || 0,
            grund: document.getElementById('sonderrabattGrund')?.value || ''
        }
    };
}

// Legacy-Funktion für Kompatibilität
function toggleFruehbucher(active) {
    toggleRabatt('fruehbucher', active);
}

function getFruehbucherData() {
    const data = getRabattData();
    return {
        aktiv: data.fruehbucher.aktiv,
        prozent: data.fruehbucher.prozent,
        gueltigBis: data.fruehbucher.gueltigBis
    };
}
