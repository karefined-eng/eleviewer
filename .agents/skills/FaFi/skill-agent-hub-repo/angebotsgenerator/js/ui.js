// ============================================
// FASSADENFIX ANGEBOTSGENERATOR - UI.JS
// UI-Rendering und Event-Handler
// ============================================

// ============================================
// IMMOBILIEN RENDERING
// ============================================
function renderImmobilien() {
    const container = document.getElementById('immobilienContainer');

    container.innerHTML = immobilien.map((immo, immoIdx) => {
        const aktiveSeitenCount = Object.values(immo.seiten).filter(s => s.zuReinigen === true).length;
        const gesamtFlaeche = Object.values(immo.seiten).filter(s => s.zuReinigen === true).reduce((sum, s) => sum + (s.flaeche || 0), 0);

        return `
        <div class="immobilie-card">
            <div class="immobilie-header">
                <span class="immobilie-nummer">Immobilie ${immo.nummer}</span>
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:12px;">${aktiveSeitenCount}/4 Seiten • ${gesamtFlaeche.toLocaleString('de-DE')} m²</span>
                    ${immobilien.length > 1 ? `<button class="position-remove" onclick="removeImmobilie(${immoIdx})">×</button>` : ''}
                </div>
            </div>
            <div class="immobilie-body">
                <!-- ADRESSE -->
                <div style="margin-bottom:15px;padding-bottom:15px;border-bottom:1px solid var(--ff-border);">
                    <div class="form-row">
                        <div class="form-group" style="flex:2;">
                            <label>Straße</label>
                            <input type="text" value="${immo.adresse.strasse}" onchange="updateImmobilieAdresse(${immoIdx},'strasse',this.value)">
                        </div>
                        <div class="form-group" style="flex:1;">
                            <label>Hausnummer(n)</label>
                            <input type="text" value="${immo.adresse.hausnummer}" placeholder="z.B. 10-12" onchange="updateImmobilieAdresse(${immoIdx},'hausnummer',this.value)">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group" style="max-width:100px;">
                            <label>PLZ</label>
                            <input type="text" value="${immo.adresse.plz}" onchange="updateImmobilieAdresse(${immoIdx},'plz',this.value)">
                        </div>
                        <div class="form-group">
                            <label>Ort</label>
                            <input type="text" value="${immo.adresse.ort}" onchange="updateImmobilieAdresse(${immoIdx},'ort',this.value)">
                        </div>
                    </div>
                </div>

                <!-- PFLICHTABFRAGEN -->
                <div style="margin-bottom:15px;padding:12px;background:${immo.reinigungMoeglich === false ? '#fef2f2' : '#f8fafc'};border-radius:8px;border:2px solid ${immo.reinigungMoeglich === null ? '#f59e0b' : (immo.reinigungMoeglich === false ? '#ef4444' : 'var(--ff-green)')};">
                    <div style="font-size:11px;font-weight:600;color:${immo.reinigungMoeglich === false ? '#ef4444' : 'var(--ff-green)'};text-transform:uppercase;margin-bottom:10px;">
                        ⚠️ Pflichtabfragen
                    </div>
                    
                    <!-- 1. Reinigung möglich? -->
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding:10px;background:#fff;border-radius:6px;border-left:3px solid ${immo.reinigungMoeglich === null ? '#f59e0b' : (immo.reinigungMoeglich === false ? '#ef4444' : 'var(--ff-green)')};">
                        <span style="font-weight:600;font-size:13px;">1. Ist Reinigung möglich?</span>
                        <div style="display:flex;gap:4px;">
                            <button type="button" class="toggle-btn-sm ${immo.reinigungMoeglich === true ? 'active yes' : ''}" onclick="setPflichtabfrage(${immoIdx},'reinigungMoeglich',true)">✓ Ja</button>
                            <button type="button" class="toggle-btn-sm ${immo.reinigungMoeglich === false ? 'active no' : ''}" onclick="setPflichtabfrage(${immoIdx},'reinigungMoeglich',false)">✗ Nein</button>
                        </div>
                    </div>
                    ${immo.reinigungMoeglich === false ? `
                    <div style="background:#fef2f2;border:1px solid #ef4444;border-radius:6px;padding:10px;margin-bottom:12px;">
                        <div style="color:#ef4444;font-weight:600;font-size:12px;">⛔ Angebotserstellung nicht möglich</div>
                        <div style="color:#991b1b;font-size:11px;margin-top:4px;">Die Reinigung dieser Immobilie wurde als nicht möglich markiert. Ein Angebot kann nicht erstellt werden.</div>
                    </div>
                    ` : ''}
                    
                    <!-- 2. Marketing geeignet? -->
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px;background:#fff;border-radius:6px;border-left:3px solid ${immo.marketingGeeignet === true ? '#8b5cf6' : 'var(--ff-border)'};">
                        <div>
                            <span style="font-weight:600;font-size:13px;">2. Marketing geeignet?</span>
                            ${immo.marketingGeeignet === true ? '<span style="margin-left:8px;font-size:10px;background:#8b5cf6;color:white;padding:2px 6px;border-radius:10px;">📸 Marketing</span>' : ''}
                        </div>
                        <div style="display:flex;gap:4px;">
                            <button type="button" class="toggle-btn-sm ${immo.marketingGeeignet === true ? 'active yes' : ''}" onclick="setPflichtabfrage(${immoIdx},'marketingGeeignet',true)" style="${immo.marketingGeeignet === true ? 'background:#8b5cf6 !important;' : ''}">✓ Ja</button>
                            <button type="button" class="toggle-btn-sm ${immo.marketingGeeignet === false ? 'active no' : ''}" onclick="setPflichtabfrage(${immoIdx},'marketingGeeignet',false)">✗ Nein</button>
                        </div>
                    </div>
                    ${immo.marketingGeeignet === true ? `
                    <div style="background:#ede9fe;border:1px solid #8b5cf6;border-radius:6px;padding:10px;margin-top:8px;">
                        <div style="color:#7c3aed;font-weight:600;font-size:12px;">📸 Marketing-Kandidat markiert</div>
                        <div style="color:#6d28d9;font-size:11px;margin-top:4px;">
                            ${immo.marketingAufgabeErstellt
                    ? '✓ HubSpot-Aufgabe wurde erstellt (48h Frist für Abstimmung)'
                    : '⏳ HubSpot-Aufgabe wird bei Speicherung/Sync erstellt'
                }
                        </div>
                    </div>
                    ` : ''}
                </div>
                
                <!-- NEU: KOPFDATEN (Objektaufnahme) -->
                <div style="margin-bottom:15px;padding-bottom:15px;border-bottom:1px solid var(--ff-border);background:#f0fdf4;border-radius:8px;padding:12px;">
                    <div style="font-size:11px;font-weight:600;color:var(--ff-green);text-transform:uppercase;margin-bottom:10px;">📝 Objektaufnahme</div>
                    <div class="form-row">
                        <div class="form-group" style="flex:1;">
                            <label>Datum Objektaufnahme</label>
                            <input type="date" value="${immo.datumObjektaufnahme || ''}" onchange="updateImmobilieKopfdaten(${immoIdx},'datumObjektaufnahme',this.value)">
                        </div>
                        <div class="form-group" style="flex:1;">
                            <label>FassadenFix Mitarbeiter</label>
                            <select onchange="updateImmobilieKopfdaten(${immoIdx},'ffMitarbeiter',this.value)">
                                <option value="">-- Bitte wählen --</option>
                                ${Object.entries(hubspotOwners).map(([id, owner]) =>
                    `<option value="${id}" ${immo.ffMitarbeiter === id ? 'selected' : ''}>${owner.name}</option>`
                ).join('')}
                            </select>
                        </div>
                    </div>
                    
                    <!-- AG-Mitarbeiter (optional) -->
                    <details style="margin-top:10px;">
                        <summary style="cursor:pointer;font-size:12px;color:var(--ff-gray);">+ Anwesender AG-Mitarbeiter (optional)</summary>
                        <div style="margin-top:10px;padding:10px;background:#fff;border-radius:6px;border:1px solid var(--ff-border);">
                            <div class="form-row">
                                <div class="form-group" style="flex:1;">
                                    <label>Name</label>
                                    <input type="text" value="${immo.agMitarbeiter?.name || ''}" placeholder="z.B. Max Mustermann" onchange="updateAGMitarbeiter(${immoIdx},'name',this.value)">
                                </div>
                                <div class="form-group" style="flex:1;">
                                    <label>Position/Funktion</label>
                                    <input type="text" value="${immo.agMitarbeiter?.position || ''}" placeholder="z.B. Hausmeister" onchange="updateAGMitarbeiter(${immoIdx},'position',this.value)">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group" style="flex:1;">
                                    <label>E-Mail</label>
                                    <input type="email" value="${immo.agMitarbeiter?.email || ''}" placeholder="email@firma.de" onchange="updateAGMitarbeiter(${immoIdx},'email',this.value)">
                                </div>
                                <div class="form-group" style="flex:1;">
                                    <label>Telefon</label>
                                    <input type="tel" value="${immo.agMitarbeiter?.telefon || ''}" placeholder="+49..." onchange="updateAGMitarbeiter(${immoIdx},'telefon',this.value)">
                                </div>
                            </div>
                        </div>
                    </details>
                </div>
                
                <!-- ALLE SEITEN -->
                <div style="margin-bottom:15px;">
                    <label class="checkbox-label" style="font-weight:600;font-size:13px;">
                        <input type="checkbox" ${Object.values(immo.seiten).every(s => s.zuReinigen === true) ? 'checked' : ''} onchange="toggleAlleSeiten(${immoIdx},this.checked)">
                        <span style="color:var(--ff-green);">✓ Alle 4 Seiten zur Reinigung auswählen</span>
                    </label>
                </div>
                
                <!-- 4 SEITEN -->
                <div class="seiten-container">
                    ${Object.entries(immo.seiten).map(([key, seite]) => renderSeite(immoIdx, key, seite)).join('')}
                </div>
                
                <!-- POSITIONEN FÜR DIESE IMMOBILIE -->
                <div style="margin-top:20px;padding-top:15px;border-top:2px solid var(--ff-green);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                        <div style="font-size:13px;font-weight:600;color:var(--ff-green);">
                            📋 Positionen für Immobilie ${immo.nummer}
                        </div>
                        <span style="font-size:11px;color:#666;">
                            ${positions.filter(p => p.immoNummer === immo.nummer).length} Positionen
                        </span>
                    </div>
                    
                    <!-- Position X.0.0 - Immobilien-Eckdaten (Zusammenfassung) -->
                    ${gesamtFlaeche > 0 ? `
                    <div style="background:linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);border-radius:8px;padding:12px;margin-bottom:10px;border:1px solid #7AB80033;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <strong style="font-size:14px;color:var(--ff-green);">Pos ${immo.nummer}.0.0</strong>
                                <span style="font-size:12px;color:#666;margin-left:8px;">Immobilien-Eckdaten</span>
                            </div>
                            <strong style="color:var(--ff-green);">${gesamtFlaeche.toLocaleString('de-DE')} m²</strong>
                        </div>
                        <div style="font-size:11px;color:#666;margin-top:6px;">
                            ${immo.adresse.strasse} ${immo.adresse.hausnummer}, ${immo.adresse.plz} ${immo.adresse.ort}<br>
                            ${Object.entries(immo.seiten).filter(([k, s]) => s.zuReinigen === true).map(([k, s]) =>
                    SEITEN_TYPEN[k].label + ' (' + (s.flaeche || 0).toLocaleString('de-DE') + ' m²)'
                ).join(', ') || 'Keine Seiten ausgewählt'}
                        </div>
                    </div>
                    ` : `
                    <div style="background:#fef3c7;border-radius:8px;padding:12px;text-align:center;font-size:12px;color:#92400e;">
                        ⚠️ Bitte mindestens eine Seite mit Fläche zur Reinigung auswählen
                    </div>
                    `}
                    
                    <!-- Einzelpositionen dieser Immobilie -->
                    <div id="immoPositions-${immo.nummer}">
                        ${renderPositionsForImmo(immo.nummer)}
                    </div>
                </div>
            </div>
        </div>
    `}).join('');

    // Immobilien-Counter aktualisieren
    const immoCountEl = document.getElementById('immoCount');
    if (immoCountEl) immoCountEl.textContent = immobilien.length;

    // Positions-Statistik aktualisieren
    updatePositionStats();
}

function renderSeite(immoIdx, seiteKey, seite) {
    const typ = SEITEN_TYPEN[seiteKey];
    const flaecheBerechnet = seite.breite && seite.hoehe ? Math.round(seite.breite * seite.hoehe) : seite.flaeche || 0;
    const zuReinigenStatus = seite.zuReinigen;
    const statusClass = zuReinigenStatus === true ? 'zu-reinigen-ja' : (zuReinigenStatus === false ? 'zu-reinigen-nein' : 'zu-reinigen-unentschieden');

    return `
    <div class="seite-card ${zuReinigenStatus === true ? 'active' : 'inactive'} ${statusClass}">
        <div class="seite-header">
            <div class="seite-title">
                <span>${typ.icon} ${typ.label}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <!-- ZU REINIGEN? - Pflichtfeld -->
                <div class="zu-reinigen-toggle" style="display:flex;gap:2px;background:#e5e7eb;border-radius:6px;padding:2px;">
                    <button type="button" class="toggle-btn ${zuReinigenStatus === true ? 'active yes' : ''}" 
                            onclick="setZuReinigen(${immoIdx},'${seiteKey}',true)" 
                            style="padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:600;transition:all 0.2s;">
                        ✓ Ja
                    </button>
                    <button type="button" class="toggle-btn ${zuReinigenStatus === false ? 'active no' : ''}" 
                            onclick="setZuReinigen(${immoIdx},'${seiteKey}',false)" 
                            style="padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:600;transition:all 0.2s;">
                        ✗ Nein
                    </button>
                </div>
                ${zuReinigenStatus === true ? `<span class="seite-flaeche">${flaecheBerechnet.toLocaleString('de-DE')} m²</span>` : ''}
                ${zuReinigenStatus === true ? `<span style="font-size:16px;color:var(--ff-gray);cursor:pointer;" onclick="toggleSeiteExpand(${immoIdx},'${seiteKey}')">▼</span>` : ''}
            </div>
        </div>
        ${zuReinigenStatus === true ? `
        <div class="seite-body expanded" id="seite-body-${immoIdx}-${seiteKey}">
            ${renderSeiteDetails(immoIdx, seiteKey, seite, flaecheBerechnet)}
        </div>
        ` : (zuReinigenStatus === null ? `
        <div class="seite-body" style="padding:10px;background:#fef3c7;border-radius:0 0 8px 8px;">
            <span style="font-size:11px;color:#92400e;">⚠️ Bitte entscheiden: Soll diese Seite gereinigt werden?</span>
        </div>
        ` : '')}
    </div>
    `;
}

function renderSeiteDetails(immoIdx, seiteKey, seite, flaecheBerechnet) {
    // Bühnen-Preis ermitteln
    const buehneTyp = seite.buehne?.typ || 'keine';
    const buehnePreisInfo = BUEHNEN_PREISE[buehneTyp] || BUEHNEN_PREISE['keine'];
    const istSonderbuehne = buehnePreisInfo.preis === 'anfrage';

    return `
        <!-- 2.1 KOPFBEREICH SEITE -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid var(--ff-border);">
            <div class="form-group">
                <label>Letzte Sanierung (Jahr)</label>
                <input type="number" min="1900" max="2030" value="${seite.letzteSanierung || ''}" placeholder="z.B. 2018" onchange="updateSeite(${immoIdx},'${seiteKey}','letzteSanierung',this.value)">
            </div>
            <div class="form-group">
                <label>Farbwerte</label>
                <input type="text" value="${seite.farbwerte || ''}" placeholder="z.B. RAL 9010" onchange="updateSeite(${immoIdx},'${seiteKey}','farbwerte',this.value)">
            </div>
        </div>
        
        <!-- 2.2 MASSE -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:15px;">
            <div class="form-group">
                <label>Breite (m)</label>
                <input type="number" step="0.1" value="${seite.breite || ''}" placeholder="0" onchange="updateSeite(${immoIdx},'${seiteKey}','breite',parseFloat(this.value)||0)">
            </div>
            <div class="form-group">
                <label>Höhe (m)</label>
                <input type="number" step="0.1" value="${seite.hoehe || ''}" placeholder="0" onchange="updateSeite(${immoIdx},'${seiteKey}','hoehe',parseFloat(this.value)||0)">
            </div>
            <div class="form-group">
                <label>Fläche (m²)</label>
                <input type="number" value="${flaecheBerechnet}" style="background:#f0f0f0;font-weight:600;" onchange="updateSeite(${immoIdx},'${seiteKey}','flaeche',parseFloat(this.value)||0)">
            </div>
        </div>
        
        <!-- 2.3 ABFRAGEN MIT LOGIK -->
        <div class="abfragen-container" style="display:flex;flex-direction:column;gap:12px;">
            
            <!-- A) BALKONE VORHANDEN? -->
            <div class="abfrage-item" style="background:#f8fafc;border-radius:8px;padding:12px;border-left:3px solid var(--ff-border);">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:600;font-size:13px;">A) Balkone vorhanden?</span>
                    <div class="ja-nein-toggle" style="display:flex;gap:4px;">
                        <button type="button" class="toggle-btn-sm ${seite.balkone === true ? 'active yes' : ''}" onclick="updateSeite(${immoIdx},'${seiteKey}','balkone',true)">Ja</button>
                        <button type="button" class="toggle-btn-sm ${seite.balkone === false ? 'active no' : ''}" onclick="updateSeite(${immoIdx},'${seiteKey}','balkone',false)">Nein</button>
                    </div>
                </div>
            </div>
            
            <!-- B) BÜHNEN-TYP -->
            <div class="abfrage-item" style="background:#f8fafc;border-radius:8px;padding:12px;border-left:3px solid ${istSonderbuehne ? '#f59e0b' : 'var(--ff-green)'};">
                <div style="font-weight:600;font-size:13px;margin-bottom:8px;">B) Bühnen-Typ</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">
                    <label class="radio-pill ${buehneTyp === 'keine' ? 'selected' : ''}" onclick="setBuehneTyp(${immoIdx},'${seiteKey}','keine')">
                        <input type="radio" name="buehne-${immoIdx}-${seiteKey}" ${buehneTyp === 'keine' ? 'checked' : ''}>
                        Keine Bühne <span style="color:var(--ff-green);font-weight:600;">0 €</span>
                    </label>
                    <label class="radio-pill ${buehneTyp === 'standard' ? 'selected' : ''}" onclick="setBuehneTyp(${immoIdx},'${seiteKey}','standard')">
                        <input type="radio" name="buehne-${immoIdx}-${seiteKey}" ${buehneTyp === 'standard' ? 'checked' : ''}>
                        FassadenFix Standard <span style="color:var(--ff-green);font-weight:600;">390 €/Tag</span>
                    </label>
                    <label class="radio-pill ${istSonderbuehne ? 'selected warning' : ''}" onclick="setBuehneTyp(${immoIdx},'${seiteKey}','sonder')">
                        <input type="radio" name="buehne-${immoIdx}-${seiteKey}" ${istSonderbuehne ? 'checked' : ''}>
                        Sonderbühne <span style="color:#f59e0b;font-weight:600;">Auf Anfrage</span>
                    </label>
                </div>
                
                ${istSonderbuehne ? `
                <!-- Sonderbühnen-Dropdown (aufgeklappt) -->
                <div class="submenu" style="margin-top:10px;padding:10px;background:#fff;border-radius:6px;border:1px solid #f59e0b;">
                    <label style="font-size:12px;font-weight:500;margin-bottom:6px;display:block;">Sonderbühnen-Typ:</label>
                    <select onchange="updateSeite(${immoIdx},'${seiteKey}','buehne',{...immobilien[${immoIdx}].seiten['${seiteKey}'].buehne, sonderTyp: this.value})" style="width:100%;">
                        <option value="" ${!seite.buehne?.sonderTyp ? 'selected' : ''}>-- Bitte wählen --</option>
                        <option value="gelenkbuehne" ${seite.buehne?.sonderTyp === 'gelenkbuehne' ? 'selected' : ''}>Gelenkbühne</option>
                        <option value="teleskopbuehne" ${seite.buehne?.sonderTyp === 'teleskopbuehne' ? 'selected' : ''}>Teleskopbühne</option>
                        <option value="lkwbuehne" ${seite.buehne?.sonderTyp === 'lkwbuehne' ? 'selected' : ''}>LKW-Bühne</option>
                        <option value="kletterer" ${seite.buehne?.sonderTyp === 'kletterer' ? 'selected' : ''}>Industriekletterer</option>
                        <option value="geruest" ${seite.buehne?.sonderTyp === 'geruest' ? 'selected' : ''}>Gerüst</option>
                        <option value="sonstiges" ${seite.buehne?.sonderTyp === 'sonstiges' ? 'selected' : ''}>Sonstiges</option>
                    </select>
                    <div style="margin-top:8px;padding:8px;background:#fef3c7;border-radius:4px;font-size:11px;color:#92400e;">
                        ⚠️ Preis wird mit "Auf Anfrage" im Angebot angezeigt - Rücksprache erforderlich
                    </div>
                </div>
                ` : ''}
                
                ${buehneTyp === 'standard' ? `
                <div class="submenu" style="margin-top:10px;padding:10px;background:#fff;border-radius:6px;border:1px solid var(--ff-green);">
                    <div class="form-group">
                        <label style="font-size:12px;">Anzahl Tage</label>
                        <input type="number" min="1" value="${seite.buehne?.tage || 1}" style="width:80px;" onchange="updateSeite(${immoIdx},'${seiteKey}','buehne',{...immobilien[${immoIdx}].seiten['${seiteKey}'].buehne, tage: parseInt(this.value)||1})">
                    </div>
                </div>
                ` : ''}
            </div>
            
            <!-- C) REINIGUNGSPRODUKT -->
            <div class="abfrage-item" style="background:#f8fafc;border-radius:8px;padding:12px;border-left:3px solid ${seite.reinigungsprodukt?.zusaetzlichErforderlich ? '#f59e0b' : 'var(--ff-green)'};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-weight:600;font-size:13px;">C) Reinigungsprodukt</span>
                    <span style="font-size:11px;color:var(--ff-green);font-weight:500;">✓ Standard: FFC / FFC Plus</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <label class="checkbox-label" style="font-size:12px;">
                        <input type="checkbox" ${seite.reinigungsprodukt?.zusaetzlichErforderlich ? 'checked' : ''} onchange="toggleReinigungsproduktZusatz(${immoIdx},'${seiteKey}',this.checked)">
                        Anderes/Zusätzliches erforderlich
                    </label>
                </div>
                
                ${seite.reinigungsprodukt?.zusaetzlichErforderlich ? `
                <!-- Reinigungsprodukt Untermenü -->
                <div class="submenu" style="margin-top:10px;padding:10px;background:#fff;border-radius:6px;border:1px solid #f59e0b;">
                    <div style="margin-bottom:10px;">
                        <label style="font-size:12px;font-weight:500;display:block;margin-bottom:6px;">1. Produkt (Multi-Select):</label>
                        <div style="display:flex;flex-wrap:wrap;gap:6px;">
                            ${['icarly_stone', 's1_steinaner', 'm1', 'sonstiges'].map(prod => `
                                <label class="checkbox-pill ${(seite.reinigungsprodukt?.zusaetzlichProdukte || []).includes(prod) ? 'checked' : ''}" onclick="toggleZusatzProdukt(${immoIdx},'${seiteKey}','${prod}',this)">
                                    <input type="checkbox" ${(seite.reinigungsprodukt?.zusaetzlichProdukte || []).includes(prod) ? 'checked' : ''}>
                                    ${prod === 'icarly_stone' ? 'iCarly Stone' : prod === 's1_steinaner' ? 'S.1/Steinaner' : prod === 'm1' ? 'M1' : 'Sonstiges'}
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    <div style="margin-bottom:10px;">
                        <label style="font-size:12px;font-weight:500;display:block;margin-bottom:6px;">2. Anwendung:</label>
                        <div style="display:flex;gap:8px;">
                            <label class="radio-pill ${seite.reinigungsprodukt?.anwendung === 'zusaetzlich' ? 'selected' : ''}" onclick="setReinigungsproduktAnwendung(${immoIdx},'${seiteKey}','zusaetzlich')">
                                <input type="radio" name="anwendung-${immoIdx}-${seiteKey}" ${seite.reinigungsprodukt?.anwendung === 'zusaetzlich' ? 'checked' : ''}>
                                Zusätzlich
                            </label>
                            <label class="radio-pill ${seite.reinigungsprodukt?.anwendung === 'stattdessen' ? 'selected' : ''}" onclick="setReinigungsproduktAnwendung(${immoIdx},'${seiteKey}','stattdessen')">
                                <input type="radio" name="anwendung-${immoIdx}-${seiteKey}" ${seite.reinigungsprodukt?.anwendung === 'stattdessen' ? 'checked' : ''}>
                                Stattdessen
                            </label>
                        </div>
                    </div>
                    <div>
                        <label style="font-size:12px;font-weight:500;display:block;margin-bottom:6px;">3. Begründung: <span style="color:#9ca3af;">🎤 Sprache-zu-Text</span></label>
                        <div style="display:flex;gap:6px;">
                            <input type="text" value="${seite.reinigungsprodukt?.begruendung || ''}" placeholder="Begründung eingeben..." style="flex:1;" onchange="setReinigungsproduktBegruendung(${immoIdx},'${seiteKey}',this.value)">
                            <button type="button" class="btn-mic" onclick="startSpeechToText(${immoIdx},'${seiteKey}','reinigungsprodukt.begruendung')" title="Spracheingabe">🎤</button>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
            
            <!-- D) ZUGÄNGLICHKEIT -->
            <div class="abfrage-item" style="background:#f8fafc;border-radius:8px;padding:12px;border-left:3px solid ${seite.zugaenglichkeit?.typ === 'eingeschraenkt' ? '#f59e0b' : 'var(--ff-green)'};">
                <div style="font-weight:600;font-size:13px;margin-bottom:8px;">D) Zugänglichkeit</div>
                <div style="display:flex;gap:8px;margin-bottom:8px;">
                    <label class="radio-pill ${seite.zugaenglichkeit?.typ === 'ungehindert' ? 'selected' : ''}" onclick="setZugaenglichkeit(${immoIdx},'${seiteKey}','ungehindert')">
                        <input type="radio" name="zugang-${immoIdx}-${seiteKey}" ${seite.zugaenglichkeit?.typ === 'ungehindert' ? 'checked' : ''}>
                        ✓ Ungehindert
                    </label>
                    <label class="radio-pill ${seite.zugaenglichkeit?.typ === 'eingeschraenkt' ? 'selected warning' : ''}" onclick="setZugaenglichkeit(${immoIdx},'${seiteKey}','eingeschraenkt')">
                        <input type="radio" name="zugang-${immoIdx}-${seiteKey}" ${seite.zugaenglichkeit?.typ === 'eingeschraenkt' ? 'checked' : ''}>
                        ⚠ Eingeschränkt
                    </label>
                </div>
                
                ${seite.zugaenglichkeit?.typ === 'eingeschraenkt' ? `
                <!-- Zugänglichkeit Untermenü -->
                <div class="submenu" style="margin-top:8px;padding:10px;background:#fff;border-radius:6px;border:1px solid #f59e0b;">
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;">
                        ${['gehweg', 'parkplatz', 'strasse', 'gruenschnitt', 'sonstiges'].map(typ => `
                            <label class="checkbox-pill ${(seite.zugaenglichkeit?.einschraenkungen || []).includes(typ) ? 'checked' : ''}" onclick="toggleZugaenglichkeitOption(${immoIdx},'${seiteKey}','${typ}',this)">
                                <input type="checkbox" ${(seite.zugaenglichkeit?.einschraenkungen || []).includes(typ) ? 'checked' : ''}>
                                ${typ === 'gehweg' ? 'Gehweg-Sperrung nötig' : typ === 'parkplatz' ? 'Parkplatz-Sperrung nötig' : typ === 'strasse' ? 'Straßensperrung nötig' : typ === 'gruenschnitt' ? 'Grünschnitt nötig' : 'Sonstiges'}
                            </label>
                        `).join('')}
                    </div>
                    ${(seite.zugaenglichkeit?.einschraenkungen || []).includes('sonstiges') ? `
                    <div style="display:flex;gap:6px;">
                        <input type="text" value="${seite.zugaenglichkeit?.sonstigesBeschreibung || ''}" placeholder="Sonstiges beschreiben..." style="flex:1;" onchange="setZugaenglichkeitSonstiges(${immoIdx},'${seiteKey}',this.value)">
                        <button type="button" class="btn-mic" onclick="startSpeechToText(${immoIdx},'${seiteKey}','zugaenglichkeit.sonstigesBeschreibung')" title="Spracheingabe">🎤</button>
                    </div>
                    ` : ''}
                </div>
                ` : ''}
            </div>
            
            <!-- E) SCHÄDEN/BESONDERHEITEN -->
            <div class="abfrage-item" style="background:#f8fafc;border-radius:8px;padding:12px;border-left:3px solid ${seite.schaeden?.vorhanden ? '#ef4444' : 'var(--ff-border)'};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-weight:600;font-size:13px;">E) Schäden/Besonderheiten</span>
                    <div class="ja-nein-toggle" style="display:flex;gap:4px;">
                        <button type="button" class="toggle-btn-sm ${seite.schaeden?.vorhanden === false ? 'active no' : ''}" onclick="setSchaedenVorhanden(${immoIdx},'${seiteKey}',false)">Nein</button>
                        <button type="button" class="toggle-btn-sm ${seite.schaeden?.vorhanden === true ? 'active yes' : ''}" onclick="setSchaedenVorhanden(${immoIdx},'${seiteKey}',true)">Ja</button>
                    </div>
                </div>
                
                ${seite.schaeden?.vorhanden ? `
                <!-- Schäden Untermenü -->
                <div class="submenu" style="margin-top:8px;padding:10px;background:#fff;border-radius:6px;border:1px solid #ef4444;">
                    ${SCHADEN_TYPEN.map(schaden => `
                    <div style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid var(--ff-border);">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <span style="font-size:12px;font-weight:500;">${schaden.icon} ${schaden.label}</span>
                            <div class="ja-nein-toggle" style="display:flex;gap:4px;">
                                <button type="button" class="toggle-btn-xs ${seite.schaeden?.[schaden.id]?.aktiv === true ? 'active yes' : ''}" onclick="setSchadenTyp(${immoIdx},'${seiteKey}','${schaden.id}',true)">Ja</button>
                                <button type="button" class="toggle-btn-xs ${seite.schaeden?.[schaden.id]?.aktiv === false ? 'active no' : ''}" onclick="setSchadenTyp(${immoIdx},'${seiteKey}','${schaden.id}',false)">Nein</button>
                            </div>
                        </div>
                        ${seite.schaeden?.[schaden.id]?.aktiv ? `
                        <div style="display:flex;gap:6px;margin-top:6px;">
                            <button type="button" class="btn-upload" onclick="uploadSchadenFoto(${immoIdx},'${seiteKey}','${schaden.id}')" title="Foto hochladen">📷 Foto</button>
                            <input type="text" value="${seite.schaeden?.[schaden.id]?.beschreibung || ''}" placeholder="Beschreibung..." style="flex:1;" onchange="setSchadenBeschreibung(${immoIdx},'${seiteKey}','${schaden.id}',this.value)">
                            <button type="button" class="btn-mic" onclick="startSpeechToText(${immoIdx},'${seiteKey}','schaeden.${schaden.id}.beschreibung')" title="Spracheingabe">🎤</button>
                        </div>
                        ` : ''}
                    </div>
                    `).join('')}
                    
                    <div>
                        <label style="font-size:12px;font-weight:500;display:block;margin-bottom:6px;">Weitere Besonderheiten:</label>
                        <div style="display:flex;gap:6px;">
                            <input type="text" value="${seite.schaeden?.weitereBesonderheiten || ''}" placeholder="Weitere Besonderheiten..." style="flex:1;" onchange="setWeitereSchaeden(${immoIdx},'${seiteKey}',this.value)">
                            <button type="button" class="btn-mic" onclick="startSpeechToText(${immoIdx},'${seiteKey}','schaeden.weitereBesonderheiten')" title="Spracheingabe">🎤</button>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
            
            <!-- F) 360° RUNDGANG-LINK (PRO SEITE) -->
            <div class="abfrage-item" style="background:#f8fafc;border-radius:8px;padding:12px;border-left:3px solid ${seite.rundgang360Url ? 'var(--ff-green)' : 'var(--ff-border)'};">
                <div style="font-weight:600;font-size:13px;margin-bottom:8px;">
                    F) 360° Rundgang-Link
                    ${seite.rundgang360Url ? '<span style="color:var(--ff-green);margin-left:6px;">✓</span>' : ''}
                </div>
                <input type="url" value="${seite.rundgang360Url || ''}" 
                    placeholder="https://my.matterport.com/show/?m=..." 
                    onchange="updateSeite(${immoIdx},'${seiteKey}','rundgang360Url',this.value)" 
                    style="font-family:monospace;font-size:11px;width:100%;">
                <div style="font-size:10px;color:#666;margin-top:4px;">
                    Matterport, Ricoh Tours oder ähnliche 360°-Aufnahmen dieser Seite
                </div>
            </div>
            
            <!-- G) FOTOS (PRO SEITE) -->
            <div class="abfrage-item" style="background:#f8fafc;border-radius:8px;padding:12px;border-left:3px solid ${(seite.fotos?.length > 0) ? 'var(--ff-green)' : 'var(--ff-border)'};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-weight:600;font-size:13px;">
                        G) Fotos dieser Seite
                        ${(seite.fotos?.length > 0) ? `<span style="color:var(--ff-green);margin-left:6px;">(${seite.fotos.length})</span>` : ''}
                    </span>
                    <button type="button" class="btn-upload" onclick="uploadSeiteFoto(${immoIdx},'${seiteKey}')" style="padding:4px 10px;">
                        📷 + Fotos hinzufügen
                    </button>
                </div>
                ${(seite.fotos?.length > 0) ? `
                <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
                    ${seite.fotos.map((foto, fotoIdx) => `
                        <div style="position:relative;width:60px;height:60px;border-radius:4px;overflow:hidden;border:1px solid var(--ff-border);">
                            <img src="${foto}" style="width:100%;height:100%;object-fit:cover;">
                            <button type="button" onclick="removeSeiteFoto(${immoIdx},'${seiteKey}',${fotoIdx})" 
                                style="position:absolute;top:2px;right:2px;width:16px;height:16px;border-radius:50%;background:rgba(0,0,0,0.6);color:white;border:none;font-size:10px;cursor:pointer;">×</button>
                        </div>
                    `).join('')}
                </div>
                ` : `
                <div style="font-size:11px;color:#666;text-align:center;padding:10px;">
                    Noch keine Fotos hinzugefügt
                </div>
                `}
            </div>
        </div>
    `;
}

// ============================================
// POSITIONEN RENDERING
// ============================================

// Positionen für eine spezifische Immobilie rendern
function renderPositionsForImmo(immoNummer) {
    const immoPositions = positions.filter(p => p.immoNummer === immoNummer);
    const gruppenFarben = { reinigung: '#7AB800', rabatte: '#2196F3', technik: '#FF9800', nebenkosten: '#9C27B0' };

    if (immoPositions.length === 0) {
        return `<div style="font-size:12px;color:#666;text-align:center;padding:10px;">
            Positionen werden automatisch generiert, sobald Seiten zur Reinigung ausgewählt sind.
        </div>`;
    }

    return immoPositions.map((p, idx) => {
        const globalIdx = positions.findIndex(pos => pos === p);
        const gesamt = p.menge * p.einzelpreis;
        const gesamtStr = p.bedarfsposition ? `(${formatCurrency(gesamt)})` : formatCurrency(gesamt);
        const gruppeInfo = ARTIKELGRUPPEN[p.artikelgruppe] || ARTIKELGRUPPEN.reinigung;
        const gruppeColor = gruppenFarben[p.artikelgruppe] || '#7AB800';

        return `
        <div class="position-item" style="${p.bedarfsposition ? 'border-left:3px solid #999;' : `border-left:3px solid ${gruppeColor};`}margin-bottom:8px;padding:10px;background:#fff;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="display:flex;align-items:center;gap:8px;">
                    <strong style="font-size:13px;">Pos ${p.pos}</strong>
                    <span style="font-size:10px;padding:2px 6px;border-radius:10px;background:${gruppeColor}15;color:${gruppeColor};font-weight:500;">${gruppeInfo.label}</span>
                    ${p.bedarfsposition ? '<span style="font-size:10px;color:#999;">(Bedarf)</span>' : ''}
                </span>
                <div style="display:flex;align-items:center;gap:8px;">
                    <strong style="${p.bedarfsposition ? 'color:#999;' : `color:${gruppeColor};`}">${gesamtStr}</strong>
                    <button class="position-remove" onclick="removePosition(${globalIdx})" style="width:20px;height:20px;font-size:12px;">×</button>
                </div>
            </div>
            <div style="font-size:12px;margin-bottom:6px;">${p.bezeichnung}</div>
            <div style="display:flex;gap:10px;font-size:11px;color:#666;">
                <span>${p.menge.toLocaleString('de-DE')} ${p.einheit}</span>
                <span>× ${formatCurrency(p.einzelpreis)}</span>
            </div>
        </div>
        `;
    }).join('');
}

function renderPositions() {
    const container = document.getElementById('positionsContainer');
    const gruppenFarben = { reinigung: '#7AB800', rabatte: '#2196F3', technik: '#FF9800', nebenkosten: '#9C27B0' };

    container.innerHTML = positions.map((p, i) => {
        const gesamt = p.menge * p.einzelpreis;
        const gesamtStr = p.bedarfsposition ? `(${formatCurrency(gesamt)})` : formatCurrency(gesamt);
        const gruppeInfo = ARTIKELGRUPPEN[p.artikelgruppe] || ARTIKELGRUPPEN.reinigung;
        const gruppeColor = gruppenFarben[p.artikelgruppe] || '#7AB800';

        return `
        <div class="position-item" style="${p.bedarfsposition ? 'border-left:3px solid #999;' : `border-left:3px solid ${gruppeColor};`}">
            <div class="position-header">
                <span class="position-number" style="display:flex;align-items:center;gap:8px;">
                    <strong style="font-size:14px;">Pos. ${p.pos}</strong>
                    <span style="font-size:10px;padding:2px 6px;border-radius:10px;background:${gruppeColor}15;color:${gruppeColor};font-weight:500;">${gruppeInfo.label}</span>
                    ${p.bedarfsposition ? '<span style="font-size:10px;color:#999;font-weight:normal;">(Bedarf)</span>' : ''}
                </span>
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-weight:600;${p.bedarfsposition ? 'color:#999;' : `color:${gruppeColor};`}">${gesamtStr}</span>
                    <button class="position-remove" onclick="removePosition(${i})">×</button>
                </div>
            </div>
            
            <!-- Artikel-Dropdown -->
            <div class="form-group">
                <label>Artikel aus Katalog wählen</label>
                <select onchange="selectArtikelFromKatalog(${i}, this.value)">
                    ${renderArtikelDropdown()}
                </select>
            </div>
            
            <div class="form-group">
                <label>Bezeichnung</label>
                <input type="text" value="${p.bezeichnung}" onchange="updatePos(${i},'bezeichnung',this.value)">
            </div>
            
            <div style="display:grid;grid-template-columns:80px 80px 1fr 100px;gap:10px;">
                <div class="form-group">
                    <label>Menge</label>
                    <input type="number" value="${p.menge}" onchange="updatePos(${i},'menge',parseFloat(this.value))">
                </div>
                <div class="form-group">
                    <label>Einheit</label>
                    <select onchange="updatePos(${i},'einheit',this.value)">
                        <option value="m²" ${p.einheit === 'm²' ? 'selected' : ''}>m²</option>
                        <option value="Stk" ${p.einheit === 'Stk' ? 'selected' : ''}>Stk</option>
                        <option value="Tag(e)" ${p.einheit === 'Tag(e)' ? 'selected' : ''}>Tag(e)</option>
                        <option value="Pausch." ${p.einheit === 'Pausch.' ? 'selected' : ''}>Pausch.</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Beschreibung</label>
                    <input type="text" value="${p.beschreibung.split('\\n')[0]}" onchange="updatePos(${i},'beschreibung',this.value)">
                </div>
                <div class="form-group">
                    <label>€/Einheit</label>
                    <input type="number" step="0.01" value="${p.einzelpreis}" onchange="updatePos(${i},'einzelpreis',parseFloat(this.value))">
                </div>
            </div>
            
            <label class="checkbox-label" style="margin-top:8px;">
                <input type="checkbox" ${p.bedarfsposition ? 'checked' : ''} onchange="updatePos(${i},'bedarfsposition',this.checked)">
                Bedarfsposition (optional)
            </label>
        </div>
    `}).join('');

    updatePositionStats();
}

function updatePositionStats() {
    const totals = calculateTotals();
    const bedarfsCount = positions.filter(p => p.bedarfsposition).length;

    document.getElementById('posCount').textContent = positions.length;
    document.getElementById('bedarfsCount').textContent = bedarfsCount;
    document.getElementById('posNettoSum').textContent = formatCurrency(totals.netto);

    const gruppenCounts = {
        reinigung: positions.filter(p => p.artikelgruppe === 'reinigung').length,
        rabatte: positions.filter(p => p.artikelgruppe === 'rabatte').length,
        technik: positions.filter(p => p.artikelgruppe === 'technik').length,
        nebenkosten: positions.filter(p => p.artikelgruppe === 'nebenkosten').length
    };

    document.getElementById('gruppeReinigung').textContent = gruppenCounts.reinigung;
    document.getElementById('gruppeRabatte').textContent = gruppenCounts.rabatte;
    document.getElementById('gruppeTechnik').textContent = gruppenCounts.technik;
    document.getElementById('gruppeNebenkosten').textContent = gruppenCounts.nebenkosten;
}

// ============================================
// IMMOBILIEN EVENT-HANDLER 
// ============================================
function addImmobilie() {
    const neueNummer = immobilien.length + 1;
    immobilien.push(createEmptyImmobilie(neueNummer));
    renderImmobilien();
    updatePreview();
}

function removeImmobilie(index) {
    if (immobilien.length > 1) {
        immobilien.splice(index, 1);
        immobilien.forEach((immo, i) => immo.nummer = i + 1);
        renderImmobilien();
        updatePreview();
    }
}

function updateImmobilieAdresse(immoIdx, field, value) {
    immobilien[immoIdx].adresse[field] = value;
    updatePreview();
}

function toggleAlleSeiten(immoIdx, checked) {
    immobilien[immoIdx].alleSeiten = checked;
    Object.keys(immobilien[immoIdx].seiten).forEach(key => {
        immobilien[immoIdx].seiten[key].zuReinigen = checked;
        immobilien[immoIdx].seiten[key].aktiv = checked;
    });
    renderImmobilien();
    updatePreview();
}

// NEU: Kopfdaten Event-Handler
function updateImmobilieKopfdaten(immoIdx, field, value) {
    immobilien[immoIdx][field] = value;
    updatePreview();
}

// NEU: AG-Mitarbeiter Event-Handler
function updateAGMitarbeiter(immoIdx, field, value) {
    if (!immobilien[immoIdx].agMitarbeiter) {
        immobilien[immoIdx].agMitarbeiter = { name: '', email: '', telefon: '', position: '', hubspotContactId: null };
    }
    immobilien[immoIdx].agMitarbeiter[field] = value;
    updatePreview();
}

// NEU: Pflichtabfragen Event-Handler
function setPflichtabfrage(immoIdx, field, value) {
    immobilien[immoIdx][field] = value;

    // Bei Marketing geeignet = true: E-Mail-Entwurf öffnen
    if (field === 'marketingGeeignet' && value === true) {
        console.log(`📸 Marketing-Kandidat: Immobilie ${immoIdx + 1} markiert`);

        // E-Mail-Benachrichtigung vorbereiten
        const immo = immobilien[immoIdx];
        const adresse = `${immo.adresse.strasse} ${immo.adresse.hausnummer}, ${immo.adresse.plz} ${immo.adresse.ort}`;
        const firma = document.getElementById('companyName')?.value || 'Unbekannt';

        // 48h Frist berechnen
        const frist = new Date();
        frist.setHours(frist.getHours() + 48);
        const fristStr = frist.toLocaleDateString('de-DE', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

        const subject = `📸 Marketing-Kandidat: ${adresse}`;
        const body = `Hallo Marketing-Team,

die folgende Immobilie wurde als potenzieller Marketing-Kandidat markiert:

IMMOBILIE-DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Adresse: ${adresse}
• Auftraggeber: ${firma}
• Angebotsnummer: ${document.getElementById('angebotsnummer')?.value || 'n/a'}
• Markiert von: ${document.getElementById('hubspotOwnerId')?.selectedOptions[0]?.text || 'n/a'}
• Datum: ${new Date().toLocaleDateString('de-DE')}

FRIST FÜR ABSTIMMUNG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ ${fristStr} (48h)

NÄCHSTE SCHRITTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Prüfen ob Objekt für Marketing-Material geeignet ist
2. Rücksprache mit Vertrieb halten
3. Bei Interesse: Fototermin koordinieren

Bitte bis zur Frist Rückmeldung geben.

Mit freundlichen Grüßen
FassadenFix Vertrieb`;

        // mailto-Link öffnen
        const mailtoLink = `mailto:marketing@fassadenfix.de?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

        // Frage ob E-Mail gesendet werden soll
        if (confirm('📸 Marketing-Kandidat markiert!\n\nMöchten Sie jetzt eine E-Mail an das Marketing-Team senden?\n\nFrist: 48 Stunden zur Abstimmung')) {
            window.open(mailtoLink, '_blank');
            immobilien[immoIdx].marketingAufgabeErstellt = true;
        }
    }

    // Bei Reinigung möglich = false: Warnung anzeigen
    if (field === 'reinigungMoeglich' && value === false) {
        console.log(`⛔ Reinigung nicht möglich: Immobilie ${immoIdx + 1}`);
    }

    renderImmobilien();
    updatePreview();
}

// Prüfung ob Angebotserstellung möglich ist
function canCreateOffer() {
    const immoNichtMoeglich = immobilien.filter(immo => immo.reinigungMoeglich === false);
    if (immoNichtMoeglich.length > 0) {
        return {
            possible: false,
            reason: `Reinigung nicht möglich für ${immoNichtMoeglich.length} Immobilie(n). Bitte entfernen oder ändern Sie die Markierung.`
        };
    }

    const immoUnentschieden = immobilien.filter(immo => immo.reinigungMoeglich === null);
    if (immoUnentschieden.length > 0) {
        return {
            possible: false,
            reason: `Bitte beantworten Sie "Ist Reinigung möglich?" für ${immoUnentschieden.length} Immobilie(n).`
        };
    }

    return { possible: true };
}

// NEU: Zu Reinigen Toggle (Pflichtfeld)
function setZuReinigen(immoIdx, seiteKey, value) {
    immobilien[immoIdx].seiten[seiteKey].zuReinigen = value;
    immobilien[immoIdx].seiten[seiteKey].aktiv = value;

    // Prüfe ob alle Seiten ausgewählt sind
    const alleAktiv = Object.values(immobilien[immoIdx].seiten).every(s => s.zuReinigen === true);
    immobilien[immoIdx].alleSeiten = alleAktiv;

    renderImmobilien();

    // Automatisch Positionen generieren basierend auf Seiten-Auswahl
    if (typeof generatePositionsFromImmobilien === 'function') {
        generatePositionsFromImmobilien();
    }

    updatePreview();
}

function toggleSeiteAktiv(immoIdx, seiteKey, aktiv) {
    immobilien[immoIdx].seiten[seiteKey].aktiv = aktiv;
    const alleAktiv = Object.values(immobilien[immoIdx].seiten).every(s => s.aktiv);
    immobilien[immoIdx].alleSeiten = alleAktiv;
    renderImmobilien();
    updatePreview();
}

function toggleSeiteExpand(immoIdx, seiteKey) {
    const body = document.getElementById(`seite-body-${immoIdx}-${seiteKey}`);
    if (body) body.classList.toggle('expanded');
}

function updateSeite(immoIdx, seiteKey, field, value) {
    immobilien[immoIdx].seiten[seiteKey][field] = value;
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if ((field === 'breite' || field === 'hoehe') && seite.breite && seite.hoehe) {
        seite.flaeche = Math.round(seite.breite * seite.hoehe);
    }
    renderImmobilien();
    updatePreview();
}

// MBS-Felder Event-Handler
function updateSeiteMBS(immoIdx, seiteKey, path, value) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    const parts = path.split('.');

    if (parts.length === 1) {
        // Einfaches Feld (z.B. untergrund)
        seite[parts[0]] = value;
    } else if (parts.length === 2) {
        // Verschachteltes Feld (z.B. buehne.typ)
        if (!seite[parts[0]]) seite[parts[0]] = {};
        seite[parts[0]][parts[1]] = value;
    }

    renderImmobilien();
    updatePreview();
}

function toggleHindernis(immoIdx, seiteKey, hindernisId, labelEl) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.hindernisse) seite.hindernisse = [];

    const idx = seite.hindernisse.indexOf(hindernisId);
    if (idx === -1) {
        seite.hindernisse.push(hindernisId);
        labelEl.classList.add('checked');
    } else {
        seite.hindernisse.splice(idx, 1);
        labelEl.classList.remove('checked');
    }

    updatePreview();
}

// ============================================
// ABFRAGEN EVENT-HANDLER (GEMÄSS SPEZIFIKATION)
// ============================================

// B) Bühnen-Typ
function setBuehneTyp(immoIdx, seiteKey, typ) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.buehne) seite.buehne = { typ: 'keine', tage: 1, preis: 0, sonderTyp: '' };

    seite.buehne.typ = typ;

    // Preis setzen gemäß Spezifikation
    if (typ === 'keine') {
        seite.buehne.preis = 0;
    } else if (typ === 'standard') {
        seite.buehne.preis = 390;
    } else {
        seite.buehne.preis = 'anfrage';
    }

    renderImmobilien();

    // Automatisch Positionen generieren bei Bühnen-Änderung
    if (typeof generatePositionsFromImmobilien === 'function') {
        generatePositionsFromImmobilien();
    }

    updatePreview();
}

// C) Reinigungsprodukt
function toggleReinigungsproduktZusatz(immoIdx, seiteKey, checked) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.reinigungsprodukt) {
        seite.reinigungsprodukt = { standard: true, zusaetzlichErforderlich: false, zusaetzlichProdukte: [], anwendung: 'zusaetzlich', begruendung: '' };
    }
    seite.reinigungsprodukt.zusaetzlichErforderlich = checked;
    renderImmobilien();
    updatePreview();
}

function toggleZusatzProdukt(immoIdx, seiteKey, produktId, labelEl) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.reinigungsprodukt) {
        seite.reinigungsprodukt = { standard: true, zusaetzlichErforderlich: true, zusaetzlichProdukte: [], anwendung: 'zusaetzlich', begruendung: '' };
    }
    if (!seite.reinigungsprodukt.zusaetzlichProdukte) seite.reinigungsprodukt.zusaetzlichProdukte = [];

    const idx = seite.reinigungsprodukt.zusaetzlichProdukte.indexOf(produktId);
    if (idx === -1) {
        seite.reinigungsprodukt.zusaetzlichProdukte.push(produktId);
        labelEl.classList.add('checked');
    } else {
        seite.reinigungsprodukt.zusaetzlichProdukte.splice(idx, 1);
        labelEl.classList.remove('checked');
    }
    updatePreview();
}

function setReinigungsproduktAnwendung(immoIdx, seiteKey, anwendung) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.reinigungsprodukt) {
        seite.reinigungsprodukt = { standard: true, zusaetzlichErforderlich: true, zusaetzlichProdukte: [], anwendung: 'zusaetzlich', begruendung: '' };
    }
    seite.reinigungsprodukt.anwendung = anwendung;
    renderImmobilien();
    updatePreview();
}

function setReinigungsproduktBegruendung(immoIdx, seiteKey, text) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.reinigungsprodukt) {
        seite.reinigungsprodukt = { standard: true, zusaetzlichErforderlich: true, zusaetzlichProdukte: [], anwendung: 'zusaetzlich', begruendung: '' };
    }
    seite.reinigungsprodukt.begruendung = text;
    updatePreview();
}

// D) Zugänglichkeit
function setZugaenglichkeit(immoIdx, seiteKey, typ) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.zugaenglichkeit) {
        seite.zugaenglichkeit = { typ: 'ungehindert', einschraenkungen: [], sonstigesBeschreibung: '' };
    }
    seite.zugaenglichkeit.typ = typ;
    renderImmobilien();
    updatePreview();
}

function toggleZugaenglichkeitOption(immoIdx, seiteKey, optionId, labelEl) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.zugaenglichkeit) {
        seite.zugaenglichkeit = { typ: 'eingeschraenkt', einschraenkungen: [], sonstigesBeschreibung: '' };
    }
    if (!seite.zugaenglichkeit.einschraenkungen) seite.zugaenglichkeit.einschraenkungen = [];

    const idx = seite.zugaenglichkeit.einschraenkungen.indexOf(optionId);
    if (idx === -1) {
        seite.zugaenglichkeit.einschraenkungen.push(optionId);
        labelEl.classList.add('checked');
    } else {
        seite.zugaenglichkeit.einschraenkungen.splice(idx, 1);
        labelEl.classList.remove('checked');
    }

    // Re-Render für Sonstiges-Freifeld
    if (optionId === 'sonstiges') {
        renderImmobilien();
    }
    updatePreview();
}

function setZugaenglichkeitSonstiges(immoIdx, seiteKey, text) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.zugaenglichkeit) {
        seite.zugaenglichkeit = { typ: 'eingeschraenkt', einschraenkungen: ['sonstiges'], sonstigesBeschreibung: '' };
    }
    seite.zugaenglichkeit.sonstigesBeschreibung = text;
    updatePreview();
}

// E) Schäden/Besonderheiten
function setSchaedenVorhanden(immoIdx, seiteKey, vorhanden) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.schaeden) {
        seite.schaeden = {
            vorhanden: false,
            graffiti: { aktiv: false, beschreibung: '', fotos: [] },
            loecher: { aktiv: false, beschreibung: '', fotos: [] },
            risse: { aktiv: false, beschreibung: '', fotos: [] },
            weitereBesonderheiten: ''
        };
    }
    seite.schaeden.vorhanden = vorhanden;
    renderImmobilien();
    updatePreview();
}

function setSchadenTyp(immoIdx, seiteKey, schadensTyp, aktiv) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.schaeden) {
        seite.schaeden = { vorhanden: true, graffiti: { aktiv: false, beschreibung: '', fotos: [] }, loecher: { aktiv: false, beschreibung: '', fotos: [] }, risse: { aktiv: false, beschreibung: '', fotos: [] }, weitereBesonderheiten: '' };
    }
    if (!seite.schaeden[schadensTyp]) {
        seite.schaeden[schadensTyp] = { aktiv: false, beschreibung: '', fotos: [] };
    }
    seite.schaeden[schadensTyp].aktiv = aktiv;
    renderImmobilien();
    updatePreview();
}

function setSchadenBeschreibung(immoIdx, seiteKey, schadensTyp, text) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.schaeden || !seite.schaeden[schadensTyp]) return;
    seite.schaeden[schadensTyp].beschreibung = text;
    updatePreview();
}

function setWeitereSchaeden(immoIdx, seiteKey, text) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (!seite.schaeden) {
        seite.schaeden = { vorhanden: true, weitereBesonderheiten: '' };
    }
    seite.schaeden.weitereBesonderheiten = text;
    updatePreview();
}

// Foto-Upload mit File-Input und Base64-Speicherung
function uploadSchadenFoto(immoIdx, seiteKey, schadensTyp) {
    // Erstelle versteckten File-Input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.multiple = true;
    fileInput.style.display = 'none';

    fileInput.onchange = async (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        const seite = immobilien[immoIdx].seiten[seiteKey];
        if (!seite.schaeden) {
            seite.schaeden = { vorhanden: true, [schadensTyp]: { aktiv: true, beschreibung: '', fotos: [] } };
        }
        if (!seite.schaeden[schadensTyp]) {
            seite.schaeden[schadensTyp] = { aktiv: true, beschreibung: '', fotos: [] };
        }
        if (!seite.schaeden[schadensTyp].fotos) {
            seite.schaeden[schadensTyp].fotos = [];
        }

        // Konvertiere Bilder zu Base64
        for (const file of files) {
            try {
                const base64 = await fileToBase64(file);
                seite.schaeden[schadensTyp].fotos.push({
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    data: base64,
                    uploadedAt: new Date().toISOString()
                });
            } catch (err) {
                console.error('Fehler beim Konvertieren des Fotos:', err);
            }
        }

        // UI aktualisieren
        renderImmobilien();
        updatePreview();

        console.log(`${files.length} Foto(s) hochgeladen für ${SEITEN_TYPEN[seiteKey].label} - ${schadensTyp}`);
    };

    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
}

// Hilfsfunktion: File zu Base64 konvertieren
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

// ============================================
// SEITEN-FOTOS (Pro Seite, nicht pro Schaden)
// ============================================
function uploadSeiteFoto(immoIdx, seiteKey) {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.multiple = true;
    fileInput.style.display = 'none';

    fileInput.onchange = async (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        const seite = immobilien[immoIdx].seiten[seiteKey];
        if (!seite.fotos) {
            seite.fotos = [];
        }

        // Konvertiere Bilder zu Base64
        for (const file of files) {
            try {
                const base64 = await fileToBase64(file);
                seite.fotos.push(base64);
            } catch (err) {
                console.error('Fehler beim Konvertieren des Fotos:', err);
            }
        }

        // UI aktualisieren
        renderImmobilien();
        updatePreview();

        console.log(`${files.length} Foto(s) für ${SEITEN_TYPEN[seiteKey].label} hochgeladen`);
    };

    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
}

function removeSeiteFoto(immoIdx, seiteKey, fotoIdx) {
    const seite = immobilien[immoIdx].seiten[seiteKey];
    if (seite.fotos && seite.fotos[fotoIdx]) {
        seite.fotos.splice(fotoIdx, 1);
        renderImmobilien();
        updatePreview();
    }
}

// Speech-to-Text mit Web Speech API + AI-Optimierung
let currentRecognition = null;

function startSpeechToText(immoIdx, seiteKey, fieldPath) {
    // Prüfe ob Web Speech API verfügbar ist
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert('Spracheingabe wird von Ihrem Browser nicht unterstützt.\\n\\nBitte verwenden Sie Chrome, Edge oder Safari.');
        return;
    }

    // Falls bereits eine Aufnahme läuft, stoppen
    if (currentRecognition) {
        currentRecognition.stop();
        currentRecognition = null;
        return;
    }

    // Finde den Mikrofon-Button und das zugehörige Input-Feld
    const micButtons = document.querySelectorAll('.btn-mic');
    let targetButton = null;
    let targetInput = null;

    // Suche den richtigen Button basierend auf onclick-Attribut
    micButtons.forEach(btn => {
        if (btn.onclick && btn.onclick.toString().includes(`'${fieldPath}'`)) {
            targetButton = btn;
            // Input ist das vorherige Geschwister-Element
            targetInput = btn.previousElementSibling;
        }
    });

    if (!targetButton) {
        console.error('Mikrofon-Button nicht gefunden für:', fieldPath);
        return;
    }

    // Feldtyp für AI-Optimierung bestimmen
    let fieldType = 'default';
    if (fieldPath.includes('schaeden')) fieldType = 'schadensbeschreibung';
    else if (fieldPath.includes('zugaenglichkeit')) fieldType = 'zugaenglichkeit';
    else if (fieldPath.includes('reinigungsprodukt')) fieldType = 'reinigungsprodukt';
    else if (fieldPath.includes('besonderheiten')) fieldType = 'besonderheiten';

    // Starte Spracherkennung
    currentRecognition = new SpeechRecognition();
    currentRecognition.lang = 'de-DE';
    currentRecognition.continuous = false;
    currentRecognition.interimResults = true;
    currentRecognition.maxAlternatives = 1;

    // Visuelles Feedback
    targetButton.classList.add('recording');
    targetButton.innerHTML = '🔴';

    currentRecognition.onresult = async (event) => {
        const result = event.results[0];
        const transcript = result[0].transcript;

        if (targetInput) {
            // Zeige Rohtext während der Aufnahme
            targetInput.value = transcript;
            targetInput.style.opacity = '0.7';

            // Wenn final, AI-Optimierung anwenden
            if (result.isFinal) {
                targetInput.value = transcript + ' ⏳';
                targetInput.style.opacity = '0.5';

                try {
                    // AI-Optimierung via Backend
                    const optimizedText = await optimizeTextWithAI(transcript, fieldType);
                    targetInput.value = optimizedText;
                    targetInput.style.opacity = '1';

                    // Visuelles Feedback für AI-Optimierung
                    if (optimizedText !== transcript) {
                        targetInput.style.backgroundColor = '#f0fdf4';
                        setTimeout(() => {
                            targetInput.style.backgroundColor = '';
                        }, 2000);
                    }
                } catch (e) {
                    // Fallback: Original-Text
                    targetInput.value = transcript;
                    targetInput.style.opacity = '1';
                }

                // Trigger onchange Event
                targetInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    };

    currentRecognition.onerror = (event) => {
        console.error('Spracherkennungsfehler:', event.error);

        let errorMsg = 'Spracherkennung fehlgeschlagen.';
        switch (event.error) {
            case 'no-speech':
                errorMsg = 'Keine Sprache erkannt. Bitte sprechen Sie deutlicher.';
                break;
            case 'audio-capture':
                errorMsg = 'Kein Mikrofon gefunden. Bitte überprüfen Sie Ihre Mikrofoneinstellungen.';
                break;
            case 'not-allowed':
                errorMsg = 'Mikrofonzugriff verweigert. Bitte erlauben Sie den Zugriff in Ihren Browsereinstellungen.';
                break;
        }

        alert(errorMsg);

        // Aufräumen
        targetButton.classList.remove('recording');
        targetButton.innerHTML = '🎤';
        if (targetInput) targetInput.style.opacity = '1';
        currentRecognition = null;
    };

    currentRecognition.onend = () => {
        targetButton.classList.remove('recording');
        targetButton.innerHTML = '🎤';
        currentRecognition = null;
    };

    // Aufnahme starten
    try {
        currentRecognition.start();
    } catch (e) {
        console.error('Konnte Spracherkennung nicht starten:', e);
        targetButton.classList.remove('recording');
        targetButton.innerHTML = '🎤';
        currentRecognition = null;
    }
}

// ============================================
// POSITIONEN EVENT-HANDLER
// ============================================
function updatePos(i, field, value) {
    positions[i][field] = value;
    renderPositions();
    updatePreview();
}

function removePosition(i) {
    positions.splice(i, 1);
    regenerateAllPosNummern();
    renderPositions();
    updatePreview();
}

function addPosition() {
    const immoNummer = immobilien.length > 0 ? immobilien[0].nummer : 1;
    const artikelgruppe = 'reinigung';
    const nextPosNr = getNextPosNummerInGruppe(immoNummer, artikelgruppe);

    positions.push({
        pos: nextPosNr, immoNummer: immoNummer, artikelgruppe: artikelgruppe,
        menge: 1, einheit: 'm²', bezeichnung: 'Neue Position',
        beschreibung: '', einzelpreis: 0, bedarfsposition: false
    });
    renderPositions();
    updatePreview();
}

function getNextPosNummerInGruppe(immoNummer, artikelgruppe) {
    const gruppe = ARTIKELGRUPPEN[artikelgruppe];
    const existingInGruppe = positions.filter(p => p.immoNummer === immoNummer && p.artikelgruppe === artikelgruppe);
    const usedNumbers = existingInGruppe.map(p => parseInt(p.pos.split('.')[1]) || 0);

    let nextNum = gruppe.range[0];
    while (usedNumbers.includes(nextNum) && nextNum <= gruppe.range[1]) nextNum++;
    if (nextNum > gruppe.range[1]) nextNum = Math.max(...usedNumbers) + 1;

    return `${immoNummer}.${String(nextNum).padStart(2, '0')}`;
}

function regenerateAllPosNummern() {
    const groups = {};
    positions.forEach((p, idx) => {
        const key = `${p.immoNummer}-${p.artikelgruppe}`;
        if (!groups[key]) groups[key] = [];
        groups[key].push({ idx, pos: p });
    });

    Object.entries(groups).forEach(([key, items]) => {
        const [immoStr, artikelgruppe] = key.split('-');
        const immoNummer = parseInt(immoStr);
        const gruppe = ARTIKELGRUPPEN[artikelgruppe];

        items.forEach((item, i) => {
            const artikelNr = gruppe.range[0] + i;
            positions[item.idx].pos = `${immoNummer}.${String(artikelNr).padStart(2, '0')}`;
        });
    });
}
