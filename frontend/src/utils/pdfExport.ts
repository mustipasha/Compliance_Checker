import jsPDF from 'jspdf';

interface Evidence {
    text: string;
    source: string;
    page: number | string;
}

interface AlignmentOutput {
    alignment_summary: string;
    key_aligned_concepts?: string[];
    evidence_citations?: {
        chunk_id: string;
        quote: string;
        why_it_matters?: string;
    }[];
}

interface CriterionResult {
    criterion_id: string;
    title: string;
    status: string;
    reasoning: string;
    key_aligned_concepts?: string[];
    decisive_gaps_or_divergences?: string[];
    tensions_or_ambiguities?: string[];
    evidence: Evidence[];
    expected_evidence?: string[];
    alignment_findings?: AlignmentOutput;
}

interface CommitmentResult {
    commitment_id: string;
    title: string;
    results: CriterionResult[];
}

interface AssessmentReport {
    compliance_score: number;
    commitments: CommitmentResult[];
    provider?: string;
    model?: string;
    mode?: string;
    source_document?: string;
}

const COLORS = {
    primary: [30, 58, 138], // blue-900
    secondary: [71, 85, 105], // slate-600
    success: [22, 101, 52], // green-800
    danger: [153, 27, 27], // red-800
    warning: [146, 64, 14], // amber-800
    background: [248, 250, 252], // slate-50
    text: [15, 23, 42], // slate-900
    lightText: [100, 116, 139], // slate-500
    border: [226, 232, 240], // slate-200
};

export const exportResultsToPDF = (report: AssessmentReport) => {
    const doc = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4'
    });

    const margin = 20;
    const pageWidth = doc.internal.pageSize.width;
    const contentWidth = pageWidth - (margin * 2);
    let currentY = 25;

    // --- Header ---
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(24);
    doc.setTextColor(COLORS.primary[0], COLORS.primary[1], COLORS.primary[2]);
    doc.text('Compliance Assessment Report', margin, currentY);
    currentY += 10;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(COLORS.lightText[0], COLORS.lightText[1], COLORS.lightText[2]);
    doc.text(`Generated on ${new Date().toLocaleString()}`, margin, currentY);
    currentY += 15;

    // --- Summary Section ---
    doc.setDrawColor(COLORS.border[0], COLORS.border[1], COLORS.border[2]);
    doc.setFillColor(COLORS.background[0], COLORS.background[1], COLORS.background[2]);
    doc.roundedRect(margin, currentY, contentWidth, 40, 2, 2, 'FD');

    const score = report.compliance_score;
    doc.setFontSize(12);
    doc.setTextColor(COLORS.text[0], COLORS.text[1], COLORS.text[2]);
    doc.text('Overall Compliance Score', margin + 10, currentY + 12);

    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    if (score >= 80) doc.setTextColor(COLORS.success[0], COLORS.success[1], COLORS.success[2]);
    else if (score >= 50) doc.setTextColor(COLORS.warning[0], COLORS.warning[1], COLORS.warning[2]);
    else doc.setTextColor(COLORS.danger[0], COLORS.danger[1], COLORS.danger[2]);

    doc.text(`${score.toFixed(1)}%`, margin + 10, currentY + 22);

    // Stats
    const totalCriteria = report.commitments.reduce((acc, c) => acc + c.results.length, 0);
    const fulfilledScore = report.commitments.reduce((acc, c) => {
        return acc + c.results.reduce((cAcc, r) => {
            const status = r.status.toLowerCase().replace(/_/g, ' ').trim();
            if (status === 'compliant' || status === 'full') return cAcc + 1;
            if (status === 'partially compliant' || status === 'partial') return cAcc + 0.5;
            return cAcc;
        }, 0);
    }, 0);

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(COLORS.secondary[0], COLORS.secondary[1], COLORS.secondary[2]);
    doc.text(`${fulfilledScore} of ${totalCriteria} points fulfilled`, margin + contentWidth - 60, currentY + 18);

    // Metadata
    if (report.source_document) {
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(COLORS.primary[0], COLORS.primary[1], COLORS.primary[2]);
        doc.text(`Source: ${report.source_document}`, margin + 10, currentY + 32);
    }

    if (report.provider && report.model) {
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(COLORS.secondary[0], COLORS.secondary[1], COLORS.secondary[2]);
        const modeText = report.mode === 'triple' ? 'Triple Agent Pipeline' : 'Single Agent Speed';
        doc.text(`AI: ${report.provider.toUpperCase()} | ${report.model} | ${modeText}`, margin + contentWidth - 85, currentY + 32);
    }

    currentY += 55;

    // --- Commitments & Criteria ---
    report.commitments.forEach((commitment) => {
        // Commitment Header
        if (currentY > 250) {
            doc.addPage();
            currentY = 25;
        }

        const comScore = commitment.results.reduce((acc, r) => {
            const s = r.status.toLowerCase().replace(/_/g, ' ').trim();
            if (s === 'compliant' || s === 'full') return acc + 1;
            if (s === 'partially compliant' || s === 'partial') return acc + 0.5;
            return acc;
        }, 0);
        const comTotal = commitment.results.length;

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(16);
        doc.setTextColor(COLORS.primary[0], COLORS.primary[1], COLORS.primary[2]);
        doc.text(commitment.title, margin, currentY);

        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(COLORS.secondary[0], COLORS.secondary[1], COLORS.secondary[2]);
        doc.text(`${comScore} of ${comTotal} points fulfilled`, margin, currentY + 6);

        currentY += 10;
        doc.setDrawColor(COLORS.primary[0], COLORS.primary[1], COLORS.primary[2]);
        doc.setLineWidth(0.5);
        doc.line(margin, currentY, margin + 40, currentY);
        currentY += 12;

        commitment.results.forEach((result) => {
            const rawStatus = result.status.toUpperCase().replace(/_/g, ' ').trim();
            const status = rawStatus;
            let statusColor = COLORS.secondary;

            if (rawStatus === 'COMPLIANT' || rawStatus === 'FULL') {
                statusColor = COLORS.success;
            } else if (rawStatus === 'PARTIALLY COMPLIANT' || rawStatus === 'PARTIAL') {
                statusColor = COLORS.warning;
            } else if (rawStatus === 'NOT COMPLIANT' || rawStatus === 'NON COMPLIANT' || rawStatus === 'FAIL') {
                statusColor = COLORS.danger;
            }

            // Check space for a "card" (roughly 40mm)
            if (currentY > 240) {
                doc.addPage();
                currentY = 25;
            }

            // const startY = currentY;

            // ID & Title
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(COLORS.text[0], COLORS.text[1], COLORS.text[2]);
            doc.text(`${result.criterion_id}: ${result.title}`, margin, currentY);

            // Status Badge
            const statusWidth = doc.getTextWidth(status) + 4;
            doc.setFillColor(statusColor[0], statusColor[1], statusColor[2]);
            doc.roundedRect(pageWidth - margin - statusWidth, currentY - 5, statusWidth, 7, 1, 1, 'F');
            doc.setFontSize(8);
            doc.setTextColor(255, 255, 255);
            doc.text(status, pageWidth - margin - statusWidth + 2, currentY);

            currentY += 8;

            // Reasoning
            doc.setFontSize(10);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(COLORS.secondary[0], COLORS.secondary[1], COLORS.secondary[2]);
            const reasoningLines = doc.splitTextToSize(result.reasoning, contentWidth - 5);
            doc.text(reasoningLines, margin + 2, currentY);
            currentY += (reasoningLines.length * 5) + 5;

            const renderSection = (title: string, items: string[] | undefined, iconColor: number[]) => {
                if (!items || items.length === 0) return;

                if (currentY > 260) {
                    doc.addPage();
                    currentY = 25;
                }

                doc.setFont('helvetica', 'bold');
                doc.setFontSize(9);
                doc.setTextColor(iconColor[0], iconColor[1], iconColor[2]);
                doc.text(title.toUpperCase(), margin + 2, currentY);
                currentY += 6;

                doc.setFont('helvetica', 'normal');
                doc.setFontSize(9);
                doc.setTextColor(COLORS.text[0], COLORS.text[1], COLORS.text[2]);

                items.forEach(item => {
                    const lines = doc.splitTextToSize(`• ${item}`, contentWidth - 8);
                    if (currentY + (lines.length * 4.5) > 280) {
                        doc.addPage();
                        currentY = 25;
                    }
                    doc.text(lines, margin + 5, currentY);
                    currentY += (lines.length * 4.5) + 2;
                });
                currentY += 5;
            };

            renderSection('Key Aligned Concepts', result.key_aligned_concepts, COLORS.success);

            // AI Evidence Citations (NEW)
            if (result.alignment_findings?.evidence_citations && result.alignment_findings.evidence_citations.length > 0) {
                if (currentY > 260) {
                    doc.addPage();
                    currentY = 25;
                }
                doc.setFont('helvetica', 'bold');
                doc.setFontSize(9);
                doc.setTextColor(COLORS.primary[0], COLORS.primary[1], COLORS.primary[2]); // Blue
                doc.text('DECISIVE EVIDENCE QUOTES (AI SELECTED)', margin + 2, currentY);
                currentY += 8;

                result.alignment_findings.evidence_citations.forEach((cite: any) => {
                    doc.setFont('helvetica', 'italic');
                    doc.setFontSize(9);
                    doc.setTextColor(COLORS.text[0], COLORS.text[1], COLORS.text[2]);
                    const quoteLines = doc.splitTextToSize(`"${cite.quote}"`, contentWidth - 10);

                    const quoteHeight = (quoteLines.length * 4.5) + (cite.why_it_matters ? 15 : 5); // Estimate height
                    if (currentY + quoteHeight > 280) {
                        doc.addPage();
                        currentY = 25;
                    }

                    doc.text(quoteLines, margin + 5, currentY);
                    currentY += quoteLines.length * 4.5 + 2;

                    if (cite.why_it_matters) {
                        doc.setFont('helvetica', 'bold');
                        doc.setFontSize(8);
                        doc.setTextColor(COLORS.primary[0], COLORS.primary[1], COLORS.primary[2]);
                        doc.text('FOCUS POINT:', margin + 5, currentY);
                        doc.setFont('helvetica', 'normal');
                        doc.setTextColor(COLORS.secondary[0], COLORS.secondary[1], COLORS.secondary[2]);
                        const focusLines = doc.splitTextToSize(cite.why_it_matters, contentWidth - 25);
                        doc.text(focusLines, margin + 25, currentY);
                        currentY += (focusLines.length * 4) + 6;
                    } else {
                        currentY += 4;
                    }
                });
                currentY += 4;
            }

            renderSection('Decisive Gaps & Divergences', result.decisive_gaps_or_divergences, COLORS.danger);
            renderSection('Tensions & Ambiguities', result.tensions_or_ambiguities, [249, 115, 22]); // orange-500

            // Evidence
            if (result.evidence && result.evidence.length > 0) {
                if (currentY > 260) {
                    doc.addPage();
                    currentY = 25;
                }

                doc.setFont('helvetica', 'bold');
                doc.setFontSize(9);
                doc.setTextColor(COLORS.primary[0], COLORS.primary[1], COLORS.primary[2]);
                doc.text('EVIDENCE FOUND', margin + 2, currentY);
                currentY += 6;

                result.evidence.forEach((ev) => {
                    const evText = `"${ev.text}"`;
                    const pageText = typeof ev.page === 'number' ? `p. ${ev.page + 1}` : `p. ${ev.page}`;
                    const sourceText = `- ${ev.source}, ${pageText}`;
                    const lines = doc.splitTextToSize(evText, contentWidth - 15);

                    const evHeight = (lines.length * 4.5) + 10;

                    if (currentY + evHeight > 275) {
                        doc.addPage();
                        currentY = 25;
                    }

                    // Evidence Background
                    doc.setFillColor(241, 245, 249); // slate-100
                    doc.roundedRect(margin + 5, currentY, contentWidth - 10, evHeight - 2, 1, 1, 'F');

                    doc.setFont('helvetica', 'italic');
                    doc.setFontSize(9);
                    doc.setTextColor(COLORS.text[0], COLORS.text[1], COLORS.text[2]);
                    doc.text(lines, margin + 10, currentY + 6);

                    currentY += (lines.length * 4.5) + 7;

                    doc.setFont('helvetica', 'bold');
                    doc.setFontSize(8);
                    doc.setTextColor(COLORS.lightText[0], COLORS.lightText[1], COLORS.lightText[2]);
                    doc.text(sourceText, margin + 10, currentY);

                    currentY += 8;
                });
                currentY += 2;
            }

            renderSection('Expected Evidence', result.expected_evidence, [20, 184, 166]); // teal-500

            currentY += 5; // Spacing between criteria
        });

        currentY += 10; // Spacing between commitments
    });

    // Footer
    const pageCount = (doc as any).internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(COLORS.lightText[0], COLORS.lightText[1], COLORS.lightText[2]);
        doc.text(
            `Page ${i} of ${pageCount}`,
            pageWidth / 2,
            doc.internal.pageSize.height - 10,
            { align: 'center' }
        );
    }

    doc.save(`Compliance_Report_${new Date().getTime()}.pdf`);
};
