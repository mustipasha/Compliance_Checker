import React, { useEffect, useState } from 'react';
import { BookOpen, ChevronRight, Target } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PdfViewer } from './PdfViewer';
import { API_BASE_URL } from '../config';

interface Criterion {
    id: string;
    title: string;
    description: string;
    requirement: string;
    assessment_question?: string;
    extracted_keywords?: string[];
    extracted_artifacts?: string[];
    page?: number;
}

interface Commitment {
    id: string;
    title: string;
    description: string;
    criteria: Criterion[];
}

export const CommitmentExplorer: React.FC = () => {
    const navigate = useNavigate();
    const [commitments, setCommitments] = useState<Commitment[]>([]);
    const [selectedCommitment, setSelectedCommitment] = useState<Commitment | null>(null);
    const [loading, setLoading] = useState(true);
    const [viewingPdfPage, setViewingPdfPage] = useState<number | null>(null);

    useEffect(() => {
        // ... (fetch logic same as before)
        fetch(`${API_BASE_URL}/criteria`)
            .then(res => res.json())
            .then(data => {
                let comms = data.commitments || [];
                // Natural Sort: "SS-10" should come after "SS-2"
                comms.sort((a: Commitment, b: Commitment) => {
                    const numA = parseInt(a.id.replace(/\D/g, '')) || 0;
                    const numB = parseInt(b.id.replace(/\D/g, '')) || 0;
                    return numA - numB;
                });
                setCommitments(comms);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load criteria:", err);
                setLoading(false);
            });
    }, []);

    // Helper to open PDF
    const openPdf = (page?: number) => {
        setViewingPdfPage(page || 1);
    };

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading Framework...</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
            {/* PDF Viewer Modal */}
            {viewingPdfPage !== null && (
                <PdfViewer
                    url={`${API_BASE_URL}/framework/pdf`}
                    initialPage={viewingPdfPage}
                    onClose={() => setViewingPdfPage(null)}
                />
            )}

            {/* Sidebar / List of Commitments */}
            {/* ... (rest of the component) */}
            <div className={`w-full md:w-1/3 lg:w-1/4 bg-white border-r border-gray-200 overflow-y-auto h-screen sticky top-0 ${selectedCommitment ? 'hidden md:block' : 'block'}`}>
                <div className="p-6 border-b border-gray-100 bg-white z-10 sticky top-0">
                    <div className="flex items-center gap-2 text-blue-600 mb-2">
                        <BookOpen size={20} />
                        <span className="font-bold uppercase tracking-wider text-xs">Framework Guide</span>
                    </div>
                    <h2 className="text-2xl font-black text-gray-900 leading-tight">Safety & Security Commitments</h2>
                    <p className="mt-2 text-sm text-gray-500">
                        Explore the 10 core commitments and 32 measures of the EU AI Code of Practice.
                    </p>
                </div>
                <div className="p-4 space-y-3">
                    {commitments.map((commit) => (
                        <button
                            key={commit.id}
                            onClick={() => setSelectedCommitment(commit)}
                            className={`w-full text-left p-4 rounded-xl transition-all border group relative overflow-hidden ${selectedCommitment?.id === commit.id
                                ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-200'
                                : 'bg-white border-gray-200 text-gray-700 hover:border-blue-300 hover:shadow-md'
                                }`}
                        >
                            <div className="relative z-10 flex justify-between items-start">
                                <div>
                                    <div className={`text-xs font-bold mb-1 uppercase tracking-wider ${selectedCommitment?.id === commit.id ? 'text-blue-100' : 'text-gray-400'}`}>
                                        {commit.id}
                                    </div>
                                    <div className="font-bold text-lg leading-tight">{commit.title}</div>
                                </div>
                                {selectedCommitment?.id === commit.id && <ChevronRight className="opacity-50" />}
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Content / Detail View */}
            <div className={`w-full md:w-2/3 lg:w-3/4 p-6 md:p-12 overflow-y-auto h-screen ${selectedCommitment ? 'block' : 'hidden md:flex md:items-center md:justify-center'}`}>
                {selectedCommitment ? (
                    <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-right-4 duration-300">
                        <button
                            onClick={() => setSelectedCommitment(null)}
                            className="md:hidden flex items-center gap-1 text-gray-500 mb-6 text-sm font-bold"
                        >
                            ← Back to List
                        </button>

                        <div className="mb-12">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-wider mb-4">
                                {selectedCommitment.id}
                            </div>
                            <h1 className="text-4xl md:text-5xl font-black text-gray-900 mb-6">{selectedCommitment.title}</h1>
                            <p className="text-xl text-gray-600 leading-relaxed max-w-2xl">{selectedCommitment.description}</p>
                        </div>

                        <div className="grid gap-8">
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest border-b border-gray-200 pb-2">
                                Measures ({selectedCommitment.criteria.length})
                            </h3>

                            {selectedCommitment.criteria.map((measure) => (
                                <div key={measure.id} className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
                                    <div className="flex flex-col md:flex-row gap-6">
                                        <div className="w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center flex-shrink-0 text-indigo-600 font-bold text-lg">
                                            {measure.id.split('-').pop()}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-start mb-3">
                                                <h4 className="text-2xl font-bold text-gray-900">{measure.title}</h4>
                                                <button
                                                    onClick={() => openPdf(measure.page)}
                                                    className="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 text-xs font-bold uppercase tracking-wider border border-indigo-100 hover:border-indigo-300 px-3 py-1 bg-indigo-50 rounded-lg transition-colors"
                                                >
                                                    <BookOpen size={14} />
                                                    {measure.page ? `Read on Page ${measure.page}` : 'Read in Code of Practice'}
                                                </button>
                                            </div>

                                            {/* Key Objective / Assessment Question */}
                                            {measure.assessment_question && (
                                                <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100 mb-6">
                                                    <h5 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1 flex items-center gap-2">
                                                        <Target size={12} /> Key Objective
                                                    </h5>
                                                    <p className="text-gray-800 font-medium text-lg leading-snug">
                                                        {measure.assessment_question}
                                                    </p>
                                                </div>
                                            )}

                                            <div className="grid md:grid-cols-2 gap-6 mb-6">
                                                {/* Key Concepts Tags */}
                                                {measure.extracted_keywords && measure.extracted_keywords.length > 0 && (
                                                    <div>
                                                        <h5 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Key Concepts</h5>
                                                        <div className="flex flex-wrap gap-2">
                                                            {measure.extracted_keywords.map((kw, idx) => (
                                                                <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-md border border-gray-200">
                                                                    {kw}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Required Artifacts */}
                                                {measure.extracted_artifacts && measure.extracted_artifacts.length > 0 && (
                                                    <div>
                                                        <h5 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Required Artifacts</h5>
                                                        <div className="flex flex-wrap gap-2">
                                                            {measure.extracted_artifacts.map((art, idx) => (
                                                                <span key={idx} className="px-2 py-1 bg-amber-50 text-amber-800 text-xs font-bold rounded-md border border-amber-100 flex items-center gap-1">
                                                                    📄 {art}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>

                                            <div className="bg-gray-50 p-5 rounded-xl text-gray-700 text-sm leading-relaxed border border-gray-200 mb-4">
                                                <strong className="block text-gray-900 text-xs uppercase tracking-wider mb-2">Full Requirement Text</strong>
                                                {measure.requirement}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-20 pt-10 border-t border-gray-100 flex justify-between items-center">
                            <p className="text-gray-400 text-sm">Ready to check your compliance?</p>
                            <button
                                onClick={() => navigate('/assess')}
                                className="px-8 py-3 bg-gray-900 text-white font-bold rounded-xl hover:bg-gray-800 transition-colors shadow-lg"
                            >
                                Start Assessment →
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="text-center text-gray-400 max-w-md">
                        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Target className="w-10 h-10 text-gray-300" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Select a Commitment</h3>
                        <p>Choose a commitment from the sidebar to explore its specific measures and requirements.</p>
                    </div>
                )}
            </div>
        </div>
    );
};
