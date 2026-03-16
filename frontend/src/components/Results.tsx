import React, { useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, HelpCircle, Info, X, FileText, Quote, Download, ExternalLink } from 'lucide-react';
import { exportResultsToPDF } from '../utils/pdfExport';
import { PdfViewer } from './PdfViewer';
import { WorkflowTrace } from './WorkflowTrace';
import { API_BASE_URL } from '../config';

interface Evidence {
    text: string;
    source: string;
    page: number | string;
    chunk_id?: string;
    chapter?: string;
}

interface EvidenceCitation {
    chunk_id: string;
    quote: string;
    why_it_matters?: string;
}

interface AlignmentOutput {
    alignment_summary: string;
    key_aligned_concepts: string[];
    evidence_citations?: EvidenceCitation[];
    assumptions?: string[];
}

interface CriterionResult {
    criterion_id: string;
    title: string;
    requirement?: string;
    expected_evidence?: string[];
    status: string;
    score: number;
    evidence_coverage?: number;
    met_indicators_count?: number;
    total_indicators_count?: number;
    reasoning: string;
    key_aligned_concepts?: string[];
    decisive_gaps_or_divergences?: string[];
    tensions_or_ambiguities?: string[];
    evidence: Evidence[];
    alignment_findings: AlignmentOutput;
    gap_analysis: any;
    synthesis_result: any;
}

interface CommitmentResult {
    commitment_id: string;
    title: string;
    results: CriterionResult[];
}

interface AssessmentReport {
    compliance_score: number;
    source_document?: string;
    provider?: string;
    model?: string;
    mode?: string;
    commitments: CommitmentResult[];
}

interface ResultsProps {
    report: AssessmentReport;
}

const StatusIcon = ({ status, size = 5 }: { status: string, size?: number }) => {
    const className = `w-${size} h-${size}`;
    const normalizedStatus = status.toLowerCase().replace(/_/g, ' ');
    switch (normalizedStatus) {
        case 'compliant':
            return <CheckCircle className={`${className} text-green-500`} />;
        case 'partially compliant':
            return <AlertTriangle className={`${className} text-yellow-500`} />;
        case 'not compliant':
            return <XCircle className={`${className} text-red-500`} />;
        default:
            return <HelpCircle className={`${className} text-gray-400`} />;
    }
};

const StatusBadge = ({ status }: { status: string }) => {
    const colors = {
        'compliant': 'bg-green-100 text-green-800',
        'partially compliant': 'bg-yellow-100 text-yellow-800',
        'not compliant': 'bg-red-100 text-red-800',
        'unknown': 'bg-gray-100 text-gray-800',
    };
    const normalizedStatus = status.toLowerCase().replace(/_/g, ' ');
    const colorClass = colors[normalizedStatus as keyof typeof colors] || colors['unknown'];

    return (
        <span className={`px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded ${colorClass}`}>
            {normalizedStatus}
        </span>
    );
};

const MeasureDetailModal = ({ measure, onClose, onViewSource }: {
    measure: CriterionResult,
    onClose: () => void,
    onViewSource: (evidence: Evidence) => void
}) => {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-in fade-in duration-200" onClick={onClose}>
            <div
                className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Modal Header */}
                <div className="p-6 border-b border-gray-100 flex items-start justify-between bg-gray-50/50">
                    <div className="space-y-1">
                        <div className="flex items-center gap-3">
                            <span className="text-[10px] font-black text-blue-600 bg-blue-50 px-2 py-0.5 rounded uppercase tracking-widest">
                                {measure.criterion_id}
                            </span>
                            <StatusBadge status={measure.status} />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 leading-tight">
                            {measure.title}
                        </h3>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-200 rounded-full transition-colors text-gray-400 hover:text-gray-600"
                    >
                        <X size={30} />
                    </button>
                </div>

                {/* Modal Content */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                    {/* Requirement Section */}
                    {measure.requirement && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                                    <Info size={14} className="text-purple-500" /> Requirement
                                </div>
                                {(measure.evidence_coverage !== undefined || measure.met_indicators_count !== undefined) && (
                                    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg">
                                        <div className="flex flex-col items-end">
                                            <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mb-1">Evidence Coverage</span>
                                            <div className="flex items-center gap-2">
                                                {measure.met_indicators_count !== undefined && (
                                                    <span className="text-[10px] font-black text-blue-600">
                                                        {measure.met_indicators_count}/{measure.total_indicators_count} <span className="text-gray-400 font-bold uppercase tracking-tighter">Indicators</span>
                                                    </span>
                                                )}
                                                <div className="h-1.5 w-16 bg-gray-200 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full transition-all duration-500 ${measure.evidence_coverage! > 0.8 ? 'bg-green-500' : measure.evidence_coverage! > 0.5 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                                        style={{ width: `${(measure.evidence_coverage || 0) * 100}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs font-black text-gray-900 leading-none">
                                                    {((measure.evidence_coverage || 0) * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                            <div className="bg-purple-50/30 p-6 rounded-2xl border border-purple-100/50">
                                <p className="text-sm text-gray-700 leading-relaxed font-medium break-words whitespace-pre-wrap">
                                    {measure.requirement}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Key Aligned Concepts */}
                    {measure.key_aligned_concepts && measure.key_aligned_concepts.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                                <CheckCircle size={14} className="text-green-500" /> Key Aligned Concepts
                            </div>
                            <ul className="grid gap-2">
                                {measure.key_aligned_concepts.map((concept, idx) => (
                                    <li key={idx} className="bg-green-50/50 px-4 py-3 rounded-xl border border-green-100 flex items-start gap-3">
                                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 shrink-0" />
                                        <span className="text-sm text-gray-700 font-medium break-words">{concept}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* AI Evidence Citations - NEW SECTION */}
                    {measure.alignment_findings?.evidence_citations && measure.alignment_findings.evidence_citations.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                                <Quote size={14} className="text-blue-500" /> Decisive Evidence Quotes (AI Selected)
                            </div>
                            <div className="grid gap-3">
                                {measure.alignment_findings.evidence_citations.map((cite, idx) => (
                                    <div key={idx} className="bg-blue-50/50 p-5 rounded-2xl border border-blue-100 space-y-3">
                                        <div className="flex items-start gap-3">
                                            <Quote size={16} className="text-blue-400 shrink-0 mt-1" />
                                            <p className="text-sm text-gray-800 font-semibold italic leading-relaxed">
                                                "{cite.quote}"
                                            </p>
                                        </div>
                                        {cite.why_it_matters && (
                                            <div className="pl-7 border-l-2 border-blue-200">
                                                <p className="text-[11px] font-bold text-blue-600 uppercase tracking-wider mb-0.5">Focus Point</p>
                                                <p className="text-xs text-gray-600 leading-relaxed font-medium">
                                                    {cite.why_it_matters}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Decisive Gaps */}
                    {measure.decisive_gaps_or_divergences && measure.decisive_gaps_or_divergences.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                                <AlertTriangle size={14} className="text-red-500" /> Decisive Gaps & Divergences
                            </div>
                            <ul className="grid gap-2">
                                {measure.decisive_gaps_or_divergences.map((gap, idx) => (
                                    <li key={idx} className="bg-red-50/50 px-4 py-3 rounded-xl border border-red-100 flex items-start gap-3">
                                        <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-2 shrink-0" />
                                        <span className="text-sm text-gray-700 font-medium break-words">{gap}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Ambiguities */}
                    {measure.tensions_or_ambiguities && measure.tensions_or_ambiguities.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                                <HelpCircle size={14} className="text-orange-500" /> Tensions & Ambiguities
                            </div>
                            <ul className="grid gap-2">
                                {measure.tensions_or_ambiguities.map((tension, idx) => (
                                    <li key={idx} className="bg-orange-50/50 px-4 py-3 rounded-xl border border-orange-100 flex items-start gap-3">
                                        <div className="w-1.5 h-1.5 rounded-full bg-orange-400 mt-2 shrink-0" />
                                        <span className="text-sm text-gray-700 font-medium break-words">{tension}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Reasoning Section */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                            <Info size={14} className="text-blue-500" /> Assessment Reasoning
                        </div>
                        <div className="bg-blue-50/30 p-6 rounded-2xl border border-blue-100/50">
                            <p className="text-sm text-gray-700 leading-relaxed break-words whitespace-pre-wrap">
                                {measure.reasoning}
                            </p>
                        </div>
                    </div>

                    {/* Workflow Trace Section */}
                    <div className="bg-gray-50/50 p-8 rounded-3xl border border-gray-100 shadow-inner">
                        <WorkflowTrace result={measure} />
                    </div>

                    {/* Evidence Section */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                            <FileText size={14} className="text-indigo-500" /> Evidence Found
                        </div>
                        {measure.evidence.length > 0 ? (
                            <div className="grid gap-4">
                                {measure.evidence.map((ev, i) => (
                                    <div key={i} className="relative bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:border-indigo-100 transition-colors w-full min-w-0 overflow-hidden">
                                        <Quote size={24} className="absolute top-4 right-4 text-indigo-50/50" />
                                        <p className="text-sm text-gray-700 leading-relaxed italic pr-8 break-words whitespace-pre-wrap">
                                            "{ev.text}"
                                        </p>
                                        <div className="mt-4 flex items-center justify-between text-[10px] font-bold text-indigo-500 uppercase tracking-widest">
                                            <span className="flex items-center gap-1.5 max-w-[70%] truncate">
                                                <FileText size={10} /> {ev.source}
                                                {ev.chapter && <span className="opacity-60">| {ev.chapter}</span>}
                                            </span>
                                            {ev.page !== undefined && <span>Page {typeof ev.page === 'number' ? ev.page + 1 : ev.page}</span>}
                                        </div>

                                        <button
                                            onClick={() => onViewSource(ev)}
                                            className="mt-3 w-full flex items-center justify-center gap-2 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors"
                                        >
                                            <ExternalLink size={14} /> View Source Context
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                                <p className="text-sm text-gray-400">No specific evidence snippets were extracted.</p>
                            </div>
                        )}
                    </div>

                    {/* Expected Evidence */}
                    {measure.expected_evidence && measure.expected_evidence.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em]">
                                <FileText size={14} className="text-teal-500" /> Expected Evidence
                            </div>
                            <ul className="grid gap-2">
                                {measure.expected_evidence.map((evidence, idx) => (
                                    <li key={idx} className="bg-teal-50/50 px-4 py-3 rounded-xl border border-teal-100 flex items-start gap-3">
                                        <div className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-2 shrink-0" />
                                        <span className="text-sm text-gray-700 font-medium break-words leading-relaxed">{evidence}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>

                {/* Modal Footer */}
                <div className="p-6 border-t border-gray-100 bg-gray-50/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2.5 bg-gray-900 text-white text-xs font-bold uppercase tracking-widest rounded-xl hover:bg-gray-800 transition-all shadow-lg shadow-gray-200"
                    >
                        Close Details
                    </button>
                </div>
            </div>
        </div >
    );
};

const CommitmentWidget = ({ commitment, onMeasureClick }: { commitment: CommitmentResult, onMeasureClick: (m: CriterionResult) => void }) => {
    const score = commitment.results.reduce((acc, r) => {
        const status = r.status.toLowerCase().replace(/_/g, ' ');
        if (status === 'compliant') return acc + 1;
        if (status === 'partially compliant') return acc + 0.5;
        return acc;
    }, 0);
    const totalCount = commitment.results.length;
    const progress = (score / totalCount) * 100;

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col h-full overflow-hidden transition-all hover:shadow-md hover:border-blue-100">
            {/* Widget Header */}
            <div className="p-5 border-b border-gray-50 bg-gradient-to-r from-white to-gray-50/50">
                <div className="flex items-start justify-between mb-3">
                    <span className="text-[10px] font-black text-blue-600 bg-blue-50 px-2 py-0.5 rounded uppercase tracking-widest">
                        {commitment.commitment_id}
                    </span>
                    <div className="flex items-center gap-1.5">
                        <span className="text-xs font-bold text-gray-900">{score}/{totalCount}</span>
                        <div className="w-12 bg-gray-100 rounded-full h-1.5 overflow-hidden">
                            <div
                                className="bg-blue-600 h-full rounded-full transition-all duration-500"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </div>
                </div>
                <h3 className="text-sm font-bold text-gray-800 leading-tight line-clamp-2 min-h-[2.5rem]">
                    {commitment.title}
                </h3>
                {/* Context Toggle */}
                <div className="mt-3 pt-3 border-t border-gray-100">
                    <details className="group">
                        <summary className="list-none flex items-center gap-1.5 text-[10px] font-bold text-gray-400 uppercase tracking-wider cursor-pointer hover:text-blue-500 transition-colors">
                            <Info size={12} /> Why this matters
                        </summary>
                        <p className="mt-2 text-xs text-gray-500 leading-relaxed font-medium animate-in fade-in slide-in-from-top-1 duration-200">
                            This commitment ensures that {commitment.title.toLowerCase()} are properly addressed to mitigate systemic risks in accordance with the EU AI Act.
                        </p>
                    </details>
                </div>
            </div>

            {/* Measures List */}
            <div className="flex-1 overflow-y-auto max-h-[400px] p-2 space-y-1">
                {commitment.results.map((res) => (
                    <div
                        key={res.criterion_id}
                        className="p-3 rounded-xl cursor-pointer transition-all hover:bg-blue-50/50 group"
                        onClick={() => onMeasureClick(res)}
                    >
                        <div className="flex items-center justify-between gap-3">
                            <div className="flex items-center gap-3 min-w-0">
                                <StatusIcon status={res.status} size={4} />
                                <div className="truncate">
                                    <p className="text-xs font-semibold text-gray-700 truncate group-hover:text-blue-700 transition-colors">{res.title}</p>
                                    <div className="flex items-center gap-2 mt-0.5">
                                        <span className="text-[9px] font-medium text-gray-400 uppercase tracking-tighter">{res.criterion_id}</span>
                                        <StatusBadge status={res.status} />
                                    </div>
                                </div>
                            </div>
                            <Info size={14} className="text-gray-300 group-hover:text-blue-400 transition-colors" />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export const Results: React.FC<ResultsProps> = ({ report }) => {
    const [selectedMeasure, setSelectedMeasure] = useState<CriterionResult | null>(null);
    const [viewingEvidence, setViewingEvidence] = useState<Evidence | null>(null);

    return (
        <div className="max-w-7xl mx-auto space-y-8 pb-20 px-4">
            {/* PDF Viewer Modal */}
            {viewingEvidence && (
                <PdfViewer
                    url={`${API_BASE_URL}/documents/${encodeURIComponent(viewingEvidence.source)}/content`}
                    initialPage={(() => {
                        const p = viewingEvidence.page;
                        if (typeof p === 'number') return p + 1;
                        if (typeof p === 'string' && p.includes('-')) {
                            const start = parseInt(p.split('-')[0]);
                            return isNaN(start) ? 1 : start + 1;
                        }
                        const parsed = parseInt(String(p));
                        return isNaN(parsed) ? 1 : parsed + 1;
                    })()}
                    highlightText={viewingEvidence.text}
                    onClose={() => setViewingEvidence(null)}
                />
            )}
            {/* Header / Score Section */}
            <div className="relative overflow-hidden p-8 bg-gradient-to-br from-blue-700 to-indigo-900 rounded-3xl shadow-2xl text-white">
                <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-8">
                    <div className="space-y-3">
                        <div className="flex items-center gap-3">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-[10px] font-bold uppercase tracking-widest">
                                <ShieldCheck className="w-3 h-3 text-blue-300" /> Compliance Dashboard
                            </div>
                            <button
                                onClick={() => exportResultsToPDF(report)}
                                className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-md border border-white/30 text-[10px] font-bold uppercase tracking-widest transition-all cursor-pointer"
                            >
                                <Download className="w-3 h-3 text-blue-300" /> Export PDF
                            </button>
                        </div>
                        <h2 className="text-4xl font-black tracking-tight">Assessment Report</h2>
                        <div className="flex flex-wrap items-center gap-3">
                            <span className="text-[10px] font-bold px-2 py-0.5 bg-white/20 rounded uppercase tracking-wider border border-white/10">
                                {report.provider || 'N/A'}
                            </span>
                            <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-400/30 rounded uppercase tracking-wider border border-white/10">
                                {report.model || 'N/A'}
                            </span>
                            <span className="text-[10px] font-bold px-2 py-0.5 bg-indigo-400/30 rounded uppercase tracking-wider border border-white/10">
                                {report.mode === 'triple' ? 'Triple Agent Pipeline' : 'Single Agent Speed'}
                            </span>
                        </div>
                        <p className="text-blue-100 text-sm max-w-lg leading-relaxed">
                            Detailed evaluation of your AI system against the EU AI Act Safety & Security Code of Practice.
                            Results are categorized by commitment areas for targeted improvements.
                        </p>
                    </div>

                    <div className="flex items-center gap-8 bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 shadow-inner">
                        <div className="text-center">
                            <div className="text-5xl font-black mb-1 tracking-tighter">{report.compliance_score.toFixed(1)}%</div>
                            <div className="text-[10px] font-bold uppercase tracking-widest text-blue-200 opacity-80">Overall Score</div>
                        </div>
                        <div className="w-px h-16 bg-white/20" />
                        <div className="text-center">
                            <div className="text-5xl font-black mb-1 tracking-tighter">{report.commitments.length}</div>
                            <div className="text-[10px] font-bold uppercase tracking-widest text-blue-200 opacity-80">Commitments</div>
                        </div>
                    </div>
                </div>
                {/* Decorative background elements */}
                <div className="absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-blue-400/20 rounded-full blur-3xl" />
                <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-64 h-64 bg-indigo-400/20 rounded-full blur-3xl" />
            </div>

            {/* Widgets Grid */}
            <div className="space-y-6">
                <div className="flex items-center justify-between px-2">
                    <h3 className="text-xs font-black text-gray-400 uppercase tracking-[0.2em]">Commitment Widgets</h3>
                    <div className="flex gap-4 text-[10px] font-bold text-gray-400 uppercase tracking-tighter">
                        <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-green-500" /> Compliant</div>
                        <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-yellow-400" /> Partial</div>
                        <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-red-500" /> Non-Compliant</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {report.commitments.map((commitment) => (
                        <CommitmentWidget
                            key={commitment.commitment_id}
                            commitment={commitment}
                            onMeasureClick={setSelectedMeasure}
                        />
                    ))}
                </div>
            </div>

            {/* Detail Modal */}
            {selectedMeasure && (
                <MeasureDetailModal
                    measure={selectedMeasure}
                    onClose={() => setSelectedMeasure(null)}
                    onViewSource={(ev) => setViewingEvidence(ev)}
                />
            )}
        </div>
    );
};

// Helper component for the header
const ShieldCheck = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
);
