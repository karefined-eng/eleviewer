// ============================================
// FASSADENFIX ANGEBOTSGENERATOR - HUBSPOT.JS
// HubSpot-Suche und Synchronisation via Backend
// ============================================

// Backend API URL - dynamisch basierend auf Environment
// Bei GitHub Pages: Render.com Backend verwenden
// Lokal: localhost:3001
const isProduction = window.location.hostname.includes('github.io') ||
    window.location.hostname.includes('fassadenfix');
const API_BASE_URL = isProduction
    ? 'https://fassadenfix-backend.onrender.com/api'  // Render.com Backend
    : 'http://localhost:3001/api';  // Lokale Entwicklung

// ============================================
// COMPANY SUCHE (via Backend)
// ============================================
let searchTimeout;

async function searchCompanies(query) {
    clearTimeout(searchTimeout);
    const resultsDiv = document.getElementById('companyResults');

    if (query.length < 2) {
        resultsDiv.classList.remove('active');
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/hubspot/companies/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();

            const companies = data.results || [];

            resultsDiv.innerHTML = companies.map(c => `
                <div class="search-result-item" onclick="selectCompany(${JSON.stringify(c).replace(/"/g, '&quot;')})">
                    <div class="search-result-name">${c.name}</div>
                    <div class="search-result-info">${c.address || ''} ${c.zip || ''} ${c.city || ''}</div>
                    ${data.mock ? '<span style="font-size:9px;color:#f59e0b;">(Demo-Daten)</span>' : ''}
                </div>
            `).join('');

            resultsDiv.innerHTML += `
                <div class="search-result-item search-result-new" onclick="createNewCompany('${query.replace(/'/g, "\\'")}')">
                    <div class="search-result-name">+ Neues Unternehmen anlegen</div>
                    <div class="search-result-info">"${query}" als neues Unternehmen erfassen</div>
                </div>
            `;

            resultsDiv.classList.add('active');
        } catch (error) {
            console.error('Company Search Error:', error);
            resultsDiv.innerHTML = `
                <div class="search-result-item" style="color:#ef4444;">
                    ⚠️ Backend nicht erreichbar. Bitte Backend starten: <code>npm start</code>
                </div>
            `;
            resultsDiv.classList.add('active');
        }
    }, 300);
}

function selectCompany(company) {
    selectedCompany = company;
    document.getElementById('hubspotCompanyId').value = company.id;
    document.getElementById('companyName').value = company.name || '';

    // Adresse parsen (falls als einzelnes Feld)
    if (company.address) {
        const addressParts = company.address.match(/^(.+?)\s+(\d+.*)$/) || [null, company.address, ''];
        document.getElementById('companyStreet').value = addressParts[1] || company.address;
        document.getElementById('companyStreetNumber').value = addressParts[2] || '';
    }

    document.getElementById('companyZip').value = company.zip || '';
    document.getElementById('companyCity').value = company.city || '';
    document.getElementById('companyPhone').value = company.phone || '';
    document.getElementById('companyEmail').value = company.email || company.domain ? `info@${company.domain}` : '';

    document.getElementById('companySearch').value = company.name;
    document.getElementById('companyResults').classList.remove('active');

    // Kundennummer aus Company-ID ableiten (kann später durch echtes Feld ersetzt werden)
    if (company.id) {
        document.getElementById('kundennummer').value = company.id;
    }

    loadCompanyContacts(company.id);
    updatePreview();
}

function createNewCompany(name) {
    document.getElementById('hubspotCompanyId').value = '';
    document.getElementById('companyName').value = name;
    document.getElementById('companyStreet').value = '';
    document.getElementById('companyStreetNumber').value = '';
    document.getElementById('companyZip').value = '';
    document.getElementById('companyCity').value = '';
    document.getElementById('companySearch').value = name;
    document.getElementById('companyResults').classList.remove('active');
    document.getElementById('contactSelect').innerHTML = '<option value="">-- Kontakt wählen oder neu anlegen --</option>';
    updatePreview();
}

// ============================================
// KONTAKTE LADEN (via Backend)
// ============================================
async function loadCompanyContacts(companyId) {
    const selectEl = document.getElementById('contactSelect');
    selectEl.innerHTML = '<option value="">Lade Kontakte...</option>';

    try {
        const response = await fetch(`${API_BASE_URL}/hubspot/companies/${companyId}/contacts`);
        const data = await response.json();

        const contacts = data.results || [];

        selectEl.innerHTML = '<option value="">-- Kontakt wählen oder neu anlegen --</option>';
        contacts.forEach(c => {
            const displayName = `${c.salutation || ''} ${c.firstname || ''} ${c.lastname || ''} (${c.jobtitle || 'keine Position'})`.trim();
            selectEl.innerHTML += `<option value='${JSON.stringify(c).replace(/'/g, "&#39;")}'>${displayName}</option>`;
        });
        selectEl.innerHTML += '<option value="new">+ Neuen Kontakt anlegen</option>';
    } catch (error) {
        console.error('Load Contacts Error:', error);
        selectEl.innerHTML = '<option value="">⚠️ Kontakte konnten nicht geladen werden</option>';
    }
}

async function searchContacts(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/hubspot/contacts/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        return data.results || [];
    } catch (error) {
        console.error('Contact Search Error:', error);
        return [];
    }
}

function selectContact(value) {
    if (!value) return;

    if (value === 'new') {
        document.getElementById('hubspotContactId').value = '';
        document.getElementById('contactSalutation').value = '';
        document.getElementById('contactFirstname').value = '';
        document.getElementById('contactLastname').value = '';
        document.getElementById('contactJobtitle').value = '';
        document.getElementById('contactEmail').value = '';
        document.getElementById('contactPhone').value = '';
        document.getElementById('contactMobile').value = '';
    } else {
        const contact = JSON.parse(value);
        selectedContact = contact;
        document.getElementById('hubspotContactId').value = contact.id;
        document.getElementById('contactSalutation').value = contact.salutation || '';
        document.getElementById('contactFirstname').value = contact.firstname || '';
        document.getElementById('contactLastname').value = contact.lastname || '';
        document.getElementById('contactJobtitle').value = contact.jobtitle || '';
        document.getElementById('contactEmail').value = contact.email || '';
        document.getElementById('contactPhone').value = contact.phone || '';
        document.getElementById('contactMobile').value = contact.mobile || '';
    }
    updatePreview();
}

// ============================================
// OWNER/MITARBEITER LADEN (via Backend)
// ============================================
async function loadOwners() {
    try {
        const response = await fetch(`${API_BASE_URL}/hubspot/owners`);
        const data = await response.json();

        const owners = data.results || [];
        const selectEl = document.getElementById('hubspotOwnerId');

        if (selectEl && owners.length > 0) {
            selectEl.innerHTML = owners.map(owner =>
                `<option value="${owner.id}|${owner.name}|${owner.email}|">${owner.name}</option>`
            ).join('');
        }

        // Auch für Immobilien-Dropdown
        window.hubspotOwners = {};
        owners.forEach(owner => {
            window.hubspotOwners[owner.id] = { name: owner.name, email: owner.email };
        });

    } catch (error) {
        console.error('Load Owners Error:', error);
    }
}

function updateOwnerDetails() {
    const select = document.getElementById('hubspotOwnerId');
    const parts = select.value.split('|');
    if (parts.length >= 2) {
        selectedOwner = { id: parts[0], name: parts[1], email: parts[2] || '', phone: parts[3] || '' };
    }
    updatePreview();
}

// ============================================
// AI TEXT-OPTIMIERUNG (via Backend)
// ============================================
async function optimizeTextWithAI(text, fieldType = 'default') {
    try {
        const response = await fetch(`${API_BASE_URL}/ai/optimize-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, fieldType })
        });

        const data = await response.json();
        return data.optimizedText || text;
    } catch (error) {
        console.error('AI Optimize Error:', error);
        return text; // Fallback: Original-Text
    }
}

// ============================================
// HUBSPOT SYNC (Simuliert - TODO: Echte Implementation)
// ============================================
function syncToHubspot() {
    const modal = document.getElementById('hubspotModal');
    const msg = document.getElementById('modalMessage');
    modal.classList.add('active');

    const totals = calculateTotals();
    const companyName = document.getElementById('companyName').value;
    const angNr = document.getElementById('angebotsnummer').value;

    msg.innerHTML = `
        <div style="text-align:center;padding:15px;">
            <div style="font-size:40px;color:#7AB800;margin-bottom:10px;">✓</div>
            <strong style="color:#7AB800;font-size:16px;">Synchronisation erfolgreich!</strong>
        </div>
        <div style="background:#f5f5f5;border-radius:6px;padding:15px;margin-top:15px;">
            <div style="font-weight:600;">Company: ${companyName}</div>
            <div style="font-weight:600;">Deal: Angebot ${angNr}</div>
            <div style="font-weight:600;color:#7AB800;">Summe: ${formatCurrency(totals.brutto)}</div>
        </div>
        <div style="margin-top:15px;padding:10px;background:#e8f5e9;border-radius:4px;font-size:11px;color:#2e7d32;">
            ✓ ${positions.length} Positionen synchronisiert<br>
            ✓ ${immobilien.length} Immobilie(n) verknüpft
        </div>
    `;
}

function closeModal() {
    document.getElementById('hubspotModal').classList.remove('active');
}

// ============================================
// INITIALISIERUNG
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Owners beim Start laden
    loadOwners();

    // Backend-Status prüfen
    fetch(`${API_BASE_URL}/health`)
        .then(res => res.json())
        .then(data => {
            console.log('Backend Status:', data);
            if (!data.hubspot) {
                console.warn('⚠️ HubSpot nicht konfiguriert - Mock-Modus aktiv');
            }
            if (!data.openai) {
                console.warn('⚠️ OpenAI nicht konfiguriert - Textoptimierung deaktiviert');
            }
        })
        .catch(err => {
            console.error('❌ Backend nicht erreichbar:', err.message);
        });
});
