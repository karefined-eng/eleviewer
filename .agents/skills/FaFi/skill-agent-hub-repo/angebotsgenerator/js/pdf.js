// ============================================
// FASSADENFIX ANGEBOTSGENERATOR - PDF.JS
// PDF-Export mit jsPDF - Exakt wie Original ANG-2644
// ============================================

const GREEN = [122, 184, 0];
const GREEN_LIGHT = [143, 194, 27];
const DARK = [26, 26, 26];
const GRAY = [90, 90, 90];
const GRAY_LIGHT = [156, 163, 175];

// Variable zum Speichern des geladenen Logos
let cachedLogoImage = null;

// Logo beim Start laden
async function loadLogoForPDF() {
    try {
        const response = await fetch('assets/logo.png');
        const blob = await response.blob();
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                cachedLogoImage = reader.result;
                resolve(reader.result);
            };
            reader.readAsDataURL(blob);
        });
    } catch (e) {
        console.warn('Logo konnte nicht geladen werden:', e);
        return null;
    }
}

// Logo beim Seitenstart vorladen
document.addEventListener('DOMContentLoaded', () => {
    loadLogoForPDF();
});

async function generatePDF() {
    // Validierung: Ist Angebotserstellung möglich?
    if (typeof canCreateOffer === 'function') {
        const check = canCreateOffer();
        if (!check.possible) {
            alert('⛔ PDF-Export nicht möglich:\n\n' + check.reason);
            return;
        }
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    const margin = 20;
    const pageW = 210;
    const pageH = 297;
    const contentW = pageW - 2 * margin;
    const sidebarX = pageW - margin - 28;

    // Logo laden falls noch nicht gecached
    if (!cachedLogoImage) {
        await loadLogoForPDF();
    }

    // Daten sammeln
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
        ansprechpartner: fullContact,
        strasse: fullStreet,
        plz: document.getElementById('companyZip').value,
        ort: document.getElementById('companyCity').value,
        angNr: document.getElementById('angebotsnummer').value,
        kundNr: document.getElementById('kundennummer').value,
        datum: formatDate(document.getElementById('angebotsdatum').value),
        immobilien: immobilien
    };

    const ff = [ownerParts[1] || '', ownerParts[2] || '', ownerParts[3] || ''];
    const totals = calculateTotals();

    // === SEITE 1 HEADER ===
    drawHeader(doc, margin, pageW, data, ff, cachedLogoImage);

    // === IMMOBILIEN ===
    let y = 102;
    data.immobilien.forEach((immo, idx) => {
        const adresse = getFormattedAdresse(immo);
        const aktivSeiten = Object.entries(immo.seiten)
            .filter(([k, s]) => s.aktiv)
            .map(([k, s]) => ({ key: k, ...s, label: SEITEN_TYPEN[k].label }));
        const gesamtFlaeche = aktivSeiten.reduce((sum, s) => sum + (s.flaeche || 0), 0);
        const seitenBeschreibung = aktivSeiten.map(s => s.label).join(', ');

        if (idx > 0) {
            doc.setDrawColor(200, 200, 200);
            doc.line(margin, y - 2, pageW - margin - 32, y - 2);
            y += 2;
        }

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(...DARK);
        doc.text(`Immobilie ${immo.nummer}: ${adresse}`, margin, y);
        y += 5;

        doc.setTextColor(...GREEN);
        const objText = `${seitenBeschreibung} - ${gesamtFlaeche.toLocaleString('de-DE')}m²`;
        const objLines = doc.splitTextToSize(objText, contentW - 35);
        doc.text(objLines, margin, y);
        y += objLines.length * 5;

        // Seiten-Details (klein)
        if (aktivSeiten.length > 0) {
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(8);
            doc.setTextColor(...GRAY);
            const detailText = aktivSeiten.map(s => `${s.label}: ${(s.flaeche || 0).toLocaleString('de-DE')}m²`).join(' | ');
            doc.text(detailText, margin, y);
        }
    });

    // === POSITIONS-TABELLE === (direkt nach Immobilien)
    y += 8;

    // === POSITIONS-TABELLE ===
    y = drawTableHeader(doc, y, margin, pageW, contentW);

    // Tabellen-Zeilen
    doc.setFontSize(9);
    positions.forEach((p, idx) => {
        // Seitenumbruch prüfen
        if (y > 245) {
            addFooter(doc, pageW, pageH, margin);
            addSidebarLogos(doc, sidebarX);
            doc.addPage();
            y = 35;
            y = drawTableHeader(doc, y, margin, pageW, contentW);
        }

        const ges = p.menge * p.einzelpreis;
        const gesStr = p.bedarfsposition ? `(${formatCurrency(ges)})` : formatCurrency(ges);
        const color = p.bedarfsposition ? GRAY : DARK;

        // Position
        doc.setTextColor(...GREEN);
        doc.setFont('helvetica', 'normal');
        doc.text(p.pos, margin + 2, y);

        // Menge
        doc.setTextColor(...color);
        doc.text(`${p.menge} ${p.einheit}`, margin + 14, y);

        // Bezeichnung (fett)
        doc.setFont('helvetica', 'bold');
        const bezText = p.bedarfsposition ? `${p.bezeichnung} (Bedarfsposition)` : p.bezeichnung;
        const bezLines = doc.splitTextToSize(bezText, 65);
        doc.text(bezLines, margin + 38, y);

        // Beschreibung (normal, kleiner)
        let bezHeight = bezLines.length * 4;
        if (p.beschreibung && !p.bedarfsposition) {
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(8);
            const beschrLines = doc.splitTextToSize(p.beschreibung.replace(/\n/g, ' '), 65);
            if (beschrLines.length > 0) {
                doc.text(beschrLines, margin + 38, y + bezHeight);
                bezHeight += beschrLines.length * 3.5;
            }
            doc.setFontSize(9);
        }

        doc.setFont('helvetica', 'normal');

        // Preise
        doc.setTextColor(...color);
        doc.text(formatCurrency(p.einzelpreis), margin + 125, y, { align: 'right' });
        doc.text(gesStr, margin + 150, y, { align: 'right' });

        // Trennlinie
        doc.setDrawColor(230, 230, 230);
        doc.setLineWidth(0.15);
        const nextY = y + Math.max(bezHeight, 5) + 2;
        doc.line(margin, nextY, pageW - margin - 32, nextY);

        y = nextY + 4;
    });

    // === SUMMEN ===
    y += 6;
    if (y > 250) {
        addFooter(doc, pageW, pageH, margin);
        addSidebarLogos(doc, sidebarX);
        doc.addPage();
        y = 50;
    }

    const sumX = margin + 95;
    const sumValX = margin + 150;

    // Bedarfspositionen (wenn vorhanden)
    if (totals.bedarfs !== 0) {
        doc.setTextColor(...GRAY);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.text('Bedarfspositionen', sumX, y);
        doc.text(`(${formatCurrency(totals.bedarfs)})`, sumValX, y, { align: 'right' });
        y += 5;
    }

    doc.setTextColor(...DARK);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.text('Nettobetrag', sumX, y);
    doc.text(formatCurrency(totals.netto), sumValX, y, { align: 'right' });
    y += 5;

    doc.text('zzgl. 19% MwSt.', sumX, y);
    doc.text(formatCurrency(totals.mwst), sumValX, y, { align: 'right' });
    y += 3;

    // Trennlinie vor Gesamtsumme
    doc.setDrawColor(...DARK);
    doc.setLineWidth(0.4);
    doc.line(sumX, y, sumValX, y);
    y += 5;

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text('Gesamtsumme', sumX, y);
    doc.text(formatCurrency(totals.brutto), sumValX, y, { align: 'right' });

    // === WICHTIGER HINWEIS ===
    y += 18;
    if (y > 240) {
        addFooter(doc, pageW, pageH, margin);
        addSidebarLogos(doc, sidebarX);
        doc.addPage();
        y = 40;
    }

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.setTextColor(...DARK);
    doc.text('WICHTIGER HINWEIS ZUM OBJEKT:', margin, y);

    y += 6;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    const hinweisText = 'Um bei der Umsetzung der Reinigungsarbeiten die notwendige Zugänglichkeit und Arbeitsfreiheit gewährleisten zu können, ist die kurzzeitige Nutzung der Parkplätze, Gehwege und ggf. Straßenteilbereiche notwendig. Mit erfolgter Auftragsbestätigung stehen wir Ihnen hierzu für die konkrete Abstimmung und Vorbereitung gerne unterstützend zur Verfügung.';
    const hinweisLines = doc.splitTextToSize(hinweisText, contentW - 35);
    doc.text(hinweisLines, margin, y);
    y += hinweisLines.length * 4;

    // === UNTERSCHRIFTSFELD ===
    y += 12;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.text('Angebot erhalten und bestätigt:', margin, y);

    y += 20;
    doc.setDrawColor(...DARK);
    doc.setLineWidth(0.3);
    doc.line(margin, y, margin + 45, y);
    doc.line(margin + 60, y, margin + 120, y);

    doc.setFontSize(7);
    doc.setTextColor(...GRAY);
    doc.text('Ort, Datum', margin, y + 4);
    doc.text('Unterschrift', margin + 60, y + 4);

    // === FOOTER & SIDEBAR AUF ALLEN SEITEN ===
    const totalPages = doc.internal.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        addFooter(doc, pageW, pageH, margin);
        addSidebarLogos(doc, sidebarX);
    }

    // Speichern
    doc.save(`Angebot-${data.angNr}-${data.firma.replace(/[^a-zA-Z0-9]/g, '-')}.pdf`);
}

// === HELPER FUNCTIONS ===

function drawHeader(doc, margin, pageW, data, ff, logoImage) {
    // Logo als Bild einfügen (falls geladen)
    if (logoImage) {
        doc.addImage(logoImage, 'PNG', margin, 10, 60, 14);
    } else {
        // Fallback: Logo-Balken zeichnen
        doc.setFillColor(...GREEN);
        doc.roundedRect(margin, 12, 5, 15, 1, 1, 'F');
        doc.roundedRect(margin + 6, 8, 5, 19, 1, 1, 'F');
        doc.roundedRect(margin + 12, 14, 5, 13, 1, 1, 'F');

        // Logo-Text
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(22);
        doc.setTextColor(...DARK);
        doc.text('FASSADEN', margin + 20, 22);
        doc.setTextColor(...GREEN);
        doc.text('FIX', margin + 58, 22);
    }

    // Grüne Linie
    doc.setDrawColor(...GREEN);
    doc.setLineWidth(0.8);
    doc.line(margin, 28, pageW - margin, 28);

    // Absenderzeile
    doc.setFontSize(7);
    doc.setTextColor(...GRAY);
    doc.setFont('helvetica', 'normal');
    doc.text('FASSADENFIX • Immobiliengruppe Retzlaff OHG • An der Saalebahn 8a • 06118 Halle', margin, 34);

    // Empfängeradresse
    let y = 42;
    doc.setFontSize(10);
    doc.setTextColor(...DARK);
    doc.setFont('helvetica', 'bold');
    doc.text(data.firma, margin, y);
    doc.setFont('helvetica', 'normal');
    doc.text(data.ansprechpartner, margin, y + 5);
    doc.text(data.strasse, margin, y + 10);
    doc.text(`${data.plz} ${data.ort}`, margin, y + 15);

    // Meta-Daten rechts
    const metaX = 120;
    const metaValX = pageW - margin;
    doc.setFontSize(9);
    const metaRows = [
        ['Angebotsnummer', data.angNr],
        ['Kundennummer', data.kundNr],
        ['Datum', data.datum],
        ['Ansprechpartner', ff[0]],
        ['Mobil', ff[2]],
        ['E-Mail', ff[1]]
    ];
    metaRows.forEach((row, i) => {
        doc.setTextColor(...GRAY);
        doc.setFont('helvetica', 'normal');
        doc.text(row[0], metaX, y + i * 5);
        doc.setTextColor(...DARK);
        doc.setFont('helvetica', 'bold');
        doc.text(row[1], metaValX, y + i * 5, { align: 'right' });
    });

    // Titel
    y = 80;
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...DARK);
    const titleText = `Angebot Nr. ${data.angNr}`;
    doc.text(titleText, margin, y);
    doc.setLineWidth(0.4);
    doc.setDrawColor(...DARK);
    doc.line(margin, y + 1, margin + doc.getTextWidth(titleText), y + 1);

    // Einleitungstext
    y = 90;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text('Wir freuen uns über Ihr Interesse an unserer FassadenFix - Systemreinigung.', margin, y);
    doc.text('Gerne erstellen wir Ihnen wunschgemäß ein Angebot.', margin, y + 5);
}

function drawTableHeader(doc, y, margin, pageW, contentW) {
    doc.setFillColor(248, 250, 252);
    doc.rect(margin, y - 4, contentW - 30, 8, 'F');
    doc.setDrawColor(...GREEN);
    doc.setLineWidth(0.6);
    doc.line(margin, y + 4, pageW - margin - 30, y + 4);

    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...GREEN);
    doc.text('Pos', margin + 2, y + 1);
    doc.setTextColor(...DARK);
    doc.text('Menge', margin + 14, y + 1);
    doc.text('Bezeichnung', margin + 38, y + 1);
    doc.text('Einheitspreis', margin + 105, y + 1);
    doc.text('Gesamt', margin + 138, y + 1);

    return y + 10;
}

function addFooter(doc, pageW, pageH, margin) {
    // Grüner Balken am unteren Rand
    doc.setFillColor(...GREEN);
    doc.rect(0, pageH - 8, pageW, 8, 'F');

    // Footer-Infos
    const footerY = pageH - 23;
    doc.setFontSize(7);

    // Spalte 1: Firma
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...GREEN);
    doc.text('FASSADENFIX', margin, footerY);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...GRAY);
    doc.text('Immobiliengruppe Retzlaff oHG', margin, footerY + 3);
    doc.text('An der Saalebahn 8a', margin, footerY + 6);
    doc.text('06118 Halle (Saale)', margin, footerY + 9);

    // Spalte 2: Kontakt
    doc.text('T  0345 218392 35', margin + 45, footerY);
    doc.text('E  info@fassadenfix.de', margin + 45, footerY + 3);
    doc.text('W www.fassadenfix.de', margin + 45, footerY + 6);
    doc.text('S  110 / 151 / 09205', margin + 45, footerY + 9);

    // Spalte 3: Bank
    doc.text('Commerzbank', margin + 90, footerY);
    doc.text('Inhaber: Immobiliengruppe Retzlaff oHG', margin + 90, footerY + 3);
    doc.text('IBAN: DE49 8004 0000 0325 0123 00', margin + 90, footerY + 6);
    doc.text('BIC:    COBADEFFXXX', margin + 90, footerY + 9);

    // Spalte 4: Register
    doc.text('Geschäftsführer:', margin + 145, footerY);
    doc.text('Alexander Retzlaff', margin + 145, footerY + 3);
    doc.text('Handelsregister Stendal', margin + 145, footerY + 6);
    doc.text('HRA 4244', margin + 145, footerY + 9);
}

function addSidebarLogos(doc, sideX) {
    let sideY = 90;

    // ProvenExpert Badge
    doc.setFillColor(245, 245, 245);
    doc.roundedRect(sideX, sideY - 4, 26, 24, 2, 2, 'F');
    doc.setFontSize(5);
    doc.setTextColor(255, 102, 0);
    doc.setFont('helvetica', 'bold');
    doc.text('★ Proven Expert', sideX + 3, sideY + 1);
    doc.setFontSize(8);
    doc.setTextColor(255, 180, 0);
    doc.text('★★★★★', sideX + 4, sideY + 6);
    doc.setFontSize(7);
    doc.setTextColor(0, 0, 0);
    doc.setFont('helvetica', 'bold');
    doc.text('SEHR GUT', sideX + 4, sideY + 11);
    doc.setFontSize(5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...GRAY);
    doc.text('4.74 / 5.00 (289)', sideX + 3, sideY + 15);

    // Google Rating
    sideY += 30;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(66, 133, 244);
    doc.text('G', sideX + 2, sideY);
    doc.setTextColor(234, 67, 53);
    doc.text('o', sideX + 7, sideY);
    doc.setTextColor(251, 188, 5);
    doc.text('o', sideX + 11, sideY);
    doc.setTextColor(66, 133, 244);
    doc.text('g', sideX + 15, sideY);
    doc.setTextColor(52, 168, 83);
    doc.text('l', sideX + 19.5, sideY);
    doc.setTextColor(234, 67, 53);
    doc.text('e', sideX + 22, sideY);

    doc.setFontSize(5);
    doc.setTextColor(...GRAY);
    doc.setFont('helvetica', 'normal');
    doc.text('Kunden Bewertungen', sideX + 1, sideY + 4);
    doc.setFontSize(14);
    doc.setTextColor(...GREEN);
    doc.setFont('helvetica', 'bold');
    doc.text('4,9/5', sideX + 4, sideY + 12);
    doc.setFontSize(8);
    doc.setTextColor(255, 180, 0);
    doc.text('★★★★★', sideX + 2, sideY + 17);
    doc.setFontSize(5);
    doc.setTextColor(...GRAY);
    doc.setFont('helvetica', 'normal');
    doc.text('55 Rezensionen', sideX + 4, sideY + 21);

    // DESWOS (vereinfacht)
    sideY += 32;
    doc.setFillColor(26, 95, 42);
    doc.triangle(sideX + 13, sideY - 6, sideX + 4, sideY + 4, sideX + 22, sideY + 4, 'F');
    doc.setFillColor(255, 255, 255);
    doc.rect(sideX + 10, sideY - 1, 6, 5, 'F');
    doc.setFontSize(8);
    doc.setTextColor(26, 95, 42);
    doc.setFont('helvetica', 'bold');
    doc.text('DESWOS', sideX + 3, sideY + 10);

    // vdw (vereinfacht mit Dreiecken)
    sideY += 22;
    doc.setFillColor(...GREEN);
    doc.triangle(sideX + 2, sideY + 6, sideX + 9, sideY - 2, sideX + 16, sideY + 6, 'F');
    doc.setFillColor(51, 51, 51);
    doc.triangle(sideX + 10, sideY + 6, sideX + 17, sideY - 2, sideX + 24, sideY + 6, 'F');
    doc.setFontSize(5);
    doc.setTextColor(...GRAY);
    doc.setFont('helvetica', 'normal');
    doc.text('Die Wohnungswirtschaft', sideX, sideY + 10);
    doc.setFontSize(11);
    doc.setTextColor(...GREEN);
    doc.setFont('helvetica', 'bold');
    doc.text('vdw', sideX + 7, sideY + 17);
}
