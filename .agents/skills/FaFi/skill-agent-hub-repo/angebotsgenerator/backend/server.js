// ============================================
// FASSADENFIX BACKEND SERVER
// HubSpot API Proxy & AI Textoptimierung
// ============================================

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const hubspot = require('@hubspot/api-client');
const OpenAI = require('openai');

const app = express();
const PORT = process.env.PORT || 3001;

// === MIDDLEWARE ===
app.use(cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:8888',
    credentials: true
}));
app.use(express.json());

// === HUBSPOT CLIENT ===
let hubspotClient = null;

function getHubSpotClient() {
    if (!hubspotClient && process.env.HUBSPOT_ACCESS_TOKEN) {
        hubspotClient = new hubspot.Client({
            accessToken: process.env.HUBSPOT_ACCESS_TOKEN
        });
    }
    return hubspotClient;
}

// === OPENAI CLIENT ===
let openaiClient = null;

function getOpenAIClient() {
    if (!openaiClient && process.env.OPENAI_API_KEY) {
        openaiClient = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY
        });
    }
    return openaiClient;
}

// ============================================
// HUBSPOT API ROUTES
// ============================================

// Suche nach Companies
app.get('/api/hubspot/companies/search', async (req, res) => {
    try {
        const { query } = req.query;
        const client = getHubSpotClient();

        if (!client) {
            return res.status(503).json({
                error: 'HubSpot nicht konfiguriert',
                mock: true,
                results: getMockCompanies(query)
            });
        }

        const searchResponse = await client.crm.companies.searchApi.doSearch({
            query: query,
            limit: 10,
            properties: ['name', 'city', 'address', 'zip', 'phone', 'domain', 'hs_object_id']
        });

        const companies = searchResponse.results.map(company => ({
            id: company.id,
            name: company.properties.name,
            city: company.properties.city,
            address: company.properties.address,
            zip: company.properties.zip,
            phone: company.properties.phone,
            domain: company.properties.domain
        }));

        res.json({ results: companies, mock: false });
    } catch (error) {
        console.error('HubSpot Company Search Error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Hole Company Details
app.get('/api/hubspot/companies/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const client = getHubSpotClient();

        if (!client) {
            return res.status(503).json({ error: 'HubSpot nicht konfiguriert' });
        }

        const company = await client.crm.companies.basicApi.getById(id, [
            'name', 'city', 'address', 'zip', 'phone', 'domain',
            'kundennummer', 'customer_id', 'hs_object_id'
        ]);

        res.json(company.properties);
    } catch (error) {
        console.error('HubSpot Company Get Error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Suche nach Contacts
app.get('/api/hubspot/contacts/search', async (req, res) => {
    try {
        const { query, companyId } = req.query;
        const client = getHubSpotClient();

        if (!client) {
            return res.status(503).json({
                error: 'HubSpot nicht konfiguriert',
                mock: true,
                results: getMockContacts(query)
            });
        }

        let searchRequest = {
            query: query || '',
            limit: 20,
            properties: ['firstname', 'lastname', 'email', 'phone', 'mobilephone', 'jobtitle', 'salutation']
        };

        // Wenn companyId angegeben, nur assoziierte Contacts
        if (companyId) {
            searchRequest.filterGroups = [{
                filters: [{
                    propertyName: 'associatedcompanyid',
                    operator: 'EQ',
                    value: companyId
                }]
            }];
        }

        const searchResponse = await client.crm.contacts.searchApi.doSearch(searchRequest);

        const contacts = searchResponse.results.map(contact => ({
            id: contact.id,
            firstname: contact.properties.firstname,
            lastname: contact.properties.lastname,
            email: contact.properties.email,
            phone: contact.properties.phone,
            mobile: contact.properties.mobilephone,
            jobtitle: contact.properties.jobtitle,
            salutation: contact.properties.salutation
        }));

        res.json({ results: contacts, mock: false });
    } catch (error) {
        console.error('HubSpot Contact Search Error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Hole assoziierte Contacts für eine Company
app.get('/api/hubspot/companies/:id/contacts', async (req, res) => {
    try {
        const { id } = req.params;
        const client = getHubSpotClient();

        if (!client) {
            return res.status(503).json({ error: 'HubSpot nicht konfiguriert' });
        }

        const associations = await client.crm.companies.associationsApi.getAll(
            id, 'contacts'
        );

        if (associations.results.length === 0) {
            return res.json({ results: [] });
        }

        const contactIds = associations.results.map(a => a.id);

        const batchRead = await client.crm.contacts.batchApi.read({
            inputs: contactIds.map(id => ({ id })),
            properties: ['firstname', 'lastname', 'email', 'phone', 'mobilephone', 'jobtitle', 'salutation']
        });

        const contacts = batchRead.results.map(contact => ({
            id: contact.id,
            firstname: contact.properties.firstname,
            lastname: contact.properties.lastname,
            email: contact.properties.email,
            phone: contact.properties.phone,
            mobile: contact.properties.mobilephone,
            jobtitle: contact.properties.jobtitle,
            salutation: contact.properties.salutation
        }));

        res.json({ results: contacts });
    } catch (error) {
        console.error('HubSpot Associations Error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Hole Deals für eine Company
app.get('/api/hubspot/companies/:id/deals', async (req, res) => {
    try {
        const { id } = req.params;
        const client = getHubSpotClient();

        if (!client) {
            return res.status(503).json({ error: 'HubSpot nicht konfiguriert' });
        }

        const associations = await client.crm.companies.associationsApi.getAll(
            id, 'deals'
        );

        if (associations.results.length === 0) {
            return res.json({ results: [] });
        }

        const dealIds = associations.results.map(a => a.id);

        const batchRead = await client.crm.deals.batchApi.read({
            inputs: dealIds.map(id => ({ id })),
            properties: ['dealname', 'amount', 'dealstage', 'pipeline', 'hubspot_owner_id', 'closedate']
        });

        const deals = batchRead.results.map(deal => ({
            id: deal.id,
            name: deal.properties.dealname,
            amount: deal.properties.amount,
            stage: deal.properties.dealstage,
            pipeline: deal.properties.pipeline,
            ownerId: deal.properties.hubspot_owner_id,
            closeDate: deal.properties.closedate
        }));

        res.json({ results: deals });
    } catch (error) {
        console.error('HubSpot Deals Error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Hole HubSpot Owners (Mitarbeiter)
app.get('/api/hubspot/owners', async (req, res) => {
    try {
        const client = getHubSpotClient();

        if (!client) {
            return res.status(503).json({
                error: 'HubSpot nicht konfiguriert',
                mock: true,
                results: getMockOwners()
            });
        }

        const ownersResponse = await client.crm.owners.ownersApi.getPage();

        const owners = ownersResponse.results.map(owner => ({
            id: owner.id,
            email: owner.email,
            firstName: owner.firstName,
            lastName: owner.lastName,
            name: `${owner.firstName} ${owner.lastName}`.trim()
        }));

        res.json({ results: owners, mock: false });
    } catch (error) {
        console.error('HubSpot Owners Error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// ============================================
// AI TEXTOPTIMIERUNG ROUTES
// ============================================

app.post('/api/ai/optimize-text', async (req, res) => {
    try {
        const { text, context, fieldType } = req.body;
        const client = getOpenAIClient();

        if (!client) {
            return res.status(503).json({
                error: 'OpenAI nicht konfiguriert',
                optimizedText: text // Fallback: Original-Text
            });
        }

        const contextPrompts = {
            'schadensbeschreibung': 'Du optimierst Schadensbeschreibungen für Fassadenreinigungsangebote.',
            'zugaenglichkeit': 'Du optimierst Beschreibungen zur Baustellen-Zugänglichkeit.',
            'reinigungsprodukt': 'Du optimierst Begründungen für spezielle Reinigungsprodukte.',
            'besonderheiten': 'Du optimierst allgemeine Besonderheiten zu Gebäudefassaden.',
            'default': 'Du optimierst technische Beschreibungen für professionelle Angebote.'
        };

        const systemPrompt = `${contextPrompts[fieldType] || contextPrompts.default}

Deine Aufgabe:
1. Entferne Füllwörter (ähm, also, halt, so'n bisschen, etc.)
2. Formuliere klar, präzise und professionell
3. Behalte alle fachlichen Details
4. Verwende technisch korrekte Begriffe
5. Maximal 2-3 Sätze
6. Antworte NUR mit dem optimierten Text, keine Erklärungen`;

        const completion = await client.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: `Optimiere diesen Text:\n\n"${text}"` }
            ],
            temperature: 0.3,
            max_tokens: 200
        });

        const optimizedText = completion.choices[0].message.content.trim();

        res.json({
            originalText: text,
            optimizedText: optimizedText,
            tokensUsed: completion.usage?.total_tokens || 0
        });
    } catch (error) {
        console.error('OpenAI Error:', error.message);
        res.status(500).json({
            error: error.message,
            optimizedText: req.body.text // Fallback
        });
    }
});

// ============================================
// MOCK DATA (für Entwicklung ohne API-Keys)
// ============================================

function getMockCompanies(query) {
    const mockData = [
        { id: '12345', name: 'Nibelungen-Wohnbau GmbH', city: 'Braunschweig', address: 'Freyastraße 10', zip: '38106' },
        { id: '12346', name: 'Stadtwerke Halle GmbH', city: 'Halle (Saale)', address: 'Bornknechtstraße 5', zip: '06108' },
        { id: '12347', name: 'WBG Wohnungsbaugesellschaft mbH', city: 'Leipzig', address: 'Musterweg 42', zip: '04109' },
        { id: '12348', name: 'Gewobau Erlangen', city: 'Erlangen', address: 'Schuhstraße 40', zip: '91052' },
        { id: '12349', name: 'GEWOBA AG Wohnen und Bauen', city: 'Bremen', address: 'Rembertiring 27', zip: '28195' }
    ];

    if (!query) return mockData;
    return mockData.filter(c => c.name.toLowerCase().includes(query.toLowerCase()));
}

function getMockContacts(query) {
    const mockData = [
        { id: '111', firstname: 'Michael', lastname: 'Hertstein', email: 'm.hertstein@nibelungen.de', jobtitle: 'Technischer Leiter', salutation: 'Herr' },
        { id: '112', firstname: 'Sabine', lastname: 'Müller', email: 's.mueller@nibelungen.de', jobtitle: 'Facility Managerin', salutation: 'Frau' },
        { id: '113', firstname: 'Thomas', lastname: 'Schmidt', email: 't.schmidt@stadtwerke.de', jobtitle: 'Objektbetreuer', salutation: 'Herr' }
    ];

    if (!query) return mockData;
    const q = query.toLowerCase();
    return mockData.filter(c =>
        c.firstname.toLowerCase().includes(q) ||
        c.lastname.toLowerCase().includes(q) ||
        c.email.toLowerCase().includes(q)
    );
}

function getMockOwners() {
    return [
        { id: '753843912', name: 'Sebastian Siebenhühner', email: 's.siebenhuehner@fassadenfix.de' },
        { id: '522379976', name: 'Alexander Retzlaff', email: 'a.retzlaff@fassadenfix.de' },
        { id: '1178553498', name: 'Rocco Seitz', email: 'r.seitz@fassadenfix.de' },
        { id: '753849449', name: 'Matthias Breier', email: 'm.breier@fassadenfix.de' }
    ];
}

// ============================================
// HEALTH CHECK & STATUS
// ============================================

app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        hubspot: !!process.env.HUBSPOT_ACCESS_TOKEN,
        openai: !!process.env.OPENAI_API_KEY
    });
});

app.get('/api/status', (req, res) => {
    res.json({
        hubspot: {
            configured: !!process.env.HUBSPOT_ACCESS_TOKEN,
            portalId: process.env.HUBSPOT_PORTAL_ID || null
        },
        openai: {
            configured: !!process.env.OPENAI_API_KEY
        },
        environment: process.env.NODE_ENV || 'development'
    });
});

// ============================================
// SERVER START
// ============================================

app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════╗
║       FASSADENFIX BACKEND SERVER                      ║
╠═══════════════════════════════════════════════════════╣
║  Server läuft auf: http://localhost:${PORT}              ║
║                                                       ║
║  Status:                                              ║
║  - HubSpot: ${process.env.HUBSPOT_ACCESS_TOKEN ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}                       ║
║  - OpenAI:  ${process.env.OPENAI_API_KEY ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}                       ║
║                                                       ║
║  API Endpoints:                                       ║
║  GET  /api/health                                     ║
║  GET  /api/hubspot/companies/search?query=...         ║
║  GET  /api/hubspot/contacts/search?query=...          ║
║  GET  /api/hubspot/owners                             ║
║  POST /api/ai/optimize-text                           ║
╚═══════════════════════════════════════════════════════╝
    `);
});
